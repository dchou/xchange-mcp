"""FastMCP server: all 17 exchange tools."""

from __future__ import annotations

import logging
import os

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from config import settings as _settings
from error_handling import handle_exception
from models import (
    CancelAllOrdersInput,
    CancelOrderInput,
    ClosePositionInput,
    CreateOrderInput,
    FetchBalanceInput,
    FetchMyTradesInput,
    FetchOhlcvInput,
    FetchOrderBookInput,
    FetchOrderInput,
    FetchOrdersInput,
    FetchPositionsInput,
    FetchTickerInput,
    GetClosedPnlsInput,
    InitExchangeInput,
    SessionInput,
    SetLeverageInput,
)

logger = logging.getLogger(__name__)

_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=bool(_settings.allowed_hosts),
    allowed_hosts=_settings.allowed_hosts,
)
mcp = FastMCP("xchange-mcp", transport_security=_security)

# session_manager is injected by main.py after startup
_session_manager = None


def set_session_manager(sm) -> None:
    global _session_manager
    _session_manager = sm


# ---------------------------------------------------------------------------
# Session tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def init_exchange(
    exchange_name: str,
    api_key: str = "",
    api_secret: str = "",
    api_password: str | None = None,
    is_testnet: bool = False,
    market_type: str = "swap",
    exchange_id: str | None = None,
    user_id: str | None = None,
    sub_account_id: str | None = None,
    symbol: str | None = None,
    leverage: int | None = None,
    margin_mode: str | None = None,
    position_mode: str | None = None,
) -> dict:
    """Initialize an exchange connection and return a session_id for subsequent calls."""
    config = {k: v for k, v in {
        "exchange_name": exchange_name,
        "api_key": api_key,
        "api_secret": api_secret,
        "api_password": api_password,
        "is_testnet": is_testnet,
        "market_type": market_type,
        "exchange_id": exchange_id,
        "user_id": user_id,
        "sub_account_id": sub_account_id,
        "symbol": symbol,
        "leverage": leverage,
        "margin_mode": margin_mode,
        "position_mode": position_mode,
    }.items() if v is not None}
    try:
        session_id = await _session_manager.create_session(config)
        return {"success": True, "session_id": session_id, "exchange_name": exchange_name}
    except Exception as exc:
        return handle_exception(exc)


@mcp.tool()
async def close_exchange(session_id: str) -> dict:
    """Close an exchange connection and clean up the session."""
    try:
        await _session_manager.destroy_session(session_id)
        return {"success": True, "session_id": session_id}
    except Exception as exc:
        return handle_exception(exc)


# ---------------------------------------------------------------------------
# Account tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def fetch_balance(session_id: str) -> dict:
    """Fetch account balance for all currencies."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.fetch_balance()
        return {"success": True, "balance": result}
    except Exception as exc:
        return handle_exception(exc)


@mcp.tool()
async def fetch_positions(session_id: str, symbol: str | None = None) -> dict:
    """Fetch open positions (swap/futures accounts)."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.fetch_positions(symbol)
        return {"success": True, "positions": result}
    except Exception as exc:
        return handle_exception(exc)


@mcp.tool()
async def get_closed_pnls(session_id: str, symbol: str | None = None) -> dict:
    """Get closed PnL history using FIFO matching."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.get_closed_pnls(symbol)
        return {"success": True, "pnls": result}
    except Exception as exc:
        return handle_exception(exc)


# ---------------------------------------------------------------------------
# Order tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def create_order(
    session_id: str,
    symbol: str,
    order_type: str,
    side: str,
    amount: float,
    price: float | None = None,
    params: dict | None = None,
) -> dict:
    """Create a new order (market or limit)."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.create_order(
            symbol, order_type, side, amount, price, params or {}
        )
        return {"success": True, "order": result}
    except Exception as exc:
        return handle_exception(exc)


@mcp.tool()
async def cancel_order(session_id: str, order_id: str, symbol: str) -> dict:
    """Cancel an open order by ID."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.cancel_order(order_id, symbol)
        return {"success": True, "order": result}
    except Exception as exc:
        return handle_exception(exc)


@mcp.tool()
async def cancel_all_orders(session_id: str, symbol: str | None = None) -> dict:
    """Cancel all open orders, optionally filtered by symbol."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.cancel_all_orders(symbol)
        return {"success": True, "cancelled": result}
    except Exception as exc:
        return handle_exception(exc)


@mcp.tool()
async def fetch_order(session_id: str, order_id: str, symbol: str | None = None) -> dict:
    """Fetch details for a specific order."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.fetch_order(order_id, symbol)
        return {"success": True, "order": result}
    except Exception as exc:
        return handle_exception(exc)


@mcp.tool()
async def fetch_open_orders(session_id: str, symbol: str | None = None) -> dict:
    """Fetch all open orders, optionally filtered by symbol."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.fetch_open_orders(symbol)
        return {"success": True, "orders": result}
    except Exception as exc:
        return handle_exception(exc)


@mcp.tool()
async def fetch_closed_orders(session_id: str, symbol: str | None = None) -> dict:
    """Fetch closed/filled orders, optionally filtered by symbol."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.fetch_closed_orders(symbol)
        return {"success": True, "orders": result}
    except Exception as exc:
        return handle_exception(exc)


@mcp.tool()
async def close_position(
    session_id: str,
    symbol: str,
    side: str,
    amount: float | None = None,
) -> dict:
    """Close an open position. Side must be 'long' or 'short'."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.close_position(symbol, side, amount)
        return {"success": True, "order": result}
    except Exception as exc:
        return handle_exception(exc)


@mcp.tool()
async def fetch_my_trades(session_id: str, symbol: str | None = None, limit: int = 50) -> dict:
    """Fetch personal trade history, optionally filtered by symbol."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.fetch_my_trades(symbol, limit=limit)
        return {"success": True, "trades": result}
    except Exception as exc:
        return handle_exception(exc)


@mcp.tool()
async def set_leverage(session_id: str, symbol: str, leverage: int) -> dict:
    """Set leverage for a symbol."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.set_leverage(symbol, leverage)
        return {"success": True, "result": result}
    except Exception as exc:
        return handle_exception(exc)


# ---------------------------------------------------------------------------
# Market data tools
# ---------------------------------------------------------------------------

@mcp.tool()
async def fetch_ticker(session_id: str, symbol: str) -> dict:
    """Fetch current ticker price and stats for a symbol."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.fetch_ticker(symbol)
        return {"success": True, "ticker": result}
    except Exception as exc:
        return handle_exception(exc)


@mcp.tool()
async def fetch_order_book(
    session_id: str,
    symbol: str,
    limit: int | None = None,
) -> dict:
    """Fetch order book (bids/asks) for a symbol."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.fetch_order_book(symbol, limit)
        return {"success": True, "order_book": result}
    except Exception as exc:
        return handle_exception(exc)


@mcp.tool()
async def fetch_ohlcv(
    session_id: str,
    symbol: str,
    timeframe: str = "1h",
    since: int | None = None,
    limit: int | None = None,
) -> dict:
    """Fetch OHLCV (candlestick) data for a symbol."""
    try:
        client = await _session_manager.get_client(session_id)
        result = await client.fetch_ohlcv(symbol, timeframe, since, limit)
        return {"success": True, "ohlcv": result}
    except Exception as exc:
        return handle_exception(exc)
