"""
@llm-type module-init
@llm-legend Input Capture Tool Module - Advanced input monitoring and analysis
@llm-key Provides comprehensive keyboard and mouse capture with privacy controls
@llm-map Input capture tool module in the Unhinged tool architecture
@llm-axiom Input monitoring must respect user privacy and provide transparent controls
@llm-contract Exports InputCaptureTool class and factory function for tool system
@llm-token input_capture_module: Advanced input monitoring tool module
"""

from .tool import InputCaptureTool, create_tool

__all__ = ['InputCaptureTool', 'create_tool']
