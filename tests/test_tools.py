"""Unit tests for each MCP tool (direct async calls, no HTTP)."""

from __future__ import annotations

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "xchange-mcp"))

pytestmark = pytest.mark.asyncio

# Import the tool functions and the module-level setter
import server as server_module
from server import (
    init_exchange,
    close_exchange,
    fetch_balance,
    create_order,
    cancel_order,
    cancel_all_orders,
    fetch_order,
    fetch_open_orders,
    fetch_closed_orders,
    fetch_positions,
    close_position,
    fetch_ticker,
    fetch_order_book,
    fetch_ohlcv,
    fetch_my_trades,
    get_closed_pnls,
    set_leverage,
)
from error_handling import SessionNotFoundError


SAMPLE_CONFIG = dict(
    exchange_name="binance",
    api_key="key",
    api_secret="secret",
    market_type="spot",
)


@pytest_asyncio.fixture(autouse=True)
async def inject_mock_session_manager(mock_exchange_client):
    """Install a mock SessionManager into server module before each test."""
    sm = AsyncMock()
    sm.get_client.return_value = mock_exchange_client
    sm.create_session.return_value = "test-session-123"
    server_module.set_session_manager(sm)
    yield sm
    server_module.set_session_manager(None)


# ---------------------------------------------------------------------------
# init_exchange
# ---------------------------------------------------------------------------

async def test_init_exchange_success(inject_mock_session_manager):
    result = await init_exchange(exchange_name="binance", api_key="k", api_secret="s")
    assert result["success"] is True
    assert result["session_id"] == "test-session-123"


async def test_init_exchange_auth_failure(inject_mock_session_manager):
    from ccxt.base.errors import AuthenticationError

    inject_mock_session_manager.create_session.side_effect = AuthenticationError("bad key")

    result = await init_exchange(exchange_name="binance")
    assert result["success"] is False
    assert result["error_code"] == "AUTH_ERROR"


# ---------------------------------------------------------------------------
# close_exchange
# ---------------------------------------------------------------------------

async def test_close_exchange(inject_mock_session_manager):
    result = await close_exchange(session_id="test-session-123")
    assert result["success"] is True
    inject_mock_session_manager.destroy_session.assert_awaited_once_with("test-session-123")


# ---------------------------------------------------------------------------
# fetch_balance
# ---------------------------------------------------------------------------

async def test_fetch_balance(inject_mock_session_manager, mock_exchange_client):
    result = await fetch_balance(session_id="test-session-123")
    assert result["success"] is True
    assert "balance" in result
    mock_exchange_client.fetch_balance.assert_awaited_once()


# ---------------------------------------------------------------------------
# create_order
# ---------------------------------------------------------------------------

async def test_create_order_market(inject_mock_session_manager, mock_exchange_client):
    result = await create_order(
        session_id="s", symbol="BTC/USDT", order_type="market", side="buy", amount=0.1
    )
    assert result["success"] is True
    mock_exchange_client.create_order.assert_awaited_once_with(
        "BTC/USDT", "market", "buy", 0.1, None, {}
    )


async def test_create_order_limit(inject_mock_session_manager, mock_exchange_client):
    result = await create_order(
        session_id="s", symbol="BTC/USDT", order_type="limit", side="sell",
        amount=0.1, price=50000.0
    )
    assert result["success"] is True
    mock_exchange_client.create_order.assert_awaited_once_with(
        "BTC/USDT", "limit", "sell", 0.1, 50000.0, {}
    )


# ---------------------------------------------------------------------------
# cancel_order
# ---------------------------------------------------------------------------

async def test_cancel_order(inject_mock_session_manager, mock_exchange_client):
    result = await cancel_order(session_id="s", order_id="order123", symbol="BTC/USDT")
    assert result["success"] is True
    mock_exchange_client.cancel_order.assert_awaited_once_with("order123", "BTC/USDT")


# ---------------------------------------------------------------------------
# cancel_all_orders
# ---------------------------------------------------------------------------

async def test_cancel_all_orders(inject_mock_session_manager, mock_exchange_client):
    result = await cancel_all_orders(session_id="s", symbol="BTC/USDT")
    assert result["success"] is True
    mock_exchange_client.cancel_all_orders.assert_awaited_once_with("BTC/USDT")


