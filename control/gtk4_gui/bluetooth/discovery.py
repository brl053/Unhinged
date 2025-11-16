"""
@llm-doc Bluetooth Device Discovery
@llm-version 1.0.0
@llm-date 2025-11-15

Device discovery and scanning operations.
"""

import logging
import subprocess
import time

logger = logging.getLogger(__name__)


class DiscoveryManager:
    """Manages Bluetooth device discovery operations."""

    def __init__(self, bus):
        """Initialize discovery manager."""
        self._bus = bus

    def start_discovery(self) -> bool:
        """Start device discovery using multiple methods."""
        success = False

        if self._bus:
            try:
                import dbus

                adapter_path = "/org/bluez/hci0"
                adapter = dbus.Interface(
                    self._bus.get_object("org.bluez", adapter_path),
                    "org.bluez.Adapter1",
                )
                adapter.StartDiscovery()
                success = True
                logger.debug("Started discovery via D-Bus")
            except Exception as e:
                logger.debug(f"D-Bus discovery start failed: {e}")

        if not success:
            try:
                result = subprocess.run(
                    ["bluetoothctl", "scan", "on"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                success = result.returncode == 0
                if success:
                    logger.debug("Started discovery via bluetoothctl")
            except Exception as e:
                logger.debug(f"bluetoothctl discovery start failed: {e}")

        return success

    def stop_discovery(self) -> bool:
        """Stop device discovery using multiple methods."""
        success = False

        if self._bus:
            try:
                import dbus

                adapter_path = "/org/bluez/hci0"
                adapter = dbus.Interface(
                    self._bus.get_object("org.bluez", adapter_path),
                    "org.bluez.Adapter1",
                )
                adapter.StopDiscovery()
                success = True
                logger.debug("Stopped discovery via D-Bus")
            except Exception as e:
                logger.debug(f"D-Bus discovery stop failed: {e}")

        if not success:
            try:
                result = subprocess.run(
                    ["bluetoothctl", "scan", "off"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                success = result.returncode == 0
                if success:
                    logger.debug("Stopped discovery via bluetoothctl")
            except Exception as e:
                logger.debug(f"bluetoothctl discovery stop failed: {e}")

        return success

    def get_discovered_devices(self, bus, bluetooth_device):
        """Get discovered devices from D-Bus."""
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
            logger.debug(f"D-Bus discovered devices enumeration failed: {e}")

        return devices

