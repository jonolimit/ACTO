# ACTO API Documentation

The ACTO Verification API provides a hosted service for submitting and verifying execution proofs. All API endpoints require Bearer token authentication.

## Base URL

```
https://api.actobotics.net
```

## Authentication

All API endpoints (except `/health`, `/metrics`, and `/dashboard`) require Bearer token authentication.

Include your API key in the `Authorization` header:

```
Authorization: Bearer <your-api-key>
```

### Getting Your API Key

1. Visit the [API Key Dashboard](https://api.actobotics.net/dashboard)
2. Create a new API key with a descriptive name
3. **Copy the key immediately** - it's only shown once
4. Store it securely for use in your API requests

### Using Your API Key

**cURL Example:**
```bash
curl -X POST https://api.actobotics.net/v1/proofs \
  -H "Authorization: Bearer your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"envelope": {...}}'
```

**Python Example:**
```python
import httpx

headers = {
    "Authorization": "Bearer your-api-key-here",
    "Content-Type": "application/json"
}

response = httpx.post(
    "https://api.actobotics.net/v1/proofs",
    headers=headers,
    json={"envelope": proof_envelope}
)
```

**JavaScript/TypeScript Example:**
```javascript
const response = await fetch('https://api.actobotics.net/v1/proofs', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key-here',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ envelope: proofEnvelope })
});
```

## API Key Dashboard

The dashboard at `https://api.actobotics.net/dashboard` provides a web interface for managing your API keys.

### Features

- **Create API Keys**: Generate new API keys with descriptive names
- **View Keys**: See all your API keys with creation date and last used time
- **Delete Keys**: Deactivate API keys you no longer need

### Dashboard Usage

1. **Creating a Key**:
   - Enter a descriptive name (e.g., "Production Key", "Development Key")
   - Click "Create API Key"
   - Copy the key immediately - it won't be shown again
   - The key is automatically stored in your browser's localStorage

2. **Viewing Keys**:
   - All your active keys are listed with:
     - Key ID
     - Creation timestamp
     - Last used timestamp
     - Status (Active/Inactive)

3. **Deleting Keys**:
   - Click "Delete" on any active key
   - Confirm the deletion
   - The key will be deactivated immediately

**Note**: Once a key is deleted, it cannot be recovered. You'll need to create a new key to continue using the API.

## API Endpoints

### Public Endpoints

#### Health Check
```http
GET /health
```

Returns the health status of the API.

**Response:**
```json
{
  "ok": true,
  "service": "acto",
  "version": "0.4.0"
}
```

#### Metrics
```http
GET /metrics
```

Returns Prometheus-compatible metrics.

### Protected Endpoints

All endpoints below require Bearer token authentication.

#### Submit Proof
```http
POST /v1/proofs
```

Submit a new execution proof to the registry.

**Request Body:**
```json
{
  "envelope": {
    "payload": {
      "version": "1",
      "subject": {
        "task_id": "cleaning-run-001",
        "robot_id": "robot-001",
        "run_id": "run-2025-01-15"
      },
      "created_at": "2025-01-15T10:30:00Z",
      "telemetry_normalized": {...},
      "telemetry_hash": "...",
      "payload_hash": "...",
      "hash_alg": "blake3",
      "signature_alg": "ed25519",
      "meta": {}
    },
    "signer_public_key_b64": "...",
    "signature_b64": "...",
    "anchor_ref": null
  }
}
```

**Response:**
```json
{
  "proof_id": "abc123..."
}
```

#### List Proofs
```http
GET /v1/proofs?limit=50
```

List proofs from the registry.

**Query Parameters:**
- `limit` (optional): Maximum number of proofs to return (default: 50)

**Response:**
```json
{
  "items": [
    {
      "proof_id": "...",
      "task_id": "...",
      "created_at": "...",
      ...
    }
  ]
}
```

#### Get Proof
```http
GET /v1/proofs/{proof_id}
```

Retrieve a specific proof by ID.

**Response:**
```json
{
  "proof_id": "abc123...",
  "envelope": {
    "payload": {...},
    "signer_public_key_b64": "...",
    "signature_b64": "..."
  }
}
```

#### Verify Proof
```http
POST /v1/verify
```

Verify a proof's signature and integrity.

**Request Body:**
```json
{
  "envelope": {
    "payload": {...},
    "signer_public_key_b64": "...",
    "signature_b64": "..."
  }
}
```

**Response:**
```json
{
  "valid": true,
  "reason": "ok"
}
```

#### Score Proof
```http
POST /v1/score
```

Calculate a reputation score for a proof.

**Request Body:**
```json
{
  "envelope": {
    "payload": {...},
    "signer_public_key_b64": "...",
    "signature_b64": "..."
  }
}
```

**Response:**
```json
{
  "score": 85.5,
  "reasons": ["Valid signature", "Recent timestamp"]
}
```

#### Check Solana Token Access
```http
POST /v1/access/check
```

Check if a Solana wallet has sufficient token balance.

**Request Body:**
```json
{
  "rpc_url": "https://api.mainnet-beta.solana.com",
  "owner": "wallet-address",
  "mint": "token-mint-address",
  "minimum": 50000
}
```

**Response:**
```json
{
  "allowed": true,
  "reason": "Sufficient balance",
  "balance": 125000.0
}
```

### API Key Management Endpoints

#### Create API Key
```http
POST /v1/keys
```

Create a new API key. **Note**: This endpoint does not require authentication (to allow creating your first key).

**Request Body:**
```json
{
  "name": "Production Key"
}
```

**Response:**
```json
{
  "key_id": "xyz789...",
  "key": "acto_abc123...",
  "name": "Production Key",
  "created_at": "2025-01-15T10:30:00Z",
  "created_by": null
}
```

**Important**: The `key` field is only returned once. Store it securely immediately.

#### List API Keys
```http
GET /v1/keys
```

List all your API keys (without the actual key values).

**Response:**
```json
{
  "keys": [
    {
      "key_id": "xyz789...",
      "name": "Production Key",
      "created_at": "2025-01-15T10:30:00Z",
      "last_used_at": "2025-01-15T11:00:00Z",
      "is_active": true,
      "created_by": null
    }
  ]
}
```

#### Delete API Key
```http
DELETE /v1/keys/{key_id}
```

Deactivate an API key.

**Response:**
```json
{
  "success": true,
  "key_id": "xyz789..."
}
```

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid Bearer token
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- Default: 5 requests per second
- Burst: Up to 20 requests in a short period

If you exceed the rate limit, you'll receive a `429 Too Many Requests` response.

## Best Practices

1. **Store Keys Securely**: Never commit API keys to version control
2. **Use Environment Variables**: Store keys in environment variables or secret management systems
3. **Rotate Keys Regularly**: Delete old keys and create new ones periodically
4. **Use Descriptive Names**: Name your keys clearly (e.g., "Production", "Development", "CI/CD")
5. **Monitor Key Usage**: Check the "last used" timestamp in the dashboard to identify unused keys
6. **Delete Unused Keys**: Remove keys you no longer need to minimize security risk

## Examples

### Complete Workflow

```python
import httpx
from acto.proof import create_proof
from acto.crypto import KeyPair
from acto.telemetry.models import TelemetryBundle, TelemetryEvent
from datetime import datetime

# 1. Create proof locally
keypair = KeyPair.generate()
bundle = TelemetryBundle(
    task_id="task-001",
    robot_id="robot-001",
    events=[
        TelemetryEvent(
            ts=datetime.now().isoformat(),
            topic="sensor",
            data={"temperature": 25.5}
        )
    ]
)
envelope = create_proof(
    bundle,
    keypair.private_key_b64,
    keypair.public_key_b64
)

# 2. Submit to API
api_key = "your-api-key-here"
response = httpx.post(
    "https://api.actobotics.net/v1/proofs",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={"envelope": envelope.model_dump()}
)

if response.status_code == 200:
    proof_id = response.json()["proof_id"]
    print(f"Proof submitted: {proof_id}")
    
    # 3. Verify the proof
    verify_response = httpx.post(
        "https://api.actobotics.net/v1/verify",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={"envelope": envelope.model_dump()}
    )
    print(f"Verification: {verify_response.json()}")
```

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/your-repo/acto).

