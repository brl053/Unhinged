#!/usr/bin/env python3
"""
@llm-doc Real-time System Information Manager for GTK4 UI
@llm-version 1.0.0
@llm-date 2025-10-28

Provides real-time system information updates for the GTK4 system info page
with efficient data collection and UI update mechanisms.
"""

import logging
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

# Import system info collection
try:
    from system_info import SystemInfoCollector, get_performance_summary
    SYSTEM_INFO_AVAILABLE = True
except ImportError:
    SYSTEM_INFO_AVAILABLE = False

# Import GTK for main thread updates
try:
    import gi
    gi.require_version('GLib', '2.0')
    from gi.repository import GLib
    GLIB_AVAILABLE = True
except ImportError:
    GLIB_AVAILABLE = False

logger = logging.getLogger(__name__)


class RealTimeSystemInfoManager:
    """
    Manages real-time system information collection and UI updates.
    
    Features:
    - Background data collection with configurable intervals
    - Thread-safe UI updates via GLib.idle_add
    - Efficient caching and change detection
    - Automatic error handling and recovery
    """

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root
        self.collector = SystemInfoCollector(project_root) if SYSTEM_INFO_AVAILABLE else None

        # Update management
        self._update_callbacks = {}  # metric_type -> callback function
        self._process_callbacks = {}  # process monitoring callbacks
        self._bluetooth_callbacks = {}  # Bluetooth monitoring callbacks
        self._update_interval = 2.0  # seconds
        self._running = False
        self._update_thread = None
        self._last_values = {}
        self._last_processes = {}  # PID -> ProcessInfo
        self._last_bluetooth_devices = {}  # Address -> BluetoothDevice

        # Performance tracking
        self._update_count = 0
        self._error_count = 0
        self._last_update_time = 0

    def register_callback(self, metric_type: str, callback: Callable[[float], None]):
        """Register a callback for metric updates."""
        self._update_callbacks[metric_type] = callback
        logger.debug(f"Registered callback for {metric_type}")

    def unregister_callback(self, metric_type: str):
        """Unregister a callback for metric updates."""
        if metric_type in self._update_callbacks:
            del self._update_callbacks[metric_type]
            logger.debug(f"Unregistered callback for {metric_type}")

    def register_process_callback(self, callback_name: str, callback: Callable):
        """Register a callback for process updates."""
        self._process_callbacks[callback_name] = callback
        logger.debug(f"Registered process callback: {callback_name}")

    def unregister_process_callback(self, callback_name: str):
        """Unregister a process callback."""
        if callback_name in self._process_callbacks:
            del self._process_callbacks[callback_name]
            logger.debug(f"Unregistered process callback: {callback_name}")

    def register_bluetooth_callback(self, callback_name: str, callback: Callable):
        """Register a callback for Bluetooth updates."""
        self._bluetooth_callbacks[callback_name] = callback
        logger.debug(f"Registered Bluetooth callback: {callback_name}")

    def unregister_bluetooth_callback(self, callback_name: str):
        """Unregister a Bluetooth callback."""
        if callback_name in self._bluetooth_callbacks:
            del self._bluetooth_callbacks[callback_name]
            logger.debug(f"Unregistered Bluetooth callback: {callback_name}")

    def start_updates(self, interval: float = 2.0):
        """Start real-time updates."""
        if not SYSTEM_INFO_AVAILABLE or not GLIB_AVAILABLE:
            logger.warning("Real-time updates not available - missing dependencies")
            return False

        if self._running:
            logger.warning("Updates already running")
            return True

        self._update_interval = interval
        self._running = True
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()

        logger.info(f"Started real-time updates with {interval}s interval")
        return True

    def stop_updates(self):
        """Stop real-time updates."""
        if not self._running:
            return

        self._running = False
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=5.0)

        logger.info("Stopped real-time updates")

    def _update_loop(self):
        """Background update loop."""
        while self._running:
            try:
                start_time = time.time()

                # Collect current performance data
                performance_data = self._collect_performance_data()

                # Collect process data if there are process callbacks
                if self._process_callbacks:
                    process_data = self._collect_process_data()
                    self._process_process_updates(process_data)

                # Collect Bluetooth data if there are Bluetooth callbacks
                if self._bluetooth_callbacks:
                    bluetooth_data = self._collect_bluetooth_data()
                    self._process_bluetooth_updates(bluetooth_data)

                # Check for changes and trigger callbacks
                self._process_updates(performance_data)

                # Update performance tracking
                self._update_count += 1
                self._last_update_time = time.time()

                # Calculate sleep time to maintain interval
                elapsed = time.time() - start_time
                sleep_time = max(0, self._update_interval - elapsed)

                if sleep_time > 0:
                    time.sleep(sleep_time)

            except Exception as e:
                self._error_count += 1
                logger.error(f"Update loop error: {e}")
                time.sleep(self._update_interval)  # Continue after error

    def _collect_performance_data(self) -> dict[str, float]:
        """Collect current performance data."""
        if not self.collector:
            return {}

        try:
            # Get performance summary (uses caching internally)
            summary = self.collector.get_performance_summary()

            return {
                'cpu': summary.get('cpu_usage', 0.0),
                'memory': summary.get('memory_usage', 0.0),
                'disk': summary.get('storage_usage', 0.0),
                'network': 0.0  # Placeholder for network usage
            }

        except Exception as e:
            logger.error(f"Failed to collect performance data: {e}")
            return {}

    def _collect_process_data(self) -> dict[int, Any]:
        """Collect current process data for monitoring."""
        try:
            # Import process monitor
            from process_monitor import get_top_processes

            # Get top processes (limit to reduce overhead)
            processes = get_top_processes(limit=100, sort_by='cpu_percent')

            # Convert to dict keyed by PID
            process_dict = {proc.pid: proc for proc in processes}

            return process_dict

        except Exception as e:
            logger.error(f"Failed to collect process data: {e}")
            return {}

    def _process_process_updates(self, process_data: dict[int, Any]):
        """Process process updates and trigger callbacks for changes."""
        try:
            # Detect new, updated, and removed processes
            current_pids = set(process_data.keys())
            last_pids = set(self._last_processes.keys())

            new_pids = current_pids - last_pids
            removed_pids = last_pids - current_pids
            existing_pids = current_pids & last_pids

            # Check for significant changes in existing processes
            updated_processes = []
            for pid in existing_pids:
                current_proc = process_data[pid]
                last_proc = self._last_processes[pid]

                # Check for significant CPU or memory changes (>1% change)
                if (abs(current_proc.cpu_percent - last_proc.cpu_percent) > 1.0 or
                    abs(current_proc.memory_percent - last_proc.memory_percent) > 1.0):
                    updated_processes.append(current_proc)

            # Trigger callbacks if there are changes
            if new_pids or removed_pids or updated_processes:
                for callback_name, callback in self._process_callbacks.items():
                    if GLIB_AVAILABLE:
                        GLib.idle_add(callback, {
                            'new': [process_data[pid] for pid in new_pids],
                            'removed': [self._last_processes[pid] for pid in removed_pids],
                            'updated': updated_processes,
                            'all': list(process_data.values())
                        })
                    else:
                        # Fallback for testing without GTK
                        callback({
                            'new': [process_data[pid] for pid in new_pids],
                            'removed': [self._last_processes[pid] for pid in removed_pids],
                            'updated': updated_processes,
                            'all': list(process_data.values())
                        })

            # Update last processes
            self._last_processes = process_data.copy()

        except Exception as e:
            logger.error(f"Failed to process process updates: {e}")

    def _collect_bluetooth_data(self) -> dict[str, Any]:
        """Collect current Bluetooth data for monitoring."""
        try:
            # Import Bluetooth monitor
            from bluetooth_monitor import get_bluetooth_adapters, get_bluetooth_devices

            # Get devices and adapters
            devices = get_bluetooth_devices(include_unpaired=True)
            adapters = get_bluetooth_adapters()

            # Convert devices to dict keyed by address
            device_dict = {device.address: device for device in devices}

            return {
                'devices': device_dict,
                'adapters': adapters,
                'device_count': len(devices),
                'adapter_count': len(adapters)
            }

        except Exception as e:
            logger.error(f"Failed to collect Bluetooth data: {e}")
            return {'devices': {}, 'adapters': [], 'device_count': 0, 'adapter_count': 0}

    def _process_bluetooth_updates(self, bluetooth_data: dict[str, Any]):
        """Process Bluetooth updates and trigger callbacks for changes."""
        try:
            current_devices = bluetooth_data.get('devices', {})
            current_addresses = set(current_devices.keys())
            last_addresses = set(self._last_bluetooth_devices.keys())

            new_addresses = current_addresses - last_addresses
            removed_addresses = last_addresses - current_addresses
            existing_addresses = current_addresses & last_addresses

            # Check for connection state changes in existing devices
            updated_devices = []
            for address in existing_addresses:
                current_device = current_devices[address]
                last_device = self._last_bluetooth_devices[address]

                # Check for connection or pairing state changes
                if (current_device.connected != last_device.connected or
                    current_device.paired != last_device.paired or
                    current_device.trusted != last_device.trusted or
                    current_device.blocked != last_device.blocked):
                    updated_devices.append(current_device)

            # Trigger callbacks if there are changes
            if new_addresses or removed_addresses or updated_devices:
                for callback_name, callback in self._bluetooth_callbacks.items():
                    if GLIB_AVAILABLE:
                        GLib.idle_add(callback, {
                            'new': [current_devices[addr] for addr in new_addresses],
                            'removed': [self._last_bluetooth_devices[addr] for addr in removed_addresses],
                            'updated': updated_devices,
                            'all_devices': list(current_devices.values()),
                            'adapters': bluetooth_data.get('adapters', []),
                            'device_count': bluetooth_data.get('device_count', 0),
                            'adapter_count': bluetooth_data.get('adapter_count', 0)
                        })
                    else:
                        # Fallback for testing without GTK
                        callback({
                            'new': [current_devices[addr] for addr in new_addresses],
                            'removed': [self._last_bluetooth_devices[addr] for addr in removed_addresses],
                            'updated': updated_devices,
                            'all_devices': list(current_devices.values()),
                            'adapters': bluetooth_data.get('adapters', []),
                            'device_count': bluetooth_data.get('device_count', 0),
                            'adapter_count': bluetooth_data.get('adapter_count', 0)
                        })

            # Update last devices
            self._last_bluetooth_devices = current_devices.copy()

        except Exception as e:
            logger.error(f"Failed to process Bluetooth updates: {e}")

    def _process_updates(self, performance_data: dict[str, float]):
        """Process updates and trigger callbacks if values changed."""
        for metric_type, current_value in performance_data.items():
            if metric_type not in self._update_callbacks:
                continue

            # Check if value changed significantly (>0.5% change)
            last_value = self._last_values.get(metric_type, 0.0)
            if abs(current_value - last_value) > 0.5:
                self._last_values[metric_type] = current_value

                # Schedule UI update on main thread
                callback = self._update_callbacks[metric_type]
                if GLIB_AVAILABLE:
                    GLib.idle_add(callback, current_value)
                else:
                    # Fallback for testing without GTK
                    callback(current_value)

    def get_current_value(self, metric_type: str) -> float | None:
        """Get the current value for a metric type."""
        return self._last_values.get(metric_type)

    def get_statistics(self) -> dict[str, Any]:
        """Get update statistics for monitoring."""
        return {
            'running': self._running,
            'update_count': self._update_count,
            'error_count': self._error_count,
            'last_update_time': self._last_update_time,
            'update_interval': self._update_interval,
            'registered_callbacks': list(self._update_callbacks.keys()),
            'error_rate': self._error_count / max(self._update_count, 1)
        }

    def cleanup(self):
        """Clean up resources."""
        self.stop_updates()
        self._update_callbacks.clear()
        self._process_callbacks.clear()
        self._bluetooth_callbacks.clear()
        self._last_values.clear()
        self._last_processes.clear()
        self._last_bluetooth_devices.clear()


