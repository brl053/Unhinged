"""
@llm-doc Bluetooth Device Enumeration
@llm-version 1.0.0
@llm-date 2025-11-15

Device enumeration and parsing.
"""

import logging
import subprocess
import time

logger = logging.getLogger(__name__)


class DeviceEnumerator:
    """Manages Bluetooth device enumeration."""

    def __init__(self, bus):
        """Initialize device enumerator."""
        self._bus = bus

    def get_devices_dbus(self, bluetooth_device) -> list:
        """Get devices using D-Bus."""
        devices = []

        if not self._bus:
            return devices

        try:
            import dbus

            manager = dbus.Interface(
                self._bus.get_object("org.bluez", "/"),
                "org.freedesktop.DBus.ObjectManager",
            )

            objects = manager.GetManagedObjects()

            for _path, interfaces in objects.items():
                if "org.bluez.Device1" in interfaces:
                    props = interfaces["org.bluez.Device1"]

                    device = bluetooth_device(
                        address=str(props.get("Address", "")),
                        name=str(props.get("Name", "")),
                        alias=str(props.get("Alias", "")),
                        device_class=int(props.get("Class", 0)),
                        device_type=str(props.get("Icon", "")),
                        paired=bool(props.get("Paired", False)),
                        connected=bool(props.get("Connected", False)),
                        trusted=bool(props.get("Trusted", False)),
                        blocked=bool(props.get("Blocked", False)),
                        rssi=props.get("RSSI"),
                        uuids=[str(uuid) for uuid in props.get("UUIDs", [])],
                        adapter=str(props.get("Adapter", "")),
                        last_seen=time.time(),
                    )

                    devices.append(device)

        except Exception as e:
            logger.error(f"D-Bus device enumeration failed: {e}")

        return devices

    def get_devices_bluetoothctl(self, bluetooth_device) -> list:
        """Get devices using bluetoothctl fallback."""
        devices = []

        try:
            result = subprocess.run(
                ["bluetoothctl", "devices"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                logger.warning("bluetoothctl devices failed")
                return devices

            for line in result.stdout.split("\n"):
                line = line.strip()
                if not line or not line.startswith("Device"):
                    continue

                device = self._parse_bluetoothctl_device(line, bluetooth_device)
                if device:
                    devices.append(device)

        except Exception as e:
            logger.error(f"Failed to get devices via bluetoothctl: {e}")

        return devices

    @staticmethod
    def _parse_bluetoothctl_device(line: str, bluetooth_device):
        """Parse a device line from bluetoothctl output."""
        try:
            parts = line.split()
            if len(parts) < 3:
                return None

            address = parts[1]
            name = " ".join(parts[2:])

            return bluetooth_device(
                address=address,
                name=name,
                alias=name,
                device_class=0,
                device_type="",
                paired=False,
                connected=False,
                trusted=False,
                blocked=False,
                rssi=None,
                uuids=[],
                adapter="",
                last_seen=time.time(),
            )

        except Exception as e:
            logger.error(f"Failed to parse device line: {e}")
            return None

