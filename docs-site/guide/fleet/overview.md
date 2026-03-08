# Fleet Management Overview

Monitor and manage your robot fleet with ACTO's fleet management features.

## Features

- **Device Overview** - See all devices with status and activity
- **Health Monitoring** - Track CPU, memory, battery, and custom metrics
- **Device Groups** - Organize robots by location or function
- **Drag-and-Drop** - Assign devices to groups and reorder with drag-and-drop
- **Device Deletion** - Remove devices from fleet (soft delete preserves history)
- **Activity Logs** - Complete proof history per device
- **Custom Names** - Rename devices for easy identification

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        Your Robots                              │
├────────────────────────────────────────────────────────────────┤
│  Robot A      Robot B      Robot C      Robot D                │
│  (Warehouse)  (Warehouse)  (Assembly)   (Inspection)           │
└──────┬──────────┬──────────┬──────────────┬────────────────────┘
       │          │          │              │
       │  Submit Proofs + Health Reports    │
       ▼          ▼          ▼              ▼
┌────────────────────────────────────────────────────────────────┐
│                       ACTO API                                  │
│                                                                 │
│   • Automatic device discovery from proofs                      │
│   • Health metrics storage (30 days)                           │
│   • Device grouping and organization                           │
└────────────────────────────────────────────────────────────────┘
       │
       │  Dashboard / SDK
       ▼
┌────────────────────────────────────────────────────────────────┐
│                    Fleet Dashboard                              │
│                                                                 │
│   📊 Overview    🤖 Devices    📁 Groups    📈 Analytics       │
└────────────────────────────────────────────────────────────────┘
```

## Automatic Device Discovery

Devices are automatically discovered when they submit proofs:

```python
bundle = TelemetryBundle(
    task_id="inspection-001",
    robot_id="robot-warehouse-01",  # ← This creates/updates the device
    events=[...]
)
```

No separate registration required - just include `robot_id` in your proofs.

## Device Status

| Status | Condition |
|--------|-----------|
| 🟢 **Active** | Activity within last hour |
| 🟡 **Idle** | Activity within last 24 hours |
| 🔴 **Inactive** | No activity in 24+ hours |
| ⚪ **Unknown** | No activity recorded |

## Dashboard Access

Access fleet management via the web dashboard:

1. Go to [https://acto-production.up.railway.app/dashboard](https://https://acto-production.up.railway.app/dashboard)
2. Connect your wallet
3. Click the **Fleet** tab

## SDK Access

Use the Python SDK for programmatic fleet management:

```python
from acto.client import ACTOClient

client = ACTOClient(api_key="...", wallet_address="...")

# Get fleet overview
fleet = client.fleet.get_overview()

print(f"Total devices: {fleet.summary.total_devices}")
print(f"Active: {fleet.summary.active_devices}")

# List devices
for device in fleet.devices:
    print(f"- {device.id}: {device.status}")
```

## Use Cases

### Production Monitoring

Track robot fleet health in real-time:
- CPU/memory usage alerts
- Battery level monitoring
- Uptime tracking

### Compliance

Maintain audit trails:
- Complete proof history per device
- Activity timestamps
- Operator metadata

### Operations

Organize and manage fleet:
- Group by location
- Custom naming
- Task distribution tracking

## Next Steps

- [Device Monitoring](/guide/fleet/devices) - Monitor individual devices
- [Device Groups](/guide/fleet/groups) - Organize your fleet
- [Health Reporting](/guide/fleet/health) - Report device metrics

