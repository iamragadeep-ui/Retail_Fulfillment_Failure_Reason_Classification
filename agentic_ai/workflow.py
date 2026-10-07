from __future__ import annotations

import uuid
from typing import Any, Dict, List

from langgraph.graph import END, StateGraph

from .agents import infer_agents_for_case
from .mock_services import get_order_status_snapshot
from .prompts import PROMPT_REGISTRY
from .rag import PolicyRAGService
from .security import input_guardrails, output_guardrails
from .state import FulfillmentState
from .tools import ToolExecutor

from .guardrails.input_guardrail import InputGuardrail
from .guardrails.planning_guardrail import PlanningGuardrail
from .guardrails.tool_guardrail import ToolGuardrail
from .guardrails.action_guardrail import ActionGuardrail
from .guardrails.human_approval import HumanApprovalGuardrail
from .guardrails.output_guardrail import OutputGuardrail

input_policy_guardrail = InputGuardrail()
planning_policy_guardrail = PlanningGuardrail()
tool_policy_guardrail = ToolGuardrail()
action_policy_guardrail = ActionGuardrail()
human_approval_guardrail = HumanApprovalGuardrail()
output_policy_guardrail = OutputGuardrail()


def _build_status_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    order_data = state.get("order_data", {})
    return {
        "payment_status": order_data.get("payment_status", "UNKNOWN"),
        "inventory_status": order_data.get("inventory_status", "UNKNOWN"),
        "warehouse_status": order_data.get("warehouse_status", "UNKNOWN"),
        "carrier_status": order_data.get("carrier_status", "UNKNOWN"),
        "shipping_address_status": order_data.get("shipping_address_status", "UNKNOWN"),
    }


def _normalize(reason: str | None) -> str:
    return (reason or "UNKNOWN_REQUIRES_REVIEW").strip()


def _determine_failure_reason(state: Dict[str, Any]) -> Dict[str, Any]:
    order_data = state.get("order_data", {})
    payment = order_data.get("payment_status")
    inventory = order_data.get("inventory_status")
    warehouse = order_data.get("warehouse_status")
    carrier = order_data.get("carrier_status")
    address = order_data.get("shipping_address_status")

    if payment == "FAILED":
        reason = "PAYMENT_FAILURE"
        severity = "HIGH"
        recommended = "Retry payment authorization and contact the customer if the card is declined."
    elif inventory == "OUT_OF_STOCK":
        reason = "INVENTORY_SHORTAGE"
        severity = "HIGH"
        recommended = "Create a replenishment or substitute-item action and update customer communication."
    elif warehouse == "PICKING_DELAYED":
        reason = "WAREHOUSE_PROCESSING_DELAY"
        severity = "MEDIUM"
        recommended = "Escalate warehouse queue backlog and monitor fulfillment SLA."
    elif carrier == "DELAYED" and payment == "SUCCESS" and inventory == "AVAILABLE" and warehouse in {"DISPATCHED", "PICKING_DELAYED"}:
        reason = "CARRIER_DELAY"
        severity = "MEDIUM"
        recommended = "Open a carrier delivery exception investigation and provide the customer with a revised ETA."
    elif address == "INVALID":
        reason = "ADDRESS_ISSUE"
        severity = "MEDIUM"
        recommended = "Request address correction and reattempt carrier delivery after validation."
    elif any(value in {"UNKNOWN", ""} for value in [payment, inventory, warehouse, carrier, address]):
        reason = "UNKNOWN_REQUIRES_REVIEW"
        severity = "MEDIUM"
        recommended = "Collect missing operational evidence and send the case to a human reviewer."
    else:
        reason = "UNKNOWN_REQUIRES_REVIEW"
        severity = "MEDIUM"
        recommended = "Review case details and evidence quality before automatic classification."

    return {
        "failure_reason": reason,
        "severity": severity,
        "recommended_action": recommended,
        "requires_human_review": reason == "UNKNOWN_REQUIRES_REVIEW",
    }


