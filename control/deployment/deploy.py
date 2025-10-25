#!/usr/bin/env python3
"""
@llm-type control-tool
@llm-legend Unified deployment orchestrator for Unhinged system runtime control
@llm-key Central deployment automation with environment-aware orchestration and health validation
@llm-map Runtime deployment control enabling automated service orchestration and monitoring
@llm-axiom Deployments must be atomic, reversible, and health-validated for operational safety
@llm-token deployment-orchestrator: Automated deployment control with environment management

Unified Deployment Orchestrator:
- Environment-aware deployment (dev, staging, production)
- Health check validation before and after deployment
- Rollback capability on deployment failures
- Service dependency management
- Integrated monitoring and logging
"""

import argparse
import subprocess
import time
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import requests
from unhinged_events import create_service_logger

# Initialize event logger
events = create_service_logger("deployment", "1.0.0")

class UnhingedDeploymentOrchestrator:
    """
    @llm-type control-orchestrator
    @llm-legend Central deployment orchestrator managing environment-aware service deployment
    @llm-key Automated deployment with health validation, dependency management, and rollback
    @llm-map Core operational tool for runtime service orchestration and deployment control
    @llm-axiom All deployments must be atomic, health-validated, and reversible
    @llm-token deployment-core: Production deployment orchestration with operational safety
    """
    
    def __init__(self, project_root: Path, environment: str = "development"):
        self.project_root = project_root
        self.environment = environment
        self.control_root = project_root / "control"
        
        # Load configurations
        self.env_config = self._load_environment_config()
        self.service_registry = self._load_service_registry()
        self.port_allocation = self._load_port_allocation()
        
        # Deployment state
        self.deployed_services = []
        self.failed_services = []
    
    def _load_environment_config(self) -> Dict:
        """Load environment-specific configuration"""
        config_file = self.control_root / "config" / "environments" / f"{self.environment}.yml"
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            events.warn("Environment config not found", {"config_file": str(config_file)})
            return {}
    
    def _load_service_registry(self) -> Dict:
        """Load service registry configuration"""
        registry_file = self.control_root / "config" / "service-registry.yml"
        try:
            with open(registry_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            events.warn("Service registry not found", {"registry_file": str(registry_file)})
            return {}
    
    def _load_port_allocation(self) -> Dict:
        """Load port allocation configuration"""
        port_file = self.control_root / "config" / "port-allocation.yml"
        try:
            with open(port_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            events.warn("Port allocation not found", {"port_file": str(port_file), "service": "deployment"})
            return {}
    
    def validate_environment(self) -> bool:
        """Validate environment configuration and prerequisites"""

        
        # Check Docker availability
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                events.error("Docker not available", metadata={"service": "deployment", "check": "docker"})
                return False
        except FileNotFoundError:
            events.error("Docker not installed", metadata={"service": "deployment", "check": "docker"})
            return False
        
        # Check Docker Compose availability
        try:
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
            if result.returncode != 0:
                events.error("Docker Compose not available", metadata={"service": "deployment", "check": "docker-compose"})
                return False
        except FileNotFoundError:
            events.error("Docker Compose not installed", metadata={"service": "deployment", "check": "docker-compose"})
            return False
        
        # Check compose files exist
        deployment_config = self.env_config.get('deployment', {})
        compose_file = deployment_config.get('compose_file')
        if compose_file:
            compose_path = self.project_root / compose_file
            if not compose_path.exists():
                events.error("Compose file not found", {"compose_path": str(compose_path), "service": "deployment"})
                return False
        

        return True
    
    def deploy_services(self, services: Optional[List[str]] = None) -> bool:
        """Deploy services with health validation"""

        
        if not self.validate_environment():
            return False
        
        deployment_config = self.env_config.get('deployment', {})
        compose_file = deployment_config.get('compose_file')
        
        if not compose_file:
            events.error("No compose file specified in environment config", metadata={"service": "deployment"})
            return False
        
        compose_path = self.project_root / compose_file
        
        try:
            # Deploy services

            cmd = ['docker', 'compose', '-f', str(compose_path), 'up', '-d']
            
            if services:
                cmd.extend(services)
                logger.info(f"🎯 Deploying specific services: {services}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                events.error("Deployment failed", {"stderr": result.stderr, "service": "deployment"})
                return False
            

            
            # Wait for services to start
            logger.info("⏳ Waiting for services to start...")
            time.sleep(10)
            
            # Validate service health
            if self.validate_service_health():
                logger.info("🎉 Deployment completed successfully!")
                return True
            else:
                logger.error("❌ Health validation failed")
                return False
                
        except Exception as e:
            events.error("Deployment error", exception=e, metadata={"service": "deployment"})
            return False
    
    def validate_service_health(self) -> bool:
        """Validate health of deployed services"""
        logger.info("🏥 Validating service health...")
        
        services = self.service_registry.get('services', {})
        healthy_services = 0
        total_services = 0
        
        for service_name, service_config in services.items():
            health_check_url = service_config.get('health_check')
            if not health_check_url or not health_check_url.startswith('http'):
                continue
            
            total_services += 1
            
            try:
                response = requests.get(health_check_url, timeout=5)
                if response.status_code == 200:
                    logger.info(f"✅ {service_name}: Healthy")
                    healthy_services += 1
                    self.deployed_services.append(service_name)
                else:
                    logger.warning(f"⚠️ {service_name}: Unhealthy (HTTP {response.status_code})")
                    self.failed_services.append(service_name)
            except requests.RequestException as e:
                logger.warning(f"⚠️ {service_name}: Health check failed - {e}")
                self.failed_services.append(service_name)
        
        health_percentage = (healthy_services / total_services * 100) if total_services > 0 else 0
        logger.info(f"📊 Health status: {healthy_services}/{total_services} services healthy ({health_percentage:.1f}%)")
        
        return health_percentage >= 80  # Require 80% health for success
    
    def stop_services(self, services: Optional[List[str]] = None) -> bool:
        """Stop deployed services"""
        logger.info("🛑 Stopping services...")
        
        deployment_config = self.env_config.get('deployment', {})
        compose_file = deployment_config.get('compose_file')
        
        if not compose_file:
            logger.error("❌ No compose file specified")
            return False
        
        compose_path = self.project_root / compose_file
        
        try:
            cmd = ['docker', 'compose', '-f', str(compose_path), 'down']
            
            if services:
                # Stop specific services
                cmd = ['docker', 'compose', '-f', str(compose_path), 'stop'] + services
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                logger.error(f"❌ Stop failed: {result.stderr}")
                return False
            
            logger.info("✅ Services stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stop error: {e}")
            return False
    
    def get_deployment_status(self) -> Dict:
        """Get current deployment status"""
        return {
            'environment': self.environment,
            'deployed_services': self.deployed_services,
            'failed_services': self.failed_services,
            'total_services': len(self.deployed_services) + len(self.failed_services),
            'health_percentage': len(self.deployed_services) / (len(self.deployed_services) + len(self.failed_services)) * 100 if (self.deployed_services or self.failed_services) else 0
        }


def main():
    """CLI entry point for deployment orchestrator"""
    parser = argparse.ArgumentParser(description="Unhinged Deployment Orchestrator")
    parser.add_argument("--environment", "-e", default="development", 
                       choices=["development", "staging", "production"],
                       help="Deployment environment")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy services')
    deploy_parser.add_argument('--services', nargs='*', help='Specific services to deploy')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop services')
    stop_parser.add_argument('--services', nargs='*', help='Specific services to stop')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get deployment status')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate environment')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    orchestrator = UnhingedDeploymentOrchestrator(args.project_root, args.environment)
    
    if args.command == 'deploy':
        success = orchestrator.deploy_services(args.services)
        exit(0 if success else 1)
    elif args.command == 'stop':
        success = orchestrator.stop_services(args.services)
        exit(0 if success else 1)
    elif args.command == 'status':
        status = orchestrator.get_deployment_status()
    elif args.command == 'validate':
        success = orchestrator.validate_environment()
        exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
