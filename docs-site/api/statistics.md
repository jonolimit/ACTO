# Statistics

Get wallet statistics and analytics.

## Endpoint

<div class="endpoint-card">
  <span class="method-badge get">GET</span>
  <span class="path">/v1/stats/wallet/{wallet_address}</span>
</div>

## Request

### Headers

```http
Authorization: Bearer YOUR_API_KEY
X-Wallet-Address: YOUR_WALLET_ADDRESS
```

### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `wallet_address` | string | Wallet to get stats for |

## Response

```json
{
  "wallet_address": "5K8vK...",
  "total_proofs_submitted": 25,
  "total_verifications": 150,
  "successful_verifications": 145,
  "failed_verifications": 5,
  "verification_success_rate": 96.7,
  "average_reputation_score": 85.5,
  "first_activity": "2025-01-01T00:00:00Z",
  "last_activity": "2025-12-20T10:30:00Z",
  "proofs_by_robot": {
    "robot-alpha-01": 10,
    "robot-beta-02": 15
  },
  "proofs_by_task": {
    "pick-and-place": 12,
    "quality-inspection": 13
  },
  "activity_timeline": [
    {"date": "2025-12-01", "proof_count": 3},
    {"date": "2025-12-02", "proof_count": 5}
  ]
}
```

## Examples

### cURL

```bash
curl https://api.actobotics.net/v1/stats/wallet/5K8vK... \
  -H "Authorization: Bearer acto_abc123..." \
  -H "X-Wallet-Address: 5K8vK..."
```

### Python SDK

```python
from acto.client import ACTOClient

client = ACTOClient(api_key="...", wallet_address="...")

# Get your own stats
stats = client.get_wallet_stats()

print(f"Total proofs: {stats.total_proofs_submitted}")
print(f"Success rate: {stats.verification_success_rate}%")
print(f"Avg reputation: {stats.average_reputation_score}")

# Breakdown by robot
for robot, count in stats.proofs_by_robot.items():
    print(f"  {robot}: {count} proofs")
```

## Response Fields

| Field | Description |
|-------|-------------|
| `total_proofs_submitted` | Total proofs from this wallet |
| `total_verifications` | Total verification requests |
| `successful_verifications` | Verifications that passed |
| `failed_verifications` | Verifications that failed |
| `verification_success_rate` | Success percentage |
| `average_reputation_score` | Average proof quality score |
| `first_activity` | First proof submission |
| `last_activity` | Most recent activity |
| `proofs_by_robot` | Breakdown by robot_id |
| `proofs_by_task` | Breakdown by task_id |
| `activity_timeline` | Daily proof counts |

