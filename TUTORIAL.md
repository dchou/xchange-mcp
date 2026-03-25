# xchange-mcp Tutorial

A step-by-step guide to installing, configuring, and using the `xchange-mcp` server with Claude Code.

---

## What is xchange-mcp?

`xchange-mcp` is an MCP (Model Context Protocol) server that exposes 17 crypto exchange tools to AI clients like Claude Code. It wraps the `xchange` library (built on top of CCXT) and supports 20+ exchanges including Binance, Bybit, OKX, Gate.io, Hyperliquid, Deribit, Kraken, KuCoin, Bitget, and more.

---

## Prerequisites

- Python 3.10+
- Redis (required for session storage)

### Install Redis

```bash
# macOS
brew install redis && brew services start redis

# Ubuntu/Debian
sudo apt install redis-server && sudo systemctl start redis
```

Verify Redis is running:
```bash
redis-cli ping
# PONG
```

---

## Installation

### Install xchange-mcp

```bash
pip install git+https://github.com/dchou/xchange-mcp.git
```

### Install the xchange library

```bash
pip install "xchange @ git+https://github.com/dchou/xchange.git"
```

### Upgrade to latest versions

```bash
pip install --upgrade "xchange @ git+https://github.com/dchou/xchange.git"
pip install --force-reinstall git+https://github.com/dchou/xchange-mcp.git
```

### Using uv

```bash
uv pip install --upgrade "xchange @ git+https://github.com/dchou/xchange.git"
uv pip install git+https://github.com/dchou/xchange-mcp.git
```

---

## run on public server

Now on the remote server, create a .env file in the src/xchange-mcp/ directory:
```
echo 'MCP_ALLOWED_HOSTS=["tokyo2.ezcoin.cc:8888","localhost:8888"]' >> ~/xchange-mcp/src/xchange-mcp/.env
``

---

## Adding xchange-mcp to Claude Code

Claude Code uses stdio transport — no manual server startup needed. Claude Code launches the process automatically.

### Step 1: Add to Claude Code settings

Edit `~/.claude/settings.json` and add an `mcpServers` section:

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

Or use the Claude Code CLI to add it:

```bash
claude mcp add xchange -- xchange-mcp --transport stdio
```

### Step 2: Restart Claude Code

The MCP server will be available in new sessions automatically.

### Step 3: Verify it's connected

Run `/mcp` inside Claude Code to see connected servers. You should see `xchange` listed.

---

## Credential Management

### Store credentials in a .env file

Create a `.env` file in your project directory. Use a consistent naming convention:

```
# Format: <prefix>_API_KEY, <prefix>_SECRET_KEY, <prefix>_PASSPHRASE
# Prefix convention: <exchange_abbrev><market_type><env>
#   market_type: D=derivatives/swap, S=spot, A=all
#   env: Demo=testnet/demo, Debug=live-debug, Prod=production

# Bybit demo (testnet)
bbDDemo_API_KEY=your_api_key_here
bbDDemo_SECRET_KEY=your_secret_key_here

# Binance swap testnet
bnDDemo_API_KEY=your_api_key_here
bnDDemo_SECRET_KEY=your_secret_key_here

# OKX simulation account
okDDemo_API_KEY=your_api_key_here
okDDemo_SECRET_KEY=your_secret_key_here
okDDemo_PASSPHRASE=your_passphrase_here

# Bitget (UTA) demo
bgDDemo_API_KEY=your_api_key_here
bgDDemo_SECRET_KEY=your_secret_key_here
bgDDemo_PASSPHRASE=your_passphrase_here
```

> **Security:** Never commit `.env` to version control. Add it to `.gitignore`.

### Set up CLAUDE.md for credential security

Create a `CLAUDE.md` in your project directory to prevent Claude from displaying credentials:

```markdown
# Rules

## Credentials Security

Never display `api_key`, `api_secret`, or `api_password` values anywhere in the
conversation — this includes tool call parameter displays, output summaries, and
any text responses.

When calling `mcp__xchange__init_exchange`, pass credentials silently. Only mention
non-sensitive parameters (e.g. `exchange_name`, `market_type`, `is_testnet`) in
any text output.
```

---

## Usage Pattern

All tools follow a two-step pattern:

1. **`init_exchange`** — authenticate and get a `session_id`
2. **Any other tool** — pass the `session_id` to perform operations

```
init_exchange(...) → session_id → fetch_balance(session_id)
                                → fetch_positions(session_id)
                                → create_order(session_id, ...)
                                → ...
