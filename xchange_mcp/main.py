"""FastAPI application: lifespan, health endpoint, SSE/stdio mount."""

from __future__ import annotations

import argparse
import logging
import os
import sys

# Make library modules importable
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi_key_auth import AuthorizerMiddleware

from config import settings
from server import mcp, set_session_manager
from session import SessionManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_session_manager: SessionManager | None = None

# Initialize the streamable HTTP sub-app now so mcp.session_manager is available for lifespan
_mcp_http_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _session_manager

    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    _session_manager = SessionManager(redis_client, settings)
    set_session_manager(_session_manager)

    logger.info(f"MCP server started (Redis: {settings.redis_url})")
    async with mcp.session_manager.run():
        yield

    logger.info("MCP server shutting down — closing all sessions...")
    await _session_manager.close_all()
    await redis_client.aclose()


app = FastAPI(title="xchange MCP", lifespan=lifespan)
app.add_middleware(AuthorizerMiddleware, public_paths=["/health"])
# app.add_middleware(AuthorizerMiddleware, public_paths=["/mcp"], key_pattern="API_KEY_")
# optional use regex startswith
# app.add_middleware(AuthorizerMiddleware, public_paths=["/ping", "^/users"])
# app.add_middleware(AuthorizerMiddleware, public_paths=["/health", "/mcp"])   <--- this is literally no auth needed

@app.get("/health")
async def health():
    return {"status": "ok"}


# Streamable-HTTP transport: POST /mcp (internal path within the sub-app)
# Must be mounted at "/" so the sub-app's internal "/mcp" route is reachable at POST /mcp
app.mount("/", _mcp_http_app)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="xchange MCP server")
    parser.add_argument(
        "--transport",
        choices=["sse", "stdio"],
        default="sse",
        help="Transport mode (default: sse)",
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=os.environ.get("MCP_SERVER_PORT", 8000))
    args = parser.parse_args()

    if args.transport == "stdio":
        # aioredis.from_url() is synchronous construction; actual I/O happens
        # inside mcp.run()'s event loop when tools are called.
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        _session_manager = SessionManager(redis_client, settings)
        set_session_manager(_session_manager)
        mcp.run(transport="stdio")
    else:
        import uvicorn
        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=False, #LIVE 
            #DEBUG reload=True, 
        )


if __name__ == "__main__":
    main()
