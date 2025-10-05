#!/usr/bin/env python3

"""
Unhinged Build System Runner

Reads build-config.yml and orchestrates docker-compose, protobuf generation,
testing, and deployment across the monorepo.

Usage:
    python scripts/build-system.py dev                    # Start development
    python scripts/build-system.py cdc                    # Start CDC system
    python scripts/build-system.py test                   # Run tests
    python scripts/build-system.py deploy --env staging   # Deploy to staging
    python scripts/build-system.py cleanup development    # Clean up dev env

Author: LLM Agent
Version: 1.0.0
Date: 2025-01-04
"""

import argparse
import subprocess
import sys
import time
import yaml
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

class BuildSystem:
    def __init__(self, config_path: str = "build-config.yml"):
        self.project_root = Path(__file__).parent.parent
        self.config_path = self.project_root / config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load build configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Config file not found: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing config file: {e}")
            sys.exit(1)
    
    def run_target(self, target_name: str, parameters: Dict[str, str] = None) -> bool:
        """Run a build target with optional parameters"""
        if target_name not in self.config.get('targets', {}):
            print(f"❌ Unknown target: {target_name}")
            return False
        
        target = self.config['targets'][target_name]
        print(f"🚀 Running target: {target_name}")
        print(f"📝 Description: {target['description']}")
        
        # Handle parameters
        if parameters:
            for key, value in parameters.items():
                print(f"📋 Parameter: {key} = {value}")
        
        # Execute steps
        for step in target['steps']:
            if not self._execute_step(step, parameters):
                print(f"❌ Target {target_name} failed")
                return False
        
        print(f"✅ Target {target_name} completed successfully")
        return True
    
    def _execute_step(self, step: Dict[str, Any], parameters: Dict[str, str] = None) -> bool:
        """Execute a single build step"""
        step_name = step.get('name', 'Unnamed step')
        print(f"\n🔧 Executing: {step_name}")
        
        # Check conditions
        if 'condition' in step:
            if not self._check_condition(step['condition']):
                print(f"⏭️  Skipping step (condition not met): {step['condition']}")
                return True
        
        # Handle different step types
        if 'command' in step:
            return self._run_command(step['command'], parameters)
        elif 'target' in step:
            return self.run_target(step['target'], parameters)
        else:
            print(f"⚠️  Unknown step type: {step}")
            return True
    
    def _run_command(self, command: str, parameters: Dict[str, str] = None) -> bool:
        """Run a shell command"""
        # Substitute parameters
        if parameters:
            for key, value in parameters.items():
                command = command.replace(f"${{{key}}}", value)
                command = command.replace(f"${key}", value)
        
        print(f"💻 Command: {command}")
        
        try:
            # Change to project root
            os.chdir(self.project_root)
            
            # Run command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.stdout:
                print(f"📤 Output: {result.stdout.strip()}")
            
            if result.stderr and result.returncode != 0:
                print(f"📥 Error: {result.stderr.strip()}")
            
            if result.returncode == 0:
                print(f"✅ Command succeeded")
                return True
            else:
                print(f"❌ Command failed with exit code {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Command timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"❌ Command execution error: {e}")
            return False
    
    def _check_condition(self, condition: str) -> bool:
        """Check if a condition is met"""
        # Simple condition checking - can be expanded
        if condition == "proto files changed":
            # Check if proto files are newer than generated files
            proto_dir = self.project_root / "proto"
            if not proto_dir.exists():
                return True
            
            proto_files = list(proto_dir.glob("*.proto"))
            if not proto_files:
                return False
            
            # Check if any generated files exist
            frontend_proto = self.project_root / "frontend" / "src" / "types" / "proto"
            if not frontend_proto.exists():
                return True
            
            # Simple timestamp check
            latest_proto = max(f.stat().st_mtime for f in proto_files)
            generated_files = list(frontend_proto.glob("*.ts"))
            if not generated_files:
                return True
            
            latest_generated = max(f.stat().st_mtime for f in generated_files)
            return latest_proto > latest_generated
        
        elif condition == "kafka is ready":
            return self._wait_for_service("kafka://localhost:9092")
        
        # Default: condition is met
        return True
    
    def _wait_for_service(self, service_url: str, timeout: int = 60) -> bool:
        """Wait for a service to be ready"""
        print(f"⏳ Waiting for service: {service_url}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if service_url.startswith("postgres://"):
                    # Check PostgreSQL
                    result = subprocess.run(
                        ["pg_isready", "-h", "localhost", "-p", "5432", "-U", "postgres"],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return True
                
                elif service_url.startswith("kafka://"):
                    # Check Kafka
                    result = subprocess.run(
                        ["kafka-topics", "--bootstrap-server", "localhost:9092", "--list"],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return True
                
                elif service_url.startswith("http://"):
                    # Check HTTP service
                    result = subprocess.run(
                        ["curl", "-f", "-s", service_url],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return True
                
            except subprocess.TimeoutExpired:
                pass
            except Exception:
                pass
            
            time.sleep(2)
        
        print(f"⏰ Service not ready after {timeout} seconds: {service_url}")
        return False
    
    def run_workflow(self, workflow_name: str, parameters: Dict[str, str] = None) -> bool:
        """Run a complete workflow"""
        if workflow_name not in self.config.get('workflows', {}):
            print(f"❌ Unknown workflow: {workflow_name}")
            return False
        
        workflow = self.config['workflows'][workflow_name]
        print(f"🔄 Running workflow: {workflow_name}")
        print(f"📝 Description: {workflow['description']}")
        
        for step in workflow['steps']:
            if not self._execute_step(step, parameters):
                print(f"❌ Workflow {workflow_name} failed")
                return False
        
        print(f"✅ Workflow {workflow_name} completed successfully")
        return True
    
    def list_targets(self):
        """List all available targets"""
        print("📋 Available targets:")
        for name, target in self.config.get('targets', {}).items():
            print(f"  • {name}: {target['description']}")
    
    def list_workflows(self):
        """List all available workflows"""
        print("🔄 Available workflows:")
        for name, workflow in self.config.get('workflows', {}).items():
            print(f"  • {name}: {workflow['description']}")

def main():
    parser = argparse.ArgumentParser(description="Unhinged Build System")
    parser.add_argument('action', nargs='?', help='Target, workflow, or action to run')
    parser.add_argument('--env', '--environment', help='Environment parameter')
    parser.add_argument('--list-targets', action='store_true', help='List available targets')
    parser.add_argument('--list-workflows', action='store_true', help='List available workflows')
    parser.add_argument('--config', default='build-config.yml', help='Config file path')

    args = parser.parse_args()

    build_system = BuildSystem(args.config)

    if args.list_targets:
        build_system.list_targets()
        return

    if args.list_workflows:
        build_system.list_workflows()
        return

    if not args.action:
        print("❌ No action specified")
        print("\nAvailable targets:")
        build_system.list_targets()
        print("\nAvailable workflows:")
        build_system.list_workflows()
        return
    
    # Prepare parameters
    parameters = {}
    if args.env:
        parameters['environment'] = args.env
    
    # Check if it's a workflow first, then target
    if args.action in build_system.config.get('workflows', {}):
        success = build_system.run_workflow(args.action, parameters)
    elif args.action in build_system.config.get('targets', {}):
        success = build_system.run_target(args.action, parameters)
    else:
        print(f"❌ Unknown action: {args.action}")
        print("\nAvailable targets:")
        build_system.list_targets()
        print("\nAvailable workflows:")
        build_system.list_workflows()
        sys.exit(1)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
