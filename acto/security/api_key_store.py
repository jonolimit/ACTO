from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from acto.errors import AccessError
from acto.registry.models import Base
from acto.registry.db import make_engine, make_session_factory
from acto.config.settings import Settings


class ApiKeyRecord(Base):
    """Database model for API keys."""

    __tablename__ = "api_keys"

    key_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    key_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    last_used_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    created_by: Mapped[str | None] = mapped_column(String(256), nullable=True)


def generate_api_key(prefix: str = "acto") -> str:
    """Generate a new API key."""
    return f"{prefix}_{secrets.token_urlsafe(32)}"


def hash_api_key(key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


class ApiKeyStore:
    """Database-backed API key store."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = make_engine(settings)
        self.Session = make_session_factory(self.engine)
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Ensure database tables exist."""
        Base.metadata.create_all(self.engine)

    def create_key(self, name: str, created_by: str | None = None) -> dict[str, Any]:
        """Create a new API key and return both the key and its metadata."""
        key = generate_api_key()
        key_hash = hash_api_key(key)
        key_id = secrets.token_urlsafe(16)

        now = datetime.now(timezone.utc).isoformat()

        record = ApiKeyRecord(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            created_at=now,
            last_used_at=None,
            is_active=True,
            created_by=created_by,
        )

        with self.Session() as session:
            session.add(record)
            session.commit()

        return {
            "key_id": key_id,
            "key": key,  # Only returned once!
            "name": name,
            "created_at": now,
            "created_by": created_by,
        }

    def is_valid(self, key: str) -> bool:
        """Check if an API key is valid and active."""
        key_hash = hash_api_key(key)
        with self.Session() as session:
            record = session.query(ApiKeyRecord).filter(
                ApiKeyRecord.key_hash == key_hash,
                ApiKeyRecord.is_active == True,  # noqa: E712
            ).first()
            if record:
                # Update last_used_at
                record.last_used_at = datetime.now(timezone.utc).isoformat()
                session.commit()
                return True
        return False

    def require(self, key: str | None) -> None:
        """Require a valid API key, raise AccessError if invalid."""
        if not key or not self.is_valid(key):
            raise AccessError("Invalid or missing API key. Please provide a valid Bearer token.")

    def list_keys(self, include_inactive: bool = False) -> list[dict[str, Any]]:
        """List all API keys (without the actual key values)."""
        with self.Session() as session:
            query = session.query(ApiKeyRecord)
            if not include_inactive:
                query = query.filter(ApiKeyRecord.is_active == True)  # noqa: E712
            records = query.order_by(ApiKeyRecord.created_at.desc()).all()

            return [
                {
                    "key_id": record.key_id,
                    "name": record.name,
                    "created_at": record.created_at,
                    "last_used_at": record.last_used_at,
                    "is_active": record.is_active,
                    "created_by": record.created_by,
                }
                for record in records
            ]

    def delete_key(self, key_id: str) -> bool:
        """Delete (deactivate) an API key."""
        with self.Session() as session:
            record = session.query(ApiKeyRecord).filter(ApiKeyRecord.key_id == key_id).first()
            if record:
                record.is_active = False
                session.commit()
                return True
        return False

    def get_key(self, key_id: str) -> dict[str, Any] | None:
        """Get API key metadata by ID."""
        with self.Session() as session:
            record = session.query(ApiKeyRecord).filter(ApiKeyRecord.key_id == key_id).first()
            if record:
                return {
                    "key_id": record.key_id,
                    "name": record.name,
                    "created_at": record.created_at,
                    "last_used_at": record.last_used_at,
                    "is_active": record.is_active,
                    "created_by": record.created_by,
                }
        return None