# Global instance for easy access
_realtime_manager = None

def get_realtime_manager(project_root: Path | None = None) -> RealTimeSystemInfoManager:
    """Get the global real-time manager instance."""
    global _realtime_manager
    if _realtime_manager is None:
        _realtime_manager = RealTimeSystemInfoManager(project_root)
    return _realtime_manager

def start_realtime_updates(interval: float = 2.0) -> bool:
    """Start real-time updates with the global manager."""
    manager = get_realtime_manager()
    return manager.start_updates(interval)

def stop_realtime_updates():
    """Stop real-time updates with the global manager."""
    manager = get_realtime_manager()
    manager.stop_updates()

def register_metric_callback(metric_type: str, callback: Callable[[float], None]):
    """Register a callback for metric updates."""
    manager = get_realtime_manager()
    manager.register_callback(metric_type, callback)

def unregister_metric_callback(metric_type: str):
    """Unregister a callback for metric updates."""
    manager = get_realtime_manager()
    manager.unregister_callback(metric_type)

def register_process_callback(callback_name: str, callback: Callable):
    """Register a callback for process updates."""
    manager = get_realtime_manager()
    manager.register_process_callback(callback_name, callback)

def unregister_process_callback(callback_name: str):
    """Unregister a process callback."""
    manager = get_realtime_manager()
    manager.unregister_process_callback(callback_name)

