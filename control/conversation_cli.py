#!/usr/bin/env python3

"""
@llm-type service.api
@llm-does conversation-based cli interface for unhinged dual-system...
@llm-rule voice-first interaction must be immediate, natural, and work seamlessly acros...
"""

import asyncio
import json
import sys
import time
import subprocess
import signal
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Add event framework to path
sys.path.append(str(Path(__file__).parent.parent / "libs" / "event-framework" / "python" / "src"))

try:
    from events import create_gui_session_logger, GUIOutputCapture
    SESSION_LOGGING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Session logging not available: {e}")
    SESSION_LOGGING_AVAILABLE = False

class ConversationMode(Enum):
    """Conversation interface modes"""
    VOICE_FIRST = "voice_first"
    TEXT_ONLY = "text_only"
    HYBRID = "hybrid"

class SystemContext(Enum):
    """System context for dual-system architecture"""
    GTK4_CONTROL_PLANE = "gtk4_control_plane"
    ALPINE_NATIVE = "alpine_native"
    UNKNOWN = "unknown"

@dataclass
class ConversationConfig:
    """Configuration for conversation interface"""
    mode: ConversationMode = ConversationMode.VOICE_FIRST
    system_context: SystemContext = SystemContext.UNKNOWN
    voice_service_port: int = 1101
    session_logging: bool = True
    auto_voice_detection: bool = True
    conversation_timeout: float = 30.0
    max_conversation_length: int = 1000

