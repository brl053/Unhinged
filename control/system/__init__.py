"""
@llm-type misc.control-plane-package
@llm-does system control abstraction layer package for unhinged
@llm-rule all system operations must be auditable, reversible, and provide clear operat...
"""

from .system_controller import SystemController
from .operation_result import OperationResult

__all__ = ['SystemController', 'OperationResult']
__version__ = '0.1.0-alpha'