```

Sessions are stored in Redis with a default TTL of 1 hour. You can reuse a `session_id` across multiple tool calls within the session lifetime.

---

## Tool Reference

### Exchange Session

| Tool | Description |
|------|-------------|
| `init_exchange` | Initialize exchange session with API credentials |
| `close_exchange` | Close an exchange session and free resources |

### Account Data

| Tool | Description |
|------|-------------|
| `fetch_balance` | Get account balances for all currencies |
| `fetch_positions` | Get all open positions |
| `fetch_my_trades` | List recent trade history |
| `get_closed_pnls` | Get realized PnL history |

### Order Management

| Tool | Description |
|------|-------------|
| `create_order` | Place a market or limit order |
| `cancel_order` | Cancel an order by ID |
| `cancel_all_orders` | Cancel all open orders (optionally for a symbol) |
| `fetch_order` | Get details of a specific order |
| `fetch_open_orders` | List all open orders |
| `fetch_closed_orders` | List closed/filled orders |
| `close_position` | Close an open position |
| `set_leverage` | Set leverage multiplier for a symbol |

### Market Data (no credentials required)

| Tool | Description |
|------|-------------|
| `fetch_ticker` | Get current price and 24h stats |
| `fetch_order_book` | Get order book depth |
| `fetch_ohlcv` | Get OHLCV candlestick data |

---

## Examples

### Check account balance

> "Get my Bybit demo balance"

Claude will:
1. `init_exchange(exchange_name="bybit", market_type="swap", is_testnet=true)` → `session_id`
2. `fetch_balance(session_id="...")` → balances by currency

---

### Get current BTC price (no credentials needed)

> "What's the BTC/USDT price on OKX?"

Claude will:
1. `init_exchange(exchange_name="okx", market_type="spot")` → `session_id`
2. `fetch_ticker(session_id="...", symbol="BTC/USDT")` → `{"last": 84000, ...}`

---

### Place a limit buy order

> "On my Bybit futures demo account, buy 0.01 BTC/USDT:USDT at $80,000 with 10x leverage"

Claude will:
1. `init_exchange(exchange_name="bybit", market_type="swap", is_testnet=true)`
2. `set_leverage(session_id="...", symbol="BTC/USDT:USDT", leverage=10)`
3. `create_order(session_id="...", symbol="BTC/USDT:USDT", order_type="limit", side="buy", amount=0.01, price=80000)`

---

### Check open positions and PnL

> "Show me my open positions and recent PnL on Bitget demo"

Claude will:
1. `init_exchange(exchange_name="bitget", market_type="swap")`
2. `fetch_positions(session_id="...")`
3. `get_closed_pnls(session_id="...")`

---

### Cancel all orders and close a position

> "Cancel all DOGE/USDT:USDT orders and close my short on Bitget"

Claude will:
1. `init_exchange(exchange_name="bitget", market_type="swap")`
2. `cancel_all_orders(session_id="...", symbol="DOGE/USDT:USDT")`
3. `close_position(session_id="...", symbol="DOGE/USDT:USDT", side="short")`

---

### Fetch OHLCV candlestick data

> "Get the last 100 hourly candles for ETH/USDT on Kraken"

Claude will:
1. `init_exchange(exchange_name="kraken", market_type="spot")`
2. `fetch_ohlcv(session_id="...", symbol="ETH/USDT", timeframe="1h", limit=100)`

---

### Fetch order book

> "Show me the top 10 levels of the BTC/USDT order book on Binance"

Claude will:
1. `init_exchange(exchange_name="binance", market_type="spot")`
2. `fetch_order_book(session_id="...", symbol="BTC/USDT", limit=10)`

---

## init_exchange Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `exchange_name` | string | required | Exchange ID (e.g. `bybit`, `binance`, `okx`) |
| `api_key` | string | `""` | API key (omit for public data) |
| `api_secret` | string | `""` | API secret |
| `api_password` | string | `null` | Passphrase (required for OKX, Bitget, KuCoin) |
| `market_type` | string | `"swap"` | `"spot"`, `"swap"`, `"future"` |
| `is_testnet` | bool | `false` | Use exchange testnet/demo environment |
| `leverage` | int | `null` | Set default leverage on init |
| `margin_mode` | string | `null` | `"isolated"` or `"cross"` |
| `position_mode` | string | `null` | `"one_way"` or `"hedge"` |
| `sub_account_id` | string | `null` | Sub-account identifier |

---

## Server Configuration

These environment variables control server behavior (set in `mcpServers.env` or `.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `MCP_SESSION_TTL` | `3600` | Session expiry in seconds |
| `MCP_MAX_POOL_SIZE` | `50` | Max concurrent exchange connections |
| `MCP_ENCRYPTION_KEY` | — | Optional Fernet key to encrypt stored credentials |
| `MCP_DRYRUN` | `false` | Paper-trading mode (simulate orders) |

