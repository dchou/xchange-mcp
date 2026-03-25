# xchange-mcp

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Community-Telegram-2CA5E0?logo=telegram)](https://t.me/xchange_mcp)

MCP server exposing 17 crypto exchange tools via the [xchange](https://github.com/dchou/xchange) library. Supports 20+ exchanges (Binance, Bybit, OKX, Gate.io, Hyperliquid, Deribit, Kraken, KuCoin, Bitget, and more).

**[Join the Telegram community](https://t.me/xchange_mcp)** — share feedback, report bugs, request features.

## Features

- 17 MCP tools: order management, balance/position queries, market data, PnL
- Session management with Redis persistence and in-memory LRU pool
- SSE and stdio transport support
- Optional paper-trading mode (DryRun)
- Structured error codes for reliable AI parsing

## Prerequisites

- Python 3.10+
- Redis (required for session storage)

```bash
# macOS
brew install redis && brew services start redis

# Ubuntu/Debian
sudo apt install redis-server && sudo systemctl start redis
```

## Installation

**From PyPI / git (end users):**
```bash
pip install git+https://github.com/dchou/xchange-mcp.git
```

## Install xchange package:
```bash
pip install "xchange @ git+https://github.com/dchou/xchange.git"
```

### Upgrade to latest version of xchange package:
```bash
pip install --upgrade "xchange @ git+https://github.com/dchou/xchange.git"
```
Or to reinstall the whole project with the latest xchange:
```bash
pip install --force-reinstall "xchange @ git+https://github.com/dchou/xchange.git"
```

### uv-managed environment:
```bash
uv pip install --upgrade "xchange @ git+https://github.com/dchou/xchange.git"
```

**Local development:**
```bash
git clone https://github.com/dchou/xchange-mcp.git
cd xchange-mcp
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Quick Start

### SSE server (for network/HTTP clients)

```bash
# Start Redis first (see Prerequisites above)

# Copy and edit config (optional — defaults work for local Redis)
cp .env.template .env

# Install the package into your venv if you haven't already
pip install -e .

# Start the SSE server on port 8000
xchange-mcp --transport sse
```

Test it's running:
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### stdio (for desktop AI clients)

stdio mode is configured directly in the client (see below). No manual startup needed — the client launches the process.

## Adding to AI Clients

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "xchange": {
      "command": "xchange-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "MCP_REDIS_URL": "redis://localhost:6379/0",
        "MCP_DRYRUN": "false"
      }
    }
  }
}
```

Restart Claude Desktop after saving.

### OpenCode

Add to your `opencode.json` config (or `~/.config/opencode/opencode.json`):

```json
{
  "mcp": {
    "xchange": {
      "type": "local",
      "command": ["xchange-mcp", "--transport", "stdio"],
      "env": {
        "MCP_REDIS_URL": "redis://localhost:6379/0",
        "MCP_DRYRUN": "false"
      }
    }
  }
}
```

### OpenClaw

Add to your OpenClaw MCP config (typically `~/.config/openclaw/mcp.json`):

```json
{
  "servers": {
    "xchange": {
      "command": "xchange-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "MCP_REDIS_URL": "redis://localhost:6379/0",
        "MCP_DRYRUN": "false"
      }
    }
  }
}
```

### SSE / Streamable-HTTP URL (any HTTP-transport client)

When running the SSE server, two endpoints are available:

| Endpoint | Transport | Notes |
|----------|-----------|-------|
| `http://localhost:8000/sse` | SSE (legacy) | Older clients |
| `http://localhost:8000/mcp` | Streamable-HTTP | Preferred for MCP ≥ 1.0 clients |

> **Note:** WebSocket (`ws://`) is **not** supported. If your client is connecting to `/ws` and getting 403, change the URL to `http://localhost:8000/mcp`.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `MCP_SESSION_TTL` | `3600` | Session expiry in seconds |
| `MCP_MAX_POOL_SIZE` | `50` | Max live exchange connections |
| `MCP_ENCRYPTION_KEY` | — | Optional Fernet key for encrypting stored credentials |
| `MCP_DRYRUN` | `false` | Enable paper-trading mode |

## Usage Examples

All tools follow the same pattern: first call `init_exchange` to get a `session_id`, then pass that `session_id` to any other tool.

### Check your Binance balance

> Initialize a Binance connection with my API key `AKEYHERE` and secret `SECRETHERE`, then fetch my balance.

**Claude will call:**
1. `init_exchange(exchange_name="binance", api_key="AKEYHERE", api_secret="SECRETHERE", market_type="spot")` → returns `session_id`
2. `fetch_balance(session_id="...")` → returns balances

---

### Get BTC price on OKX

> What's the current BTC/USDT price on OKX?

**Claude will call:**
1. `init_exchange(exchange_name="okx", market_type="spot")` → `session_id` (no keys needed for public data)
2. `fetch_ticker(session_id="...", symbol="BTC/USDT")` → `{"last": 67420.5, ...}`

---

### Place a limit buy order

> On my Bybit futures account (API key: KEY, secret: SECRET), buy 0.01 BTC/USDT:USDT at $65,000 with 10x leverage.

**Claude will call:**
1. `init_exchange(exchange_name="bybit", api_key="KEY", api_secret="SECRET", market_type="swap")`
2. `set_leverage(session_id="...", symbol="BTC/USDT:USDT", leverage=10)`
3. `create_order(session_id="...", symbol="BTC/USDT:USDT", order_type="limit", side="buy", amount=0.01, price=65000)`

---

### Check open positions and PnL

> Show me all open positions and realized PnL on my Hyperliquid account (key: KEY, secret: SECRET).

**Claude will call:**
1. `init_exchange(exchange_name="hyperliquid", api_key="KEY", api_secret="SECRET", market_type="swap")`
2. `fetch_positions(session_id="...")`
3. `get_closed_pnls(session_id="...")`

---

### Paper trading

> Set MCP_DRYRUN=true in .env (or env config), then use any tool normally. Orders will be simulated without hitting the exchange.

---

### Cancel all orders and close a position

> Cancel all my open DOGE/USDT:USDT orders and close my short position on Bitget (key: KEY, secret: SECRET).

**Claude will call:**
1. `init_exchange(exchange_name="bitget", api_key="KEY", api_secret="SECRET", market_type="swap")`
2. `cancel_all_orders(session_id="...", symbol="DOGE/USDT:USDT")`
3. `close_position(session_id="...", symbol="DOGE/USDT:USDT", side="short")`

---

### Get OHLCV candlestick data

> Fetch the last 100 hourly candles for ETH/USDT on Kraken.

**Claude will call:**
1. `init_exchange(exchange_name="kraken", market_type="spot")`
2. `fetch_ohlcv(session_id="...", symbol="ETH/USDT", timeframe="1h", limit=100)`

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

## Feedback & Community

**[Telegram: t.me/xchange_mcp](https://t.me/xchange_mcp)**

Three things I want to know:
1. What's working well for you?
2. What's broken or confusing? (include: exchange name + error message + what you tried)
3. What tool or feature is missing that you wish existed?

You can also [open a GitHub Issue](https://github.com/dchou/xchange-mcp/issues/new/choose) for bugs and feature requests.

## License

Proprietary. See [LICENSE](LICENSE).
