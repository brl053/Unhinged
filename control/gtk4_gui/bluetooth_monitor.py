#!/usr/bin/env python3
"""
@llm-doc Bluetooth Information Collection for GTK4 UI
@llm-version 1.0.0
@llm-date 2025-11-15

Cross-platform Bluetooth monitoring using D-Bus and bluetoothctl for device discovery,
pairing management, connection tracking, and adapter control capabilities.
"""

import logging
from dataclasses import dataclass
from typing import Any

# Import D-Bus for BlueZ communication
try:
    import dbus
    import dbus.mainloop.glib

    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False

# Import specialized managers
from .bluetooth_adapter import AdapterManager
from .bluetooth_device_enum import DeviceEnumerator
from .bluetooth_device_ops import DeviceOperations
from .bluetooth_discovery import DiscoveryManager

logger = logging.getLogger(__name__)


@dataclass
class BluetoothDevice:
    """Bluetooth device information data structure"""

    address: str
    name: str
    alias: str
    device_class: int
    device_type: str
    paired: bool
    connected: bool
    trusted: bool
    blocked: bool
    rssi: int | None
    uuids: list[str]
    adapter: str
    last_seen: float

    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure name is not empty
        if not self.name:
            self.name = self.alias or "Unknown Device"

        # Determine device type from class if not set
        if not self.device_type:
            self.device_type = self._classify_device()

    def _classify_device(self) -> str:
        """Classify device type based on device class and UUIDs"""
        if not self.device_class:
            return "unknown"

        # Major device class (bits 8-12)
        major_class = (self.device_class >> 8) & 0x1F

        device_types = {
            0x01: "computer",
            0x02: "phone",
            0x03: "network",
            0x04: "audio",
            0x05: "peripheral",
            0x06: "imaging",
            0x07: "wearable",
            0x08: "toy",
            0x09: "health",
        }

        return device_types.get(major_class, "unknown")


@dataclass
class BluetoothAdapter:
    """Bluetooth adapter information data structure"""

    address: str
    name: str
    alias: str
    powered: bool
    discoverable: bool
    pairable: bool
    discovering: bool
    uuids: list[str]
    manufacturer: int
    version: int

    def __post_init__(self):
        """Post-initialization processing"""
        if not self.name:
            self.name = self.alias or "Unknown Adapter"


