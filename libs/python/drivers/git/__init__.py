"""
@llm-type driver.git
@llm-does Git driver for repository operations and quality gate enforcement

Git driver encapsulates all Git-specific operations including:
- Pre-commit hook management
- Quality gate enforcement
- Repository state inspection
- Commit operations with validation
"""

from .hooks import GitHookManager
from .quality_gates import QualityGateEnforcer

__all__ = ["GitHookManager", "QualityGateEnforcer"]
