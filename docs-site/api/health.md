# Health Check

Check API health status.

## Endpoint

<div class="endpoint-card">
  <span class="method-badge get">GET</span>
  <span class="path">/health</span>
</div>

## Authentication

**None required** - Public endpoint.

## Response

```json
{
  "ok": true,
  "service": "acto",
  "version": "0.9.5"
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | Service healthy |
| `service` | string | Service name |
| `version` | string | API version |

## Examples

### cURL

```bash
curl https://api.actobotics.net/health
```

### Python

```python
import httpx

response = httpx.get("https://api.actobotics.net/health")
data = response.json()

if data["ok"]:
    print(f"ACTO API v{data['version']} is healthy")
```

### Python SDK

```python
from acto.client import ACTOClient

client = ACTOClient(api_key="...", wallet_address="...")
health = client.health()

print(f"OK: {health.ok}")
print(f"Version: {health.version}")
```

## Monitoring

Use this endpoint for:
- Uptime monitoring
- Load balancer health checks
- CI/CD deployment verification

## Prometheus Metrics

For detailed metrics:

```bash
curl https://api.actobotics.net/metrics
```

Returns Prometheus-format metrics.

