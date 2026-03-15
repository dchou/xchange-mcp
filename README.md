# xchange-mcp

MCP server exposing 17 crypto exchange tools via the [xchange](https://github.com/dchou/xchange) library. Supports 20+ exchanges (Binance, Bybit, OKX, Gate.io, Hyperliquid, Deribit, Kraken, KuCoin, Bitget, and more).

## Features

- 17 MCP tools: order management, balance/position queries, market data, PnL
- Session management with Redis persistence and in-memory LRU pool
- SSE and stdio transport support
- Optional paper-trading mode (DryRun)
- Structured error codes for reliable AI parsing

## Installation

```bash
pip install git+https://github.com/dchou/xchange-mcp.git
```

## Quick Start

```bash
cp .env.template .env
# Edit .env with your settings

# SSE server (default port 8000)
xchange-mcp --transport sse

# stdio (for Claude Desktop)
xchange-mcp --transport stdio
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `MCP_SESSION_TTL` | `3600` | Session expiry in seconds |
| `MCP_MAX_POOL_SIZE` | `50` | Max live exchange connections |
| `MCP_ENCRYPTION_KEY` | — | Optional key for encrypting stored credentials |
| `MCP_DRYRUN` | `false` | Enable paper-trading mode |

## Tools

| Tool | Description |
|------|-------------|
| `init_exchange` | Initialize exchange session with API credentials |
| `close_exchange` | Close an exchange session |
| `fetch_balance` | Get account balances |
| `fetch_positions` | Get open positions |
| `create_order` | Place a new order |
| `cancel_order` | Cancel an order by ID |
| `cancel_all_orders` | Cancel all open orders |
| `fetch_order` | Get order details |
| `fetch_open_orders` | List open orders |
| `fetch_closed_orders` | List closed orders |
| `fetch_my_trades` | List recent trades |
| `close_position` | Close an open position |
| `set_leverage` | Set leverage for a symbol |
| `get_closed_pnls` | Get realized PnL history |
| `fetch_ticker` | Get current price/ticker |
| `fetch_order_book` | Get order book depth |
| `fetch_ohlcv` | Get candlestick data |

## License

Proprietary. See [LICENSE](LICENSE).
