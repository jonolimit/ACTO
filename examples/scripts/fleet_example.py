"""
Fleet Management API Example

This script demonstrates how to use the Fleet Management API to:
- Get fleet overview
- Rename devices
- Create and manage device groups
- Report device health metrics

Prerequisites:
- A running ACTO server (local or api.actobotics.net)
- A valid JWT token from wallet authentication

Usage:
    python fleet_example.py
"""

from __future__ import annotations

import httpx


# Configuration
BASE_URL = "http://127.0.0.1:8080"  # Use "https://api.actobotics.net" for production
JWT_TOKEN = "your-jwt-token-here"  # Get this from wallet authentication

# Headers for authenticated requests
HEADERS = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json",
}


def get_fleet_overview() -> dict:
    """Get overview of all devices and groups."""
    response = httpx.get(f"{BASE_URL}/v1/fleet", headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def get_device_details(device_id: str) -> dict:
    """Get detailed info for a specific device."""
    response = httpx.get(
        f"{BASE_URL}/v1/fleet/devices/{device_id}",
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def rename_device(device_id: str, new_name: str) -> dict:
    """Rename a device with a custom name."""
    response = httpx.patch(
        f"{BASE_URL}/v1/fleet/devices/{device_id}/name",
        headers=HEADERS,
        json={"name": new_name},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def report_device_health(
    device_id: str,
    cpu_percent: float | None = None,
    memory_percent: float | None = None,
    battery_percent: float | None = None,
    battery_charging: bool | None = None,
    disk_percent: float | None = None,
    temperature: float | None = None,
    uptime_seconds: int | None = None,
    network_connected: bool | None = None,
    custom_metrics: dict | None = None,
) -> dict:
    """
    Report health metrics for a device.
    All parameters are optional - only send what your device supports.
    """
    # Build payload with only non-None values
    payload = {}
    if cpu_percent is not None:
        payload["cpu_percent"] = cpu_percent
    if memory_percent is not None:
        payload["memory_percent"] = memory_percent
    if battery_percent is not None:
        payload["battery_percent"] = battery_percent
    if battery_charging is not None:
        payload["battery_charging"] = battery_charging
    if disk_percent is not None:
        payload["disk_percent"] = disk_percent
    if temperature is not None:
        payload["temperature"] = temperature
    if uptime_seconds is not None:
        payload["uptime_seconds"] = uptime_seconds
    if network_connected is not None:
        payload["network_connected"] = network_connected
    if custom_metrics is not None:
        payload["custom_metrics"] = custom_metrics

    response = httpx.post(
        f"{BASE_URL}/v1/fleet/devices/{device_id}/health",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def create_group(name: str, description: str | None = None) -> dict:
    """Create a new device group."""
    payload = {"name": name}
    if description:
        payload["description"] = description

    response = httpx.post(
        f"{BASE_URL}/v1/fleet/groups",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def list_groups() -> dict:
    """List all device groups."""
    response = httpx.get(f"{BASE_URL}/v1/fleet/groups", headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def assign_devices_to_group(group_id: str, device_ids: list[str]) -> dict:
    """Assign devices to a group."""
    response = httpx.post(
        f"{BASE_URL}/v1/fleet/groups/{group_id}/assign",
        headers=HEADERS,
        json={"device_ids": device_ids},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def delete_group(group_id: str) -> dict:
    """Delete a device group."""
    response = httpx.delete(
        f"{BASE_URL}/v1/fleet/groups/{group_id}",
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main() -> int:
    """Example usage of Fleet Management API."""
    
    print("=" * 60)
    print("Fleet Management API Example")
    print("=" * 60)
    
    try:
        # 1. Get fleet overview
        print("\n1. Getting fleet overview...")
        fleet = get_fleet_overview()
        print(f"   Total devices: {fleet['summary']['total_devices']}")
        print(f"   Active devices: {fleet['summary']['active_devices']}")
        print(f"   Total groups: {fleet['summary']['total_groups']}")
        
        if fleet["devices"]:
            device = fleet["devices"][0]
            device_id = device["id"]
            print(f"\n   First device: {device['name']} ({device_id})")
            
            # 2. Get device details
            print(f"\n2. Getting details for {device_id}...")
            details = get_device_details(device_id)
            print(f"   Proof count: {details['proof_count']}")
            print(f"   Task count: {details['task_count']}")
            print(f"   Status: {details['status']}")
            
            # 3. Rename device
            print(f"\n3. Renaming device...")
            result = rename_device(device_id, "My Robot Alpha")
            print(f"   New name: {result['name']}")
            
            # 4. Report health (example - all fields optional)
            print(f"\n4. Reporting health metrics...")
            health = report_device_health(
                device_id,
                cpu_percent=45.2,
                memory_percent=68.0,
                battery_percent=85.0,
                battery_charging=True,
                temperature=42.5,
                uptime_seconds=86400,
                network_connected=True,
            )
            print(f"   Health recorded: {health['success']}")
        
        # 5. Create a group
        print("\n5. Creating device group...")
        group = create_group("Warehouse A", "Main warehouse robots")
        group_id = group["group"]["id"]
        print(f"   Created group: {group['group']['name']} ({group_id})")
        
        # 6. List all groups
        print("\n6. Listing all groups...")
        groups = list_groups()
        for g in groups["groups"]:
            print(f"   - {g['name']} ({g.get('device_count', 0)} devices)")
        
        # 7. Assign device to group (if we have a device)
        if fleet["devices"]:
            print(f"\n7. Assigning device to group...")
            result = assign_devices_to_group(group_id, [device_id])
            print(f"   Assigned: {result['assigned']}")
        
        # 8. Delete the group (cleanup)
        print(f"\n8. Deleting group...")
        result = delete_group(group_id)
        print(f"   Deleted: {result['success']}")
        
        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)
        return 0
        
    except httpx.HTTPStatusError as e:
        print(f"\nHTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        if e.response.status_code == 401:
            print("\nTip: Make sure you have a valid JWT token from wallet authentication.")
        return 1
    except httpx.ConnectError:
        print(f"\nConnection Error: Could not connect to {BASE_URL}")
        print("Tip: Make sure the ACTO server is running.")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

