# Batch Verify

Verify multiple proofs in a single request for improved efficiency.

## Endpoint

<div class="endpoint-card">
  <span class="method-badge post">POST</span>
  <span class="path">/v1/verify/batch</span>
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
  "envelopes": [
    {
      "payload": {...},
      "signer_public_key_b64": "...",
      "signature_b64": "..."
    },
    {
      "payload": {...},
      "signer_public_key_b64": "...",
      "signature_b64": "..."
    },
    {
      "payload": {...},
      "signer_public_key_b64": "...",
      "signature_b64": "..."
    }
  ]
}
```

### Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `envelopes` | `ProofEnvelope[]` | Yes | Array of proof envelopes |

::: tip Batch Size
Maximum recommended batch size is **100 proofs** per request.
:::

## Response

### Success (200 OK)

```json
{
  "results": [
    {
      "index": 0,
      "valid": true,
      "reason": "ok",
      "payload_hash": "abc123..."
    },
    {
      "index": 1,
      "valid": true,
      "reason": "ok",
      "payload_hash": "def456..."
    },
    {
      "index": 2,
      "valid": false,
      "reason": "Invalid signature",
      "payload_hash": null
    }
  ],
  "total": 3,
  "valid_count": 2,
  "invalid_count": 1
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `results` | `array` | Individual verification results |
| `results[].index` | `number` | Position in input array |
| `results[].valid` | `boolean` | Whether proof is valid |
| `results[].reason` | `string` | Verification result reason |
| `results[].payload_hash` | `string\|null` | Hash if valid, null if invalid |
| `total` | `number` | Total proofs verified |
| `valid_count` | `number` | Number of valid proofs |
| `invalid_count` | `number` | Number of invalid proofs |

## Examples

### cURL

```bash
curl -X POST https://api.actobotics.net/v1/verify/batch \
  -H "Authorization: Bearer acto_abc123..." \
  -H "X-Wallet-Address: 5K8vK..." \
  -H "Content-Type: application/json" \
  -d '{
    "envelopes": [
      {"payload": {...}, "signature_b64": "...", "signer_public_key_b64": "..."},
      {"payload": {...}, "signature_b64": "...", "signer_public_key_b64": "..."},
      {"payload": {...}, "signature_b64": "...", "signer_public_key_b64": "..."}
    ]
  }'
```

### Python SDK

```python
from acto.client import ACTOClient

client = ACTOClient(api_key="...", wallet_address="...")

# Verify multiple proofs
results = client.verify_batch([envelope1, envelope2, envelope3])

print(f"Total: {results.total}")
print(f"Valid: {results.valid_count}")
print(f"Invalid: {results.invalid_count}")

# Check individual results
for r in results.results:
    status = "✅" if r.valid else "❌"
    print(f"  {status} Index {r.index}: {r.reason}")
```

### JavaScript

```javascript
const response = await fetch('https://api.actobotics.net/v1/verify/batch', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'X-Wallet-Address': WALLET_ADDRESS,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    envelopes: [envelope1, envelope2, envelope3]
  })
});

const { valid_count, invalid_count, results } = await response.json();
console.log(`Valid: ${valid_count}/${valid_count + invalid_count}`);
```

## Use Cases

### Bulk Import Verification

```python
import json

# Load proofs from file
with open("proofs.json") as f:
    envelopes = [ProofEnvelope.model_validate(p) for p in json.load(f)]

# Verify in batches of 100
for i in range(0, len(envelopes), 100):
    batch = envelopes[i:i+100]
    results = client.verify_batch(batch)
    
    print(f"Batch {i//100 + 1}: {results.valid_count}/{results.total} valid")
    
    # Handle invalid proofs
    for r in results.results:
        if not r.valid:
            print(f"  Invalid proof at index {r.index}: {r.reason}")
```

### Submit Only Valid Proofs

```python
# Verify batch
results = client.verify_batch(envelopes)

# Submit only valid proofs
for r in results.results:
    if r.valid:
        envelope = envelopes[r.index]
        proof_id = client.submit_proof(envelope)
        print(f"Submitted: {proof_id}")
```

## Performance

Batch verification is more efficient than individual calls:

| Approach | 100 Proofs | Network Round-trips |
|----------|------------|---------------------|
| Individual `/v1/verify` | ~10 seconds | 100 |
| Batch `/v1/verify/batch` | ~0.5 seconds | 1 |

## Notes

- All proofs in a batch are verified independently
- A single invalid proof doesn't affect others
- Results maintain the same order as input
- Empty batch returns empty results

