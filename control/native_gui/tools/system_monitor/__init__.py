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
🏥 System Health Monitor Tool

Real-time system monitoring and health metrics.
Displays CPU, memory, disk, and service status.
"""

from .tool import SystemMonitorTool

__all__ = ["SystemMonitorTool"]
