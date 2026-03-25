"""Map ccxt exceptions to structured MCP error dicts."""

from __future__ import annotations

from typing import Any

try:
    from ccxt.base.errors import (
        AuthenticationError,
        ExchangeError,
        InsufficientFunds,
        InvalidOrder,
        NetworkError,
        OrderNotFound,
        RateLimitExceeded,
    )
    _CCXT_AVAILABLE = True
except ImportError:
    _CCXT_AVAILABLE = False


class SessionNotFoundError(Exception):
    """Raised when a session_id is not found in the pool or Redis."""


def error_response(code: str, message: str, detail: Any = None) -> dict:
    resp: dict = {"success": False, "error_code": code, "error": message}
    if detail is not None:
        resp["detail"] = str(detail)
    return resp


def handle_exception(exc: Exception) -> dict:
    """Convert any exception into a structured error dict."""
    if isinstance(exc, SessionNotFoundError):
        return error_response("SESSION_NOT_FOUND", str(exc))

    if not _CCXT_AVAILABLE:
        return error_response("UNKNOWN_ERROR", str(exc))

    if isinstance(exc, AuthenticationError):
        return error_response("AUTH_ERROR", "Authentication failed", exc)
    if isinstance(exc, InsufficientFunds):
        return error_response("INSUFFICIENT_FUNDS", "Insufficient funds", exc)
    if isinstance(exc, InvalidOrder):
        return error_response("INVALID_ORDER", "Invalid order parameters", exc)
    if isinstance(exc, OrderNotFound):
        return error_response("ORDER_NOT_FOUND", "Order not found", exc)
    if isinstance(exc, RateLimitExceeded):
        return error_response("RATE_LIMIT", "Rate limit exceeded", exc)
    if isinstance(exc, NetworkError):
        return error_response("NETWORK_ERROR", "Network error", exc)
    if isinstance(exc, ExchangeError):
        return error_response("EXCHANGE_ERROR", "Exchange error", exc)

    return error_response("UNKNOWN_ERROR", "Unexpected error", exc)
