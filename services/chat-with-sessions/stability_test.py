#!/usr/bin/env python3
"""
24-Hour Stability Test for Write-Through Session Management
Production deployment validation as specified by consultant
"""

import json
import random
import signal
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "libs" / "python"))

from events import create_service_logger
from session.session_store import SessionStore, SessionStoreConfig

# Initialize event logger
events = create_service_logger("stability-test", "1.0.0")

@dataclass
class StabilityMetrics:
    """Metrics collection for stability test"""
    start_time: float
    end_time: float = 0.0
    duration_hours: float = 0.0

    # Operation counts
    sessions_created: int = 0
    sessions_retrieved: int = 0
    messages_added: int = 0
    messages_retrieved: int = 0
    health_checks: int = 0

    # Error counts
    session_errors: int = 0
    message_errors: int = 0
    health_errors: int = 0
    connection_errors: int = 0

    # Performance metrics
    avg_write_latency_ms: float = 0.0
    avg_read_latency_ms: float = 0.0
    max_write_latency_ms: float = 0.0
    max_read_latency_ms: float = 0.0

    # Resource usage
    redis_memory_usage: list[float] = None
    crdb_connection_count: list[int] = None

    def __post_init__(self):
        if self.redis_memory_usage is None:
            self.redis_memory_usage = []
        if self.crdb_connection_count is None:
            self.crdb_connection_count = []

