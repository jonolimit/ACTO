from __future__ import annotations

from pydantic import BaseModel

from acto.proof.models import ProofEnvelope


class ProofSubmitRequest(BaseModel):
    envelope: ProofEnvelope


class ProofSubmitResponse(BaseModel):
    proof_id: str


class VerifyRequest(BaseModel):
    envelope: ProofEnvelope


class VerifyResponse(BaseModel):
    valid: bool
    reason: str


class AccessCheckRequest(BaseModel):
    rpc_url: str
    owner: str
    mint: str
    minimum: float


class AccessCheckResponse(BaseModel):
    allowed: bool
    reason: str
    balance: float | None = None


class ApiKeyCreateRequest(BaseModel):
    name: str


class ApiKeyCreateResponse(BaseModel):
    key_id: str
    key: str
    name: str
    created_at: str
    created_by: str | None = None


class ApiKeyListResponse(BaseModel):
    keys: list[dict]


class ApiKeyDeleteResponse(BaseModel):
    success: bool
    key_id: str
