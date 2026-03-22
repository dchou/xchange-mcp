"""MCP server configuration via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    session_ttl: int = 3600          # seconds
    max_pool_size: int = 50
    encryption_key: str = ""         # optional Fernet key for encrypting configs in Redis
    dryrun: bool = False
    allowed_hosts: list[str] = []    # e.g. ["myserver.com:8888", "localhost:8888"]

    model_config = {"env_prefix": "MCP_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
