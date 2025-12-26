# Device Details

Get detailed information about a specific device.

## Get Device

<div class="endpoint-card">
  <span class="method-badge get">GET</span>
  <span class="path">/v1/fleet/devices/{device_id}</span>
</div>

### Response

```json
{
  "id": "robot-alpha-01",
  "name": "Robot Alpha 01",
  "custom_name": "Warehouse Bot 1",
  "display_name": "Warehouse Bot 1",
  "group_id": "grp_abc123",
  "group_name": "Warehouse A",
  "proof_count": 42,
  "task_count": 15,
  "last_activity": "2025-01-15T10:30:00Z",
  "first_activity": "2024-06-01T08:00:00Z",
  "status": "active",
  "health": {...},
  "recent_logs": [
    {
      "timestamp": "2025-01-15T10:30:00Z",
      "level": "success",
      "message": "Proof submitted for task 'pick-and-place'",
      "proof_id": "abc123...",
      "task_id": "pick-and-place"
    }
  ],
  "task_history": ["pick-and-place", "quality-inspection", "transport"]
}
```

## Rename Device

<div class="endpoint-card">
  <span class="method-badge patch">PATCH</span>
  <span class="path">/v1/fleet/devices/{device_id}/name</span>
</div>

### Request

```json
{
  "name": "Warehouse Bot Alpha"
}
```

### Response

```json
{
  "success": true,
  "device_id": "robot-alpha-01",
  "name": "Warehouse Bot Alpha"
}
```

## Delete Device

<div class="endpoint-card">
  <span class="method-badge delete">DELETE</span>
  <span class="path">/v1/fleet/devices/{device_id}</span>
</div>

Soft-delete a device from the fleet. The device's proofs are preserved, but it won't appear in the fleet list.

### Response

```json
{
  "success": true,
  "device_id": "robot-alpha-01"
}
```

> **Note:** This is a soft delete. Historical proofs are preserved.

## Reorder Devices

<div class="endpoint-card">
  <span class="method-badge patch">PATCH</span>
  <span class="path">/v1/fleet/devices/order</span>
</div>

Update the sort order of multiple devices for custom ordering in the fleet list.

### Request

```json
{
  "device_orders": [
    { "device_id": "robot-alpha-01", "sort_order": 0 },
    { "device_id": "robot-beta-02", "sort_order": 1 }
  ]
}
```

### Response

```json
{
  "success": true,
  "updated": 2
}
```

> **Tip:** Use drag-and-drop in the dashboard for easy reordering.

## Examples

### Python SDK

```python
# Get device details
device = client.fleet.get_device("robot-alpha-01")
print(f"Status: {device.status}")
print(f"Proofs: {device.proof_count}")

# Rename device
client.fleet.rename_device("robot-alpha-01", "Warehouse Bot 1")
```

