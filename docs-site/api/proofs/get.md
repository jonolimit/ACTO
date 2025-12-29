# Get Proof

Retrieve a specific proof by ID.

## Endpoint

<div class="endpoint-card">
  <span class="method-badge get">GET</span>
  <span class="path">/v1/proofs/{proof_id}</span>
</div>

## Request

### Headers

```http
Authorization: Bearer YOUR_API_KEY
X-Wallet-Address: YOUR_WALLET_ADDRESS
```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `proof_id` | `string` | Yes | The proof ID (payload_hash) |

## Response

### Success (200 OK)

```json
{
  "proof_id": "abc123...",
  "envelope": {
    "payload": {
      "version": "1",
      "subject": {
        "task_id": "pick-and-place-001",
        "robot_id": "robot-alpha-01",
        "run_id": "run-2025-01-15"
      },
      "created_at": "2025-01-15T10:30:00Z",
      "telemetry_normalized": {...},
      "telemetry_hash": "...",
      "payload_hash": "abc123...",
      "hash_alg": "blake3",
      "signature_alg": "ed25519",
      "meta": {}
    },
    "signer_public_key_b64": "...",
    "signature_b64": "..."
  }
}
```

### Error (404 Not Found)

```json
{
  "detail": "Proof not found"
}
```

## Examples

### cURL

```bash
curl https://api.actobotics.net/v1/proofs/abc123... \
  -H "Authorization: Bearer acto_abc123..." \
  -H "X-Wallet-Address: 5K8vK..."
```

### Python SDK

```python
from acto.client import ACTOClient

client = ACTOClient(api_key="...", wallet_address="...")

# Get a specific proof
envelope = client.get_proof("abc123...")

print(f"Task: {envelope.payload.subject.task_id}")
print(f"Robot: {envelope.payload.subject.robot_id}")
print(f"Created: {envelope.payload.created_at}")
```

### JavaScript

```javascript
const response = await fetch(`https://api.actobotics.net/v1/proofs/${proofId}`, {
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'X-Wallet-Address': WALLET_ADDRESS
  }
});

if (response.status === 404) {
  console.log('Proof not found');
} else {
  const { envelope } = await response.json();
  console.log(envelope.payload.subject.task_id);
}
```

## Notes

- The `proof_id` is the `payload_hash` of the envelope
- Returns the full envelope including telemetry data
- Use this to retrieve and re-verify proofs

