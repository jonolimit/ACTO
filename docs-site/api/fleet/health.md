# Health Reporting

Report and retrieve device health metrics.

## Report Health

<div class="endpoint-card">
  <span class="method-badge post">POST</span>
  <span class="path">/v1/fleet/devices/{device_id}/health</span>
</div>

### Request

All fields are optional - only send metrics your device supports.

```json
{
  "cpu_percent": 45.2,
  "cpu_temperature": 52.0,
  "memory_percent": 68.0,
  "memory_used_mb": 2048,
  "memory_total_mb": 4096,
  "battery_percent": 85.0,
  "battery_charging": true,
  "disk_percent": 42.0,
  "network_connected": true,
  "network_type": "wifi",
  "uptime_seconds": 86400,
  "temperature": 42.5,
  "custom_metrics": {
    "motor_temp": 38.0,
    "sensor_status": "ok"
  }
}
```

### Response

```json
{
  "success": true,
  "device_id": "robot-alpha-01",
  "health": {...}
}
```

## Get Health

<div class="endpoint-card">
  <span class="method-badge get">GET</span>
  <span class="path">/v1/fleet/devices/{device_id}/health</span>
</div>

### Response

```json
{
  "device_id": "robot-alpha-01",
  "health": {
    "cpu_percent": 45.2,
    "memory_percent": 68.0,
    "battery_percent": 85.0,
    "last_updated": "2025-01-15T10:30:00Z"
  },
  "available": true
}
```

## Examples

### Python SDK

```python
# Report health
client.fleet.report_health(
    "robot-001",
    cpu_percent=45.2,
    memory_percent=68.0,
    battery_percent=85.0
)

# Get health
health = client.fleet.get_health("robot-001")
print(f"CPU: {health.cpu_percent}%")
```

