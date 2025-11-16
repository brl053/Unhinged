"""
@llm-doc Network Information Collection
@llm-version 1.0.0
@llm-date 2025-11-15

Network interface and connectivity information collection using psutil and ip command.
"""

import logging
import platform

from subprocess_utils import SubprocessRunner

# Import psutil with fallback
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class NetworkCollector:
    """Collects network information."""

    def __init__(self):
        self.runner = SubprocessRunner(timeout=10)

    def collect_network_info(self):
        """Collect network information"""
        from ..system_info import NetworkInfo, NetworkInterface

        network_info = NetworkInfo()
        network_info.hostname = platform.node()

        if PSUTIL_AVAILABLE:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)

            for interface_name, addresses in interfaces.items():
                if interface_name == "lo":
                    continue

                interface = NetworkInterface(name=interface_name)

                for addr in addresses:
                    if addr.family.name == "AF_INET":
                        interface.ip_address = addr.address
                    elif addr.family.name == "AF_PACKET":
                        interface.mac_address = addr.address

                if interface_name in stats:
                    interface.status = "Up" if stats[interface_name].isup else "Down"

                if interface_name in io_counters:
                    io = io_counters[interface_name]
                    interface.bytes_sent = io.bytes_sent
                    interface.bytes_recv = io.bytes_recv
                    network_info.total_bytes_sent += io.bytes_sent
                    network_info.total_bytes_recv += io.bytes_recv

                network_info.interfaces.append(interface)
        else:
            # Fallback to ip command
            result = self.runner.run_list(["ip", "addr", "show"])
            if result["success"]:
                current_interface = None
                for line in result["output"].split("\n"):
                    line = line.strip()
                    if ": " in line and "state" in line:
                        parts = line.split(": ")
                        if len(parts) > 1:
                            interface_name = parts[1].split("@")[0]
                            if interface_name != "lo":
                                current_interface = NetworkInterface(name=interface_name)
                                if "state UP" in line:
                                    current_interface.status = "Up"
                                else:
                                    current_interface.status = "Down"
                                network_info.interfaces.append(current_interface)
                    elif current_interface and "inet " in line:
                        parts = line.split()
                        if len(parts) > 1:
                            current_interface.ip_address = parts[1].split("/")[0]
                    elif current_interface and "link/ether" in line:
                        parts = line.split()
                        if len(parts) > 1:
                            current_interface.mac_address = parts[1]

        return network_info
