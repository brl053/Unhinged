#!/usr/bin/env python3

"""
Service Health Monitor with Auto-Recovery

Monitors the health of all 4 core services and automatically restarts
failed containers to ensure the voice/AI pipeline is fully operational.
"""

import json
import logging
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ServiceConfig:
    """Configuration for a monitored service"""
    name: str
    container_name: str
    health_url: Optional[str]
    health_port: int
    compose_service: str
    compose_file: str
    timeout: int = 10
    critical: bool = True


class ServiceHealthMonitor:
    """Monitors and auto-recovers failed services"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logging.getLogger(__name__)
        self.services = self._load_service_configs()
        
    def _load_service_configs(self) -> Dict[str, ServiceConfig]:
        """Load service configurations"""
        return {
            'llm': ServiceConfig(
                name='LLM Service (Ollama)',
                container_name='ollama-service',
                health_url='http://localhost:1500/api/tags',
                health_port=1500,
                compose_service='llm',
                compose_file='orchestration/docker-compose.production.yml',
                timeout=15,
                critical=True
            ),
            'persistence': ServiceConfig(
                name='Persistence Platform',
                container_name='persistence-platform-service',
                health_url='http://localhost:1300/api/v1/health',
                health_port=1300,
                compose_service='persistence-platform',
                compose_file='orchestration/docker-compose.production.yml',
                timeout=10,
                critical=True
            ),
            'database': ServiceConfig(
                name='Database',
                container_name='unhinged-postgres',
                health_url=None,  # TCP port check only
                health_port=1200,
                compose_service='database',
                compose_file='orchestration/docker-compose.production.yml',
                timeout=5,
                critical=True
            ),
            'speech-to-text': ServiceConfig(
                name='Speech-to-Text Service',
                container_name='speech-to-text-service',
                health_url=None,  # gRPC service, use TCP port check
                health_port=1191,  # gRPC port
                compose_service='speech-to-text',
                compose_file='orchestration/docker-compose.production.yml',
                timeout=10,
                critical=True
            )
        }
    
    def check_service_health(self, service_id: str) -> Tuple[bool, str]:
        """Check health of a specific service"""
        if service_id not in self.services:
            return False, f"Unknown service: {service_id}"
        
        service = self.services[service_id]
        
        # First check if container is running
        container_running = self._is_container_running(service.container_name)
        if not container_running:
            return False, f"Container {service.container_name} is not running"
        
        # Check health endpoint if available
        if service.health_url:
            try:
                response = requests.get(service.health_url, timeout=service.timeout)
                if response.status_code == 200:
                    return True, "Service healthy"
                else:
                    return False, f"Health check failed: HTTP {response.status_code}"
            except requests.exceptions.RequestException as e:
                return False, f"Health check failed: {e}"
        else:
            # TCP port check for services without HTTP health endpoints
            return self._check_tcp_port(service.health_port), "Port check"
    
    def _is_container_running(self, container_name: str) -> bool:
        """Check if Docker container is running"""
        try:
            result = subprocess.run([
                'docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Names}}'
            ], capture_output=True, text=True, timeout=10)
            
            return container_name in result.stdout
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Timeout checking container {container_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error checking container {container_name}: {e}")
            return False
    
    def _check_tcp_port(self, port: int) -> bool:
        """Check if TCP port is listening"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def restart_service(self, service_id: str) -> Tuple[bool, str]:
        """Restart a failed service"""
        if service_id not in self.services:
            return False, f"Unknown service: {service_id}"
        
        service = self.services[service_id]
        compose_file = self.project_root / service.compose_file
        
        if not compose_file.exists():
            return False, f"Compose file not found: {compose_file}"
        
        try:
            self.logger.info(f"🔄 Restarting service: {service.name}")
            
            # Stop the service
            stop_result = subprocess.run([
                'docker', 'compose', '-f', str(compose_file), 'stop', service.compose_service
            ], capture_output=True, text=True, timeout=30)
            
            if stop_result.returncode != 0:
                self.logger.warning(f"Stop command had issues: {stop_result.stderr}")
            
            # Remove the container
            rm_result = subprocess.run([
                'docker', 'compose', '-f', str(compose_file), 'rm', '-f', service.compose_service
            ], capture_output=True, text=True, timeout=30)
            
            if rm_result.returncode != 0:
                self.logger.warning(f"Remove command had issues: {rm_result.stderr}")
            
            # Start the service
            start_result = subprocess.run([
                'docker', 'compose', '-f', str(compose_file), 'up', '-d', service.compose_service
            ], capture_output=True, text=True, timeout=120)
            
            if start_result.returncode != 0:
                return False, f"Failed to start service: {start_result.stderr}"
            
            # Wait for service to be ready
            self.logger.info(f"⏳ Waiting for {service.name} to be ready...")
            for attempt in range(12):  # 60 seconds total
                time.sleep(5)
                healthy, status = self.check_service_health(service_id)
                if healthy:
                    self.logger.info(f"✅ {service.name} is now healthy")
                    return True, f"Service restarted successfully"
                self.logger.info(f"🔄 Attempt {attempt + 1}/12: {status}")
            
            return False, f"Service started but failed health checks after 60 seconds"
            
        except subprocess.TimeoutExpired:
            return False, f"Timeout while restarting service"
        except Exception as e:
            return False, f"Error restarting service: {e}"
    
    def monitor_and_recover_all(self) -> Dict[str, Dict]:
        """Monitor all services and auto-recover failed ones"""
        results = {}
        
        self.logger.info("🏥 Starting comprehensive service health check...")
        
        for service_id, service in self.services.items():
            self.logger.info(f"🔍 Checking {service.name}...")
            
            healthy, status = self.check_service_health(service_id)
            
            if healthy:
                self.logger.info(f"🟢 {service.name}: Healthy")
                results[service_id] = {
                    'status': 'healthy',
                    'message': status,
                    'action': 'none'
                }
            else:
                self.logger.warning(f"🔴 {service.name}: {status}")
                
                if service.critical:
                    self.logger.info(f"🔄 Attempting auto-recovery for {service.name}...")
                    success, message = self.restart_service(service_id)
                    
                    if success:
                        self.logger.info(f"✅ {service.name}: Auto-recovery successful")
                        results[service_id] = {
                            'status': 'recovered',
                            'message': message,
                            'action': 'restarted'
                        }
                    else:
                        self.logger.error(f"❌ {service.name}: Auto-recovery failed - {message}")
                        results[service_id] = {
                            'status': 'failed',
                            'message': message,
                            'action': 'restart_failed'
                        }
                else:
                    results[service_id] = {
                        'status': 'unhealthy',
                        'message': status,
                        'action': 'skipped_non_critical'
                    }
        
        return results
    
    def get_service_status_summary(self) -> Dict:
        """Get current status of all services without recovery"""
        summary = {
            'healthy': [],
            'unhealthy': [],
            'total': len(self.services),
            'critical_healthy': 0,
            'critical_total': 0
        }
        
        for service_id, service in self.services.items():
            healthy, status = self.check_service_health(service_id)
            
            service_info = {
                'id': service_id,
                'name': service.name,
                'status': status,
                'critical': service.critical
            }
            
            if healthy:
                summary['healthy'].append(service_info)
                if service.critical:
                    summary['critical_healthy'] += 1
            else:
                summary['unhealthy'].append(service_info)
            
            if service.critical:
                summary['critical_total'] += 1
        
        summary['health_percentage'] = (len(summary['healthy']) / summary['total']) * 100
        summary['critical_health_percentage'] = (summary['critical_healthy'] / summary['critical_total']) * 100 if summary['critical_total'] > 0 else 0
        
        return summary