# ---------------------------------------------------------------------------
# fetch_order
# ---------------------------------------------------------------------------

async def test_fetch_order(inject_mock_session_manager, mock_exchange_client):
    result = await fetch_order(session_id="s", order_id="order123")
    assert result["success"] is True
    mock_exchange_client.fetch_order.assert_awaited_once_with("order123", None)


# ---------------------------------------------------------------------------
# fetch_open_orders
# ---------------------------------------------------------------------------

async def test_fetch_open_orders(inject_mock_session_manager, mock_exchange_client):
    result = await fetch_open_orders(session_id="s")
    assert result["success"] is True
    assert "orders" in result


# ---------------------------------------------------------------------------
# fetch_positions
# ---------------------------------------------------------------------------

async def test_fetch_positions(inject_mock_session_manager, mock_exchange_client):
    result = await fetch_positions(session_id="s")
    assert result["success"] is True
    assert "positions" in result


# ---------------------------------------------------------------------------
# close_position
# ---------------------------------------------------------------------------

async def test_close_position(inject_mock_session_manager, mock_exchange_client):
    result = await close_position(session_id="s", symbol="BTC/USDT", side="long")
    assert result["success"] is True
    mock_exchange_client.close_position.assert_awaited_once_with("BTC/USDT", "long", None)


# ---------------------------------------------------------------------------
# fetch_ticker
# ---------------------------------------------------------------------------

async def test_fetch_ticker(inject_mock_session_manager, mock_exchange_client):
    result = await fetch_ticker(session_id="s", symbol="BTC/USDT")
    assert result["success"] is True
    assert result["ticker"]["last"] == 50000.0


# ---------------------------------------------------------------------------
# fetch_order_book
# ---------------------------------------------------------------------------

async def test_fetch_order_book(inject_mock_session_manager, mock_exchange_client):
    result = await fetch_order_book(session_id="s", symbol="BTC/USDT")
    assert result["success"] is True
    assert "order_book" in result


# ---------------------------------------------------------------------------
# fetch_ohlcv
# ---------------------------------------------------------------------------

async def test_fetch_ohlcv(inject_mock_session_manager, mock_exchange_client):
    result = await fetch_ohlcv(session_id="s", symbol="BTC/USDT", timeframe="1h")
    assert result["success"] is True
    mock_exchange_client.fetch_ohlcv.assert_awaited_once_with("BTC/USDT", "1h", None, None)


# ---------------------------------------------------------------------------
# fetch_my_trades
# ---------------------------------------------------------------------------

async def test_fetch_my_trades(inject_mock_session_manager, mock_exchange_client):
    result = await fetch_my_trades(session_id="s")
    assert result["success"] is True


# ---------------------------------------------------------------------------
# get_closed_pnls
# ---------------------------------------------------------------------------

async def test_get_closed_pnls(inject_mock_session_manager, mock_exchange_client):
    result = await get_closed_pnls(session_id="s")
    assert result["success"] is True


# ---------------------------------------------------------------------------
# set_leverage
# ---------------------------------------------------------------------------

async def test_set_leverage(inject_mock_session_manager, mock_exchange_client):
    result = await set_leverage(session_id="s", symbol="BTC/USDT", leverage=10)
    assert result["success"] is True
    mock_exchange_client.set_leverage.assert_awaited_once_with("BTC/USDT", 10)


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

async def test_session_not_found_returns_error_dict(inject_mock_session_manager):
    inject_mock_session_manager.get_client.side_effect = SessionNotFoundError("not found")
    result = await fetch_balance(session_id="bad-id")
    assert result["success"] is False
    assert result["error_code"] == "SESSION_NOT_FOUND"


async def test_exchange_error_passthrough(inject_mock_session_manager, mock_exchange_client):
    from ccxt.base.errors import ExchangeError

    mock_exchange_client.fetch_balance.side_effect = ExchangeError("exchange down")
    result = await fetch_balance(session_id="s")
    assert result["success"] is False
    assert result["error_code"] == "EXCHANGE_ERROR"
