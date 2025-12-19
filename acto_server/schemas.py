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


class WalletConnectRequest(BaseModel):
    wallet_address: str


class WalletConnectResponse(BaseModel):
    challenge: str
    message: str


class WalletVerifyRequest(BaseModel):
    wallet_address: str
    signature: str
    challenge: str


class WalletVerifyResponse(BaseModel):
    success: bool
    user_id: str
    wallet_address: str
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class ApiKeyStatsResponse(BaseModel):
    key_id: str
    request_count: int
    endpoint_usage: dict[str, int]
    last_used_at: str | None
