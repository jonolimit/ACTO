from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_config_files() -> list[str]:
    """Get list of config files to load."""
    files = [".env"]
    home = Path.home()
    config_file = home / ".acto" / "config.toml"
    if config_file.exists():
        files.append(str(config_file))
    return files


class Settings(BaseSettings):
    """Central configuration for ACTO."""

    model_config = SettingsConfigDict(
        env_prefix="ACTO_",
        env_file=_get_config_files(),
        extra="ignore",
    )

    # Storage
    db_url: str = "sqlite:///./data/acto.sqlite"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600

    # Logging
    log_level: str = "INFO"
    json_logs: bool = False

    # Proof defaults
    proof_version: str = "1"
    proof_hash_alg: str = "blake3"
    proof_signature_alg: str = "ed25519"

    # Server
    host: str = "127.0.0.1"
    port: int = 8080

    # API security
    api_auth_enabled: bool = False

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_rps: float = 5.0
    rate_limit_burst: int = 20

    # Upload limits
    max_telemetry_bytes: int = 8_000_000

    # Caching
    cache_enabled: bool = False
    cache_backend: str = "memory"  # "memory" or "redis"
    cache_ttl: int = 3600  # Time-to-live in seconds
    redis_url: str = "redis://localhost:6379/0"
    redis_password: str | None = None
