# Device Groups

Organize devices into groups.

## List Groups

<div class="endpoint-card">
  <span class="method-badge get">GET</span>
  <span class="path">/v1/fleet/groups</span>
</div>

### Response

```json
{
  "groups": [
    {
      "id": "grp_abc123",
      "name": "Warehouse A",
      "description": "Main warehouse robots",
      "device_count": 5,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 3
}
```

## Create Group

<div class="endpoint-card">
  <span class="method-badge post">POST</span>
  <span class="path">/v1/fleet/groups</span>
</div>

### Request

```json
{
  "name": "Production Line 1",
  "description": "Assembly line robots"
}
```

### Response

```json
{
  "success": true,
  "group": {
    "id": "grp_xyz789",
    "name": "Production Line 1",
    "description": "Assembly line robots"
  }
}
```

## Assign Devices

<div class="endpoint-card">
  <span class="method-badge post">POST</span>
  <span class="path">/v1/fleet/groups/{group_id}/assign</span>
</div>

### Request

```json
{
  "device_ids": ["robot-alpha-01", "robot-alpha-02"]
}
```

## Unassign Devices

<div class="endpoint-card">
  <span class="method-badge post">POST</span>
  <span class="path">/v1/fleet/groups/{group_id}/unassign</span>
</div>

## Delete Group

<div class="endpoint-card">
  <span class="method-badge delete">DELETE</span>
  <span class="path">/v1/fleet/groups/{group_id}</span>
</div>

### Response

```json
{
  "success": true,
  "group_id": "grp_abc123",
  "devices_unassigned": 5
}
```

## Examples

### Python SDK

```python
# Create group
result = client.fleet.create_group(
    name="Warehouse A",
    description="Main warehouse robots"
)

# Assign devices
client.fleet.assign_devices(
    result.group.id,
    ["robot-001", "robot-002"]
)

# List groups
groups = client.fleet.list_groups()
for group in groups.groups:
    print(f"{group.name}: {group.device_count} devices")
```

