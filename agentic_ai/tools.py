from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from pydantic import BaseModel, Field, ValidationError, field_validator


class ToolInputSchema(BaseModel):
    tool_id: str
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    permissions: List[str] = Field(default_factory=list)
    timeout: int = 10
    retry_policy: Dict[str, Any] = Field(default_factory=lambda: {"max_retries": 2, "backoff_seconds": 1})
    risk_classification: str = "LOW"
    audit_requirement: str = "required"


@dataclass
class ToolResult:
    tool_id: str
    name: str
    status: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class ToolExecutor:
    def __init__(self) -> None:
        self.available_tools = {
            "order_lookup": self.lookup_order,
            "inventory_lookup": self.lookup_inventory,
            "payment_lookup": self.lookup_payment,
            "warehouse_lookup": self.lookup_warehouse,
            "carrier_lookup": self.lookup_carrier,
            "address_validation": self.validate_address,
            "policy_retrieval": self.policy_retrieval,
        }

    def validate_tool_args(self, tool_name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name not in self.available_tools:
            raise ValueError(f"Unsupported tool: {tool_name}")
        if not isinstance(kwargs, dict):
            raise TypeError("Tool arguments must be a dictionary.")
        cleaned = {k: v for k, v in kwargs.items() if v is not None}
        return cleaned

    def lookup_order(self, order_id: str) -> Dict[str, Any]:
        from .mock_services import get_mock_order

        return get_mock_order(order_id)

    def lookup_inventory(self, sku: str, order_id: str | None = None) -> Dict[str, Any]:
        if sku and sku.startswith("SKU-"):
            stock = {"SKU-778": "AVAILABLE", "SKU-201": "OUT_OF_STOCK", "SKU-111": "AVAILABLE", "SKU-333": "AVAILABLE", "SKU-999": "UNKNOWN", "SKU-560": "AVAILABLE"}
            return {"sku": sku, "available_stock": 10 if stock.get(sku) == "AVAILABLE" else 0, "status": stock.get(sku, "UNKNOWN"), "reservation_status": "OK" if stock.get(sku) == "AVAILABLE" else "FAILED"}
        return {"sku": sku, "status": "UNKNOWN", "available_stock": 0, "reservation_status": "UNKNOWN"}

    def lookup_payment(self, order_id: str) -> Dict[str, Any]:
        from .mock_services import get_mock_order

        case = get_mock_order(order_id)
        payment_status = case.get("payment_status", "UNKNOWN")
        return {"order_id": order_id, "payment_status": payment_status, "authorization_status": "APPROVED" if payment_status == "SUCCESS" else "DECLINED", "capture_status": "CAPTURED" if payment_status == "SUCCESS" else "NOT_CAPTURED"}

    def lookup_warehouse(self, warehouse_id: str | None = None, order_id: str | None = None) -> Dict[str, Any]:
        from .mock_services import get_mock_order

        case = get_mock_order(order_id or "ORD123")
        warehouse_status = case.get("warehouse_status", "UNKNOWN")
        return {"warehouse_id": warehouse_id or case.get("warehouse_id", "UNKNOWN"), "warehouse_status": warehouse_status, "queue_length": 12 if warehouse_status == "PICKING_DELAYED" else 4, "dispatch_status": "DISPATCHED" if warehouse_status == "DISPATCHED" else "PENDING"}

    def lookup_carrier(self, tracking_id: str | None = None, order_id: str | None = None) -> Dict[str, Any]:
        from .mock_services import get_mock_order

        case = get_mock_order(order_id or "ORD123")
        carrier_status = case.get("carrier_status", "UNKNOWN")
        return {"tracking_id": tracking_id or case.get("tracking_id", ""), "carrier_status": carrier_status, "carrier_name": case.get("carrier_name", "UNKNOWN"), "delivery_exception": carrier_status in {"DELAYED", "DELIVERY_ATTEMPTED"}, "estimated_delivery": case.get("expected_delivery_date")}

    def validate_address(self, address_status: str | None = None, order_id: str | None = None) -> Dict[str, Any]:
        from .mock_services import get_mock_order

        case = get_mock_order(order_id or "ORD123")
        status = address_status or case.get("shipping_address_status", "UNKNOWN")
        return {"address_status": status, "is_valid": status == "VALID", "carrier_rejection": status == "INVALID", "needs_review": status in {"INVALID", "UNKNOWN"}}

    def policy_retrieval(self, query: str) -> Dict[str, Any]:
        return {"query": query, "documents": [{"title": "Delivery Exception Policy", "match": "Carrier delays are handled as delivery exceptions; if the order exceeds SLA and upstream operations succeeded, classify as CARRIER_DELAY.", "source": "policy/manual.md"}]}

    def execute(self, tool_name: str, **kwargs: Any) -> ToolResult:
        try:
            cleaned = self.validate_tool_args(tool_name, kwargs)
            data = self.available_tools[tool_name](**cleaned)
            return ToolResult(tool_id=tool_name, name=tool_name, status="SUCCESS", data=data)
        except Exception as exc:  # pragma: no cover - defensive path
            return ToolResult(tool_id=tool_name, name=tool_name, status="FAILED", error=str(exc))


TOOL_METADATA = {
    "order_lookup": {
        "tool_id": "order_lookup",
        "name": "Order Lookup Tool",
        "description": "Returns order-level information to assess lifecycle anomalies.",
        "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]},
        "output_schema": {"type": "object"},
        "permissions": ["order:read"],
        "timeout": 5,
        "retry_policy": {"max_retries": 2, "backoff_seconds": 1},
        "risk_classification": "LOW",
        "audit_requirement": "required",
    },
    "inventory_lookup": {
        "tool_id": "inventory_lookup",
        "name": "Inventory Lookup Tool",
        "description": "Retrieves inventory availability and reservation details.",
        "input_schema": {"type": "object", "properties": {"sku": {"type": "string"}, "order_id": {"type": "string"}}, "required": ["sku"]},
        "output_schema": {"type": "object"},
        "permissions": ["inventory:read"],
        "timeout": 5,
        "retry_policy": {"max_retries": 2, "backoff_seconds": 1},
        "risk_classification": "LOW",
        "audit_requirement": "required",
    },
    "payment_lookup": {
        "tool_id": "payment_lookup",
        "name": "Payment Lookup Tool",
        "description": "Provides payment status and authorization details.",
        "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]},
        "output_schema": {"type": "object"},
        "permissions": ["payment:read"],
        "timeout": 5,
        "retry_policy": {"max_retries": 2, "backoff_seconds": 1},
        "risk_classification": "LOW",
        "audit_requirement": "required",
    },
    "warehouse_lookup": {
        "tool_id": "warehouse_lookup",
        "name": "Warehouse Lookup Tool",
        "description": "Returns dispatch and warehouse processing status.",
        "input_schema": {"type": "object", "properties": {"warehouse_id": {"type": "string"}, "order_id": {"type": "string"}}, "required": ["order_id"]},
        "output_schema": {"type": "object"},
        "permissions": ["warehouse:read"],
        "timeout": 5,
        "retry_policy": {"max_retries": 2, "backoff_seconds": 1},
        "risk_classification": "LOW",
        "audit_requirement": "required",
    },
    "carrier_lookup": {
        "tool_id": "carrier_lookup",
        "name": "Carrier Tracking Tool",
        "description": "Returns delivery and shipment status from carrier systems.",
        "input_schema": {"type": "object", "properties": {"tracking_id": {"type": "string"}, "order_id": {"type": "string"}}, "required": ["order_id"]},
        "output_schema": {"type": "object"},
        "permissions": ["carrier:read"],
        "timeout": 5,
        "retry_policy": {"max_retries": 2, "backoff_seconds": 1},
        "risk_classification": "LOW",
        "audit_requirement": "required",
    },
    "address_validation": {
        "tool_id": "address_validation",
        "name": "Address Validation Tool",
        "description": "Validates shipping address and carrier acceptance.",
        "input_schema": {"type": "object", "properties": {"address_status": {"type": "string"}, "order_id": {"type": "string"}}, "required": ["order_id"]},
        "output_schema": {"type": "object"},
        "permissions": ["address:read"],
        "timeout": 5,
        "retry_policy": {"max_retries": 2, "backoff_seconds": 1},
        "risk_classification": "LOW",
        "audit_requirement": "required",
    },
    "policy_retrieval": {
        "tool_id": "policy_retrieval",
        "name": "Policy Retrieval Tool",
        "description": "Retrieves policy evidence from the knowledge base.",
        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        "output_schema": {"type": "object"},
        "permissions": ["policy:read"],
        "timeout": 10,
        "retry_policy": {"max_retries": 2, "backoff_seconds": 2},
        "risk_classification": "MEDIUM",
        "audit_requirement": "required",
    },
}
