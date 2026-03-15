"""FastAPI application: lifespan, health endpoint, SSE/stdio mount."""

from __future__ import annotations

import argparse
import logging
import os
import sys

# Make library modules importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI

from .config import settings
from .server import mcp, set_session_manager
from .session import SessionManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_session_manager: SessionManager | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _session_manager

    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    _session_manager = SessionManager(redis_client, settings)
    set_session_manager(_session_manager)

    logger.info(f"MCP server started (Redis: {settings.redis_url})")
    yield

    logger.info("MCP server shutting down — closing all sessions...")
    await _session_manager.close_all()
    await redis_client.aclose()


app = FastAPI(title="exchange-client MCP", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Mount FastMCP SSE routes
app.mount("/", mcp.sse_app())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="exchange-client MCP server")
    parser.add_argument(
        "--transport",
        choices=["sse", "stdio"],
        default="sse",
        help="Transport mode (default: sse)",
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.transport == "stdio":
        import asyncio
        import redis.asyncio as aioredis

        async def run_stdio():
            global _session_manager
            redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
            _session_manager = SessionManager(redis_client, settings)
            set_session_manager(_session_manager)
            try:
                await mcp.run_async(transport="stdio")
            finally:
                await _session_manager.close_all()
                await redis_client.aclose()

        asyncio.run(run_stdio())
    else:
        import uvicorn
        uvicorn.run(
            "mcp_server.main:app",
            host=args.host,
            port=args.port,
            reload=False,
        )


if __name__ == "__main__":
    main()