def main():
    """CLI interface for service health monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Service Health Monitor with Auto-Recovery')
    parser.add_argument('--status', action='store_true', help='Show service status only')
    parser.add_argument('--recover', action='store_true', help='Monitor and auto-recover failed services')
    parser.add_argument('--service', help='Check specific service only')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    monitor = ServiceHealthMonitor(Path('.'))
    
    if args.service:
        healthy, status = monitor.check_service_health(args.service)
        print(f"{'🟢' if healthy else '🔴'} {args.service}: {status}")
        return 0 if healthy else 1
    
    elif args.status:
        summary = monitor.get_service_status_summary()
        print(f"\n🏥 SERVICE HEALTH SUMMARY")
        print(f"Overall Health: {summary['health_percentage']:.1f}% ({len(summary['healthy'])}/{summary['total']})")
        print(f"Critical Services: {summary['critical_health_percentage']:.1f}% ({summary['critical_healthy']}/{summary['critical_total']})")
        
        print(f"\n🟢 HEALTHY SERVICES:")
        for service in summary['healthy']:
            print(f"  • {service['name']}")
        
        if summary['unhealthy']:
            print(f"\n🔴 UNHEALTHY SERVICES:")
            for service in summary['unhealthy']:
                print(f"  • {service['name']}: {service['status']}")
        
        return 0 if summary['critical_health_percentage'] == 100 else 1
    
    elif args.recover:
        results = monitor.monitor_and_recover_all()
        
        print(f"\n🏥 AUTO-RECOVERY RESULTS:")
        for service_id, result in results.items():
            service_name = monitor.services[service_id].name
            status_icon = {
                'healthy': '🟢',
                'recovered': '✅', 
                'failed': '❌',
                'unhealthy': '🔴'
            }.get(result['status'], '🔵')
            
            print(f"{status_icon} {service_name}: {result['message']}")
        
        # Return success if all critical services are healthy or recovered
        critical_ok = all(
            results[sid]['status'] in ['healthy', 'recovered'] 
            for sid, service in monitor.services.items() 
            if service.critical
        )
        return 0 if critical_ok else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    exit(main())
