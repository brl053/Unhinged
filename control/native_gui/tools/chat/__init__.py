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
💬 Chat Tool - Persistent Chat Experience

Provides a native chat interface for conversing with the LLM operating system.
Features speech-to-text input, animated chat bubbles, and real-time conversation.

Components:
    pass
- ChatTool: Main tool class for integration with Control Center
- ChatInterface: Primary chat UI widget
- SpeechInput: Microphone and text input widget
- MessageBubble: Individual chat message display
- AnimationManager: Smooth transitions and animations

Architecture:
    pass
- Pure GTK4 native widgets (no web technologies)
- gRPC integration with speech-to-text and LLM services
- Real-time conversation with loading states
- Persistent chat history and session management
"""

# Tool plugin exports
# The tool is imported dynamically by the tool manager