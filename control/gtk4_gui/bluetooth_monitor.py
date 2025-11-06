#!/usr/bin/env python3
"""
@llm-doc Bluetooth Information Collection for GTK4 UI
@llm-version 1.0.0
@llm-date 2025-10-28

Cross-platform Bluetooth monitoring using D-Bus and bluetoothctl for device discovery,
pairing management, connection tracking, and adapter control capabilities.
"""

import logging
import subprocess
import time
from dataclasses import dataclass
from typing import Any

# Import D-Bus for BlueZ communication
try:
    import dbus
    import dbus.mainloop.glib
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False

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
            0x09: "health"
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
        self.cache_duration = 2.0  # Cache for 2 seconds
        self._device_cache = {}
        self._adapter_cache = {}
        self._last_update = 0

        # Performance tracking
        self._collection_count = 0
        self._error_count = 0

        # D-Bus setup
        self._bus = None
        self._setup_dbus()

    def _setup_dbus(self):
        """Setup D-Bus connection for BlueZ communication"""
        if not DBUS_AVAILABLE:
            logger.warning("D-Bus not available - falling back to bluetoothctl")
            return

        try:
            # Set a timeout for D-Bus operations to prevent freezing
            self._bus = dbus.SystemBus(timeout=5000)  # 5 second timeout
            logger.debug("D-Bus system bus connected with 5s timeout")
        except Exception as e:
            logger.warning(f"Failed to connect to D-Bus: {e}")
            self._bus = None

    def get_adapters(self) -> list[BluetoothAdapter]:
        """Get list of Bluetooth adapters."""
        try:
            if self._bus:
                return self._get_adapters_dbus()
            else:
                return self._get_adapters_bluetoothctl()
        except Exception as e:
            logger.error(f"Failed to get adapters: {e}")
            self._error_count += 1
            return []

    def get_devices(self, include_unpaired: bool = True) -> list[BluetoothDevice]:
        """
        Get list of Bluetooth devices.

        Args:
            include_unpaired: Whether to include unpaired devices from discovery

        Returns:
            List of BluetoothDevice objects
        """
        try:
            if self._bus:
                devices = self._get_devices_dbus()
            else:
                devices = self._get_devices_bluetoothctl()

            # If include_unpaired is True, also get discovered devices
            if include_unpaired:
                discovered_devices = self._get_discovered_devices()
                # Merge discovered devices, avoiding duplicates
                existing_addresses = {d.address for d in devices}
                for discovered in discovered_devices:
                    if discovered.address not in existing_addresses:
                        devices.append(discovered)

            # Filter unpaired devices if requested
            if not include_unpaired:
                devices = [d for d in devices if d.paired]

            self._collection_count += 1
            return devices

        except Exception as e:
            logger.error(f"Failed to get devices: {e}")
            self._error_count += 1
            return []

    def _get_adapters_dbus(self) -> list[BluetoothAdapter]:
        """Get adapters using D-Bus"""
        adapters = []

        try:
            # Use bluetoothctl fallback if D-Bus is slow
            return self._get_adapters_bluetoothctl()
        except Exception as e:
            logger.error(f"D-Bus adapter enumeration failed: {e}")

        return adapters

    def _get_adapters_bluetoothctl(self) -> list[BluetoothAdapter]:
        """Get adapters using bluetoothctl fallback"""
        adapters = []

        try:
            result = subprocess.run(
                ['bluetoothctl', 'show'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                adapter_data = self._parse_bluetoothctl_show(result.stdout)
                if adapter_data:
                    adapters.append(adapter_data)

        except subprocess.TimeoutExpired:
            logger.warning("bluetoothctl show timeout")
        except Exception as e:
            logger.error(f"bluetoothctl show failed: {e}")

        return adapters

    def _get_devices_dbus(self) -> list[BluetoothDevice]:
        """Get devices using D-Bus"""
        devices = []

        try:
            # Use bluetoothctl fallback to avoid D-Bus timeout issues
            return self._get_devices_bluetoothctl()
        except Exception as e:
            logger.error(f"D-Bus device enumeration failed: {e}")

        return devices

    def _get_devices_bluetoothctl(self) -> list[BluetoothDevice]:
        """Get devices using bluetoothctl fallback"""
        devices = []

        try:
            result = subprocess.run(
                ['bluetoothctl', 'devices'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line.startswith('Device '):
                        device = self._parse_bluetoothctl_device(line)
                        if device:
                            devices.append(device)

        except subprocess.TimeoutExpired:
            logger.warning("bluetoothctl devices timeout")
        except Exception as e:
            logger.error(f"bluetoothctl devices failed: {e}")

        return devices

    def _parse_bluetoothctl_show(self, output: str) -> BluetoothAdapter | None:
        """Parse bluetoothctl show output"""
        lines = output.strip().split('\n')
        adapter_data = {}

        for line in lines:
            line = line.strip()
            if line.startswith('Controller '):
                adapter_data['address'] = line.split()[1]
            elif line.startswith('Name: '):
                adapter_data['name'] = line[6:]
            elif line.startswith('Alias: '):
                adapter_data['alias'] = line[7:]
            elif line.startswith('Powered: '):
                adapter_data['powered'] = line[9:] == 'yes'
            elif line.startswith('Discoverable: '):
                adapter_data['discoverable'] = line[14:] == 'yes'
            elif line.startswith('Pairable: '):
                adapter_data['pairable'] = line[10:] == 'yes'
            elif line.startswith('Discovering: '):
                adapter_data['discovering'] = line[13:] == 'yes'

        if 'address' in adapter_data:
            return BluetoothAdapter(
                address=adapter_data.get('address', ''),
                name=adapter_data.get('name', ''),
                alias=adapter_data.get('alias', ''),
                powered=adapter_data.get('powered', False),
                discoverable=adapter_data.get('discoverable', False),
                pairable=adapter_data.get('pairable', False),
                discovering=adapter_data.get('discovering', False),
                uuids=[],
                manufacturer=0,
                version=0
            )

        return None

    def _parse_bluetoothctl_device(self, line: str) -> BluetoothDevice | None:
        """Parse bluetoothctl device line"""
        parts = line.split(' ', 2)
        if len(parts) >= 3:
            address = parts[1]
            name = parts[2]

            return BluetoothDevice(
                address=address,
                name=name,
                alias=name,
                device_class=0,
                device_type="unknown",
                paired=False,  # Would need additional info command
                connected=False,
                trusted=False,
                blocked=False,
                rssi=None,
                uuids=[],
                adapter="",
                last_seen=time.time()
            )

        return None

    def _get_discovered_devices(self) -> list[BluetoothDevice]:
        """Get devices discovered through active scanning with multiple methods."""
        devices = []

        # Skip D-Bus discovery to avoid timeouts - use bluetoothctl only
        # Try hcitool with shorter timeout
        try:
            # Use hcitool scan with very short timeout
            result = subprocess.run(
                ['hcitool', 'scan', '--flush'],
                capture_output=True,
                text=True,
                timeout=3  # Very short timeout
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    line = line.strip()
                    if line and not line.startswith('Scanning'):
                        # Parse line format: "ADDRESS\tNAME"
                        parts = line.split('\t', 1)
                        if len(parts) >= 2:
                            address = parts[0].strip()
                            name = parts[1].strip()

                            # Create discovered device
                            device = BluetoothDevice(
                                address=address,
                                name=name,
                                alias=name,
                                device_class=0,
                                device_type="unknown",  # Will be classified
                                paired=False,  # Discovered devices are not paired
                                connected=False,
                                trusted=False,
                                blocked=False,
                                rssi=None,  # hcitool scan doesn't provide RSSI
                                uuids=[],
                                adapter="",
                                last_seen=time.time()
                            )

                            devices.append(device)

        except subprocess.TimeoutExpired:
            logger.debug("hcitool scan timeout (expected)")
        except FileNotFoundError:
            logger.debug("hcitool not available")
        except Exception as e:
            logger.debug(f"hcitool scan failed: {e}")

        return devices

    def _get_discovered_devices_dbus(self) -> list[BluetoothDevice]:
        """Get discovered devices using D-Bus (more reliable than hcitool)."""
        devices = []

        if not self._bus:
            return devices

        try:
            # Get all objects from BlueZ
            manager = dbus.Interface(
                self._bus.get_object("org.bluez", "/"),
                "org.freedesktop.DBus.ObjectManager"
            )

            objects = manager.GetManagedObjects()

            for path, interfaces in objects.items():
                if "org.bluez.Device1" in interfaces:
                    props = interfaces["org.bluez.Device1"]

                    # Only include devices that are not paired (discovered)
                    if not props.get("Paired", False):
                        device = BluetoothDevice(
                            address=str(props.get("Address", "")),
                            name=str(props.get("Name", "")),
                            alias=str(props.get("Alias", "")),
                            device_class=int(props.get("Class", 0)),
                            device_type="",  # Will be classified
                            paired=False,
                            connected=bool(props.get("Connected", False)),
                            trusted=bool(props.get("Trusted", False)),
                            blocked=bool(props.get("Blocked", False)),
                            rssi=props.get("RSSI"),
                            uuids=[str(uuid) for uuid in props.get("UUIDs", [])],
                            adapter=str(props.get("Adapter", "")),
                            last_seen=time.time()
                        )

                        devices.append(device)

        except Exception as e:
            logger.debug(f"D-Bus discovered devices enumeration failed: {e}")

        return devices

    def start_discovery(self) -> bool:
        """Start device discovery using multiple methods"""
        success = False

        # Try D-Bus method first
        if self._bus:
            try:
                # Get the first adapter
                adapters = self.get_adapters()
                if adapters:
                    adapter_path = "/org/bluez/hci0"  # Assume hci0 for now
                    adapter = dbus.Interface(
                        self._bus.get_object("org.bluez", adapter_path),
                        "org.bluez.Adapter1"
                    )
                    adapter.StartDiscovery()
                    success = True
                    logger.debug("Started discovery via D-Bus")
            except Exception as e:
                logger.debug(f"D-Bus discovery start failed: {e}")

        # Fallback to bluetoothctl
        if not success:
            try:
                result = subprocess.run(
                    ['bluetoothctl', 'scan', 'on'],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                success = result.returncode == 0
                if success:
                    logger.debug("Started discovery via bluetoothctl")
            except Exception as e:
                logger.debug(f"bluetoothctl discovery start failed: {e}")

        return success

    def stop_discovery(self) -> bool:
        """Stop device discovery using multiple methods"""
        success = False

        # Try D-Bus method first
        if self._bus:
            try:
                adapter_path = "/org/bluez/hci0"  # Assume hci0 for now
                adapter = dbus.Interface(
                    self._bus.get_object("org.bluez", adapter_path),
                    "org.bluez.Adapter1"
                )
                adapter.StopDiscovery()
                success = True
                logger.debug("Stopped discovery via D-Bus")
            except Exception as e:
                logger.debug(f"D-Bus discovery stop failed: {e}")

        # Fallback to bluetoothctl
        if not success:
            try:
                result = subprocess.run(
                    ['bluetoothctl', 'scan', 'off'],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                success = result.returncode == 0
                if success:
                    logger.debug("Stopped discovery via bluetoothctl")
            except Exception as e:
                logger.debug(f"bluetoothctl discovery stop failed: {e}")

        return success

    def _find_device_path(self, address: str) -> str | None:
        """Find the D-Bus path for a device by its address."""
        if not self._bus:
            return None

        try:
            manager = dbus.Interface(
                self._bus.get_object("org.bluez", "/"),
                "org.freedesktop.DBus.ObjectManager"
            )

            objects = manager.GetManagedObjects()

            for path, interfaces in objects.items():
                if "org.bluez.Device1" in interfaces:
                    props = interfaces["org.bluez.Device1"]
                    if str(props.get("Address", "")).upper() == address.upper():
                        return path

        except Exception as e:
            logger.error(f"Failed to find device path for {address}: {e}")

        return None

    def connect_device(self, address: str) -> bool:
        """
        Connect to a Bluetooth device.

        Args:
            address: Device MAC address (e.g., "AA:BB:CC:DD:EE:FF")

        Returns:
            True if connection was successful, False otherwise
        """
        if not self._bus:
            logger.warning("D-Bus not available - trying bluetoothctl fallback")
            return self._connect_device_bluetoothctl(address)

        try:
            device_path = self._find_device_path(address)
            if not device_path:
                logger.error(f"Device not found: {address}")
                return False

            device = dbus.Interface(
                self._bus.get_object("org.bluez", device_path),
                "org.bluez.Device1"
            )

            device.Connect()
            logger.info(f"Connected to device: {address}")
            return True

        except dbus.exceptions.DBusException as e:
            logger.error(f"D-Bus error connecting to {address}: {e}")
            # Try bluetoothctl fallback
            return self._connect_device_bluetoothctl(address)
        except Exception as e:
            logger.error(f"Failed to connect to device {address}: {e}")
            return False

    def disconnect_device(self, address: str) -> bool:
        """
        Disconnect from a Bluetooth device.

        Args:
            address: Device MAC address (e.g., "AA:BB:CC:DD:EE:FF")

        Returns:
            True if disconnection was successful, False otherwise
        """
        if not self._bus:
            logger.warning("D-Bus not available - trying bluetoothctl fallback")
            return self._disconnect_device_bluetoothctl(address)

        try:
            device_path = self._find_device_path(address)
            if not device_path:
                logger.error(f"Device not found: {address}")
                return False

            device = dbus.Interface(
                self._bus.get_object("org.bluez", device_path),
                "org.bluez.Device1"
            )

            device.Disconnect()
            logger.info(f"Disconnected from device: {address}")
            return True

        except dbus.exceptions.DBusException as e:
            logger.error(f"D-Bus error disconnecting from {address}: {e}")
            # Try bluetoothctl fallback
            return self._disconnect_device_bluetoothctl(address)
        except Exception as e:
            logger.error(f"Failed to disconnect from device {address}: {e}")
            return False

    def pair_device(self, address: str) -> bool:
        """
        Pair with a Bluetooth device.

        Args:
            address: Device MAC address (e.g., "AA:BB:CC:DD:EE:FF")

        Returns:
            True if pairing was successful, False otherwise
        """
        if not self._bus:
            logger.warning("D-Bus not available - trying bluetoothctl fallback")
            return self._pair_device_bluetoothctl(address)

        try:
            device_path = self._find_device_path(address)
            if not device_path:
                logger.error(f"Device not found: {address}")
                return False

            device = dbus.Interface(
                self._bus.get_object("org.bluez", device_path),
                "org.bluez.Device1"
            )

            device.Pair()
            logger.info(f"Paired with device: {address}")
            return True

        except dbus.exceptions.DBusException as e:
            logger.error(f"D-Bus error pairing with {address}: {e}")
            # Try bluetoothctl fallback
            return self._pair_device_bluetoothctl(address)
        except Exception as e:
            logger.error(f"Failed to pair with device {address}: {e}")
            return False

    def set_trusted(self, address: str, trusted: bool) -> bool:
        """
        Set the Trusted property of a device (enables auto-connect).

        Args:
            address: Device MAC address (e.g., "AA:BB:CC:DD:EE:FF")
            trusted: Whether to trust the device

        Returns:
            True if property was set successfully, False otherwise
        """
        if not self._bus:
            logger.warning("D-Bus not available - cannot set trusted property")
            return False

        try:
            device_path = self._find_device_path(address)
            if not device_path:
                logger.error(f"Device not found: {address}")
                return False

            device = dbus.Interface(
                self._bus.get_object("org.bluez", device_path),
                "org.freedesktop.DBus.Properties"
            )

            device.Set("org.bluez.Device1", "Trusted", dbus.Boolean(trusted))
            logger.info(f"Set Trusted={trusted} for device: {address}")
            return True

        except dbus.exceptions.DBusException as e:
            logger.error(f"D-Bus error setting Trusted property for {address}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to set Trusted property for device {address}: {e}")
            return False

    def _connect_device_bluetoothctl(self, address: str) -> bool:
        """Connect to device using bluetoothctl fallback."""
        try:
            result = subprocess.run(
                ['bluetoothctl', 'connect', address],
                capture_output=True,
                text=True,
                timeout=10
            )
            success = result.returncode == 0
            if success:
                logger.info(f"Connected to device via bluetoothctl: {address}")
            else:
                logger.error(f"bluetoothctl connect failed: {result.stderr}")
            return success
        except subprocess.TimeoutExpired:
            logger.error("bluetoothctl connect timeout")
            return False
        except Exception as e:
            logger.error(f"bluetoothctl connect failed: {e}")
            return False

    def _disconnect_device_bluetoothctl(self, address: str) -> bool:
        """Disconnect from device using bluetoothctl fallback."""
        try:
            result = subprocess.run(
                ['bluetoothctl', 'disconnect', address],
                capture_output=True,
                text=True,
                timeout=10
            )
            success = result.returncode == 0
            if success:
                logger.info(f"Disconnected from device via bluetoothctl: {address}")
            else:
                logger.error(f"bluetoothctl disconnect failed: {result.stderr}")
            return success
        except subprocess.TimeoutExpired:
            logger.error("bluetoothctl disconnect timeout")
            return False
        except Exception as e:
            logger.error(f"bluetoothctl disconnect failed: {e}")
            return False

    def _pair_device_bluetoothctl(self, address: str) -> bool:
        """Pair with device using bluetoothctl fallback."""
        try:
            result = subprocess.run(
                ['bluetoothctl', 'pair', address],
                capture_output=True,
                text=True,
                timeout=30
            )
            success = result.returncode == 0
            if success:
                logger.info(f"Paired with device via bluetoothctl: {address}")
            else:
                logger.error(f"bluetoothctl pair failed: {result.stderr}")
            return success
        except subprocess.TimeoutExpired:
            logger.error("bluetoothctl pair timeout")
            return False
        except Exception as e:
            logger.error(f"bluetoothctl pair failed: {e}")
            return False

    def get_statistics(self) -> dict[str, Any]:
        """Get monitoring statistics."""
        return {
            'dbus_available': DBUS_AVAILABLE,
            'collection_count': self._collection_count,
            'error_count': self._error_count,
            'error_rate': self._error_count / max(self._collection_count, 1),
            'cache_duration': self.cache_duration
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
