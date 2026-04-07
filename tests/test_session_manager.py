"""Unit tests for SessionManager."""

from __future__ import annotations

import json
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from error_handling import SessionNotFoundError
from session import SessionManager, _config_key


pytestmark = pytest.mark.asyncio


SAMPLE_CONFIG = {
    "exchange_name": "binance",
    "api_key": "test_key",
    "api_secret": "test_secret",
    "market_type": "spot",
}


async def test_create_session_stores_config_in_redis(session_manager, fake_redis):
    sm, MockClass, mock_client = session_manager

    session_id = await sm.create_session(SAMPLE_CONFIG)

    raw = await fake_redis.get(_config_key(session_id))
    assert raw is not None
    stored = json.loads(raw)
    assert stored["exchange_name"] == "binance"


async def test_create_session_returns_unique_ids(session_manager):
    sm, MockClass, mock_client = session_manager

    id1 = await sm.create_session(SAMPLE_CONFIG)
    id2 = await sm.create_session(SAMPLE_CONFIG)

    assert id1 != id2


async def test_get_client_returns_cached_instance(session_manager):
    sm, MockClass, mock_client = session_manager

    session_id = await sm.create_session(SAMPLE_CONFIG)

    # First call after creation — already in pool
    client1 = await sm.get_client(session_id)
    client2 = await sm.get_client(session_id)

    assert client1 is client2
    # ExchangeClient.create should only have been called once (during create_session)
    MockClass.create.assert_awaited_once()


async def test_get_client_rebuilds_from_redis_after_pool_miss(session_manager, fake_redis):
    sm, MockClass, mock_client = session_manager

    session_id = await sm.create_session(SAMPLE_CONFIG)

    # Remove from in-memory pool manually
    async with sm._lock:
        del sm._pool[session_id]
        del sm._last_used[session_id]

    MockClass.create.reset_mock()

    # Should rebuild from Redis
    client = await sm.get_client(session_id)

    assert client is mock_client
    MockClass.create.assert_awaited_once()


async def test_session_not_found_raises_error(session_manager):
    sm, _, _ = session_manager

    with pytest.raises(SessionNotFoundError):
        await sm.get_client("nonexistent-session-id")


async def test_destroy_session_removes_from_pool_and_redis(session_manager, fake_redis):
    sm, MockClass, mock_client = session_manager

    session_id = await sm.create_session(SAMPLE_CONFIG)
    await sm.destroy_session(session_id)

    # Pool should not have the session
    assert session_id not in sm._pool

    # Redis key should be gone
    raw = await fake_redis.get(_config_key(session_id))
    assert raw is None

    # Client.close should have been called
    mock_client.close.assert_awaited_once()


async def test_ttl_refreshed_on_get_client(session_manager, fake_redis):
    sm, MockClass, mock_client = session_manager

    session_id = await sm.create_session(SAMPLE_CONFIG)

    # Set a very short TTL manually
    await fake_redis.expire(_config_key(session_id), 10)
    ttl_before = await fake_redis.ttl(_config_key(session_id))
    assert ttl_before <= 10

    await sm.get_client(session_id)

    ttl_after = await fake_redis.ttl(_config_key(session_id))
    # TTL should be refreshed to the full session_ttl
    assert ttl_after > 10


async def test_lru_eviction_when_pool_full(session_manager):
    """Pool max_pool_size=3; adding a 4th should evict the oldest."""
    sm, MockClass, mock_client = session_manager

    ids = []
    for _ in range(3):
        sid = await sm.create_session(SAMPLE_CONFIG)
        ids.append(sid)

    first_id = ids[0]
    assert first_id in sm._pool

    # Add one more — pool limit is 3, so first_id should be evicted
    await sm.create_session(SAMPLE_CONFIG)

    assert first_id not in sm._pool
    assert len(sm._pool) <= sm._settings.max_pool_size
