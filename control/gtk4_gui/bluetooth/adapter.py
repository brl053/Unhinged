"""
@llm-doc Bluetooth Adapter Management
@llm-version 1.0.0
@llm-date 2025-11-15

Adapter enumeration and management.
"""

import logging
import subprocess

logger = logging.getLogger(__name__)


class AdapterManager:
    """Manages Bluetooth adapter operations."""

    def __init__(self, bus):
        """Initialize adapter manager."""
        self._bus = bus

    def get_adapters_dbus(self, BluetoothAdapter) -> list:
        """Get adapters using D-Bus."""
        adapters = []

        try:
            return self.get_adapters_bluetoothctl(BluetoothAdapter)
        except Exception as e:
            logger.error(f"D-Bus adapter enumeration failed: {e}")

        return adapters

    def get_adapters_bluetoothctl(self, BluetoothAdapter) -> list:
        """Get adapters using bluetoothctl fallback."""
        adapters = []

        try:
            result = subprocess.run(
                ["bluetoothctl", "show"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                logger.warning("bluetoothctl show failed")
                return adapters

            current_adapter = None
            for line in result.stdout.split("\n"):
                line = line.strip()

                if line.startswith("Controller"):
                    if current_adapter:
                        adapters.append(current_adapter)

                    parts = line.split()
                    if len(parts) >= 2:
                        address = parts[1]
                        name = " ".join(parts[2:]) if len(parts) > 2 else "Unknown"
                        current_adapter = {
                            "address": address,
                            "name": name,
                            "alias": name,
                            "powered": False,
                            "discoverable": False,
                            "pairable": False,
                            "discovering": False,
                            "uuids": [],
                            "manufacturer": 0,
                            "version": 0,
                        }

                elif current_adapter and ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if key == "powered":
                        current_adapter["powered"] = value.lower() == "yes"
                    elif key == "discoverable":
                        current_adapter["discoverable"] = value.lower() == "yes"
                    elif key == "pairable":
                        current_adapter["pairable"] = value.lower() == "yes"
                    elif key == "discovering":
                        current_adapter["discovering"] = value.lower() == "yes"

            if current_adapter:
                adapters.append(current_adapter)

            return [
                BluetoothAdapter(
                    address=a["address"],
                    name=a["name"],
                    alias=a["alias"],
                    powered=a["powered"],
                    discoverable=a["discoverable"],
                    pairable=a["pairable"],
                    discovering=a["discovering"],
                    uuids=a["uuids"],
                    manufacturer=a["manufacturer"],
                    version=a["version"],
                )
                for a in adapters
            ]

        except Exception as e:
            logger.error(f"Failed to get adapters via bluetoothctl: {e}")

        return adapters

