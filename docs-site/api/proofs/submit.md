# Submit Proof

Submit a new execution proof to the ACTO registry.

## Endpoint

<div class="endpoint-card">
  <span class="method-badge post">POST</span>
  <span class="path">/v1/proofs</span>
</div>

## Request

### Headers

```http
Authorization: Bearer YOUR_API_KEY
X-Wallet-Address: YOUR_WALLET_ADDRESS
Content-Type: application/json
```

### Body

```json
{
  "envelope": {
    "payload": {
      "version": "1",
      "subject": {
        "task_id": "pick-and-place-001",
        "robot_id": "robot-alpha-01",
        "run_id": "run-2025-01-15"
      },
      "created_at": "2025-01-15T10:30:00Z",
      "telemetry_normalized": {
        "events": [
          {
            "ts": "2025-01-15T10:30:00Z",
            "topic": "sensor",
            "data": {"value": 42}
          }
        ]
      },
      "telemetry_hash": "abc123...",
      "payload_hash": "def456...",
      "hash_alg": "blake3",
      "signature_alg": "ed25519",
      "meta": {}
    },
    "signer_public_key_b64": "base64_encoded_public_key",
    "signature_b64": "base64_encoded_signature",
    "anchor_ref": null
  }
}
```

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `envelope` | `ProofEnvelope` | Yes | The signed proof envelope |
| `envelope.payload` | `ProofPayload` | Yes | The proof payload |
| `envelope.payload.version` | `string` | Yes | Protocol version (currently "1") |
| `envelope.payload.subject` | `object` | Yes | Subject identifiers |
| `envelope.payload.subject.task_id` | `string` | Yes | Task identifier |
| `envelope.payload.subject.robot_id` | `string` | No | Robot identifier |
| `envelope.payload.subject.run_id` | `string` | No | Run identifier |
| `envelope.payload.created_at` | `string` | Yes | ISO 8601 timestamp |
| `envelope.payload.telemetry_normalized` | `object` | Yes | Normalized telemetry data |
| `envelope.payload.telemetry_hash` | `string` | Yes | BLAKE3 hash of telemetry |
| `envelope.payload.payload_hash` | `string` | Yes | BLAKE3 hash of payload |
| `envelope.payload.hash_alg` | `string` | Yes | Hash algorithm ("blake3") |
| `envelope.payload.signature_alg` | `string` | Yes | Signature algorithm ("ed25519") |
| `envelope.payload.meta` | `object` | No | Arbitrary metadata |
| `envelope.signer_public_key_b64` | `string` | Yes | Base64 public key |
| `envelope.signature_b64` | `string` | Yes | Base64 signature |
| `envelope.anchor_ref` | `string` | No | Solana anchor reference |

## Response

### Success (200 OK)

```json
{
  "proof_id": "abc123def456..."
}
```

### Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Invalid API key"
}
```

**403 Forbidden:**
```json
{
  "detail": "Insufficient token balance"
}
```

**422 Unprocessable Entity:**
```json
{
  "detail": "Invalid proof envelope: missing required field 'task_id'"
}
```

## Examples

### cURL

```bash
curl -X POST https://api.actobotics.net/v1/proofs \
  -H "Authorization: Bearer acto_abc123..." \
  -H "X-Wallet-Address: 5K8vK..." \
  -H "Content-Type: application/json" \
  -d '{
    "envelope": {
      "payload": {
        "version": "1",
        "subject": {
          "task_id": "pick-and-place-001",
          "robot_id": "robot-alpha-01"
        },
        "created_at": "2025-01-15T10:30:00Z",
        "telemetry_normalized": {...},
        "telemetry_hash": "abc123...",
        "payload_hash": "def456...",
        "hash_alg": "blake3",
        "signature_alg": "ed25519",
        "meta": {}
      },
      "signer_public_key_b64": "...",
      "signature_b64": "...",
      "anchor_ref": null
    }
  }'
```

### Python SDK (Recommended)

```python
from acto.client import ACTOClient
from acto.proof import create_proof
from acto.crypto import KeyPair
from acto.telemetry.models import TelemetryBundle, TelemetryEvent

# Create the proof
keypair = KeyPair.generate()
bundle = TelemetryBundle(
    task_id="pick-and-place-001",
    robot_id="robot-alpha-01",
    events=[
        TelemetryEvent(
            ts="2025-01-15T10:30:00Z",
            topic="sensor",
            data={"value": 42}
        )
    ]
)
envelope = create_proof(bundle, keypair.private_key_b64, keypair.public_key_b64)

# Submit via SDK
client = ACTOClient(api_key="...", wallet_address="...")
proof_id = client.submit_proof(envelope)
print(f"Submitted: {proof_id}")
```

### JavaScript

```javascript
const response = await fetch('https://api.actobotics.net/v1/proofs', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'X-Wallet-Address': WALLET_ADDRESS,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ envelope })
});

const { proof_id } = await response.json();
console.log(`Submitted: ${proof_id}`);
```

## Notes

- Proofs are automatically verified on submission
- Invalid proofs will be rejected with a 422 error
- The `proof_id` is the payload hash (deterministic)
- Duplicate proofs (same payload_hash) are allowed but deduplicated

