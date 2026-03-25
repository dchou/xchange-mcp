"""Integration tests: real FastAPI server + fakeredis + mock ExchangeClient."""

from __future__ import annotations

import sys
import os
import json
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "xchange-mcp"))

import fakeredis.aioredis
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def app_with_mocks(mock_exchange_client):
    """Create FastAPI test app with fakeredis and mock ExchangeClient."""
    import main as main_module
    import server as server_module
    from config import Settings
    from session import SessionManager

    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    test_settings = Settings(
        redis_url="redis://localhost:6379/0",
        session_ttl=3600,
        max_pool_size=50,
        dryrun=False,
    )

    sm = SessionManager(fake_redis, test_settings)

    with patch("session.ExchangeClient") as MockClass:  # module-level import
        MockClass.create = AsyncMock(return_value=mock_exchange_client)
        server_module.set_session_manager(sm)
        yield sm, mock_exchange_client, MockClass

    await sm.close_all()
    await fake_redis.aclose()
    server_module.set_session_manager(None)


async def test_health_endpoint():
    from main import app
    with TestClient(app, raise_server_exceptions=False) as client:
        # health endpoint — should return 200 synchronously
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


async def test_init_and_fetch_balance_flow(app_with_mocks):
    sm, mock_client, MockClass = app_with_mocks
    from server import init_exchange, fetch_balance

    # Init
    result = await init_exchange(exchange_name="binance", api_key="k", api_secret="s")
    assert result["success"] is True
    session_id = result["session_id"]

    # Fetch balance
    bal_result = await fetch_balance(session_id=session_id)
    assert bal_result["success"] is True
    assert "balance" in bal_result


async def test_session_persists_across_requests(app_with_mocks):
    """Second get_client call should reuse the cached instance."""
    sm, mock_client, MockClass = app_with_mocks
    from server import init_exchange, fetch_balance, fetch_ticker

    result = await init_exchange(exchange_name="binance", api_key="k", api_secret="s")
    session_id = result["session_id"]

    await fetch_balance(session_id=session_id)
    await fetch_ticker(session_id=session_id, symbol="BTC/USDT")

    # ExchangeClient.create should only have been called once
    MockClass.create.assert_awaited_once()


async def test_close_exchange_cleans_up(app_with_mocks):
    from server import init_exchange, close_exchange, fetch_balance
    from error_handling import SessionNotFoundError

    sm, mock_client, MockClass = app_with_mocks

    result = await init_exchange(exchange_name="binance", api_key="k", api_secret="s")
    session_id = result["session_id"]

    # Close the session
    close_result = await close_exchange(session_id=session_id)
    assert close_result["success"] is True

    # Subsequent fetch_balance should return SESSION_NOT_FOUND error dict
    bal_result = await fetch_balance(session_id=session_id)
    assert bal_result["success"] is False
    assert bal_result["error_code"] == "SESSION_NOT_FOUND"
