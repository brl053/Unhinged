#!/usr/bin/env python3
"""
@llm-doc Real-time System Information Manager for GTK4 UI
@llm-version 1.0.0
@llm-date 2025-10-28

Provides real-time system information updates for the GTK4 system info page
with efficient data collection and UI update mechanisms.
"""

import time
import threading
from typing import Dict, Any, Callable, Optional
from pathlib import Path
import logging

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
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root
        self.collector = SystemInfoCollector(project_root) if SYSTEM_INFO_AVAILABLE else None
        
        # Update management
        self._update_callbacks = {}  # metric_type -> callback function
        self._update_interval = 2.0  # seconds
        self._running = False
        self._update_thread = None
        self._last_values = {}
        
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
    
    def _collect_performance_data(self) -> Dict[str, float]:
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
    
    def _process_updates(self, performance_data: Dict[str, float]):
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
    
    def get_current_value(self, metric_type: str) -> Optional[float]:
        """Get the current value for a metric type."""
        return self._last_values.get(metric_type)
    
    def get_statistics(self) -> Dict[str, Any]:
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
        self._last_values.clear()


# Global instance for easy access
_realtime_manager = None

def get_realtime_manager(project_root: Optional[Path] = None) -> RealTimeSystemInfoManager:
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


if __name__ == "__main__":
    # Test the real-time manager
    import sys
    
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
    print(f"\n📈 Statistics:")
    print(f"  Updates: {stats['update_count']}")
    print(f"  Errors: {stats['error_count']}")
    print(f"  Error rate: {stats['error_rate']:.2%}")
    
    print("✅ Real-time manager test completed")