def case_intake_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state.setdefault("case_id", f"CASE-{uuid.uuid4().hex[:8]}")
    order_id = state.get("order_id") or "ORD123"
    state["order_id"] = order_id
    state["customer_id"] = state.get("customer_id") or "CUST1001"
    state["sku"] = state.get("sku") or "SKU-778"
    if not state.get("failure_description"):
        state["failure_description"] = state.get("request") or "Fulfillment failure investigation requested."
    order_data = get_order_status_snapshot(order_id)
    state["order_data"] = order_data
    state["inventory_data"] = {"sku": state["sku"], "status": order_data.get("inventory_status", "UNKNOWN")}
    state["payment_data"] = {"order_id": order_id, "status": order_data.get("payment_status", "UNKNOWN")}
    state["warehouse_data"] = {"order_id": order_id, "status": order_data.get("warehouse_status", "UNKNOWN")}
    state["carrier_data"] = {"order_id": order_id, "status": order_data.get("carrier_status", "UNKNOWN")}
    state["address_data"] = {"order_id": order_id, "status": order_data.get("shipping_address_status", "UNKNOWN")}
    state["messages"] = state.get("messages", []) + [f"Case {state['case_id']} added for order {order_id}."]
    return state


def supervisor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["intent"] = "fulfillment_failure_investigation"
    state["routing_confidence"] = 0.96
    state["messages"] = state.get("messages", []) + ["Supervisor orchestrating investigation."]
    return state


def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["plan"] = {
        "goal": "Determine the primary fulfillment failure reason and validate the root cause using evidence.",
        "steps": [
            "Review order state",
            "Validate payment status",
            "Verify inventory and warehouse conditions",
            "Inspect carrier and address issues",
            "Retrieve policy evidence",
            "Classify failure reason",
            "Review the classification for contradictions",
            "Validate and finalize the decision",
        ],
        "dependencies": [
            "order",
            "inventory",
            "payment",
            "warehouse",
            "carrier",
            "policy"
        ],
        "required_agents": [
            "order",
            "inventory",
            "payment",
            "warehouse",
            "carrier",
            "policy",
            "classifier"
        ],
        "risk_level": "MEDIUM",
        "requires_human_approval": False,
    }

    # Mentor-defined planning guardrail
    planning_result = planning_policy_guardrail.validate(
        state["plan"]["steps"]
    )

    if not planning_result["allowed"]:
        state["guardrail_status"] = "BLOCKED"
        state["guardrail_reason"] = planning_result["reason"]
        state["errors"] = state.get("errors", []) + [
            planning_result["reason"]
        ]
        state["messages"] = state.get("messages", []) + [
            "Investigation plan blocked by planning guardrail."
        ]
        return state

    state["guardrail_status"] = "ALLOWED"
    state["guardrail_reason"] = planning_result["reason"]

    state["current_step"] = "plan_created"
    state["completed_steps"] = ["plan_created"]

    state["messages"] = state.get("messages", []) + [
        "Investigation plan created and validated."
    ]

    return state


def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    status_summary = _build_status_summary(state)
    selected = infer_agents_for_case(status_summary)
    state["selected_agents"] = selected
    state["routing_confidence"] = 0.9 if selected else 0.4
    state["messages"] = state.get("messages", []) + [f"Router selected agents: {', '.join(selected)}."]
    return state

def specialized_agents_node(state: Dict[str, Any]) -> Dict[str, Any]:
    findings: Dict[str, Any] = {}

    for agent in state.get("selected_agents", []):
        order_data = state.get("order_data", {})

        if agent == "order":
            findings[agent] = {
                "status": "completed",
                "summary": f"Order {order_data.get('order_id')} has status {order_data.get('order_status')}."
            }

        elif agent == "inventory":
            findings[agent] = {
                "status": "completed",
                "summary": f"Inventory status: {order_data.get('inventory_status')}."
            }

        elif agent == "payment":
            findings[agent] = {
                "status": "completed",
                "summary": f"Payment status: {order_data.get('payment_status')}."
            }

        elif agent == "warehouse":
            findings[agent] = {
                "status": "completed",
                "summary": f"Warehouse status: {order_data.get('warehouse_status')}."
            }

        elif agent == "carrier":
            findings[agent] = {
                "status": "completed",
                "summary": f"Carrier status: {order_data.get('carrier_status')}."
            }

        elif agent == "address":
            findings[agent] = {
                "status": "completed",
                "summary": f"Address status: {order_data.get('shipping_address_status')}."
            }

        elif agent == "policy":
            findings[agent] = {
                "status": "completed",
                "summary": "Policy retrieval queued."
            }

    state["agent_findings"] = findings

    state["messages"] = state.get("messages", []) + [
        "Specialized agents completed investigation tasks."
    ]

    return state