class ConversationCLI:
    """Voice-first conversation interface for dual-system architecture"""
    
    def __init__(self, config: ConversationConfig):
        self.config = config
        self.project_root = Path(__file__).parent.parent
        self.session_logger = None
        self.is_running = False
        self.conversation_history = []
        
        # Initialize session logging
        if SESSION_LOGGING_AVAILABLE and config.session_logging:
            try:
                self.session_logger = create_gui_session_logger(self.project_root)
                self.session_logger.log_gui_event(
                    "CONVERSATION_CLI_INIT",
                    f"Conversation CLI initialized in {config.system_context.value} mode"
                )
            except Exception as e:
                print(f"⚠️ Session logging initialization failed: {e}")
        
        # Detect system context if unknown
        if self.config.system_context == SystemContext.UNKNOWN:
            self.config.system_context = self._detect_system_context()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _detect_system_context(self) -> SystemContext:
        """Detect whether running in GTK4 control plane or Alpine native environment"""
        try:
            # Check for GTK4 environment
            result = subprocess.run(["python3", "-c", "import gi; gi.require_version('Gtk', '4.0')"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return SystemContext.GTK4_CONTROL_PLANE
            
            # Check for Alpine environment
            if Path("/etc/alpine-release").exists():
                return SystemContext.ALPINE_NATIVE
                
        except Exception:
            pass
        
        return SystemContext.UNKNOWN
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🔄 Received signal {signum}, shutting down conversation interface...")
        self.shutdown()
        sys.exit(0)
    
    async def start_conversation(self):
        """Start the conversation interface"""
        self.is_running = True
        
        print("🎙️ Unhinged Conversation Interface")
        print("=" * 40)
        print(f"📍 System Context: {self.config.system_context.value}")
        print(f"🗣️ Mode: {self.config.mode.value}")
        print(f"🔊 Voice Service: localhost:{self.config.voice_service_port}")
        print("=" * 40)
        print("💬 Say 'exit' or 'quit' to end conversation")
        print("🎯 Press Ctrl+C to shutdown")
        print()
        
        if self.session_logger:
            self.session_logger.log_gui_event(
                "CONVERSATION_START",
                f"Conversation started in {self.config.system_context.value} context"
            )
        
        try:
            if self.config.mode == ConversationMode.VOICE_FIRST:
                await self._voice_first_loop()
            elif self.config.mode == ConversationMode.TEXT_ONLY:
                await self._text_only_loop()
            else:  # HYBRID
                await self._hybrid_loop()
                
        except KeyboardInterrupt:
            print("\n🔄 Conversation interrupted by user")
        except Exception as e:
            print(f"\n❌ Conversation error: {e}")
            if self.session_logger:
                self.session_logger.log_gui_event("CONVERSATION_ERROR", str(e))
        finally:
            self.shutdown()
    
    async def _voice_first_loop(self):
        """Voice-first conversation loop"""
        print("🎙️ Voice-first mode active - speak to interact")
        print("⌨️ Type 'text' to switch to text input temporarily")
        
        while self.is_running:
            try:
                # Check for voice input
                voice_input = await self._capture_voice_input()
                if voice_input:
                    await self._process_conversation_input(voice_input, "voice")
                
                # Check for text input (non-blocking)
                text_input = await self._check_text_input()
                if text_input:
                    if text_input.lower() in ['exit', 'quit']:
                        break
                    elif text_input.lower() == 'text':
                        await self._text_input_session()
                    else:
                        await self._process_conversation_input(text_input, "text")
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                print(f"❌ Voice loop error: {e}")
                await asyncio.sleep(1)
    
    async def _text_only_loop(self):
        """Text-only conversation loop"""
        print("⌨️ Text-only mode active - type to interact")
        
        while self.is_running:
            try:
                user_input = input("💬 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                if user_input:
                    await self._process_conversation_input(user_input, "text")
                    
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Text loop error: {e}")
    
    async def _hybrid_loop(self):
        """Hybrid voice and text conversation loop"""
        print("🎙️⌨️ Hybrid mode active - speak or type to interact")
        
        # Implementation would combine both voice and text input
        # For now, fall back to text-only
        await self._text_only_loop()
    
    async def _capture_voice_input(self) -> Optional[str]:
        """Capture voice input and convert to text"""
        try:
            # Check if voice service is available
            if not await self._check_voice_service():
                return None
            
            # Implement voice capture logic here
            # This would integrate with the arecord → Whisper → AI pipeline
            # For now, return None to indicate no voice input
            return None
            
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_gui_event("VOICE_CAPTURE_ERROR", str(e))
            return None
    
    async def _check_text_input(self) -> Optional[str]:
        """Check for text input (non-blocking)"""
        # This would implement non-blocking text input
        # For now, return None
        return None
    
    async def _text_input_session(self):
        """Temporary text input session"""
        print("⌨️ Switched to text input (type 'voice' to return to voice mode)")
        
        while True:
            try:
                user_input = input("💬 You: ").strip()
                
                if user_input.lower() == 'voice':
                    print("🎙️ Returning to voice mode")
                    break
                elif user_input.lower() in ['exit', 'quit']:
                    self.is_running = False
                    break
                elif user_input:
                    await self._process_conversation_input(user_input, "text")
                    
            except EOFError:
                break
    
    async def _process_conversation_input(self, user_input: str, input_type: str):
        """Process conversation input and generate response"""
        timestamp = time.time()
        
        # Add to conversation history
        self.conversation_history.append({
            "timestamp": timestamp,
            "input": user_input,
            "type": input_type,
            "context": self.config.system_context.value
        })
        
        # Log the conversation
        if self.session_logger:
            self.session_logger.log_gui_event(
                f"CONVERSATION_{input_type.upper()}_INPUT",
                f"User input ({input_type}): {user_input}"
            )
        
        print(f"💭 Processing {input_type} input: {user_input}")
        
        # Generate response (placeholder implementation)
        response = await self._generate_response(user_input)
        
        print(f"🤖 Unhinged: {response}")
        
        # Log the response
        if self.session_logger:
            self.session_logger.log_gui_event(
                "CONVERSATION_RESPONSE",
                f"System response: {response}"
            )
        
        # Trim conversation history if too long
        if len(self.conversation_history) > self.config.max_conversation_length:
            self.conversation_history = self.conversation_history[-self.config.max_conversation_length:]
    
    async def _generate_response(self, user_input: str) -> str:
        """Generate response to user input"""
        # Placeholder implementation
        # This would integrate with the AI pipeline
        
        responses = [
            f"I understand you said: '{user_input}'. This is the conversation interface working!",
            f"Processing your request: '{user_input}' in {self.config.system_context.value} context.",
            f"Voice-first architecture active. Your input '{user_input}' has been received.",
            f"Dual-system conversation interface operational. Input: '{user_input}'"
        ]
        
        import random
        return random.choice(responses)
    
    async def _check_voice_service(self) -> bool:
        """Check if voice service is available"""
        try:
            # Check if voice service is running on the specified port
            result = subprocess.run([
                "nc", "-z", "localhost", str(self.config.voice_service_port)
            ], capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def shutdown(self):
        """Shutdown the conversation interface"""
        self.is_running = False
        
        if self.session_logger:
            self.session_logger.log_gui_event(
                "CONVERSATION_SHUTDOWN",
                f"Conversation interface shutdown after {len(self.conversation_history)} exchanges"
            )
            self.session_logger.close_session()
        
        print("👋 Conversation interface shutdown complete")

async def main():
    """Main entry point for conversation CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unhinged Conversation CLI")
    parser.add_argument("--mode", choices=["voice_first", "text_only", "hybrid"],
                       default="voice_first", help="Conversation mode")
    parser.add_argument("--context", choices=["gtk4_control_plane", "alpine_native"],
                       help="System context (auto-detected if not specified)")
    parser.add_argument("--voice-port", type=int, default=1101,
                       help="Voice service port")
    parser.add_argument("--no-logging", action="store_true",
                       help="Disable session logging")
    
    args = parser.parse_args()
    
    # Create configuration
    config = ConversationConfig(
        mode=ConversationMode(args.mode),
        system_context=SystemContext(args.context) if args.context else SystemContext.UNKNOWN,
        voice_service_port=args.voice_port,
        session_logging=not args.no_logging
    )
    
    # Create and start conversation interface
    cli = ConversationCLI(config)
    await cli.start_conversation()

if __name__ == "__main__":
    asyncio.run(main())
