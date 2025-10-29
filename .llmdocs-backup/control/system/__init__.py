"""
Unhinged Control System

@llm-type control-plane-package
@llm-legend System control abstraction layer package for Unhinged platform
@llm-key Provides operational abstractions over build system while preparing for future OS virtualization
@llm-map Central control plane that bridges DevOps operations with build orchestration
@llm-axiom All system operations must be auditable, reversible, and provide clear operational feedback
@llm-token control-system: Package containing system control abstractions and virtualization boundary interfaces
"""

from .system_controller import SystemController
from .operation_result import OperationResult

__all__ = ['SystemController', 'OperationResult']
__version__ = '0.1.0-alpha'
