"""
@llm-type control-plane
@llm-legend System control abstraction layer that bridges build orchestration with operations semantics
@llm-key Translates DevOps operations (start/stop/restart) into build system targets while maintaining operational context
@llm-map Central control plane that will evolve into virtualization boundary between Unhinged and host OS
@llm-axiom All system operations must be auditable, reversible, and provide clear operational feedback
@llm-contract Returns OperationResult with success status, affected services, and system state changes
@llm-token system-controller: Control plane service managing the boundary between application logic and system operations
@llm-evolution This is the foundation layer for future OS virtualization - every command here represents a potential kernel operation
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
import os
from unhinged_events import create_service_logger

# Add build system to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'build'))

from .operation_result import OperationResult, SystemStatus

# Import build system components
try:
    from orchestrator import BuildOrchestrator
    from config.build_config import BuildConfig
except ImportError as e:
    # Build system import failed, using mock implementation
    BuildOrchestrator = None
    BuildConfig = None


class SystemController:
    """
    System Control Abstraction Layer
    
    Bridges operational semantics (start/stop services) with build system implementation.
    This class represents the future boundary between Unhinged applications and the OS.
    
    @llm-future Every method here is a candidate for a future Unhinged OS system call
    @llm-virtualization This class will evolve into the primary OS interface
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.events = create_service_logger("system-controller", "1.0.0")
        self.operation_log: List[OperationResult] = []
        self.start_time = time.time()
        
        # Initialize build system integration
        if BuildOrchestrator and BuildConfig:
            try:
                config_file = config_path or str(Path(__file__).parent.parent.parent / 'build' / 'config' / 'build-config.yml')
                self.build_config = BuildConfig.from_file(config_file)
                self.build_orchestrator = BuildOrchestrator(self.build_config)
                self.build_system_available = True
                pass
            except Exception as e:
                self.events.error("Build system initialization failed", exception=e)
                self.build_system_available = False
        else:
            self.build_system_available = False
            self.events.warn("Build system not available, using fallback")
        
        # Service tier mappings (operations language → build targets)
        self.tier_mappings = {
            'infrastructure': {
                'build_target': 'start-infrastructure-services',
                'services': ['database', 'zookeeper', 'kafka', 'kafka-ui'],
                'docker_command': 'docker compose up -d database zookeeper kafka kafka-ui'
            },
            'applications': {
                'build_target': 'start-applications-services', 
                'services': ['backend', 'frontend', 'cdc-service'],
                'docker_command': 'docker compose up -d backend frontend cdc-service'
            },
            'ai_services': {
                'build_target': 'start-ai-services',
                'services': ['llm', 'whisper-tts', 'vision-ai'],
                'docker_command': 'docker compose -f docker-compose.simple.yml up -d'
            }
        }
    
    async def start_service_tier(self, tier: str) -> OperationResult:
        """
        Start a logical service tier
        
        @llm-future This will become: int sys_start_tier(tier_id_t tier)
        @llm-kernel-design Service tiers are fundamental OS abstractions in Unhinged
        """
        operation_name = f"start_tier_{tier}"
        if tier not in self.tier_mappings:
            error_msg = f"Unknown service tier: {tier}. Available: {list(self.tier_mappings.keys())}"
            self.events.error(error_msg)
            result = OperationResult(
                operation=operation_name,
                success=False,
                affected_services=[],
                system_state_change=f"Failed to start tier {tier}",
                execution_time=0.0,
                error_message=error_msg
            )
            self.operation_log.append(result)
            return result
        
        tier_config = self.tier_mappings[tier]
        start_time = time.time()
        
        try:
            if self.build_system_available:
                # Use build system
                build_target = tier_config['build_target']
                build_results = await self.build_orchestrator.build_targets([build_target])
                result = OperationResult.from_build_results(operation_name, build_results)
            else:
                # Fallback to direct Docker commands
                result = await self._execute_docker_command(operation_name, tier_config)
            
            result.execution_time = time.time() - start_time
            
            self.operation_log.append(result)

            return result

        except Exception as e:
            error_msg = f"System operation failed: {str(e)}"
            self.events.error(error_msg, exception=e)
            result = OperationResult(
                operation=operation_name,
                success=False,
                affected_services=tier_config['services'],
                system_state_change=f"Failed to start tier {tier}",
                execution_time=time.time() - start_time,
                error_message=error_msg
            )
            self.operation_log.append(result)
            return result
    
    async def stop_service_tier(self, tier: str) -> OperationResult:
        """
        Stop a logical service tier
        
        @llm-future This will become: int sys_stop_tier(tier_id_t tier)
        """
        operation_name = f"stop_tier_{tier}"

        
        if tier not in self.tier_mappings:
            error_msg = f"Unknown service tier: {tier}"
            return OperationResult(
                operation=operation_name,
                success=False,
                affected_services=[],
                system_state_change=f"Failed to stop tier {tier}",
                execution_time=0.0,
                error_message=error_msg
            )
        
        tier_config = self.tier_mappings[tier]
        start_time = time.time()
        
        try:
            # For now, use Docker compose down
            docker_cmd = tier_config['docker_command'].replace('up -d', 'down')

            
            # Execute command (simplified for now)
            import subprocess
            process = await asyncio.create_subprocess_shell(
                docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            success = process.returncode == 0
            result = OperationResult(
                operation=operation_name,
                success=success,
                affected_services=tier_config['services'],
                system_state_change=f"Tier {tier} {'stopped' if success else 'stop failed'}",
                execution_time=time.time() - start_time,
                error_message=stderr.decode() if stderr else None
            )
            
            self.operation_log.append(result)
            return result
            
        except Exception as e:
            error_msg = f"Stop operation failed: {str(e)}"
            result = OperationResult(
                operation=operation_name,
                success=False,
                affected_services=tier_config['services'],
                system_state_change=f"Failed to stop tier {tier}",
                execution_time=time.time() - start_time,
                error_message=error_msg
            )
            self.operation_log.append(result)
            return result

    async def _execute_docker_command(self, operation: str, tier_config: Dict[str, Any]) -> OperationResult:
        """
        Execute Docker command as fallback when build system unavailable

        @llm-future This direct command execution will be replaced by Unhinged container management
        """
        import subprocess

        docker_cmd = tier_config['docker_command']


        try:
            process = await asyncio.create_subprocess_shell(
                docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            success = process.returncode == 0
            return OperationResult(
                operation=operation,
                success=success,
                affected_services=tier_config['services'],
                system_state_change=f"Docker command {'succeeded' if success else 'failed'}",
                execution_time=0.0,  # Will be set by caller
                error_message=stderr.decode() if stderr else None,
                metadata={
                    'execution_method': 'docker_fallback',
                    'command': docker_cmd,
                    'stdout': stdout.decode() if stdout else None
                }
            )
        except Exception as e:
            return OperationResult(
                operation=operation,
                success=False,
                affected_services=tier_config['services'],
                system_state_change="Docker command execution failed",
                execution_time=0.0,
                error_message=str(e)
            )

    async def get_system_status(self) -> SystemStatus:
        """
        Get current system status

        @llm-future This will become: sys_get_system_info()
        """
        # For now, use docker ps to check running services
        try:
            process = await asyncio.create_subprocess_shell(
                "docker compose ps --format json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            running_services = []
            failed_services = []

            if process.returncode == 0 and stdout:
                import json
                try:
                    containers = json.loads(stdout.decode())
                    if isinstance(containers, list):
                        for container in containers:
                            service = container.get('Service', 'unknown')
                            state = container.get('State', 'unknown')
                            if 'running' in state.lower():
                                running_services.append(service)
                            else:
                                failed_services.append(service)
                except json.JSONDecodeError:
                    self.events.warn("Failed to parse docker compose ps output")

            return SystemStatus(
                running_services=running_services,
                failed_services=failed_services,
                resource_usage={'cpu': 0.0, 'memory': 0.0},  # TODO: Implement
                uptime=time.time() - self.start_time,
                last_operation=self.operation_log[-1] if self.operation_log else None
            )

        except Exception as e:
            self.events.error("Failed to get system status", exception=e)
            return SystemStatus(
                running_services=[],
                failed_services=[],
                resource_usage={},
                uptime=time.time() - self.start_time
            )

    def get_operation_history(self) -> List[OperationResult]:
        """Get history of all operations for analysis"""
        return self.operation_log.copy()

    def get_operation_patterns(self) -> Dict[str, Any]:
        """
        Analyze operation patterns for future OS design insights

        @llm-purpose Collect operational patterns that inform Unhinged OS kernel design
        """
        if not self.operation_log:
            return {}

        operations_by_type = {}
        total_operations = len(self.operation_log)
        successful_operations = sum(1 for op in self.operation_log if op.success)

        for op in self.operation_log:
            op_type = op.operation.split('_')[0]  # start, stop, etc.
            if op_type not in operations_by_type:
                operations_by_type[op_type] = {'count': 0, 'success_rate': 0, 'avg_time': 0}
            operations_by_type[op_type]['count'] += 1

        # Calculate success rates and average times
        for op_type in operations_by_type:
            type_ops = [op for op in self.operation_log if op.operation.startswith(op_type)]
            successful = sum(1 for op in type_ops if op.success)
            operations_by_type[op_type]['success_rate'] = successful / len(type_ops)
            operations_by_type[op_type]['avg_time'] = sum(op.execution_time for op in type_ops) / len(type_ops)

        return {
            'total_operations': total_operations,
            'overall_success_rate': successful_operations / total_operations,
            'operations_by_type': operations_by_type,
            'most_common_operation': max(operations_by_type.keys(), key=lambda k: operations_by_type[k]['count']) if operations_by_type else None
        }

    def get_resource_insights(self) -> Dict[str, Any]:
        """Get resource usage insights for OS design"""
        return {
            'uptime': time.time() - self.start_time,
            'operations_per_minute': len(self.operation_log) / ((time.time() - self.start_time) / 60) if self.operation_log else 0,
            'average_operation_time': sum(op.execution_time for op in self.operation_log) / len(self.operation_log) if self.operation_log else 0
        }

    def get_os_design_insights(self) -> Dict[str, Any]:
        """Generate insights for future Unhinged OS design"""
        patterns = self.get_operation_patterns()
        resources = self.get_resource_insights()

        return {
            'recommended_syscalls': [
                'sys_start_tier',
                'sys_stop_tier',
                'sys_get_system_info',
                'sys_restart_service'
            ],
            'kernel_design_recommendations': {
                'service_tier_abstraction': 'Fundamental OS concept',
                'operation_logging': 'Built into kernel',
                'async_operations': 'Default execution model',
                'resource_tracking': 'Integrated monitoring'
            },
            'performance_insights': {
                'operation_frequency': patterns.get('total_operations', 0),
                'reliability_target': patterns.get('overall_success_rate', 0),
                'response_time_target': resources.get('average_operation_time', 0)
            }
        }
