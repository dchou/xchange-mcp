"""Session manager: Redis config store + in-memory ExchangeClient pool."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Optional

from config import Settings
from error_handling import SessionNotFoundError

try:
    from xchange import ExchangeClient
except ImportError:
    ExchangeClient = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

_REDIS_KEY_PREFIX = "exchange_mcp:session:"


def _config_key(session_id: str) -> str:
    return f"{_REDIS_KEY_PREFIX}{session_id}:config"


class SessionManager:
    """Two-layer session store: Redis (persistent) + in-memory pool (fast)."""

    def __init__(self, redis_client: Any, settings: Settings):
        self._redis = redis_client
        self._settings = settings
        self._pool: dict[str, Any] = {}       # session_id → ExchangeClient
        self._last_used: dict[str, datetime] = {}
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def create_session(self, config: dict) -> str:
        """Store config in Redis, create live ExchangeClient, return session_id."""
        session_id = str(uuid.uuid4())

        # Persist config to Redis
        await self._redis.set(
            _config_key(session_id),
            json.dumps(config),
            ex=self._settings.session_ttl,
        )

        # Create live client
        client = await ExchangeClient.create(config)

        # Optionally wrap in DryRun
        dryrun = self._settings.dryrun or os.getenv("DRYRUN", "false").lower() == "true"
        if dryrun:
            import ccxt.async_support as ccxt
            from xchange import DryRunExchangeClient

            raw_exchange = client.exchange
            client.exchange = DryRunExchangeClient(
                raw_exchange,
                initial_balances={"USDT": 10_000.0},
                slippage_pct=0.05,
                db_path="dryrun.db",
            )
            logger.info(f"[{session_id}] DryRun mode enabled")

        async with self._lock:
            await self._evict_if_needed()
            self._pool[session_id] = client
            self._last_used[session_id] = datetime.now()

        logger.info(f"[{session_id}] Session created for {config.get('exchange_name')}")
        return session_id

    async def get_client(self, session_id: str) -> Any:
        """Return live ExchangeClient; rebuild from Redis config if not in pool."""
        async with self._lock:
            if session_id in self._pool:
                self._last_used[session_id] = datetime.now()
                # Refresh Redis TTL
                await self._redis.expire(
                    _config_key(session_id), self._settings.session_ttl
                )
                return self._pool[session_id]

        # Slow path: try to rebuild from Redis
        raw = await self._redis.get(_config_key(session_id))
        if raw is None:
            raise SessionNotFoundError(f"Session '{session_id}' not found")

        config = json.loads(raw)
        logger.info(f"[{session_id}] Rebuilding client from Redis config")

        client = await ExchangeClient.create(config)

        async with self._lock:
            await self._evict_if_needed()
            self._pool[session_id] = client
            self._last_used[session_id] = datetime.now()
            await self._redis.expire(_config_key(session_id), self._settings.session_ttl)

        return client

    async def destroy_session(self, session_id: str) -> None:
        """Disconnect client and remove from pool + Redis."""
        async with self._lock:
            client = self._pool.pop(session_id, None)
            self._last_used.pop(session_id, None)

        if client is not None:
            try:
                await client.disconnect()
            except Exception as exc:
                logger.warning(f"[{session_id}] Error during disconnect: {exc}")

        await self._redis.delete(_config_key(session_id))
        logger.info(f"[{session_id}] Session destroyed")

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    async def _evict_if_needed(self) -> None:
        """Evict oldest session when pool exceeds MAX_POOL_SIZE. Must hold _lock."""
        if len(self._pool) < self._settings.max_pool_size:
            return

        oldest_id = min(self._last_used, key=lambda k: self._last_used[k])
        client = self._pool.pop(oldest_id, None)
        self._last_used.pop(oldest_id, None)

        if client is not None:
            try:
                await client.disconnect()
            except Exception:
                pass

        logger.info(f"[{oldest_id}] Evicted from pool (LRU)")

    async def close_all(self) -> None:
        """Disconnect all clients in pool on shutdown, preserving Redis configs for reconnection."""
        async with self._lock:
            pool_snapshot = list(self._pool.items())
            self._pool.clear()
            self._last_used.clear()

        for sid, client in pool_snapshot:
            try:
                await client.disconnect()
            except Exception as exc:
                logger.warning(f"[{sid}] Error during disconnect: {exc}")
            logger.info(f"[{sid}] Disconnected (config preserved in Redis)")
