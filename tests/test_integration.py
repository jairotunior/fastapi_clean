"""Integration tests: full HTTP flow with auth and persistence."""

import pytest
from fastapi import status

from fastapi_clean.core.config import settings

pytestmark = pytest.mark.skipif(
    not settings.database_url,
    reason="DATABASE_URL required for integration tests",
)


def test_login_create_order_list_and_get_order(client):
    """Login, create an order, list orders, and fetch the order by id."""
    # Login
    login_resp = client.post(
        f"{settings.api_v1_prefix}/auth/login",
        json={"username": "jairo", "password": "1234"},
    )
    assert login_resp.status_code == status.HTTP_200_OK
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create order
    create_payload = {
        "customer_id": "cust-integration-1",
        "items": [{"sku": "SKU-001", "quantity": 2}, {"sku": "SKU-002", "quantity": 1}],
    }
    create_resp = client.post(
        f"{settings.api_v1_prefix}/orders",
        json=create_payload,
        headers=headers,
    )
    assert create_resp.status_code == status.HTTP_201_CREATED
    created = create_resp.json()
    assert created["customer_id"] == create_payload["customer_id"]
    assert len(created["items"]) == 2
    assert created["status"] == "created"
    order_id = created["id"]

    # List orders
    list_resp = client.get(f"{settings.api_v1_prefix}/orders", headers=headers)
    assert list_resp.status_code == status.HTTP_200_OK
    orders = list_resp.json()
    assert isinstance(orders, list)
    ids = [o["id"] for o in orders]
    assert order_id in ids

    # Get order by id
    get_resp = client.get(
        f"{settings.api_v1_prefix}/orders/{order_id}",
        headers=headers,
    )
    assert get_resp.status_code == status.HTTP_200_OK
    order = get_resp.json()
    assert order["id"] == order_id
    assert order["customer_id"] == create_payload["customer_id"]
    assert order["items"] == create_payload["items"]


def test_orders_require_auth(client):
    """Orders endpoints return 401 when no token is provided."""
    list_resp = client.get(f"{settings.api_v1_prefix}/orders")
    assert list_resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_rejects_invalid_credentials(client):
    """Login returns 401 for wrong username/password."""
    resp = client.post(
        f"{settings.api_v1_prefix}/auth/login",
        json={"username": "wrong", "password": "wrong"},
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