class StabilityTest:
    """24-hour stability test for write-through session management"""

    def __init__(self, duration_hours: float = 24.0):
        self.duration_hours = duration_hours
        self.running = False
        self.metrics = StabilityMetrics(start_time=time.time())

        # Initialize session store
        self._initialize_session_store()

        # Test configuration
        self.operations_per_second = 10
        self.max_concurrent_sessions = 100
        self.active_sessions = {}

        # Performance tracking
        self.write_latencies = []
        self.read_latencies = []

        events.info("Stability test initialized", {
            "duration_hours": duration_hours,
            "operations_per_second": self.operations_per_second,
            "max_concurrent_sessions": self.max_concurrent_sessions
        })

    def _initialize_session_store(self):
        """Initialize session store for stability testing"""
        try:
            config = SessionStoreConfig(
                redis_host='localhost',
                redis_port=6379,
                redis_db=2,  # Use separate DB for stability test
                crdb_host='localhost',
                crdb_port=26257,
                crdb_database='unhinged',
                crdb_user='root'
            )

            self.session_store = SessionStore(config)
            events.info("Session store initialized for stability test")

        except Exception as e:
            events.error("Failed to initialize session store", exception=e)
            raise

    def _create_test_session(self) -> str:
        """Create a test session with random data"""
        try:
            start_time = time.time()

            session_id = str(uuid.uuid4())
            session_data = {
                "session_id": session_id,
                "user_id": f"test_user_{random.randint(1000, 9999)}",
                "created_at": time.time(),
                "test_data": f"stability_test_{self.metrics.sessions_created}",
                "random_value": random.random()
            }

            session_key = f"stability:session:{session_id}:metadata"
            success = self.session_store.write(session_key, session_data)

            write_latency = (time.time() - start_time) * 1000
            self.write_latencies.append(write_latency)

            if success:
                self.active_sessions[session_id] = session_data
                self.metrics.sessions_created += 1
                return session_id
            else:
                self.metrics.session_errors += 1
                return None

        except Exception as e:
            self.metrics.session_errors += 1
            events.error("Session creation failed", exception=e)
            return None

    def _retrieve_test_session(self, session_id: str) -> bool:
        """Retrieve a test session"""
        try:
            start_time = time.time()

            session_key = f"stability:session:{session_id}:metadata"
            session_data = self.session_store.read(session_key)

            read_latency = (time.time() - start_time) * 1000
            self.read_latencies.append(read_latency)

            if session_data:
                self.metrics.sessions_retrieved += 1
                return True
            else:
                self.metrics.session_errors += 1
                return False

        except Exception as e:
            self.metrics.session_errors += 1
            events.error("Session retrieval failed", exception=e)
            return False

    def _add_test_message(self, session_id: str) -> bool:
        """Add a test message to session"""
        try:
            context_key = f"stability:session:{session_id}:context"
            context_data = self.session_store.read(context_key) or {"messages": []}

            message_data = {
                "id": str(uuid.uuid4()),
                "content": f"Test message {len(context_data['messages']) + 1}",
                "timestamp": time.time(),
                "test_data": random.choice(["alpha", "beta", "gamma", "delta"])
            }

            context_data["messages"].append(message_data)
            success = self.session_store.write(context_key, context_data)

            if success:
                self.metrics.messages_added += 1
                return True
            else:
                self.metrics.message_errors += 1
                return False

        except Exception as e:
            self.metrics.message_errors += 1
            events.error("Message add failed", exception=e)
            return False

    def _perform_health_check(self) -> bool:
        """Perform health check"""
        try:
            health = self.session_store.health_check()

            redis_healthy = health["redis"]["status"] == "healthy"
            crdb_healthy = health["crdb"]["status"] == "healthy"

            if redis_healthy and crdb_healthy:
                self.metrics.health_checks += 1
                return True
            else:
                self.metrics.health_errors += 1
                events.error("Health check failed", data=health)
                return False

        except Exception as e:
            self.metrics.health_errors += 1
            events.error("Health check exception", exception=e)
            return False

    def _random_operation(self):
        """Perform a random operation for load testing"""
        operation = random.choice([
            "create_session",
            "retrieve_session",
            "add_message",
            "health_check"
        ])

        if operation == "create_session":
            if len(self.active_sessions) < self.max_concurrent_sessions:
                self._create_test_session()

        elif operation == "retrieve_session" and self.active_sessions:
            session_id = random.choice(list(self.active_sessions.keys()))
            self._retrieve_test_session(session_id)

        elif operation == "add_message" and self.active_sessions:
            session_id = random.choice(list(self.active_sessions.keys()))
            self._add_test_message(session_id)

        elif operation == "health_check":
            self._perform_health_check()

    def _update_performance_metrics(self):
        """Update performance metrics"""
        if self.write_latencies:
            self.metrics.avg_write_latency_ms = sum(self.write_latencies) / len(self.write_latencies)
            self.metrics.max_write_latency_ms = max(self.write_latencies)

        if self.read_latencies:
            self.metrics.avg_read_latency_ms = sum(self.read_latencies) / len(self.read_latencies)
            self.metrics.max_read_latency_ms = max(self.read_latencies)

    def _log_progress(self):
        """Log test progress"""
        elapsed_hours = (time.time() - self.metrics.start_time) / 3600
        progress_percent = (elapsed_hours / self.duration_hours) * 100

        total_operations = (self.metrics.sessions_created +
                          self.metrics.sessions_retrieved +
                          self.metrics.messages_added +
                          self.metrics.health_checks)

        total_errors = (self.metrics.session_errors +
                       self.metrics.message_errors +
                       self.metrics.health_errors +
                       self.metrics.connection_errors)

        error_rate = (total_errors / max(total_operations, 1)) * 100

        events.info("Stability test progress", {
            "elapsed_hours": round(elapsed_hours, 2),
            "progress_percent": round(progress_percent, 1),
            "total_operations": total_operations,
            "total_errors": total_errors,
            "error_rate_percent": round(error_rate, 3),
            "active_sessions": len(self.active_sessions),
            "avg_write_latency_ms": round(self.metrics.avg_write_latency_ms, 2),
            "avg_read_latency_ms": round(self.metrics.avg_read_latency_ms, 2)
        })

    def run(self):
        """Run the 24-hour stability test"""
        self.running = True
        end_time = self.metrics.start_time + (self.duration_hours * 3600)

        events.info("Starting 24-hour stability test", {
            "duration_hours": self.duration_hours,
            "end_time": time.ctime(end_time),
            "operations_per_second": self.operations_per_second
        })

        last_progress_log = time.time()

        try:
            while self.running and time.time() < end_time:
                # Perform random operations
                for _ in range(self.operations_per_second):
                    if not self.running:
                        break
                    self._random_operation()

                # Update metrics
                self._update_performance_metrics()

                # Log progress every hour
                if time.time() - last_progress_log >= 3600:  # 1 hour
                    self._log_progress()
                    last_progress_log = time.time()

                # Sleep to maintain operations per second
                time.sleep(1.0)

        except KeyboardInterrupt:
            events.info("Stability test interrupted by user")
        except Exception as e:
            events.error("Stability test exception", exception=e)
        finally:
            self.running = False
            self._finalize_test()

    def _finalize_test(self):
        """Finalize test and generate report"""
        self.metrics.end_time = time.time()
        self.metrics.duration_hours = (self.metrics.end_time - self.metrics.start_time) / 3600

        # Final metrics update
        self._update_performance_metrics()

        # Generate final report
        self._generate_report()

        # Cleanup
        self.session_store.close()

    def _generate_report(self):
        """Generate final stability test report"""
        total_operations = (self.metrics.sessions_created +
                          self.metrics.sessions_retrieved +
                          self.metrics.messages_added +
                          self.metrics.health_checks)

        total_errors = (self.metrics.session_errors +
                       self.metrics.message_errors +
                       self.metrics.health_errors +
                       self.metrics.connection_errors)

        error_rate = (total_errors / max(total_operations, 1)) * 100
        ops_per_hour = total_operations / max(self.metrics.duration_hours, 0.001)

        report = {
            "test_summary": {
                "duration_hours": round(self.metrics.duration_hours, 2),
                "total_operations": total_operations,
                "operations_per_hour": round(ops_per_hour, 1),
                "total_errors": total_errors,
                "error_rate_percent": round(error_rate, 4),
                "final_active_sessions": len(self.active_sessions)
            },
            "operation_breakdown": {
                "sessions_created": self.metrics.sessions_created,
                "sessions_retrieved": self.metrics.sessions_retrieved,
                "messages_added": self.metrics.messages_added,
                "health_checks": self.metrics.health_checks
            },
            "error_breakdown": {
                "session_errors": self.metrics.session_errors,
                "message_errors": self.metrics.message_errors,
                "health_errors": self.metrics.health_errors,
                "connection_errors": self.metrics.connection_errors
            },
            "performance_metrics": {
                "avg_write_latency_ms": round(self.metrics.avg_write_latency_ms, 2),
                "avg_read_latency_ms": round(self.metrics.avg_read_latency_ms, 2),
                "max_write_latency_ms": round(self.metrics.max_write_latency_ms, 2),
                "max_read_latency_ms": round(self.metrics.max_read_latency_ms, 2)
            }
        }

        events.info("24-HOUR STABILITY TEST COMPLETED", report)

        # Save detailed report
        report_file = f"stability_test_report_{int(self.metrics.start_time)}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print("\n" + "="*80)
        print("🎉 24-HOUR STABILITY TEST COMPLETED")
        print("="*80)
        print(f"Duration: {report['test_summary']['duration_hours']} hours")
        print(f"Total Operations: {report['test_summary']['total_operations']:,}")
        print(f"Operations/Hour: {report['test_summary']['operations_per_hour']:,.1f}")
        print(f"Error Rate: {report['test_summary']['error_rate_percent']:.4f}%")
        print(f"Avg Write Latency: {report['performance_metrics']['avg_write_latency_ms']:.2f}ms")
        print(f"Avg Read Latency: {report['performance_metrics']['avg_read_latency_ms']:.2f}ms")
        print(f"Report saved: {report_file}")
        print("="*80)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n🛑 Received signal {signum} - shutting down stability test...")
    global stability_test
    if stability_test:
        stability_test.running = False

def main():
    """Main entry point for stability test"""
    global stability_test

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Parse duration from command line
    duration_hours = 24.0
    if len(sys.argv) > 1:
        try:
            duration_hours = float(sys.argv[1])
        except ValueError:
            print("Invalid duration specified, using 24 hours")

    # Initialize and run stability test
    stability_test = StabilityTest(duration_hours)
    stability_test.run()

if __name__ == '__main__':
    main()
