# Verify Proof

Verify a proof's cryptographic signature and integrity.

## Endpoint

<div class="endpoint-card">
  <span class="method-badge post">POST</span>
  <span class="path">/v1/verify</span>
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
}
```

## Response

### Success (200 OK)

**Valid proof:**
```json
{
  "valid": true,
  "reason": "ok"
}
```

**Invalid proof:**
```json
{
  "valid": false,
  "reason": "Invalid signature"
}
```

### Possible Reasons

| Reason | Description |
|--------|-------------|
| `ok` | Proof is valid |
| `Invalid signature` | Signature doesn't match public key |
| `Hash mismatch` | Payload hash doesn't match computed hash |
| `Invalid public key` | Public key is malformed |
| `Unsupported algorithm` | Unknown hash or signature algorithm |

## Examples

### cURL

```bash
curl -X POST https://api.actobotics.net/v1/verify \
  -H "Authorization: Bearer acto_abc123..." \
  -H "X-Wallet-Address: 5K8vK..." \
  -H "Content-Type: application/json" \
  -d '{
    "envelope": {
      "payload": {...},
      "signer_public_key_b64": "...",
      "signature_b64": "..."
    }
  }'
```

### Python SDK

```python
from acto.client import ACTOClient

client = ACTOClient(api_key="...", wallet_address="...")

result = client.verify(envelope)

if result.valid:
    print("✅ Proof is valid!")
else:
    print(f"❌ Invalid: {result.reason}")
```

### JavaScript

```javascript
const response = await fetch('https://api.actobotics.net/v1/verify', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'X-Wallet-Address': WALLET_ADDRESS,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ envelope })
});

const { valid, reason } = await response.json();
console.log(`Valid: ${valid}, Reason: ${reason}`);
```

## Verification Process

When you call `/v1/verify`, the API:

1. **Extracts** the payload_hash from the envelope
2. **Recomputes** the hash from the payload
3. **Compares** the hashes (integrity check)
4. **Verifies** the Ed25519 signature using the public key
5. **Returns** valid/invalid with reason

```
┌──────────────────────────────────────────────────────┐
│                 Verification Flow                     │
├──────────────────────────────────────────────────────┤
│                                                       │
│  1. Extract payload_hash from envelope                │
│                    ▼                                  │
│  2. Canonicalize payload to JSON                      │
│                    ▼                                  │
│  3. Compute BLAKE3 hash of payload                    │
│                    ▼                                  │
│  4. Compare with claimed payload_hash                 │
│      └── If mismatch: return "Hash mismatch"          │
│                    ▼                                  │
│  5. Decode signature_b64 and public_key_b64           │
│                    ▼                                  │
│  6. Verify Ed25519 signature over payload_hash        │
│      └── If invalid: return "Invalid signature"       │
│                    ▼                                  │
│  7. Return { valid: true, reason: "ok" }              │
│                                                       │
└──────────────────────────────────────────────────────┘
```

## Notes

::: info API-Only Verification
Starting from v0.9.1, all verification must go through the API. Local verification is no longer available in the SDK.

This ensures:
- Centralized integrity verification
- Audit trails for compliance
- Automatic fleet tracking
- Token-gated access control
:::

- Verification is idempotent - same input always gives same result
- Verification doesn't require the proof to be in the registry
- Use [batch verification](/api/verification/batch) for multiple proofs

