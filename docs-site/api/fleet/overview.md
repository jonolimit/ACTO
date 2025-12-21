# Fleet Overview

Get a complete overview of your robot fleet.

## Endpoint

<div class="endpoint-card">
  <span class="method-badge get">GET</span>
  <span class="path">/v1/fleet</span>
</div>

## Authentication

Requires JWT authentication (wallet login).

## Response

```json
{
  "devices": [
    {
      "id": "robot-alpha-01",
      "name": "Robot Alpha",
      "custom_name": "Warehouse Bot 1",
      "group_id": "grp_abc123",
      "group_name": "Warehouse A",
      "proof_count": 42,
      "task_count": 15,
      "last_activity": "2025-01-15T10:30:00Z",
      "status": "active",
      "health": {
        "cpu_percent": 45.2,
        "memory_percent": 68.0,
        "battery_percent": 85.0
      }
    }
  ],
  "groups": [
    {
      "id": "grp_abc123",
      "name": "Warehouse A",
      "description": "Main warehouse robots",
      "device_count": 5
    }
  ],
  "summary": {
    "total_devices": 10,
    "active_devices": 7,
    "warning_devices": 2,
    "offline_devices": 1,
    "total_proofs": 1250,
    "total_tasks": 89,
    "total_groups": 3
  }
}
```

## Examples

### cURL

```bash
curl https://api.actobotics.net/v1/fleet \
  -H "Authorization: Bearer JWT_TOKEN"
```

### Python SDK

```python
from acto.client import ACTOClient

client = ACTOClient(api_key="...", wallet_address="...")

fleet = client.fleet.get_overview()

print(f"Total devices: {fleet.summary.total_devices}")
print(f"Active: {fleet.summary.active_devices}")

for device in fleet.devices:
    print(f"- {device.id}: {device.status}")
```

## Device Status

| Status | Condition |
|--------|-----------|
| `active` | Activity within last hour |
| `idle` | Activity within last 24 hours |
| `inactive` | No activity in 24+ hours |

## Notes

- Devices are auto-discovered from proof submissions
- Health data shown only if recently reported
- Groups only show groups you've created

