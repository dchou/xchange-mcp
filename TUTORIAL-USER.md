# xchange-mcp User Guide

How to use the xchange-mcp tools with Claude Code to manage your crypto exchange accounts.

---

## Add xchange-mcp to Claude Code

```bash
cd working_directory
claude mcp add --transport http xchange http://tokyo2.ezcoin.cc:8888/mcp
claude mcp list
```


### Trouble shooting:


Then you can start claude to use

If you need to remove and add mcp again:
```bash
claude mcp remove xchange
claude mcp add --transport http xchange http://tokyo2.ezcoin.cc:8888/mcp
claude mcp list
```
---

## How It Works

All tools follow a two-step pattern:

1. **`init_exchange`** — connect to an exchange and get a `session_id`
2. **Any other tool** — pass the `session_id` to perform operations

You can reuse the same `session_id` for multiple operations within a session (sessions last 1 hour by default).

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

---

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

## Credentials location
The exchange credentials are in .env file, where:
- bb stands for bybit, 
- bn stands for binance, 
- ok stands for okx, 
- gt stands for gateio,
- bg stands for bitget,
- bp stands for backpack,
- bx stands for bingx,
- po stands for pionex,
- max stands for max,
- mx stands for MEXC,
- hb stands for HTX
```

---

## Connecting to an Exchange

Tell Claude which exchange and account you want to use. Claude will call `init_exchange` on your behalf.

**Examples:**
- "What is my Bybit demo balance"
- "What are the open orders of Bybit demo"
- "Connect to my Bybit demo account"
- "Initialize OKX with my okDDemo credentials"
- "Use my bgDDemo Bitget account"

For exchanges that require a passphrase (OKX, Bitget, KuCoin), Claude will pass it automatically from your `.env` file.

**Key parameters:**

| Parameter | What it does |
|-----------|-------------|
| `exchange_name` | Which exchange (`bybit`, `binance`, `okx`, `bitget`, etc.) |
| `market_type` | `"swap"` for perpetuals/futures, `"spot"` for spot trading |
| `is_testnet` | `true` for demo/testnet accounts, `false` for live |

---

## Account & Balance

### Check balance
> "Get my Bybit demo balance"
> "What's my USDT balance on Bitget?"

Returns free, used, and total amounts for each currency.

### View open positions
> "Show my open positions on OKX demo"
> "What perpetual positions do I have?"

### View realized PnL
> "Show my closed PnL on Bybit"
> "Get my recent PnL history"

---

## Orders

### Place an order

**Market order:**
> "Buy 0.01 BTC/USDT:USDT at market on my Bybit demo"

**Limit order:**
> "Place a limit buy for 0.01 BTC/USDT:USDT at $80,000 on Bybit demo"
> "Sell 100 DOGE/USDT:USDT at $0.35 limit on Bitget demo"

**With leverage:**
> "Buy 0.01 BTC/USDT:USDT at market with 10x leverage on Bybit demo"

### View orders
> "Show my open orders on OKX"
> "List my recent closed orders on Bitget"
> "Get details for order ID 12345"

### Cancel orders
> "Cancel order 12345 on Bybit"
> "Cancel all my open BTC/USDT:USDT orders on OKX"
> "Cancel all orders on my Bitget demo account"

### Close a position
> "Close my BTC long position on Bybit demo"
> "Close my ETH short on OKX"

---

## Trade History

> "Show my recent trades on Bitget"
> "What trades did I make on Bybit today?"

---

## Market Data

No credentials needed for market data tools.

### Current price
> "What's the BTC/USDT price on Bybit?"
> "Get the ETH/USDT ticker on Binance"

### Order book
> "Show me the top 10 levels of the BTC/USDT order book on OKX"

### Candlestick data (OHLCV)
> "Get the last 100 hourly candles for ETH/USDT on Kraken"
> "Fetch daily BTC/USDT candles for the past 30 days on Bybit"

Common timeframes: `1m`, `5m`, `15m`, `1h`, `4h`, `1d`

---

## Symbol Format

| Market | Format | Example |
|--------|--------|---------|
| Perpetual swap | `BASE/QUOTE:SETTLE` | `BTC/USDT:USDT` |
| Spot | `BASE/QUOTE` | `BTC/USDT` |

Most perpetual contracts use USDT as the settlement currency.

---

## Supported Exchanges

| Exchange | ID | Testnet/Demo |
|----------|----|-------------|
| Binance | `binance` | Yes |
| Bybit | `bybit` | Yes (demo account) |
| OKX | `okx` | Yes (simulation account) |
| Gate.io | `gate` | Yes |
| Hyperliquid | `hyperliquid` | Yes |
| Deribit | `deribit` | Yes |
| Kraken | `kraken` | — |
| KuCoin | `kucoin` | — |
| Bitget | `bitget` | Yes |
| Backpack | `backpack` | — |
| BingX | `bingx` | — |
| HTX (Huobi) | `htx` | — |
| MEXC | `mexc` | — |
| Pionex | `pionex` | — |
| Bitfinex | `bitfinex` | Yes |

---

## Tips

- **Demo vs live:** Demo/testnet accounts require `is_testnet=true`. If Claude connects but returns auth errors on a demo account, remind it to use testnet mode.
- **Session reuse:** Within a conversation, Claude remembers your `session_id` and reuses it automatically — you don't need to reconnect for every query.
- **Multiple exchanges:** You can work with several exchanges in the same conversation. Just tell Claude which account to use for each operation.
- **Credentials:** Claude reads credentials from your `.env` file by the prefix name (e.g. `bbDDemo` for Bybit demo). You never need to type credentials in the chat.
