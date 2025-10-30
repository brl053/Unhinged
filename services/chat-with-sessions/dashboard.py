#!/usr/bin/env python3
"""
Real-Time Dashboard for Session Management Deployment
Live monitoring of stability test and production metrics
"""

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def parse_log_line(line):
    """Parse log line to extract structured data"""
    try:
        # Look for JSON data in log lines
        json_match = re.search(r'\{.*\}', line)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return None

def get_latest_metrics():
    """Get latest metrics from log files"""
    metrics = {
        "stability_test": {"status": "unknown", "data": {}},
        "monitor": {"status": "unknown", "data": {}},
        "services": {"redis": "unknown", "crdb": "unknown"}
    }

    # Parse stability test log
    stability_log = Path("stability_test.log")
    if stability_log.exists():
        try:
            with open(stability_log) as f:
                lines = f.readlines()

            # Get latest progress info
            for line in reversed(lines[-50:]):  # Check last 50 lines
                if "Stability test progress" in line:
                    data = parse_log_line(line)
                    if data:
                        metrics["stability_test"]["status"] = "running"
                        metrics["stability_test"]["data"] = data
                        break
                elif "Starting 24-hour stability test" in line:
                    data = parse_log_line(line)
                    if data:
                        metrics["stability_test"]["status"] = "started"
                        metrics["stability_test"]["data"] = data
                        break
        except Exception as e:
            metrics["stability_test"]["status"] = f"error: {e}"

    # Parse monitor log
    monitor_log = Path("monitor.log")
    if monitor_log.exists():
        try:
            with open(monitor_log) as f:
                lines = f.readlines()

            # Get latest monitoring report
            for line in reversed(lines[-20:]):  # Check last 20 lines
                if "Production monitoring report" in line:
                    data = parse_log_line(line)
                    if data:
                        metrics["monitor"]["status"] = "active"
                        metrics["monitor"]["data"] = data

                        # Extract service status
                        session_metrics = data.get("current_session_metrics", {})
                        metrics["services"]["redis"] = session_metrics.get("redis_status", "unknown")
                        metrics["services"]["crdb"] = session_metrics.get("crdb_status", "unknown")
                        break
        except Exception as e:
            metrics["monitor"]["status"] = f"error: {e}"

    return metrics

def format_duration(seconds):
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def format_number(num):
    """Format number with commas"""
    if isinstance(num, (int, float)):
        return f"{num:,}"
    return str(num)

