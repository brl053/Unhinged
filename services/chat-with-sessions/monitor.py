#!/usr/bin/env python3
"""
Production Monitoring for Write-Through Session Management
Real-time performance and usage pattern monitoring
"""

import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import psutil

# Add paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "libs" / "python"))

from events import create_service_logger
from session.session_store import SessionStore, SessionStoreConfig

# Initialize event logger
events = create_service_logger("session-monitor", "1.0.0")


@dataclass
class SystemMetrics:
    """System resource metrics"""

    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int


@dataclass
class SessionStoreMetrics:
    """Session store specific metrics"""

    timestamp: float
    redis_latency_ms: float
    crdb_latency_ms: float
    redis_status: str
    crdb_status: str
    total_sessions: int
    active_sessions: int
    session_keys_count: int


class ProductionMonitor:
    """Production monitoring for session management system"""

    def __init__(self):
        self.start_time = time.time()
        self.metrics_history = []
        self.session_metrics_history = []

        # Initialize session store
        self._initialize_session_store()

        # Monitoring configuration
        self.monitoring_interval = 60  # 1 minute
        self.max_history_points = 1440  # 24 hours of data

        events.info(
            "Production monitor initialized",
            {
                "monitoring_interval": self.monitoring_interval,
                "max_history_points": self.max_history_points,
            },
        )

    def _initialize_session_store(self):
        """Initialize session store for monitoring"""
        try:
            config = SessionStoreConfig(
                redis_host="localhost",
                redis_port=6379,
                redis_db=0,  # Production database
                crdb_host="localhost",
                crdb_port=26257,
                crdb_database="unhinged",
                crdb_user="root",
            )

            self.session_store = SessionStore(config)
            events.info("Session store connected for monitoring")

        except Exception as e:
            events.error("Failed to connect to session store", exception=e)
            self.session_store = None

    def collect_system_metrics(self) -> SystemMetrics | None:
        """Collect system resource metrics"""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            # Disk usage
            disk = psutil.disk_usage("/")

            # Network stats
            network = psutil.net_io_counters()

            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_gb=memory.available / (1024**3),
                disk_usage_percent=disk.percent,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
            )

        except Exception as e:
            events.error("Failed to collect system metrics", exception=e)
            return None

    def collect_session_store_metrics(self) -> SessionStoreMetrics | None:
        """Collect session store specific metrics"""
        if not self.session_store:
            return None

        try:
            # Health check with latency
            health = self.session_store.health_check()

            # Count session keys
            session_keys = self.session_store.list_keys("session:*")

            # Count active sessions (those with recent activity)
            active_count = 0
            current_time = time.time()

            for key in session_keys[:50]:  # Sample first 50 for performance
                if ":metadata" in key:
                    session_data = self.session_store.read(key)
                    if session_data and isinstance(session_data, dict):
                        created_at = session_data.get("created_at", 0)
                        # Consider active if created within last 24 hours
                        if current_time - created_at < 86400:
                            active_count += 1

            return SessionStoreMetrics(
                timestamp=time.time(),
                redis_latency_ms=health["redis"].get("latency_ms", 0),
                crdb_latency_ms=health["crdb"].get("latency_ms", 0),
                redis_status=health["redis"]["status"],
                crdb_status=health["crdb"]["status"],
                total_sessions=len(session_keys),
                active_sessions=active_count,
                session_keys_count=len(session_keys),
            )

        except Exception as e:
            events.error("Failed to collect session store metrics", exception=e)
            return None

    def analyze_usage_patterns(self) -> dict[str, Any]:
        """Analyze usage patterns from recent metrics"""
        if len(self.session_metrics_history) < 2:
            return {}

        recent_metrics = self.session_metrics_history[-60:]  # Last hour

        # Calculate averages
        avg_redis_latency = sum(m.redis_latency_ms for m in recent_metrics) / len(recent_metrics)
        avg_crdb_latency = sum(m.crdb_latency_ms for m in recent_metrics) / len(recent_metrics)

        # Session growth rate
        if len(recent_metrics) >= 2:
            session_growth = recent_metrics[-1].total_sessions - recent_metrics[0].total_sessions
            session_growth_rate = session_growth / len(recent_metrics)  # per minute
        else:
            session_growth_rate = 0

        # Performance trends
        latency_trend = "stable"
        if len(recent_metrics) >= 10:
            early_avg = sum(m.redis_latency_ms for m in recent_metrics[:5]) / 5
            late_avg = sum(m.redis_latency_ms for m in recent_metrics[-5:]) / 5

            if late_avg > early_avg * 1.2:
                latency_trend = "increasing"
            elif late_avg < early_avg * 0.8:
                latency_trend = "decreasing"

        return {
            "avg_redis_latency_ms": round(avg_redis_latency, 2),
            "avg_crdb_latency_ms": round(avg_crdb_latency, 2),
            "session_growth_rate_per_minute": round(session_growth_rate, 2),
            "latency_trend": latency_trend,
            "current_total_sessions": recent_metrics[-1].total_sessions,
            "current_active_sessions": recent_metrics[-1].active_sessions,
        }

    def check_performance_thresholds(
        self, system_metrics: SystemMetrics, session_metrics: SessionStoreMetrics
    ) -> list[str]:
        """Check for performance threshold violations"""
        alerts = []

        # System resource alerts
        if system_metrics:
            if system_metrics.cpu_percent > 80:
                alerts.append(f"High CPU usage: {system_metrics.cpu_percent:.1f}%")

            if system_metrics.memory_percent > 85:
                alerts.append(f"High memory usage: {system_metrics.memory_percent:.1f}%")

            if system_metrics.memory_available_gb < 5:
                alerts.append(f"Low available memory: {system_metrics.memory_available_gb:.1f}GB")

        # Session store alerts
        if session_metrics:
            if session_metrics.redis_latency_ms > 10:
                alerts.append(f"High Redis latency: {session_metrics.redis_latency_ms:.2f}ms")

            if session_metrics.crdb_latency_ms > 50:
                alerts.append(f"High CRDB latency: {session_metrics.crdb_latency_ms:.2f}ms")

            if session_metrics.redis_status != "healthy":
                alerts.append(f"Redis unhealthy: {session_metrics.redis_status}")

            if session_metrics.crdb_status != "healthy":
                alerts.append(f"CRDB unhealthy: {session_metrics.crdb_status}")

        return alerts

    def log_monitoring_report(self):
        """Log comprehensive monitoring report"""
        uptime_hours = (time.time() - self.start_time) / 3600

        # Get latest metrics
        latest_system = self.metrics_history[-1] if self.metrics_history else None
        latest_session = self.session_metrics_history[-1] if self.session_metrics_history else None

        # Usage patterns
        usage_patterns = self.analyze_usage_patterns()

        # Performance alerts
        alerts = self.check_performance_thresholds(latest_system, latest_session)

        report = {
            "monitoring_summary": {
                "uptime_hours": round(uptime_hours, 2),
                "data_points_collected": len(self.metrics_history),
                "monitoring_healthy": latest_system is not None and latest_session is not None,
            },
            "current_system_metrics": asdict(latest_system) if latest_system else None,
            "current_session_metrics": asdict(latest_session) if latest_session else None,
            "usage_patterns": usage_patterns,
            "performance_alerts": alerts,
        }

        events.info("Production monitoring report", report)

        # Log alerts separately if any
        if alerts:
            events.warning("Performance alerts detected", {"alerts": alerts})

    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        # Collect metrics
        system_metrics = self.collect_system_metrics()
        session_metrics = self.collect_session_store_metrics()

        # Store metrics
        if system_metrics:
            self.metrics_history.append(system_metrics)
            if len(self.metrics_history) > self.max_history_points:
                self.metrics_history.pop(0)

        if session_metrics:
            self.session_metrics_history.append(session_metrics)
            if len(self.session_metrics_history) > self.max_history_points:
                self.session_metrics_history.pop(0)

        # Log report every 10 minutes
        if len(self.metrics_history) % 10 == 0:
            self.log_monitoring_report()

    def run(self):
        """Run continuous monitoring"""
        events.info(
            "Starting production monitoring",
            {"interval_seconds": self.monitoring_interval},
        )

        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(self.monitoring_interval)

        except KeyboardInterrupt:
            events.info("Monitoring stopped by user")
        except Exception as e:
            events.error("Monitoring exception", exception=e)
        finally:
            if self.session_store:
                self.session_store.close()


def main():
    """Main entry point for production monitoring"""
    monitor = ProductionMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
