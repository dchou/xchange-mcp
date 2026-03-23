"""Pytest fixtures for MCP server tests."""

from __future__ import annotations

import sys
import os
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure library root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "xchange_mcp"))

import fakeredis.aioredis

from config import Settings
from session import SessionManager


# ---------------------------------------------------------------------------
# Settings fixture with small pool to make LRU tests practical
# ---------------------------------------------------------------------------

@pytest.fixture
def test_settings():
    return Settings(
        redis_url="redis://localhost:6379/0",  # not actually used — overridden by fake_redis
        session_ttl=3600,
        max_pool_size=3,
        dryrun=False,
    )


# ---------------------------------------------------------------------------
# Fake Redis (in-memory, no real Redis needed)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def fake_redis():
    r = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield r
    await r.aclose()


# ---------------------------------------------------------------------------
# Mock ExchangeClient
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_exchange_client():
    client = AsyncMock()
    client.exchange_name = "binance"
    client.last_used = None
    client.fetch_balance.return_value = {"USDT": {"free": 1000.0, "total": 1000.0}}
    client.create_order.return_value = {"id": "order123", "status": "open"}
    client.cancel_order.return_value = {"id": "order123", "status": "canceled"}
    client.cancel_all_orders.return_value = []
    client.fetch_order.return_value = {"id": "order123", "status": "open"}
    client.fetch_open_orders.return_value = []
    client.fetch_closed_orders.return_value = []
    client.fetch_positions.return_value = []
    client.close_position.return_value = {"id": "order456", "status": "open"}
    client.fetch_ticker.return_value = {"symbol": "BTC/USDT", "last": 50000.0}
    client.fetch_order_book.return_value = {"bids": [], "asks": []}
    client.fetch_ohlcv.return_value = []
    client.fetch_my_trades.return_value = []
    client.get_closed_pnls.return_value = []
    client.set_leverage.return_value = {"leverage": 10}
    client.disconnect = AsyncMock()
    return client


# ---------------------------------------------------------------------------
# SessionManager fixture wired to fake_redis
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def session_manager(fake_redis, test_settings, mock_exchange_client):
    sm = SessionManager(fake_redis, test_settings)

    # Patch the module-level ExchangeClient in session.py
    with patch("session.ExchangeClient") as MockClass:
        MockClass.create = AsyncMock(return_value=mock_exchange_client)
        yield sm, MockClass, mock_exchange_client
