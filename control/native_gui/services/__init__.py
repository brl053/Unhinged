"""
@llm-type service
@llm-legend __init__.py - microservice component
@llm-key Core functionality for __init__
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token __init__: microservice component
"""
"""
🤖 Native GUI Services Module

Service integration layer for the native GUI.
Provides LLM clients and other service integrations.
"""

from .llm_client import LLMServiceClient

__all__ = ['LLMServiceClient']