def display_dashboard(metrics):
    """Display real-time dashboard"""
    clear_screen()

    now = datetime.now()

    print("🚀 WRITE-THROUGH SESSION MANAGEMENT - PRODUCTION DASHBOARD")
    print("=" * 80)
    print(f"📅 {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print()

    # Service Status
    print("🔧 SERVICE STATUS")
    print("-" * 40)
    redis_status = metrics["services"]["redis"]
    crdb_status = metrics["services"]["crdb"]

    redis_icon = "✅" if redis_status == "healthy" else "❌"
    crdb_icon = "✅" if crdb_status == "healthy" else "❌"

    print(f"{redis_icon} Redis:      {redis_status}")
    print(f"{crdb_icon} CockroachDB: {crdb_status}")
    print()

    # Stability Test Status
    print("🧪 24-HOUR STABILITY TEST")
    print("-" * 40)
    stability = metrics["stability_test"]

    if stability["status"] == "running" and stability["data"]:
        data = stability["data"]
        elapsed = data.get("elapsed_hours", 0)
        progress = data.get("progress_percent", 0)
        total_ops = data.get("total_operations", 0)
        total_errors = data.get("total_errors", 0)
        error_rate = data.get("error_rate_percent", 0)
        active_sessions = data.get("active_sessions", 0)

        # Progress bar
        bar_width = 50
        filled = int(bar_width * progress / 100)
        bar = "█" * filled + "░" * (bar_width - filled)

        print("Status:     🟢 RUNNING")
        print(f"Progress:   [{bar}] {progress:.1f}%")
        print(f"Elapsed:    {elapsed:.2f} hours")
        print(f"Operations: {format_number(total_ops)}")
        print(f"Errors:     {format_number(total_errors)} ({error_rate:.4f}%)")
        print(f"Sessions:   {format_number(active_sessions)} active")

        # Performance metrics
        avg_write = data.get("avg_write_latency_ms", 0)
        avg_read = data.get("avg_read_latency_ms", 0)
        print(f"Write Lat:  {avg_write:.2f}ms")
        print(f"Read Lat:   {avg_read:.2f}ms")

    elif stability["status"] == "started":
        print("Status:     🟡 STARTING")
        print("Duration:   24 hours")

    else:
        print(f"Status:     ❓ {stability['status'].upper()}")

    print()

    # Production Monitoring
    print("📊 PRODUCTION MONITORING")
    print("-" * 40)
    monitor = metrics["monitor"]

    if monitor["status"] == "active" and monitor["data"]:
        data = monitor["data"]

        # Monitoring summary
        summary = data.get("monitoring_summary", {})
        uptime = summary.get("uptime_hours", 0)
        data_points = summary.get("data_points_collected", 0)
        healthy = summary.get("monitoring_healthy", False)

        health_icon = "✅" if healthy else "❌"
        print(f"Status:     {health_icon} {'HEALTHY' if healthy else 'UNHEALTHY'}")
        print(f"Uptime:     {uptime:.2f} hours")
        print(f"Data Points: {format_number(data_points)}")

        # System metrics
        system = data.get("current_system_metrics", {})
        if system:
            cpu = system.get("cpu_percent", 0)
            memory = system.get("memory_percent", 0)
            memory_gb = system.get("memory_available_gb", 0)

            print(f"CPU:        {cpu:.1f}%")
            print(f"Memory:     {memory:.1f}% ({memory_gb:.1f}GB free)")

        # Session store metrics
        session = data.get("current_session_metrics", {})
        if session:
            redis_lat = session.get("redis_latency_ms", 0)
            crdb_lat = session.get("crdb_latency_ms", 0)
            total_sessions = session.get("total_sessions", 0)
            active_sessions = session.get("active_sessions", 0)

            print(f"Redis Lat:  {redis_lat:.2f}ms")
            print(f"CRDB Lat:   {crdb_lat:.2f}ms")
            print(f"Sessions:   {format_number(total_sessions)} total, {format_number(active_sessions)} active")

        # Usage patterns
        patterns = data.get("usage_patterns", {})
        if patterns:
            trend = patterns.get("latency_trend", "unknown")
            growth = patterns.get("session_growth_rate_per_minute", 0)

            trend_icon = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}.get(trend, "❓")
            print(f"Trend:      {trend_icon} {trend}")
            print(f"Growth:     {growth:.2f} sessions/min")

        # Alerts
        alerts = data.get("performance_alerts", [])
        if alerts:
            print(f"🚨 ALERTS:  {len(alerts)} active")
            for alert in alerts[:3]:  # Show first 3 alerts
                print(f"  • {alert}")
        else:
            print("✅ ALERTS:  None")

    else:
        print(f"Status:     ❓ {monitor['status'].upper()}")

    print()
    print("=" * 80)
    print("📝 Log Files: stability_test.log, monitor.log")
    print("🔄 Refreshing every 10 seconds... (Ctrl+C to exit)")

def main():
    """Main dashboard loop"""
    print("🚀 Starting Session Management Dashboard...")
    print("📍 Location: services/chat-with-sessions/")

    # Change to correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    try:
        while True:
            metrics = get_latest_metrics()
            display_dashboard(metrics)
            time.sleep(10)  # Refresh every 10 seconds

    except KeyboardInterrupt:
        clear_screen()
        print("👋 Dashboard stopped by user")
        print("✅ Session management deployment continues running")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")

if __name__ == '__main__':
    main()
