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

---

## Quick Connect (Hosted Server)

No installation required. Connect to the hosted server directly from your AI client.

### Claude Code

```bash
claude mcp add --transport http xchange-mcp https://xchange-mcp.ezcoin.cc/mcp
```

Verify:
```bash
claude mcp list
# xchange-mcp: https://xchange-mcp.ezcoin.cc/mcp (HTTP) - ✓ Connected
```

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "xchange-mcp": {
      "type": "http",
      "url": "https://xchange-mcp.ezcoin.cc/mcp"
    }
  }
}
```

Restart Claude Desktop after saving.

### OpenCode

Add to `opencode.json` (or `~/.config/opencode/opencode.json`):

```json
{
  "mcp": {
    "xchange-mcp": {
      "type": "remote",
      "url": "https://xchange-mcp.ezcoin.cc/mcp"
    }
  }
}
```

### OpenClaw

Add to your OpenClaw MCP config (`~/.config/openclaw/mcp.json`):

```json
{
  "servers": {
    "xchange-mcp": {
      "type": "http",
      "url": "https://xchange-mcp.ezcoin.cc/mcp"
    }
  }
}
```

---

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

> Show me all open positions and realized PnL on my Hyperliquid account.

**Claude will call:**
1. `init_exchange(exchange_name="hyperliquid", api_key="KEY", api_secret="SECRET", market_type="swap")`
2. `fetch_positions(session_id="...")`
3. `get_closed_pnls(session_id="...")`

---

### Cancel all orders and close a position

> Cancel all my open DOGE/USDT:USDT orders and close my short position on Bitget.

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

---

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
| `get_borrow_rate` | Get margin borrow rate for an asset |
| `get_borrowed_amount` | Get borrowed amount for a margin asset |
| `get_borrowed_records` | Get borrowing records for a margin asset |
| `fetch_margin_config` | Get margin trading configuration |
| `is_testnet` | Check if session is using testnet |

---

## 

**[Telegram: t.me/xchange_mcp_bot](https://t.me/xchange_mcp_bot)**

You can use xchange-mcp functions with free Telegram bot.

Useage example:
```
/help
/setKey bybit aaaaaaaa bbbbbbb
/balance bybit
/orders
/buy bybit BTC/USDT 0.01 70000 limit
/buy bybit BTC/USDT 0.01 70000 swap
/sell bybit BTC/USDT 0.01 70000 swap
/pnls
```

## Feedback & Community

**[Telegram: t.me/xchange_mcp](https://t.me/xchange_mcp)**

Three things I want to know:
1. What's working well for you?
2. What's broken or confusing? (include: exchange name + error message + what you tried)
3. What tool or feature is missing that you wish existed?

You can also [open a GitHub Issue](https://github.com/dchou/xchange-mcp/issues/new/choose) for bugs and feature requests.

---

## Self-Hosting

> For running your own xchange-mcp server. Not needed to use the hosted server above.

### Prerequisites

- Python 3.10+
- Redis

```bash
# macOS
brew install redis && brew services start redis

# Ubuntu/Debian
sudo apt install redis-server && sudo systemctl start redis
```

### Installation

```bash
git clone https://github.com/dchou/xchange-mcp.git
cd xchange-mcp
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

### Start the server

```bash
cp .env.template .env   # edit as needed
xchange-mcp --transport sse
# Listening on http://0.0.0.0:8000
```

Test it's running:
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `MCP_SESSION_TTL` | `3600` | Session expiry in seconds |
| `MCP_MAX_POOL_SIZE` | `50` | Max live exchange connections |
| `MCP_ENCRYPTION_KEY` | — | Optional Fernet key for encrypting stored credentials |
| `MCP_DRYRUN` | `false` | Enable paper-trading mode |

### SSE endpoints

| Endpoint | Transport | Notes |
|----------|-----------|-------|
| `http://localhost:8000/sse` | SSE (legacy) | Older clients |
| `http://localhost:8000/mcp` | Streamable-HTTP | Preferred for MCP ≥ 1.0 clients |

> **Note:** WebSocket (`ws://`) is not supported. Use `http://localhost:8000/mcp`.

---

## License

Proprietary. See [LICENSE](LICENSE).
