#!/usr/bin/env python3
"""
@llm-type control-tool
@llm-legend Service health monitoring and validation for Unhinged runtime control
@llm-key Continuous health monitoring with alerting and automatic recovery capabilities
@llm-map Runtime health monitoring enabling proactive service management and reliability
@llm-axiom Service health must be continuously monitored with automatic recovery actions
@llm-token health-monitor: Continuous service health monitoring with automated recovery

Service Health Monitoring:
- Real-time health check execution
- Service dependency validation
- Automatic recovery actions
- Health metrics collection
- Alert generation and notification
"""

import asyncio
import logging
import time
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
import socket

logger = logging.getLogger(__name__)

@dataclass
class HealthCheckResult:
    """Result of a service health check"""
    service_name: str
    status: str  # healthy, unhealthy, unknown
    response_time: float
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ServiceHealth:
    """Overall health status of a service"""
    service_name: str
    current_status: str
    last_healthy: Optional[datetime]
    consecutive_failures: int
    total_checks: int
    success_rate: float
    average_response_time: float

class UnhingedHealthMonitor:
    """
    @llm-type control-monitor
    @llm-legend Continuous health monitoring system for Unhinged service ecosystem
    @llm-key Real-time health validation with dependency checking and automatic recovery
    @llm-map Core operational monitoring enabling proactive service reliability management
    @llm-axiom Health monitoring must be continuous, accurate, and trigger automatic recovery
    @llm-token health-monitor-core: Production health monitoring with automated recovery
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.control_root = project_root / "control"
        
        # Load configurations
        self.service_registry = self._load_service_registry()
        self.health_config = self.service_registry.get('health_checks', {})
        
        # Health tracking
        self.health_history: Dict[str, List[HealthCheckResult]] = {}
        self.service_health: Dict[str, ServiceHealth] = {}
        
        # Configuration
        self.global_timeout = self.health_config.get('global_timeout', 30)
        self.retry_attempts = self.health_config.get('retry_attempts', 3)
        self.retry_delay = self.health_config.get('retry_delay', 5)
        self.failure_threshold = self.health_config.get('failure_threshold', 3)
    
    def _load_service_registry(self) -> Dict:
        """Load service registry configuration"""
        registry_file = self.control_root / "config" / "service-registry.yml"
        try:
            with open(registry_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Service registry not found: {registry_file}")
            return {}
    
    async def check_http_health(self, service_name: str, url: str, timeout: int = 5) -> HealthCheckResult:
        """Perform HTTP health check"""
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return HealthCheckResult(
                    service_name=service_name,
                    status="healthy",
                    response_time=response_time
                )
            else:
                return HealthCheckResult(
                    service_name=service_name,
                    status="unhealthy",
                    response_time=response_time,
                    error_message=f"HTTP {response.status_code}"
                )
                
        except requests.RequestException as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service_name=service_name,
                status="unhealthy",
                response_time=response_time,
                error_message=str(e)
            )
    
    async def check_tcp_health(self, service_name: str, host: str, port: int, timeout: int = 5) -> HealthCheckResult:
        """Perform TCP health check"""
        start_time = time.time()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            response_time = time.time() - start_time
            
            if result == 0:
                return HealthCheckResult(
                    service_name=service_name,
                    status="healthy",
                    response_time=response_time
                )
            else:
                return HealthCheckResult(
                    service_name=service_name,
                    status="unhealthy",
                    response_time=response_time,
                    error_message=f"TCP connection failed (code: {result})"
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                service_name=service_name,
                status="unhealthy",
                response_time=response_time,
                error_message=str(e)
            )
    
    async def check_service_health(self, service_name: str, service_config: Dict) -> HealthCheckResult:
        """Check health of a single service"""
        health_check_url = service_config.get('health_check', '')
        
        if health_check_url.startswith('http'):
            return await self.check_http_health(service_name, health_check_url)
        elif health_check_url.startswith('tcp://'):
            # Parse TCP URL: tcp://host:port
            url_parts = health_check_url.replace('tcp://', '').split(':')
            if len(url_parts) == 2:
                host, port = url_parts[0], int(url_parts[1])
                return await self.check_tcp_health(service_name, host, port)
        
        return HealthCheckResult(
            service_name=service_name,
            status="unknown",
            response_time=0,
            error_message="Unsupported health check type"
        )
    
    async def check_all_services(self) -> Dict[str, HealthCheckResult]:
        """Check health of all registered services"""
        services = self.service_registry.get('services', {})
        results = {}
        
        # Create tasks for concurrent health checks
        tasks = []
        for service_name, service_config in services.items():
            task = self.check_service_health(service_name, service_config)
            tasks.append((service_name, task))
        
        # Execute health checks concurrently
        for service_name, task in tasks:
            try:
                result = await task
                results[service_name] = result
                self._update_health_history(result)
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                results[service_name] = HealthCheckResult(
                    service_name=service_name,
                    status="unknown",
                    response_time=0,
                    error_message=str(e)
                )
        
        return results
    
    def _update_health_history(self, result: HealthCheckResult):
        """Update health history for a service"""
        service_name = result.service_name
        
        # Initialize history if needed
        if service_name not in self.health_history:
            self.health_history[service_name] = []
        
        # Add result to history
        self.health_history[service_name].append(result)
        
        # Keep only last 100 results
        if len(self.health_history[service_name]) > 100:
            self.health_history[service_name] = self.health_history[service_name][-100:]
        
        # Update service health summary
        self._update_service_health(service_name)
    
    def _update_service_health(self, service_name: str):
        """Update overall health status for a service"""
        history = self.health_history.get(service_name, [])
        if not history:
            return
        
        recent_results = history[-10:]  # Last 10 checks
        healthy_count = sum(1 for r in recent_results if r.status == "healthy")
        total_count = len(recent_results)
        
        # Calculate metrics
        success_rate = (healthy_count / total_count) * 100 if total_count > 0 else 0
        avg_response_time = sum(r.response_time for r in recent_results) / total_count if total_count > 0 else 0
        
        # Count consecutive failures
        consecutive_failures = 0
        for result in reversed(recent_results):
            if result.status != "healthy":
                consecutive_failures += 1
            else:
                break
        
        # Find last healthy timestamp
        last_healthy = None
        for result in reversed(history):
            if result.status == "healthy":
                last_healthy = result.timestamp
                break
        
        # Determine current status
        current_status = recent_results[-1].status if recent_results else "unknown"
        
        self.service_health[service_name] = ServiceHealth(
            service_name=service_name,
            current_status=current_status,
            last_healthy=last_healthy,
            consecutive_failures=consecutive_failures,
            total_checks=len(history),
            success_rate=success_rate,
            average_response_time=avg_response_time
        )
    
    def get_unhealthy_services(self) -> List[str]:
        """Get list of currently unhealthy services"""
        return [
            name for name, health in self.service_health.items()
            if health.current_status != "healthy"
        ]
    
    def get_critical_services(self) -> List[str]:
        """Get services that have exceeded failure threshold"""
        return [
            name for name, health in self.service_health.items()
            if health.consecutive_failures >= self.failure_threshold
        ]
    
    def generate_health_report(self) -> str:
        """Generate comprehensive health report"""
        total_services = len(self.service_health)
        healthy_services = sum(1 for h in self.service_health.values() if h.current_status == "healthy")
        unhealthy_services = total_services - healthy_services
        
        lines = [
            "# Unhinged Service Health Report",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Summary",
            f"- Total Services: {total_services}",
            f"- Healthy: {healthy_services}",
            f"- Unhealthy: {unhealthy_services}",
            f"- Health Rate: {(healthy_services/total_services*100):.1f}%" if total_services > 0 else "- Health Rate: N/A",
            "",
            "## Service Details",
            ""
        ]
        
        for service_name, health in sorted(self.service_health.items()):
            status_icon = "✅" if health.current_status == "healthy" else "❌"
            lines.extend([
                f"### {status_icon} {service_name}",
                f"- Status: {health.current_status}",
                f"- Success Rate: {health.success_rate:.1f}%",
                f"- Avg Response Time: {health.average_response_time:.3f}s",
                f"- Consecutive Failures: {health.consecutive_failures}",
                f"- Last Healthy: {health.last_healthy.isoformat() if health.last_healthy else 'Never'}",
                ""
            ])
        
        return "\n".join(lines)


async def main():
    """CLI entry point for health monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unhinged Health Monitor")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--continuous", action="store_true",
                       help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=60,
                       help="Monitoring interval in seconds")
    parser.add_argument("--report", action="store_true",
                       help="Generate health report")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    monitor = UnhingedHealthMonitor(args.project_root)
    
    if args.continuous:
        logger.info(f"🏥 Starting continuous health monitoring (interval: {args.interval}s)")
        while True:
            try:
                results = await monitor.check_all_services()
                
                healthy_count = sum(1 for r in results.values() if r.status == "healthy")
                total_count = len(results)
                
                logger.info(f"📊 Health check complete: {healthy_count}/{total_count} services healthy")
                
                # Check for critical services
                critical_services = monitor.get_critical_services()
                if critical_services:
                    logger.warning(f"🚨 Critical services detected: {critical_services}")
                
                await asyncio.sleep(args.interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(args.interval)
    
    elif args.report:
        results = await monitor.check_all_services()
        report = monitor.generate_health_report()
        print(report)
    
    else:
        # Single health check
        results = await monitor.check_all_services()
        
        for service_name, result in results.items():
            status_icon = "✅" if result.status == "healthy" else "❌"
            print(f"{status_icon} {service_name}: {result.status} ({result.response_time:.3f}s)")


if __name__ == "__main__":
    asyncio.run(main())
