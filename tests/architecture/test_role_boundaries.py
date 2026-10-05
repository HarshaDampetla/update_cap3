import pytest
from fastapi import status


@pytest.mark.nfr("NFR-04")
def test_admin_endpoints_reject_customer_role(client, customer_token):
    """NFR-04: Requests to /api/admin/* from CUSTOMER return 403 Forbidden."""
    headers = {"Authorization": f"Bearer {customer_token}"}

    # 1. Attempt admin stock creation with customer token
    res = client.post(
        "/api/admin/stocks",
        headers=headers,
        json={
            "symbol": "FAKE",
            "name": "Fake Corp",
            "sector": "Tech",
            "exchange": "NASDAQ",
            "initial_price": "100.00"
        }
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # 2. Attempt role modification with customer token
    res = client.patch(
        "/api/admin/users/1/role",
        headers=headers,
        json={"role": "ADMIN"}
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # 3. Attempt admin order statistics with customer token
    res = client.get("/api/admin/statistics/orders", headers=headers)
    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.nfr("NFR-04")
def test_admin_endpoints_reject_unauthenticated_requests(client):
    """NFR-04: Unauthenticated requests to /api/admin/* return 401 Unauthorized."""
    res = client.get("/api/admin/statistics/orders")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
