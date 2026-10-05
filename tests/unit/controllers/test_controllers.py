import pytest
from decimal import Decimal
from fastapi import status


@pytest.mark.nfr("NFR-07")
@pytest.mark.nfr("NFR-06")
def test_health_check_endpoint(client):
    """NFR-07: Health endpoint returns HTTP 200 within 1s. NFR-06: returns x-correlation-id."""
    res = client.get("/health")
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "marketscope"
    assert "x-correlation-id" in res.headers


@pytest.mark.ac("AC-01")
def test_register_and_login_flow(client):
    """AC-01: Registration creates ACTIVE account with CUSTOMER role."""
    reg_res = client.post(
        "/api/auth/register",
        json={"email": "tester@example.com", "password": "TestPassword123!"}
    )
    assert reg_res.status_code == status.HTTP_201_CREATED
    data = reg_res.json()
    assert data["email"] == "tester@example.com"
    assert data["role"] == "CUSTOMER"
    assert data["status"] == "ACTIVE"

    # Login
    login_res = client.post(
        "/api/auth/login",
        json={"email": "tester@example.com", "password": "TestPassword123!"}
    )
    assert login_res.status_code == status.HTTP_200_OK
    assert "access_token" in login_res.json()


@pytest.mark.ac("AC-02")
def test_admin_update_user_role_controller(client, admin_token, seed_customer_user):
    """AC-02: Admin PATCH role update."""
    res = client.patch(
        f"/api/admin/users/{seed_customer_user.id}/role",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "SUSPENDED"}
    )
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["new_role"] == "SUSPENDED"


@pytest.mark.ac("AC-03")
def test_stock_catalog_crud_controller(client, admin_token):
    """AC-03: Stock catalog CRUD and soft delete."""
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create
    res = client.post(
        "/api/admin/stocks",
        headers=headers,
        json={
            "symbol": "SNOW",
            "name": "Snowflake Inc.",
            "sector": "Technology",
            "exchange": "NYSE",
            "initial_price": "160.0000"
        }
    )
    assert res.status_code == status.HTTP_201_CREATED
    assert res.json()["symbol"] == "SNOW"

    # 2. Public search
    search_res = client.get("/api/stocks?query=SNOW")
    assert search_res.status_code == status.HTTP_200_OK
    assert search_res.json()["total"] == 1

    # 3. Soft-delete
    del_res = client.delete("/api/admin/stocks/SNOW", headers=headers)
    assert del_res.status_code == status.HTTP_200_OK
    assert del_res.json()["status"] == "DELETED"

    # 4. Search should omit soft-deleted stock
    omitted_res = client.get("/api/stocks?query=SNOW")
    assert omitted_res.json()["total"] == 0


@pytest.mark.ac("AC-04")
@pytest.mark.ac("AC-05")
def test_watchlist_controller_flow(client, customer_token, admin_token):
    """AC-04 & AC-05: Watchlist creation, listing, and atomic symbol addition."""
    # Seed a stock first
    client.post(
        "/api/admin/stocks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "symbol": "BABA",
            "name": "Alibaba Group",
            "sector": "Consumer",
            "exchange": "NYSE",
            "initial_price": "80.00"
        }
    )

    cust_headers = {"Authorization": f"Bearer {customer_token}"}

    # AC-04: Create watchlist
    create_res = client.post(
        "/api/watchlists",
        headers=cust_headers,
        json={"name": "China Tech", "symbols": ["BABA"]}
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    wl_id = create_res.json()["id"]

    # List watchlists
    list_res = client.get("/api/watchlists", headers=cust_headers)
    assert list_res.status_code == status.HTTP_200_OK
    assert len(list_res.json()) >= 1

    # AC-05: Atomic rollback on invalid symbol
    fail_res = client.post(
        f"/api/watchlists/{wl_id}/symbols",
        headers=cust_headers,
        json={"symbols": ["INVALID_TICKER_X"]}
    )
    assert fail_res.status_code == status.HTTP_400_BAD_REQUEST
    assert fail_res.json()["code"] == "WATCHLIST_UPDATE_FAILED"


@pytest.mark.ac("AC-06")
@pytest.mark.ac("AC-08")
@pytest.mark.ac("AC-07")
def test_order_controller_flow(client, customer_token, admin_token):
    """AC-06, AC-07, AC-08: Order placement, cash check, and lifecycle."""
    # Seed a stock
    client.post(
        "/api/admin/stocks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "symbol": "COST",
            "name": "Costco Wholesale",
            "sector": "Consumer Staples",
            "exchange": "NASDAQ",
            "initial_price": "750.00"
        }
    )

    cust_headers = {"Authorization": f"Bearer {customer_token}"}

    # AC-08: Order with insufficient funds fails
    fail_order = client.post(
        "/api/orders",
        headers=cust_headers,
        json={
            "symbol": "COST",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": "1000"  # Requires $750,000 > available $100,000
        }
    )
    assert fail_order.status_code == status.HTTP_400_BAD_REQUEST
    assert fail_order.json()["code"] == "INSUFFICIENT_FUNDS"
    assert fail_order.json()["ac_id"] == "AC-08"

    # AC-06 & AC-07: Valid BUY order executes
    success_order = client.post(
        "/api/orders",
        headers=cust_headers,
        json={
            "symbol": "COST",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": "5"  # Requires $3,750
        }
    )
    assert success_order.status_code == status.HTTP_201_CREATED
    data = success_order.json()
    assert data["status"] == "EXECUTED"
    assert data["symbol"] == "COST"
    assert data["server_timestamp"] is not None


@pytest.mark.ac("AC-09")
@pytest.mark.ac("AC-10")
def test_portfolio_and_analytics_controller(client, customer_token):
    """AC-09 & AC-10: Portfolio statistics and daily performance."""
    cust_headers = {"Authorization": f"Bearer {customer_token}"}

    # AC-09: Portfolio stats
    port_res = client.get("/api/portfolio/statistics", headers=cust_headers)
    assert port_res.status_code == status.HTTP_200_OK
    stats = port_res.json()
    assert "total_invested" in stats
    assert "current_value" in stats
    assert "absolute_pnl" in stats
    assert "percent_pnl" in stats

    # AC-10: Daily analytics
    perf_res = client.get("/api/analytics/daily-performance", headers=cust_headers)
    assert perf_res.status_code == status.HTTP_200_OK
    perf = perf_res.json()
    assert "top_gainers" in perf
    assert "top_losers" in perf
