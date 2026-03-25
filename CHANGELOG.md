# Changelog

All notable changes to xchange-mcp are documented here.

## [1.0.2] — 2026-03-25

### Changed
- Restructured source layout: moved package from `xchange_mcp/` to `src/xchange-mcp/` using setuptools `package-dir` mapping

## [1.0.1] — 2026-03-24

### Changed
- Disabled `fastapi-key-auth` middleware (auth bypass via public_paths)
- Added `fastapi-key-auth` package as middleware dependency

## [1.0.0] — 2026-03-23

### Added
- 17 MCP tools: `init_exchange`, `close_exchange`, `fetch_balance`, `fetch_positions`, `create_order`, `cancel_order`, `cancel_all_orders`, `fetch_order`, `fetch_open_orders`, `fetch_closed_orders`, `fetch_my_trades`, `close_position`, `set_leverage`, `get_closed_pnls`, `fetch_ticker`, `fetch_order_book`, `fetch_ohlcv`
- Session management with Redis persistence and in-memory LRU pool
- stdio and SSE/Streamable-HTTP transport support
- Paper-trading mode (`MCP_DRYRUN=true`)
- Optional Fernet encryption for stored credentials (`MCP_ENCRYPTION_KEY`)
- Structured error codes for reliable AI parsing
- Support for 20+ exchanges via xchange/CCXT
- Claude Desktop, OpenCode, OpenClaw client configs
- TUTORIAL.md and TUTORIAL-USER.md documentation
