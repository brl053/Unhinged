"""
@llm-doc Bluetooth Device Operations
@llm-version 1.0.0
@llm-date 2025-11-15

Device connection, pairing, and trust management.
"""

import logging
import subprocess

logger = logging.getLogger(__name__)


class DeviceOperations:
    """Manages Bluetooth device operations."""

    def __init__(self, bus):
        """Initialize device operations manager."""
        self._bus = bus

    def find_device_path(self, address: str) -> str | None:
        """Find the D-Bus path for a device by its address."""
        if not self._bus:
            return None

        try:
            import dbus

            manager = dbus.Interface(
                self._bus.get_object("org.bluez", "/"),
                "org.freedesktop.DBus.ObjectManager",
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
        """Connect to a Bluetooth device."""
        if not self._bus:
            logger.warning("D-Bus not available - trying bluetoothctl fallback")
            return self._connect_device_bluetoothctl(address)

        try:
            import dbus

            device_path = self.find_device_path(address)
            if not device_path:
                logger.error(f"Device not found: {address}")
                return False

            device = dbus.Interface(
                self._bus.get_object("org.bluez", device_path), "org.bluez.Device1"
            )

            device.Connect()
            logger.info(f"Connected to device: {address}")
            return True

        except Exception as e:
            logger.error(f"D-Bus error connecting to {address}: {e}")
            return self._connect_device_bluetoothctl(address)

    def disconnect_device(self, address: str) -> bool:
        """Disconnect from a Bluetooth device."""
        if not self._bus:
            return self._disconnect_device_bluetoothctl(address)

        try:
            import dbus

            device_path = self.find_device_path(address)
            if not device_path:
                logger.error(f"Device not found: {address}")
                return False

            device = dbus.Interface(
                self._bus.get_object("org.bluez", device_path), "org.bluez.Device1"
            )

            device.Disconnect()
            logger.info(f"Disconnected from device: {address}")
            return True

        except Exception as e:
            logger.error(f"D-Bus error disconnecting from {address}: {e}")
            return self._disconnect_device_bluetoothctl(address)

    def pair_device(self, address: str) -> bool:
        """Pair with a Bluetooth device."""
        if not self._bus:
            return self._pair_device_bluetoothctl(address)

        try:
            import dbus

            device_path = self.find_device_path(address)
            if not device_path:
                logger.error(f"Device not found: {address}")
                return False

            device = dbus.Interface(
                self._bus.get_object("org.bluez", device_path), "org.bluez.Device1"
            )

            device.Pair()
            logger.info(f"Paired with device: {address}")
            return True

        except Exception as e:
            logger.error(f"D-Bus error pairing with {address}: {e}")
            return self._pair_device_bluetoothctl(address)

    def set_trusted(self, address: str, trusted: bool) -> bool:
        """Set device trust status."""
        if not self._bus:
            return False

        try:
            import dbus

            device_path = self.find_device_path(address)
            if not device_path:
                logger.error(f"Device not found: {address}")
                return False

            device = dbus.Interface(
                self._bus.get_object("org.bluez", device_path), "org.bluez.Device1"
            )

            device.Set("org.bluez.Device1", "Trusted", dbus.Boolean(trusted))
            logger.info(f"Set device {address} trusted={trusted}")
            return True

        except Exception as e:
            logger.error(f"Failed to set trusted status for {address}: {e}")
            return False

    @staticmethod
    def _connect_device_bluetoothctl(address: str) -> bool:
        """Connect using bluetoothctl fallback."""
        try:
            result = subprocess.run(
                ["bluetoothctl", "connect", address],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"bluetoothctl connect failed: {e}")
            return False

    @staticmethod
    def _disconnect_device_bluetoothctl(address: str) -> bool:
        """Disconnect using bluetoothctl fallback."""
        try:
            result = subprocess.run(
                ["bluetoothctl", "disconnect", address],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"bluetoothctl disconnect failed: {e}")
            return False

    @staticmethod
    def _pair_device_bluetoothctl(address: str) -> bool:
        """Pair using bluetoothctl fallback."""
        try:
            result = subprocess.run(
                ["bluetoothctl", "pair", address],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"bluetoothctl pair failed: {e}")
            return False

