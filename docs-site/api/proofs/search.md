# Search Proofs

Search and filter proofs with pagination.

## Endpoint

<div class="endpoint-card">
  <span class="method-badge post">POST</span>
  <span class="path">/v1/proofs/search</span>
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
  "task_id": "pick-and-place",
  "robot_id": "robot-alpha",
  "run_id": "run-001",
  "signer_public_key": "base64_public_key",
  "created_after": "2025-01-01T00:00:00Z",
  "created_before": "2025-12-31T23:59:59Z",
  "search_text": "warehouse",
  "limit": 50,
  "offset": 0,
  "sort_field": "created_at",
  "sort_order": "desc"
}
```

### Schema

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `task_id` | `string` | No | - | Filter by task ID (partial match) |
| `robot_id` | `string` | No | - | Filter by robot ID (partial match) |
| `run_id` | `string` | No | - | Filter by run ID (partial match) |
| `signer_public_key` | `string` | No | - | Filter by signer public key |
| `created_after` | `string` | No | - | ISO 8601 start date |
| `created_before` | `string` | No | - | ISO 8601 end date |
| `search_text` | `string` | No | - | Full-text search |
| `limit` | `integer` | No | 50 | Results per page (max 100) |
| `offset` | `integer` | No | 0 | Pagination offset |
| `sort_field` | `string` | No | `created_at` | Field to sort by |
| `sort_order` | `string` | No | `desc` | `asc` or `desc` |

## Response

### Success (200 OK)

```json
{
  "items": [
    {
      "proof_id": "abc123...",
      "task_id": "pick-and-place-001",
      "robot_id": "robot-alpha-01",
      "run_id": "run-2025-01-15",
      "created_at": "2025-01-15T10:30:00Z",
      "signer_public_key": "..."
    },
    {
      "proof_id": "def456...",
      "task_id": "pick-and-place-002",
      "robot_id": "robot-alpha-01",
      "run_id": "run-2025-01-16",
      "created_at": "2025-01-16T10:30:00Z",
      "signer_public_key": "..."
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `items` | `array` | Matching proofs |
| `total` | `number` | Total matching results |
| `limit` | `number` | Results per page |
| `offset` | `number` | Current offset |
| `has_more` | `boolean` | More results available |

## Examples

### cURL

```bash
curl -X POST https://api.actobotics.net/v1/proofs/search \
  -H "Authorization: Bearer acto_abc123..." \
  -H "X-Wallet-Address: 5K8vK..." \
  -H "Content-Type: application/json" \
  -d '{
    "robot_id": "robot-alpha-01",
    "created_after": "2025-01-01T00:00:00Z",
    "limit": 10
  }'
```

### Python SDK

```python
from acto.client import ACTOClient

client = ACTOClient(api_key="...", wallet_address="...")

# Search with filters
results = client.search_proofs(
    robot_id="robot-alpha-01",
    created_after="2025-01-01T00:00:00Z",
    created_before="2025-12-31T23:59:59Z",
    limit=50
)

print(f"Found {results.total} proofs")
for proof in results.items:
    print(f"- {proof.task_id} ({proof.created_at})")

# Pagination
if results.has_more:
    more_results = client.search_proofs(
        robot_id="robot-alpha-01",
        offset=50
    )
```

### JavaScript

```javascript
const response = await fetch('https://api.actobotics.net/v1/proofs/search', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'X-Wallet-Address': WALLET_ADDRESS,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    robot_id: 'robot-alpha-01',
    limit: 50
  })
});

const { items, total, has_more } = await response.json();
```

## Search Examples

### By Robot

```python
results = client.search_proofs(robot_id="robot-alpha-01")
```

### By Task

```python
results = client.search_proofs(task_id="quality-inspection")
```

### Date Range

```python
results = client.search_proofs(
    created_after="2025-01-01T00:00:00Z",
    created_before="2025-01-31T23:59:59Z"
)
```

### Full-Text Search

```python
results = client.search_proofs(search_text="warehouse assembly")
```

### Combined Filters

```python
results = client.search_proofs(
    robot_id="robot-alpha",
    task_id="pick-and-place",
    created_after="2025-01-01T00:00:00Z",
    sort_field="created_at",
    sort_order="desc",
    limit=100
)
```

## Pagination

```python
def get_all_proofs(client, **filters):
    """Fetch all matching proofs with pagination."""
    all_proofs = []
    offset = 0
    
    while True:
        results = client.search_proofs(**filters, offset=offset, limit=100)
        all_proofs.extend(results.items)
        
        if not results.has_more:
            break
        
        offset += 100
    
    return all_proofs

# Usage
proofs = get_all_proofs(client, robot_id="robot-alpha-01")
```