### Paper Trading

Set `MCP_DRYRUN=true` to simulate all orders without sending them to the exchange:

```json
{
  "mcpServers": {
    "xchange": {
      "command": "xchange-mcp",
      "args": ["--transport", "stdio"],
      "env": {
        "MCP_REDIS_URL": "redis://localhost:6379/0",
        "MCP_DRYRUN": "true"
      }
    }
  }
}
```

---

## SSE Server (for HTTP clients)

If you need to connect via HTTP (e.g. from a web app or remote client), run the SSE server:

```bash
xchange-mcp --transport sse
# Starts on http://localhost:8000
```

| Endpoint | Transport | Use when |
|----------|-----------|----------|
| `http://localhost:8000/mcp` | Streamable-HTTP | MCP ≥ 1.0 clients (preferred) |
| `http://localhost:8000/sse` | SSE legacy | Older clients |

Health check:
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

---

## Project Structure for Claude Code

Recommended layout for a trading project using xchange-mcp with Claude Code:

```
my-trading-project/
├── .env                  # Exchange credentials (gitignored)
├── .gitignore
├── CLAUDE.md             # Claude rules (credential security, etc.)
└── .claude/
    └── settings.local.json   # Per-project tool permissions
```

### settings.local.json — restrict which tools Claude can use

```json
{
  "permissions": {
    "allow": [
      "mcp__xchange__init_exchange",
      "mcp__xchange__fetch_balance",
      "mcp__xchange__fetch_positions",
      "mcp__xchange__fetch_open_orders",
      "mcp__xchange__fetch_closed_orders",
      "mcp__xchange__fetch_my_trades",
      "mcp__xchange__get_closed_pnls",
      "mcp__xchange__fetch_ticker",
      "mcp__xchange__fetch_ohlcv"
    ]
  }
}
```

> **Tip:** Start with read-only tools in `allow`. Only add order/position mutation tools (`create_order`, `cancel_order`, etc.) when you explicitly need them and are ready to confirm each action.

---

## Supported Exchanges

| Exchange | ID | Notes |
|----------|----|-------|
| Binance | `binance` | Testnet supported |
| Bybit | `bybit` | Demo account supported |
| OKX | `okx` | Simulation account supported |
| Gate.io | `gate` | Testnet supported |
| Hyperliquid | `hyperliquid` | Testnet supported |
| Deribit | `deribit` | Testnet supported |
| Kraken | `kraken` | Futures: `krakenfutures` |
| KuCoin | `kucoin` | Passphrase required |
| Bitget | `bitget` | Passphrase required, testnet supported |
| Backpack | `backpack` | — |
| BingX | `bingx` | — |
| HTX (Huobi) | `htx` | — |
| MEXC | `mexc` | — |
| Pionex | `pionex` | — |
| Bitfinex | `bitfinex` | Testnet supported |
| MAX | `max` | — |
| Alpaca | `alpaca` | Paper trading supported |

---

## Troubleshooting

**MCP server not showing in `/mcp list`**
- Check `~/.claude/settings.json` has the `mcpServers` block
- Verify `xchange-mcp` is on your `PATH`: `which xchange-mcp`
- Restart Claude Code

**`Failed to connect to <exchange>`**
- Check Redis is running: `redis-cli ping`
- Verify your API key/secret are correct
- For demo/testnet accounts, set `is_testnet=true`
- Some exchanges (OKX, Bitget, KuCoin) require `api_password`

**Session expired**
- Sessions expire after `MCP_SESSION_TTL` seconds (default 1 hour)
- Call `init_exchange` again to get a new `session_id`

**`403` on WebSocket URL**
- WebSocket (`ws://`) is not supported — use `http://localhost:8000/mcp` instead
