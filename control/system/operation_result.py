"""
@llm-type model.entity
@llm-does operation result data model for system control
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


@dataclass
class OperationResult:
    """
    Standardized result for system operations
    
    @llm-future This data structure will become the return format for Unhinged OS system calls
    @llm-evolution Each field here represents metadata that future OS kernel will track
    """
    operation: str
    success: bool
    affected_services: List[str]
    system_state_change: str
    execution_time: float
    timestamp: datetime = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'operation': self.operation,
            'success': self.success,
            'affected_services': self.affected_services,
            'system_state_change': self.system_state_change,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp.isoformat(),
            'error_message': self.error_message,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_build_results(cls, operation: str, build_results: List[Any]) -> 'OperationResult':
        """
        Create OperationResult from build system results
        
        @llm-note This bridges build system results to operational semantics
        @llm-future This translation layer will be removed when we have direct OS operations
        """
        success = all(getattr(r, 'success', False) for r in build_results)
        total_time = sum(getattr(r, 'duration', 0.0) for r in build_results)
        
        # Extract service names from build results
        affected_services = []
        for result in build_results:
            if hasattr(result, 'target'):
                affected_services.append(result.target)
        
        # Determine system state change
        if success:
            state_change = f"Operation {operation} completed successfully"
        else:
            failed_targets = [r.target for r in build_results if not getattr(r, 'success', True)]
            state_change = f"Operation {operation} failed for targets: {', '.join(failed_targets)}"
        
        # Collect error messages
        error_messages = [getattr(r, 'error_message', '') for r in build_results if not getattr(r, 'success', True)]
        error_message = '; '.join(filter(None, error_messages)) if error_messages else None
        
        return cls(
            operation=operation,
            success=success,
            affected_services=affected_services,
            system_state_change=state_change,
            execution_time=total_time,
            error_message=error_message,
            metadata={
                'build_results_count': len(build_results),
                'build_system_version': '1.0',
                'future_os_compatibility': True
            }
        )


@dataclass
class SystemStatus:
    """
    Current system status snapshot
    
    @llm-future This will become the Unhinged OS system information structure
    """
    running_services: List[str]
    failed_services: List[str]
    resource_usage: Dict[str, float]
    uptime: float
    last_operation: Optional[OperationResult] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'running_services': self.running_services,
            'failed_services': self.failed_services,
            'resource_usage': self.resource_usage,
            'uptime': self.uptime,
            'last_operation': self.last_operation.to_dict() if self.last_operation else None
        }
