from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_analyze_endpoint_demo_case():
    payload = {
        "order_id": "ORD123",
        "customer_id": "CUST1001",
        "sku": "SKU-778",
        "payment_status": "SUCCESS",
        "inventory_status": "AVAILABLE",
        "warehouse_status": "DISPATCHED",
        "carrier_status": "DELAYED",
        "shipping_address_status": "VALID",
        "failure_description": "Order ORD123 was expected yesterday but has not arrived. Payment succeeded, inventory was available and the warehouse dispatched the package, but carrier tracking shows a delivery exception.",
    }
    response = client.post('/api/v1/cases/analyze', json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body['status'] in {'AUTO_CLASSIFIED', 'HUMAN_REVIEW'}
