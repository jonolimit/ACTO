from __future__ import annotations

import hashlib

import orjson
from sqlalchemy import select

from acto.cache import get_cache_backend
from acto.config.settings import Settings
from acto.errors import RegistryError
from acto.proof.models import ProofEnvelope
from acto.registry.db import make_engine, make_session_factory
from acto.registry.models import Base, ProofRecord


def _proof_id_from_hash(payload_hash: str) -> str:
    return hashlib.sha256(payload_hash.encode("utf-8")).hexdigest()[:32]


def _cache_key_proof(proof_id: str) -> str:
    """Generate cache key for a proof."""
    return f"proof:{proof_id}"


def _cache_key_list(limit: int, offset: int = 0) -> str:
    """Generate cache key for proof list."""
    return f"proofs:list:{limit}:{offset}"


class ProofRegistry:
    """Database-backed registry for proofs with optional caching."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.engine = make_engine(self.settings)
        self.SessionLocal = make_session_factory(self.engine)
        self.cache = get_cache_backend(self.settings)
        Base.metadata.create_all(self.engine)

    def upsert(self, envelope: ProofEnvelope) -> str:
        proof_id = _proof_id_from_hash(envelope.payload.payload_hash)
        cache_key = _cache_key_proof(proof_id)
        try:
            with self.SessionLocal() as session:
                existing = session.get(ProofRecord, proof_id)
                if existing:
                    existing.envelope_json = orjson.dumps(envelope.model_dump()).decode("utf-8")
                    existing.anchor_ref = envelope.anchor_ref
                else:
                    rec = ProofRecord(
                        proof_id=proof_id,
                        task_id=envelope.payload.subject.task_id,
                        robot_id=envelope.payload.subject.robot_id,
                        run_id=envelope.payload.subject.run_id,
                        created_at=envelope.payload.created_at,
                        payload_hash=envelope.payload.payload_hash,
                        signer_public_key_b64=envelope.signer_public_key_b64,
                        signature_b64=envelope.signature_b64,
                        envelope_json=orjson.dumps(envelope.model_dump()).decode("utf-8"),
                        anchor_ref=envelope.anchor_ref,
                    )
                    session.add(rec)
                session.commit()

            # Invalidate cache for this proof and list caches
            if self.cache:
                self.cache.set(cache_key, envelope.model_dump(), ttl=self.settings.cache_ttl)
                # Invalidate list caches (we use a simple approach: clear all list caches)
                # In production, you might want a more sophisticated cache invalidation strategy

            return proof_id
        except Exception as e:
            raise RegistryError(str(e)) from e

    def get(self, proof_id: str) -> ProofEnvelope:
        # Try cache first
        cache_key = _cache_key_proof(proof_id)
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return ProofEnvelope.model_validate(cached)

        # Cache miss, fetch from database
        with self.SessionLocal() as session:
            rec = session.get(ProofRecord, proof_id)
            if not rec:
                raise RegistryError("Proof not found.")
            envelope = ProofEnvelope.model_validate(orjson.loads(rec.envelope_json))

        # Store in cache
        if self.cache:
            self.cache.set(cache_key, envelope.model_dump(), ttl=self.settings.cache_ttl)

        return envelope

    def list(self, limit: int = 50) -> list[dict]:
        with self.SessionLocal() as session:
            stmt = select(ProofRecord).order_by(ProofRecord.created_at.desc()).limit(limit)
            rows = session.execute(stmt).scalars().all()
            return [
                {
                    "proof_id": r.proof_id,
                    "task_id": r.task_id,
                    "robot_id": r.robot_id,
                    "run_id": r.run_id,
                    "created_at": r.created_at,
                    "payload_hash": r.payload_hash,
                    "anchor_ref": r.anchor_ref,
                }
                for r in rows
            ]
