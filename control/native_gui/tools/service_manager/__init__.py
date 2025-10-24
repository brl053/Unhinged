"""
@llm-type control-system
@llm-legend __init__.py - system control component
@llm-key Core functionality for __init__
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token __init__: system control component
"""
"""
🚀 Service Manager Tool

Service lifecycle management and control.
Start, stop, restart, and monitor services.
"""

from .tool import ServiceManagerTool

__all__ = ["ServiceManagerTool"]
