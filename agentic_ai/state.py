from typing import Any, Dict, List, TypedDict


class FulfillmentState(TypedDict, total=False):
    case_id: str
    order_id: str
    customer_id: str
    sku: str
    request: str
    failure_description: str
    messages: List[str]
    intent: str
    routing_confidence: float
    plan: Dict[str, Any]
    current_step: str
    completed_steps: List[str]
    selected_agents: List[str]
    order_data: Dict[str, Any]
    inventory_data: Dict[str, Any]
    payment_data: Dict[str, Any]
    warehouse_data: Dict[str, Any]
    carrier_data: Dict[str, Any]
    address_data: Dict[str, Any]
    agent_findings: Dict[str, Any]
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    retrieved_documents: List[Dict[str, Any]]
    retrieved_context: List[str]
    citations: List[str]
    classification: Dict[str, Any]
    failure_reason: str
    confidence_score: float
    severity: str
    evidence: List[str]
    missing_evidence: List[str]
    recommended_action: str
    critic_result: Dict[str, Any]
    review_result: str
    validation_result: Dict[str, Any]
    requires_human_review: bool
    human_review_status: str
    errors: List[str]
    retry_count: int
    token_usage: int
    cost: float
    final_decision: str
    final_response: str
