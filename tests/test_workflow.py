from agentic_ai.workflow import analyze_fulfillment_case


def test_ord123_carrier_delay_demo_case():
    result = analyze_fulfillment_case({
        "order_id": "ORD123",
        "customer_id": "CUST1001",
        "sku": "SKU-778",
        "failure_description": "Order ORD123 was expected yesterday but has not arrived. Payment succeeded, inventory was available, and the warehouse dispatched the package, but carrier tracking shows a delivery exception.",
    })
    assert result["failure_reason"] == "CARRIER_DELAY"
    assert result["final_decision"] == "AUTO_CLASSIFIED"
    assert result["confidence_score"] >= 0.8


def test_ord124_inventory_shortage():
    result = analyze_fulfillment_case({
        "order_id": "ORD124",
        "customer_id": "CUST1002",
        "sku": "SKU-201",
        "failure_description": "Inventory unavailable for the order and fulfillment has not started.",
    })
    assert result["failure_reason"] == "INVENTORY_SHORTAGE"
    assert result["final_decision"] == "AUTO_CLASSIFIED"


def test_ord127_unknown_requires_review():
    result = analyze_fulfillment_case({
        "order_id": "ORD127",
        "customer_id": "CUST1005",
        "sku": "SKU-999",
        "failure_description": "Multiple statuses are unknown and insufficient evidence exists.",
    })
    assert result["failure_reason"] == "UNKNOWN_REQUIRES_REVIEW"
    assert result["final_decision"] == "HUMAN_REVIEW"
