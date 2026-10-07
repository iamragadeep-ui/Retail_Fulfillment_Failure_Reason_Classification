from typing import Optional

from fastapi import APIRouter, Query

from backend.app.observability.database import get_connection


router = APIRouter(
    prefix="/api/v1/observability",
    tags=["observability"],
)


@router.get("/logs")
def get_logs(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    log_level: Optional[str] = None,
    trace_id: Optional[str] = None,
    status: Optional[str] = None,
):
    connection = get_connection()

    try:
        conditions = []
        parameters = []

        if log_level:
            conditions.append("log_level = ?")
            parameters.append(log_level.upper())

        if trace_id:
            conditions.append("trace_id = ?")
            parameters.append(trace_id)

        if status:
            conditions.append("status = ?")
            parameters.append(status)

        where_clause = ""

        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        total = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM application_logs
            {where_clause}
            """,
            parameters,
        ).fetchone()[0]

        rows = connection.execute(
            f"""
            SELECT
                id,
                timestamp,
                log_level,
                service,
                environment,
                request_id,
                trace_id,
                session_id,
                agent_name,
                tool_name,
                model_name,
                endpoint,
                message,
                latency_ms,
                status,
                error_type,
                metadata
            FROM application_logs
            {where_clause}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            [*parameters, limit, offset],
        ).fetchall()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [dict(row) for row in rows],
        }

    finally:
        connection.close()

@router.get("/metrics")
def get_metrics():
    connection = get_connection()

    try:
        request_summary = connection.execute(
            """
            SELECT
                COUNT(*) AS total_requests,
                AVG(latency_ms) AS avg_latency_ms,
                MIN(latency_ms) AS min_latency_ms,
                MAX(latency_ms) AS max_latency_ms,
                SUM(
                    CASE
                        WHEN status = 'SUCCESS' THEN 1
                        ELSE 0
                    END
                ) AS successful_requests,
                SUM(
                    CASE
                        WHEN status = 'ERROR' THEN 1
                        ELSE 0
                    END
                ) AS failed_requests
            FROM request_metrics
            """
        ).fetchone()

        trace_summary = connection.execute(
            """
            SELECT
                COUNT(*) AS total_traces,
                SUM(
                    CASE
                        WHEN status = 'SUCCESS' THEN 1
                        ELSE 0
                    END
                ) AS successful_traces,
                SUM(
                    CASE
                        WHEN status = 'ERROR' THEN 1
                        ELSE 0
                    END
                ) AS failed_traces,
                AVG(duration_ms) AS avg_trace_duration_ms
            FROM traces
            """
        ).fetchone()

        guardrail_summary = connection.execute(
            """
            SELECT
                COUNT(*) AS total_guardrail_events,
                SUM(
                    CASE
                        WHEN decision = 'BLOCKED' THEN 1
                        ELSE 0
                    END
                ) AS blocked_events
            FROM guardrail_events
            """
        ).fetchone()

        error_summary = connection.execute(
            """
            SELECT COUNT(*) AS total_errors
            FROM error_events
            """
        ).fetchone()

        return {
            "requests": dict(request_summary),
            "traces": dict(trace_summary),
            "guardrails": dict(guardrail_summary),
            "errors": dict(error_summary),
        }

    finally:
        connection.close()

@router.get("/traces")
def get_traces(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = None,
):
    connection = get_connection()

    try:
        conditions = []
        parameters = []

        if status:
            conditions.append("status = ?")
            parameters.append(status)

        where_clause = ""

        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        total = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM traces
            {where_clause}
            """,
            parameters,
        ).fetchone()[0]

        rows = connection.execute(
            f"""
            SELECT
                id,
                trace_id,
                request_id,
                session_id,
                user_id,
                conversation_id,
                agent_run_id,
                service_name,
                start_time,
                end_time,
                duration_ms,
                status,
                metadata
            FROM traces
            {where_clause}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            [*parameters, limit, offset],
        ).fetchall()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [dict(row) for row in rows],
        }

    finally:
        connection.close()


@router.get("/traces/{trace_id}")
def get_trace_detail(trace_id: str):
    connection = get_connection()

    try:
        trace = connection.execute(
            """
            SELECT *
            FROM traces
            WHERE trace_id = ?
            """,
            (trace_id,),
        ).fetchone()

        if trace is None:
            return {
                "found": False,
                "trace_id": trace_id,
                "trace": None,
                "spans": [],
            }

        spans = connection.execute(
            """
            SELECT *
            FROM spans
            WHERE trace_id = ?
            ORDER BY id ASC
            """,
            (trace_id,),
        ).fetchall()

        return {
            "found": True,
            "trace_id": trace_id,
            "trace": dict(trace),
            "spans": [dict(row) for row in spans],
        }

    finally:
        connection.close()

@router.get("/drift")
def get_drift():
    connection = get_connection()

    try:
        drift_tables = {
            "model_drift": "model_drift",
            "data_drift": "data_drift",
            "prediction_drift": "prediction_drift",
            "concept_drift": "concept_drift",
            "prompt_drift": "prompt_drift",
            "retrieval_drift": "retrieval_drift",
            "output_drift": "output_drift",
        }

        result = {}

        for key, table_name in drift_tables.items():
            rows = connection.execute(
                f"""
                SELECT *
                FROM {table_name}
                ORDER BY id DESC
                LIMIT 50
                """
            ).fetchall()

            result[key] = [dict(row) for row in rows]

        return {
            "status": "ok",
            "drift": result,
        }

    finally:
        connection.close()