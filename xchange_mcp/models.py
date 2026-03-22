"""Pydantic input models for MCP tools."""

from typing import Optional, Any
from pydantic import BaseModel, Field


class InitExchangeInput(BaseModel):
    exchange_name: str = Field(..., description="Exchange identifier (e.g. 'binance', 'bybit')")
    api_key: str = Field(default="", description="API key")
    api_secret: str = Field(default="", description="API secret")
    api_password: Optional[str] = Field(default=None, description="API password/passphrase (OKX, Bitget, etc.)")
    is_testnet: bool = Field(default=False, description="Use testnet/sandbox")
    market_type: str = Field(default="swap", description="Market type: spot, swap, margin, stock")
    exchange_id: Optional[str] = Field(default=None, description="Optional exchange identifier override")
    user_id: Optional[str] = Field(default=None, description="Optional user identifier")
    sub_account_id: Optional[str] = Field(default=None, description="Sub-account identifier")
    symbol: Optional[str] = Field(default=None, description="Default symbol (e.g. 'BTC/USDT')")
    leverage: Optional[int] = Field(default=None, description="Default leverage")
    margin_mode: Optional[str] = Field(default=None, description="Margin mode: cross or isolated")
    position_mode: Optional[str] = Field(default=None, description="Position mode: one_way or hedge")


class SessionInput(BaseModel):
    session_id: str = Field(..., description="Session ID returned by init_exchange")


class CreateOrderInput(BaseModel):
    session_id: str
    symbol: str = Field(..., description="Trading pair (e.g. 'BTC/USDT')")
    order_type: str = Field(..., description="Order type: market or limit")
    side: str = Field(..., description="Order side: buy or sell")
    amount: float = Field(..., description="Order amount in base currency")
    price: Optional[float] = Field(default=None, description="Limit price (required for limit orders)")
    params: Optional[dict[str, Any]] = Field(default=None, description="Extra exchange-specific parameters")


class CancelOrderInput(BaseModel):
    session_id: str
    order_id: str = Field(..., description="Order ID to cancel")
    symbol: str = Field(..., description="Trading pair")


class CancelAllOrdersInput(BaseModel):
    session_id: str
    symbol: Optional[str] = Field(default=None, description="Symbol to cancel orders for; all symbols if omitted")


class FetchOrderInput(BaseModel):
    session_id: str
    order_id: str = Field(..., description="Order ID")
    symbol: Optional[str] = Field(default=None, description="Trading pair")


class FetchOrdersInput(BaseModel):
    session_id: str
    symbol: Optional[str] = Field(default=None, description="Trading pair filter")


class FetchPositionsInput(BaseModel):
    session_id: str
    symbol: Optional[str] = Field(default=None, description="Symbol filter")


class ClosePositionInput(BaseModel):
    session_id: str
    symbol: str = Field(..., description="Trading pair")
    side: str = Field(..., description="Position side: long or short")
    amount: Optional[float] = Field(default=None, description="Amount to close; full position if omitted")


class FetchTickerInput(BaseModel):
    session_id: str
    symbol: str = Field(..., description="Trading pair")


class FetchOrderBookInput(BaseModel):
    session_id: str
    symbol: str = Field(..., description="Trading pair")
    limit: Optional[int] = Field(default=None, description="Depth limit")


class FetchOhlcvInput(BaseModel):
    session_id: str
    symbol: str = Field(..., description="Trading pair")
    timeframe: str = Field(default="1h", description="Timeframe (e.g. '1m', '5m', '1h', '1d')")
    since: Optional[int] = Field(default=None, description="Start timestamp in milliseconds")
    limit: Optional[int] = Field(default=None, description="Number of candles")


class FetchMyTradesInput(BaseModel):
    session_id: str
    symbol: Optional[str] = Field(default=None, description="Trading pair filter")
    limit: Optional[int] = Field(default=50, description="Max number of trades to return (default 50)")


class GetClosedPnlsInput(BaseModel):
    session_id: str
    symbol: Optional[str] = Field(default=None, description="Symbol filter")


class SetLeverageInput(BaseModel):
    session_id: str
    symbol: str = Field(..., description="Trading pair")
    leverage: int = Field(..., description="Leverage multiplier")


class FetchBalanceInput(BaseModel):
    session_id: str
