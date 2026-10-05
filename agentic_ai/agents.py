from __future__ import annotations

from typing import Any, Dict, List

SPECIALIZED_AGENTS: Dict[str, Dict[str, Any]] = {
    "order": {
        "name": "Order Agent",
        "responsibility": "Review order lifecycle, cancellation state, and anomalies.",
        "classifies": [],
    },
    "inventory": {
        "name": "Inventory Agent",
        "responsibility": "Inspect stock availability, reservations, and product status.",
        "classifies": ["INVENTORY_SHORTAGE"],
    },
    "payment": {
        "name": "Payment Agent",
        "responsibility": "Review authorization, capture, and decline data.",
        "classifies": ["PAYMENT_FAILURE"],
    },
    "warehouse": {
        "name": "Warehouse Agent",
        "responsibility": "Review warehouse processing queue and fulfillment center health.",
        "classifies": ["WAREHOUSE_PROCESSING_DELAY"],
    },
    "carrier": {
        "name": "Carrier Agent",
        "responsibility": "Inspect shipment tracking, delivery status, and exceptions.",
        "classifies": ["CARRIER_DELAY"],
    },
    "address": {
        "name": "Address Validation Agent",
        "responsibility": "Check address validity and delivery rejection issues.",
        "classifies": ["ADDRESS_ISSUE"],
    },
    "policy": {
        "name": "Policy/RAG Agent",
        "responsibility": "Retrieve policy evidence and business rules for the case.",
        "classifies": [],
    },
    "classifier": {
        "name": "Failure Classification Agent",
        "responsibility": "Combine all evidence and assign the final failure reason.",
        "classifies": ["CARRIER_DELAY", "INVENTORY_SHORTAGE", "PAYMENT_FAILURE", "WAREHOUSE_PROCESSING_DELAY", "ADDRESS_ISSUE", "UNKNOWN_REQUIRES_REVIEW"],
    },
    "critic": {
        "name": "Critic Agent",
        "responsibility": "Challenge the classification using contradictory or missing evidence.",
        "classifies": [],
    },
    "reviewer": {
        "name": "Reviewer Agent",
        "responsibility": "Approve, revise, or escalate the classification.",
        "classifies": [],
    },
    "validator": {
        "name": "Validator Agent",
        "responsibility": "Check required structure and taxonomy compliance.",
        "classifies": [],
    },
}


def infer_agents_for_case(status_summary: Dict[str, Any]) -> List[str]:
    selected: List[str] = ["order"]
    if status_summary.get("payment_status") in {"FAILED", "UNKNOWN"}:
        selected.append("payment")
    if status_summary.get("inventory_status") in {"OUT_OF_STOCK", "UNKNOWN"}:
        selected.append("inventory")
    if status_summary.get("warehouse_status") in {"PICKING_DELAYED", "DISPATCHED", "UNKNOWN"}:
        selected.append("warehouse")
    if status_summary.get("carrier_status") in {"DELAYED", "DELIVERY_ATTEMPTED", "UNKNOWN"}:
        selected.append("carrier")
    if status_summary.get("shipping_address_status") in {"INVALID", "UNKNOWN"}:
        selected.append("address")
    selected.append("policy")
    return list(dict.fromkeys(selected))
