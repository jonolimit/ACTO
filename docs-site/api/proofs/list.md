# List Proofs

List recent proofs.

## Endpoint

<div class="endpoint-card">
  <span class="method-badge get">GET</span>
  <span class="path">/v1/proofs</span>
</div>

## Request

### Headers

```http
Authorization: Bearer YOUR_API_KEY
X-Wallet-Address: YOUR_WALLET_ADDRESS
```

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | `integer` | No | 50 | Max results (1-100) |

## Response

### Success (200 OK)

```json
{
  "items": [
    {
      "proof_id": "abc123...",
      "task_id": "pick-and-place-001",
      "robot_id": "robot-alpha-01",
      "created_at": "2025-01-15T10:30:00Z"
    },
    {
      "proof_id": "def456...",
      "task_id": "quality-inspection-002",
      "robot_id": "robot-beta-02",
      "created_at": "2025-01-15T09:15:00Z"
    }
  ]
}
```

## Examples

### cURL

```bash
curl https://api.actobotics.net/v1/proofs?limit=10 \
  -H "Authorization: Bearer acto_abc123..." \
  -H "X-Wallet-Address: 5K8vK..."
```

### Python SDK

```python
from acto.client import ACTOClient

client = ACTOClient(api_key="...", wallet_address="...")

# List recent proofs
response = client.list_proofs(limit=10)

for proof in response.items:
    print(f"- {proof.proof_id}: {proof.task_id}")
```

### JavaScript

```javascript
const response = await fetch('https://api.actobotics.net/v1/proofs?limit=10', {
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'X-Wallet-Address': WALLET_ADDRESS
  }
});

const { items } = await response.json();
```

## Notes

- Results are sorted by `created_at` descending (newest first)
- For advanced filtering, use [Search Proofs](/api/proofs/search)
- Maximum limit is 100