def register_bluetooth_callback(callback_name: str, callback: Callable):
    """Register a callback for Bluetooth updates."""
    manager = get_realtime_manager()
    manager.register_bluetooth_callback(callback_name, callback)

def unregister_bluetooth_callback(callback_name: str):
    """Unregister a Bluetooth callback."""
    manager = get_realtime_manager()
    manager.unregister_bluetooth_callback(callback_name)


if __name__ == "__main__":
    # Test the real-time manager

    print("🧪 Testing Real-time System Info Manager")
    print("=" * 50)

    def test_callback(metric_type):
        def callback(value):
            print(f"📊 {metric_type}: {value:.1f}%")
        return callback

    manager = RealTimeSystemInfoManager()

    # Register test callbacks
    manager.register_callback('cpu', test_callback('CPU'))
    manager.register_callback('memory', test_callback('Memory'))
    manager.register_callback('disk', test_callback('Disk'))

    print("Starting updates for 10 seconds...")
    manager.start_updates(interval=1.0)

    try:
        time.sleep(10)
    except KeyboardInterrupt:
        pass

    manager.stop_updates()

    stats = manager.get_statistics()
    print("\n📈 Statistics:")
    print(f"  Updates: {stats['update_count']}")
    print(f"  Errors: {stats['error_count']}")
    print(f"  Error rate: {stats['error_rate']:.2%}")

    print("✅ Real-time manager test completed")
