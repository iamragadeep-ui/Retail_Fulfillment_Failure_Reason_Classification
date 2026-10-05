from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class PolicyDocument:
    title: str
    content: str
    tags: List[str]
    source: str


POLICY_DOCUMENTS: List[PolicyDocument] = [
    PolicyDocument(
        title="Delivery Delay Policy",
        content="When a shipment is delayed after warehouse dispatch and carrier status shows an exception, classify the issue as CARRIER_DELAY if upstream payment, inventory, and warehouse steps succeeded.",
        tags=["carrier", "delivery", "delay", "shipment"],
        source="policy/delivery-delay.md",
    ),
    PolicyDocument(
        title="Inventory Shortage Policy",
        content="If inventory is unavailable or reserved stock is insufficient for the SKU, classify as INVENTORY_SHORTAGE and trigger replenishment or backorder review.",
        tags=["inventory", "stock", "shortage", "backorder"],
        source="policy/inventory-shortage.md",
    ),
    PolicyDocument(
        title="Payment Failure Policy",
        content="If payment authorization or capture fails before fulfillment begins, classify as PAYMENT_FAILURE and route to payment recovery or customer contact.",
        tags=["payment", "authorization", "capture", "failed"],
        source="policy/payment-failure.md",
    ),
    PolicyDocument(
        title="Warehouse Exception Policy",
        content="If the warehouse status indicates queue delay, picking delay, or process backlog, classify as WAREHOUSE_PROCESSING_DELAY when upstream dependencies succeeded.",
        tags=["warehouse", "picking", "delay", "processing"],
        source="policy/warehouse-delay.md",
    ),
    PolicyDocument(
        title="Address Validation Policy",
        content="When shipping address validation fails or carrier rejects the address, classify as ADDRESS_ISSUE and require correction before retrying delivery.",
        tags=["address", "invalid", "carrier rejection", "undeliverable"],
        source="policy/address-policy.md",
    ),
    PolicyDocument(
        title="Human Review Rule",
        content="If evidence is missing, contradictory, or operational facts are unknown, do not guess. Return UNKNOWN_REQUIRES_REVIEW and route to HUMAN_REVIEW.",
        tags=["human review", "unknown", "insufficient evidence"],
        source="policy/human-review.md",
    ),
    PolicyDocument(
        title="Escalation Policy",
        content="Critical business impact, conflicting evidence, or repeated workflow failures require escalation for human review or operational intervention.",
        tags=["escalation", "critical", "review"],
        source="policy/escalation.md",
    ),
]


class PolicyRAGService:
    def __init__(self, documents: List[PolicyDocument] | None = None) -> None:
        self.documents = documents or POLICY_DOCUMENTS

    def retrieve(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        lowered = (query or "").lower()
        matches: List[tuple[float, Dict[str, Any]]] = []
        for document in self.documents:
            score = 0.0
            for term in lowered.split():
                if term in document.content.lower() or term in " ".join(document.tags).lower():
                    score += 1.0
            if score > 0 or not lowered:
                matches.append((score, {"title": document.title, "content": document.content, "tags": document.tags, "source": document.source}))
        matches.sort(key=lambda item: item[0], reverse=True)
        ranked = [entry for _, entry in matches[:limit]]
        return ranked

    def validate_retrieved_documents(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid = []
        for doc in docs:
            if not doc.get("content"):
                continue
            if doc.get("content").startswith("This is a fictional"):
                continue
            valid.append(doc)
        return valid
