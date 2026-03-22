#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/xchange_mcp"

HOST="${MCP_HOST:-0.0.0.0}"
PORT="${MCP_PORT:-8888}"

echo "Starting xchange-mcp on $HOST:$PORT ..."
exec uvicorn main:app --host "$HOST" --port "$PORT" --no-access-log