class BluetoothMonitor:
    """
    Bluetooth information collection using D-Bus and bluetoothctl.

    Features:
    - Cross-platform Bluetooth device enumeration
    - Device pairing and connection management
    - Adapter control and configuration
    - Real-time device discovery
    - Error handling for permission issues
    """

    def __init__(self):
        self.cache_duration = 2.0
        self._device_cache = {}
        self._adapter_cache = {}
        self._last_update = 0

        # Performance tracking
        self._collection_count = 0
        self._error_count = 0

        # D-Bus setup
        self._bus = None
        self._setup_dbus()

        # Initialize managers
        self._adapter_manager = AdapterManager(self._bus)
        self._device_enumerator = DeviceEnumerator(self._bus)
        self._device_ops = DeviceOperations(self._bus)
        self._discovery_manager = DiscoveryManager(self._bus)

    def _setup_dbus(self):
        """Setup D-Bus connection for BlueZ communication"""
        if not DBUS_AVAILABLE:
            logger.warning("D-Bus not available - falling back to bluetoothctl")
            return

        try:
            self._bus = dbus.SystemBus(timeout=5000)
            logger.debug("D-Bus system bus connected with 5s timeout")
        except Exception as e:
            logger.warning(f"Failed to connect to D-Bus: {e}")
            self._bus = None

    def get_adapters(self) -> list[BluetoothAdapter]:
        """Delegate to AdapterManager."""
        try:
            if self._bus:
                return self._adapter_manager.get_adapters_dbus(BluetoothAdapter)
            else:
                return self._adapter_manager.get_adapters_bluetoothctl(BluetoothAdapter)
        except Exception as e:
            logger.error(f"Failed to get adapters: {e}")
            self._error_count += 1
            return []

    def get_devices(self, include_unpaired: bool = True) -> list[BluetoothDevice]:
        """Delegate to DeviceEnumerator."""
        try:
            devices = (
                self._device_enumerator.get_devices_dbus(BluetoothDevice)
                if self._bus
                else self._device_enumerator.get_devices_bluetoothctl(BluetoothDevice)
            )

            if include_unpaired:
                discovered_devices = self._discovery_manager.get_discovered_devices(
                    self._bus, BluetoothDevice
                )
                existing_addresses = {d.address for d in devices}
                for discovered in discovered_devices:
                    if discovered.address not in existing_addresses:
                        devices.append(discovered)

            if not include_unpaired:
                devices = [d for d in devices if d.paired]

            self._collection_count += 1
            return devices

        except Exception as e:
            logger.error(f"Failed to get devices: {e}")
            self._error_count += 1
            return []

    def start_discovery(self) -> bool:
        """Delegate to DiscoveryManager."""
        return self._discovery_manager.start_discovery()

    def stop_discovery(self) -> bool:
        """Delegate to DiscoveryManager."""
        return self._discovery_manager.stop_discovery()

    def connect_device(self, address: str) -> bool:
        """Delegate to DeviceOperations."""
        return self._device_ops.connect_device(address)

    def disconnect_device(self, address: str) -> bool:
        """Delegate to DeviceOperations."""
        return self._device_ops.disconnect_device(address)

    def pair_device(self, address: str) -> bool:
        """Delegate to DeviceOperations."""
        return self._device_ops.pair_device(address)

    def set_trusted(self, address: str, trusted: bool) -> bool:
        """Delegate to DeviceOperations."""
        return self._device_ops.set_trusted(address, trusted)

    def get_statistics(self) -> dict[str, Any]:
        """Get monitoring statistics."""
        return {
            "dbus_available": DBUS_AVAILABLE,
            "collection_count": self._collection_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._collection_count, 1),
            "cache_duration": self.cache_duration,
        }


# Convenience functions for easy access
def get_bluetooth_adapters() -> list[BluetoothAdapter]:
    """Get list of Bluetooth adapters."""
    monitor = BluetoothMonitor()
    return monitor.get_adapters()


def get_bluetooth_devices(include_unpaired: bool = True) -> list[BluetoothDevice]:
    """Get list of Bluetooth devices."""
    monitor = BluetoothMonitor()
    return monitor.get_devices(include_unpaired)


def start_bluetooth_discovery() -> bool:
    """Start Bluetooth device discovery."""
    monitor = BluetoothMonitor()
    return monitor.start_discovery()


def stop_bluetooth_discovery() -> bool:
    """Stop Bluetooth device discovery."""
    monitor = BluetoothMonitor()
    return monitor.stop_discovery()


if __name__ == "__main__":
    # Test the Bluetooth monitor
    print("🔵 Testing Bluetooth Monitor")
    print("=" * 40)

    monitor = BluetoothMonitor()

    # Test adapter list
    print("📡 Getting Bluetooth adapters...")
    adapters = monitor.get_adapters()
    print(f"✅ Found {len(adapters)} adapter(s)")

    for adapter in adapters:
        print(f"  📡 {adapter.name} ({adapter.address})")
        print(f"     Powered: {adapter.powered}, Discoverable: {adapter.discoverable}")

    # Test device list
    print("\n🔵 Getting Bluetooth devices...")
    devices = monitor.get_devices()
    print(f"✅ Found {len(devices)} device(s)")

    for device in devices:
        status = "Connected" if device.connected else "Paired" if device.paired else "Discovered"
        print(f"  🔵 {device.name} ({device.address})")
        print(f"     Type: {device.device_type}, Status: {status}")

    # Test statistics
    stats = monitor.get_statistics()
    print("\n📊 Statistics:")
    print(f"  D-Bus Available: {stats['dbus_available']}")
    print(f"  Collections: {stats['collection_count']}")
    print(f"  Errors: {stats['error_count']}")

    print("✅ Bluetooth monitor test completed")
