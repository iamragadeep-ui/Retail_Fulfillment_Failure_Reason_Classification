from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agentic_ai.workflow import analyze_fulfillment_case
from .config import settings
from .database import SessionLocal, get_db, init_db
from .models import AgentRun, AuditLog, Case, Classification, HumanReview, WorkflowRun
from .schemas import CaseAnalyzeRequest, CaseResponse, DashboardStats, ErrorResponse, HealthResponse, ReviewSubmission
from .observability.context import TraceContext
from .observability.instrumentation import (
    end_span,
    end_trace,
    log_event,
    record_error,
    record_request_metric,
    start_span,
    start_trace,
)
from .observability.api import router as observability_router
from .observability.schema import initialize_observability_schema

app = FastAPI(title=settings.APP_NAME, version="1.0.0")
app.include_router(observability_router)

init_db()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    initialize_observability_schema()
    seed_demo_data()


@app.get("/health", response_model=HealthResponse)
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "backend", "version": "1.0.0"}


@app.post("/api/v1/cases/analyze", status_code=status.HTTP_200_OK)
def analyze_case(payload: CaseAnalyzeRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    case_id = f"CASE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{payload.order_id}"
    request_start = time.perf_counter()

    trace_context = TraceContext.create(
        user_id=payload.customer_id or "UNKNOWN",
        conversation_id=case_id,
    )

    start_trace(
        trace_context,
        service_name="retail-fulfillment-api",
        metadata={
            "case_id": case_id,
            "order_id": payload.order_id,
            "endpoint": "/api/v1/cases/analyze",
        },
    )

    api_span_id = start_span(
        trace_context,
        span_name="analyze_case",
        span_type="API",
        input_data={
            "case_id": case_id,
            "order_id": payload.order_id,
        },
    )

    log_event(
        trace_context,
        event="REQUEST_STARTED",
        message="Fulfillment case analysis request started.",
        endpoint="/api/v1/cases/analyze",
        status="RUNNING",
        metadata={"case_id": case_id},
    )
    case_record = Case(
        case_id=case_id,
        order_id=payload.order_id,
        customer_id=payload.customer_id or "UNKNOWN",
        sku=payload.sku or "UNKNOWN",
        failure_description=payload.failure_description,
        status="ANALYZING",
    )
    db.add(case_record)
    db.commit()
    db.refresh(case_record)

    workflow_input = payload.model_dump()
    workflow_input["case_id"] = case_id
    workflow_input["request"] = payload.failure_description

    workflow_start = time.perf_counter()

    workflow_span_id = start_span(
        trace_context,
        span_name="fulfillment_workflow",
        span_type="LANGGRAPH",
        parent_span_id=api_span_id,
        input_data={
            "case_id": case_id,
            "order_id": payload.order_id,
        },
    )

    try:
        result = analyze_fulfillment_case(workflow_input)

        workflow_duration_ms = (
            time.perf_counter() - workflow_start
        ) * 1000

        end_span(
            workflow_span_id,
            status="SUCCESS",
            duration_ms=workflow_duration_ms,
            output_data={
                "final_decision": result.get("final_decision"),
                "failure_reason": result.get("failure_reason"),
            },
        )

        log_event(
            trace_context,
            event="WORKFLOW_COMPLETED",
            message="LangGraph fulfillment workflow completed.",
            endpoint="/api/v1/cases/analyze",
            latency_ms=workflow_duration_ms,
            status="SUCCESS",
            metadata={"case_id": case_id},
        )

    except Exception as exc:
        workflow_duration_ms = (
            time.perf_counter() - workflow_start
        ) * 1000

        end_span(
            workflow_span_id,
            status="ERROR",
            duration_ms=workflow_duration_ms,
            error=str(exc),
        )

        record_error(
            trace_context,
            error_type=type(exc).__name__,
            error_message=str(exc),
            endpoint="/api/v1/cases/analyze",
            metadata={
                "case_id": case_id,
                "stage": "fulfillment_workflow",
            },
        )

        raise

    decision = result.get("final_decision") or "HUMAN_REVIEW"

    classification_record = Classification(
        case_id=case_record.id,
        failure_reason=result.get("failure_reason") or "UNKNOWN_REQUIRES_REVIEW",
        confidence_score=float(result.get("confidence_score") or 0.0),
        severity=result.get("severity") or "MEDIUM",
        decision=decision,
        explanation=result.get("classification", {}).get("explanation") or result.get("final_response") or "Classification generated by workflow.",
        recommended_action=result.get("recommended_action") or "Review case manually.",
    )
    db.add(classification_record)

    workflow_record = WorkflowRun(
        workflow_id=result.get("workflow_id") or case_id,
        case_id=case_id,
        status="COMPLETED",
    )
    db.add(workflow_record)

    for agent_name in result.get("selected_agents", []):
        run = AgentRun(
            case_id=case_record.id,
            workflow_id=result.get("workflow_id") or case_id,
            agent_name=agent_name,
            status="COMPLETED",
            input_summary=result.get("failure_description") or "N/A",
            output=str(result.get("agent_findings", {}).get(agent_name, {})),
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db.add(run)

    db.add(AuditLog(case_id=case_id, event_type="CASE_ANALYZED", payload=str(result)))
    db.commit()

    case_record.status = decision
    db.commit()

    response = {
        "case_id": case_id,
        "order_id": payload.order_id,
        "status": decision,
        "final_decision": decision,
        "workflow_id": result.get("workflow_id") or case_id,
        "classification": result.get("classification") or {
            "failure_reason": "UNKNOWN_REQUIRES_REVIEW",
            "confidence_score": 0.0,
            "severity": "MEDIUM",
            "evidence": [],
            "missing_evidence": ["No evidence available."],
            "explanation": "The workflow could not resolve the failure reason.",
            "recommended_action": "Escalate for manual review.",
            "requires_human_review": True,
        },
        "result": result,
    }

    request_duration_ms = (
        time.perf_counter() - request_start
    ) * 1000

    end_span(
        api_span_id,
        status="SUCCESS",
        duration_ms=request_duration_ms,
        output_data={
            "case_id": case_id,
            "final_decision": decision,
        },
    )

    end_trace(
        trace_context,
        status="SUCCESS",
        duration_ms=request_duration_ms,
        metadata={
            "case_id": case_id,
            "order_id": payload.order_id,
            "final_decision": decision,
        },
    )

    record_request_metric(
        trace_context,
        endpoint="/api/v1/cases/analyze",
        method="POST",
        latency_ms=request_duration_ms,
        status="SUCCESS",
        status_code=200,
        metadata={
            "case_id": case_id,
            "order_id": payload.order_id,
        },
    )

    log_event(
        trace_context,
        event="REQUEST_COMPLETED",
        message="Fulfillment case analysis request completed.",
        endpoint="/api/v1/cases/analyze",
        latency_ms=request_duration_ms,
        status="SUCCESS",
        metadata={
            "case_id": case_id,
            "final_decision": decision,
        },
    )

    return response
    return response


@app.get("/api/v1/cases")
def list_cases(db: Session = Depends(get_db)) -> Dict[str, Any]:
    cases = db.query(Case).order_by(Case.created_at.desc()).all()
    return {"items": [{"case_id": case.case_id, "order_id": case.order_id, "status": case.status, "created_at": case.created_at.isoformat()} for case in cases]}


@app.get("/api/v1/cases/{case_id}")
def get_case(case_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    classification = db.query(Classification).filter(Classification.case_id == case.id).order_by(Classification.created_at.desc()).first()
    return {
        "case_id": case.case_id,
        "order_id": case.order_id,
        "customer_id": case.customer_id,
        "sku": case.sku,
        "failure_description": case.failure_description,
        "status": case.status,
        "classification": {
            "failure_reason": classification.failure_reason if classification else None,
            "confidence_score": classification.confidence_score if classification else None,
            "severity": classification.severity if classification else None,
            "decision": classification.decision if classification else None,
            "recommended_action": classification.recommended_action if classification else None,
        },
    }


@app.get("/api/v1/dashboard")
def dashboard(db: Session = Depends(get_db)) -> Dict[str, Any]:
    total_cases = db.query(Case).count()
    auto_classified = db.query(Classification).filter(Classification.decision == "AUTO_CLASSIFIED").count()
    human_review = db.query(Classification).filter(Classification.decision == "HUMAN_REVIEW").count()
    critical = db.query(Classification).filter(Classification.decision == "CRITICAL_ESCALATION").count()
    latest_case = db.query(Case).order_by(Case.created_at.desc()).first()
    recent = db.query(Classification).order_by(Classification.created_at.desc()).limit(5).all()
    return {
        "stats": {
            "total_cases": total_cases,
            "auto_classified": auto_classified,
            "human_review": human_review,
            "critical": critical,
            "latest_case": latest_case.case_id if latest_case else "N/A",
        },
        "recent_decisions": [{
            "order_id": item.case_id,
            "failure_reason": item.failure_reason,
            "confidence": f"{item.confidence_score * 100:.0f}%",
            "decision": item.decision,
            "severity": item.severity,
            "reviewer": "SYSTEM",
            "created": item.created_at.isoformat(),
        } for item in recent],
    }


@app.get("/api/v1/reviews")
def list_reviews(db: Session = Depends(get_db)) -> Dict[str, Any]:
    reviews = db.query(HumanReview).order_by(HumanReview.created_at.desc()).all()
    return {"items": [{"case_id": review.case_id, "reviewer": review.reviewer, "decision": review.decision, "notes": review.notes} for review in reviews]}


@app.get("/api/v1/reviews/{case_id}")
def get_review(case_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    review = db.query(HumanReview).filter(HumanReview.case_id == case.id).order_by(HumanReview.created_at.desc()).first()
    if not review:
        return {"case_id": case_id, "decision": "PENDING", "notes": "No review recorded."}
    return {"case_id": case_id, "reviewer": review.reviewer, "decision": review.decision, "notes": review.notes}


@app.post("/api/v1/reviews/{case_id}")
def submit_review(case_id: str, payload: ReviewSubmission, db: Session = Depends(get_db)) -> Dict[str, Any]:
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    review = HumanReview(
        case_id=case.id,
        reviewer=payload.reviewer,
        original_classification=None,
        final_classification=payload.final_classification,
        decision=payload.decision,
        notes=payload.notes,
    )
    db.add(review)
    db.commit()
    return {"case_id": case_id, "status": "review_submitted", "decision": payload.decision}


@app.get("/api/v1/workflows/{workflow_id}")
def get_workflow(workflow_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    workflow_run = db.query(WorkflowRun).filter(WorkflowRun.workflow_id == workflow_id).first()
    if not workflow_run:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"workflow_id": workflow_run.workflow_id, "status": workflow_run.status, "case_id": workflow_run.case_id}


@app.get("/api/v1/agents/runs/{case_id}")
def get_agent_runs(case_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    runs = db.query(AgentRun).filter(AgentRun.case_id == case.id).all()
    return {"case_id": case_id, "runs": [{"agent_name": run.agent_name, "status": run.status, "output": run.output} for run in runs]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