def input_guardrails_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the request using both the existing security checks
    and the mentor-defined input guardrail policy.
    """

    payload = {
        "order_id": state.get("order_id"),
        "customer_id": state.get("customer_id"),
        "failure_description": state.get("failure_description"),
        "request": state.get("request"),
    }

    # Existing project security checks
    checks = input_guardrails(payload)

    state["messages"] = state.get("messages", []) + [
        "Input guardrails checked."
    ]

    state["errors"] = []

    if checks["prompt_injection_detected"] or checks["secret_detected"]:
        state["errors"].append(
            "Unsafe request content detected."
        )

        state["guardrail_status"] = "BLOCKED"
        state["guardrail_reason"] = (
            "Existing security guardrail rejected the request."
        )

        return state

    # Mentor-defined input guardrail
    user_request = (
        state.get("failure_description")
        or state.get("request")
        or ""
    )

    policy_result = input_policy_guardrail.validate(user_request)

    if not policy_result["allowed"]:
        state["errors"].append(policy_result["reason"])

        state["guardrail_status"] = "BLOCKED"
        state["guardrail_reason"] = policy_result["reason"]

        return state

    state["guardrail_status"] = "ALLOWED"
    state["guardrail_reason"] = policy_result["reason"]

    return state

def route_after_input_guardrails(state: Dict[str, Any]) -> str:
    """
    Stop execution when input guardrails reject the request.
    """

    if state.get("guardrail_status") == "BLOCKED":
        return "blocked"

    return "continue"

def route_after_planning_guardrails(state: Dict[str, Any]) -> str:
    """
    Stop execution when planning guardrails reject the plan.
    """
    if state.get("guardrail_status") == "BLOCKED":
        return "blocked"

    return "continue"


def route_after_tool_guardrails(state: Dict[str, Any]) -> str:
    """
    Stop execution when tool guardrails block the action
    or when human approval is required.
    """
    if state.get("guardrail_status") in {"BLOCKED", "WAITING_FOR_APPROVAL"}:
        return "blocked"

    return "continue"

def tool_execution_node(state: Dict[str, Any]) -> Dict[str, Any]:
    executor = ToolExecutor()
    tool_results: List[Dict[str, Any]] = []

    for agent in state.get("selected_agents", []):

        if agent == "order":
            tool_name = "order_lookup"
            parameters = {
                "order_id": state["order_id"]
            }

        elif agent == "inventory":
            tool_name = "inventory_lookup"
            parameters = {
                "sku": state.get("sku"),
                "order_id": state.get("order_id")
            }

        elif agent == "payment":
            tool_name = "payment_lookup"
            parameters = {
                "order_id": state.get("order_id")
            }

        elif agent == "warehouse":
            tool_name = "warehouse_lookup"
            parameters = {
                "order_id": state.get("order_id")
            }

        elif agent == "carrier":
            tool_name = "carrier_lookup"
            parameters = {
                "order_id": state.get("order_id")
            }

        elif agent == "address":
            tool_name = "address_validation"
            parameters = {
                "order_id": state.get("order_id")
            }

        elif agent == "policy":
            tool_name = "policy_retrieval"
            parameters = {
                "query": (
                    state.get("failure_description")
                    or state.get("request")
                )
            }

        else:
            continue

        # Mentor-defined tool guardrail
        tool_check = tool_policy_guardrail.validate(
            tool_name,
            parameters
        )

        if not tool_check["allowed"]:
            state["guardrail_status"] = "BLOCKED"
            state["guardrail_reason"] = tool_check["reason"]
            state["errors"] = state.get("errors", []) + [
                tool_check["reason"]
            ]
            state["messages"] = state.get("messages", []) + [
                f"Tool execution blocked: {tool_name}"
            ]
            return state

              # Describe the operation that is about to execute
        action_description = f"Execute approved read-only tool {tool_name}"

        # Mentor-defined action guardrail
        action_check = action_policy_guardrail.validate(
            action_description,
            human_approved=False
        )

        if action_check["status"] == "BLOCKED":
            state["guardrail_status"] = "BLOCKED"
            state["guardrail_reason"] = action_check["reason"]
            state["errors"] = state.get("errors", []) + [
                action_check["reason"]
            ]
            return state

        if action_check["requires_approval"]:
            approval_check = human_approval_guardrail.check(
                action_description,
                approved=False
            )

            state["guardrail_status"] = "WAITING_FOR_APPROVAL"
            state["guardrail_reason"] = approval_check["reason"]
            state["human_review_status"] = "WAITING_FOR_APPROVAL"

            state["messages"] = state.get("messages", []) + [
                "Execution stopped pending explicit human approval."
            ]

            return state

        # Execute only after guardrail approval
        result = executor.execute(
            tool_name,
            **parameters
        )

        tool_results.append({
            "agent": agent,
            "tool": result.name,
            "result": result.data,
            "status": result.status
        })


def policy_retrieval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    query = state.get("failure_description") or state.get("request") or "fulfillment failure"
    rag = PolicyRAGService()
    docs = rag.retrieve(query)
    state["retrieved_documents"] = rag.validate_retrieved_documents(docs)
    state["retrieved_context"] = [doc["content"] for doc in state["retrieved_documents"]]
    state["citations"] = [doc["source"] for doc in state["retrieved_documents"]]
    return state


def classification_node(state: Dict[str, Any]) -> Dict[str, Any]:
    reason = _determine_failure_reason(state)
    evidence_list = []
    order_data = state.get("order_data", {})
    if order_data.get("payment_status") == "SUCCESS":
        evidence_list.append("Payment completed successfully")
    if order_data.get("payment_status") == "FAILED":
        evidence_list.append("Payment failed")
    if order_data.get("inventory_status") == "AVAILABLE":
        evidence_list.append("Inventory available")
    elif order_data.get("inventory_status") == "OUT_OF_STOCK":
        evidence_list.append("Inventory shortage identified")
    if order_data.get("warehouse_status") == "DISPATCHED":
        evidence_list.append("Warehouse dispatched the order")
    elif order_data.get("warehouse_status") == "PICKING_DELAYED":
        evidence_list.append("Warehouse processing was delayed")
    if order_data.get("carrier_status") == "DELAYED":
        evidence_list.append("Carrier delivery is delayed")
    if order_data.get("shipping_address_status") == "INVALID":
        evidence_list.append("Shipping address validation failed")

    confidence = 0.96 if reason["failure_reason"] != "UNKNOWN_REQUIRES_REVIEW" else 0.52
    state["classification"] = {
        "failure_reason": reason["failure_reason"],
        "confidence_score": confidence,
        "severity": reason["severity"],
        "evidence": evidence_list,
        "missing_evidence": [],
        "explanation": "Operational evidence points to the most likely root cause based on the order lifecycle and evidence availability.",
        "recommended_action": reason["recommended_action"],
        "requires_human_review": reason["requires_human_review"],
    }
    state["failure_reason"] = reason["failure_reason"]
    state["confidence_score"] = confidence
    state["severity"] = reason["severity"]
    state["evidence"] = evidence_list
    state["missing_evidence"] = []
    state["recommended_action"] = reason["recommended_action"]
    state["requires_human_review"] = reason["requires_human_review"]
    return state


def critic_node(state: Dict[str, Any]) -> Dict[str, Any]:
    criticism = {
        "supports_classification": True,
        "contradictory_signals": [],
        "missing_information": [],
        "confidence_too_high": False,
        "notes": "The evidence aligns with the selected failure path and policy guidance."
    }
    if state.get("failure_reason") == "UNKNOWN_REQUIRES_REVIEW":
        criticism["missing_information"] = ["Missing payment, inventory, or carrier state information."]
    state["critic_result"] = criticism
    return state


def reviewer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("failure_reason") == "UNKNOWN_REQUIRES_REVIEW":
        review = "HUMAN_REVIEW"
    elif state.get("confidence_score", 0) >= 0.8:
        review = "APPROVE"
    else:
        review = "REVISE"
    state["review_result"] = review
    return state


def validator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    failure_reason = _normalize(state.get("failure_reason"))
    allowed = {"INVENTORY_SHORTAGE", "PAYMENT_FAILURE", "WAREHOUSE_PROCESSING_DELAY", "CARRIER_DELAY", "ADDRESS_ISSUE", "DAMAGED_ITEM", "ORDER_CANCELLATION", "CUSTOMER_UNAVAILABLE", "SYSTEM_ERROR", "FRAUD_OR_RISK_HOLD", "UNKNOWN_REQUIRES_REVIEW"}
    valid = failure_reason in allowed and 0.0 <= float(state.get("confidence_score", 0)) <= 1.0 and bool(state.get("evidence"))
    state["validation_result"] = {
        "valid": valid,
        "taxonomy_valid": failure_reason in allowed,
        "confidence_valid": 0.0 <= float(state.get("confidence_score", 0)) <= 1.0,
        "evidence_present": bool(state.get("evidence")),
        "warnings": [] if valid else ["Result failed validation checks."],
    }
    return state


def final_decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    failure_reason = _normalize(state.get("failure_reason"))
    if failure_reason == "UNKNOWN_REQUIRES_REVIEW":
        decision = "HUMAN_REVIEW"
    elif state.get("validation_result", {}).get("valid") and float(state.get("confidence_score", 0)) >= 0.8:
        decision = "AUTO_CLASSIFIED"
    elif state.get("critic_result", {}).get("contradictory_signals"):
        decision = "HUMAN_REVIEW"
    else:
        decision = "AUTO_CLASSIFIED"
    state["final_decision"] = decision
    state["final_response"] = (
        f"Order {state.get('order_id')} classified as {failure_reason} with confidence {float(state.get('confidence_score', 0)):.0%}. "
        f"Decision: {decision}. Recommended action: {state.get('recommended_action')}"
    )
    state["messages"] = state.get("messages", []) + [f"Final decision set to {decision}."]
    return state


def output_guardrails_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Existing project output security guardrail
    state = output_guardrails(state)

    final_response = state.get("final_response", "")

    # Mentor-defined output guardrail
    output_check = output_policy_guardrail.validate(
        final_response,
        execution_success=len(state.get("errors", [])) == 0
    )

    if not output_check["allowed"]:
        state["guardrail_status"] = "BLOCKED"
        state["guardrail_reason"] = output_check["reason"]
        state["errors"] = state.get("errors", []) + [
            output_check["reason"]
        ]
        state["messages"] = state.get("messages", []) + [
            "Final response blocked by output guardrail."
        ]

        # Do not expose the unsafe response
        state["final_response"] = (
            "Final response blocked by output safety validation."
        )

        return state

    state["guardrail_status"] = "ALLOWED"
    state["guardrail_reason"] = output_check["reason"]

    state["messages"] = state.get("messages", []) + [
        "Final response passed output guardrail validation."
    ]

    return state


def route_after_validator(state: Dict[str, Any]) -> str:
    if state.get("validation_result", {}).get("valid"):
        return "final_decision"
    return "supervisor"


def route_after_reviewer(state: Dict[str, Any]) -> str:
    decision = (state.get("review_result") or "").upper()
    if decision == "HUMAN_REVIEW":
        return "human_review"
    if decision == "REVISE":
        return "revise"
    return "approve"


def build_graph() -> Any:
    workflow = StateGraph(FulfillmentState)
    workflow.add_node("input_guardrails", input_guardrails_node)
    workflow.add_node("case_intake", case_intake_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("router", router_node)
    workflow.add_node("specialized_agents", specialized_agents_node)
    workflow.add_node("tool_execution", tool_execution_node)
    workflow.add_node("policy_retrieval", policy_retrieval_node)
    workflow.add_node("classify_case", classification_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("finalize_decision", final_decision_node)
    workflow.add_node("output_guardrails", output_guardrails_node)

    workflow.set_entry_point("input_guardrails")
    workflow.add_conditional_edges(
    "input_guardrails",
    route_after_input_guardrails,
    {
        "continue": "case_intake",
        "blocked": END,
    },
)
    workflow.add_edge("case_intake", "supervisor")
    workflow.add_edge("supervisor", "planner")
    workflow.add_conditional_edges(
    "planner",
    route_after_planning_guardrails,
    {
        "continue": "router",
        "blocked": END,
    },
)
    workflow.add_edge("router", "specialized_agents")
    workflow.add_edge("specialized_agents", "tool_execution")
    workflow.add_conditional_edges(
    "tool_execution",
    route_after_tool_guardrails,
    {
        "continue": "policy_retrieval",
        "blocked": END,
    },
)
    workflow.add_edge("policy_retrieval", "classify_case")
    workflow.add_edge("classify_case", "critic")
    workflow.add_edge("critic", "reviewer")
    workflow.add_conditional_edges("reviewer", route_after_reviewer, {"approve": "validator", "revise": "planner", "human_review": "finalize_decision"})
    workflow.add_conditional_edges("validator", route_after_validator, {"final_decision": "finalize_decision", "supervisor": "supervisor"})
    workflow.add_edge("finalize_decision", "output_guardrails")
    workflow.add_edge("output_guardrails", END)

    return workflow.compile()


def analyze_fulfillment_case(case_input: Dict[str, Any]) -> Dict[str, Any]:
    graph = build_graph()
    state = {
        "case_id": case_input.get("case_id") or f"CASE-{uuid.uuid4().hex[:8]}",
        "order_id": case_input.get("order_id", "ORD123"),
        "customer_id": case_input.get("customer_id", "CUST1001"),
        "sku": case_input.get("sku", "SKU-778"),
        "request": case_input.get("failure_description") or case_input.get("request") or "Fulfillment failure analysis requested.",
        "failure_description": case_input.get("failure_description") or case_input.get("request") or "Fulfillment failure analysis requested.",
        "messages": [],
    }
    final_state = graph.invoke(state)
    final_state["workflow_id"] = final_state.get("case_id")
    return final_state
