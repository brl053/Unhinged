"""
Pluggable Intent Detection Framework

Implements expert recommendation for making detection mechanism pluggable.
Starts with regex, ready for future LLM intent parser evolution.
"""

import re
import abc
import logging
from typing import Dict, List, Optional, Any, Protocol
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """Types of intents that can be detected"""
    TEXT_CHAT = "text_chat"
    IMAGE_GENERATION = "image_generation"
    COMMAND = "command"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """Result of intent detection"""
    intent_type: IntentType
    confidence: float  # 0.0 to 1.0
    parameters: Dict[str, Any]
    original_text: str
    matched_pattern: Optional[str] = None
    
    @property
    def is_confident(self) -> bool:
        """Check if confidence is high enough to act on"""
        return self.confidence >= 0.8


class IntentDetector(Protocol):
    """Protocol for intent detection implementations"""
    
    def detect(self, text: str) -> IntentResult:
        """Detect intent from text input"""
        ...
    
    def get_supported_intents(self) -> List[IntentType]:
        """Get list of supported intent types"""
        ...


class ExplicitCommandDetector:
    """
    Explicit command-based intent detector

    Primary interface using explicit commands as recommended by expert.
    NO REGEX PATTERNS - Commands only.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Explicit commands only - NO REGEX PATTERNS
        self.commands = {
            # Image generation commands
            "/image": IntentType.IMAGE_GENERATION,
            "/generate": IntentType.IMAGE_GENERATION,
            "/draw": IntentType.IMAGE_GENERATION,
            "/create": IntentType.IMAGE_GENERATION,

            # System commands
            "/help": IntentType.COMMAND,
            "/status": IntentType.COMMAND,
            "/clear": IntentType.COMMAND,
            "/session": IntentType.COMMAND,

            # Alternative syntax
            "!image": IntentType.IMAGE_GENERATION,
            "!generate": IntentType.IMAGE_GENERATION,
            "!help": IntentType.COMMAND,
            "!status": IntentType.COMMAND
        }
    
    def detect(self, text: str) -> IntentResult:
        """Detect intent using EXPLICIT COMMANDS ONLY - NO REGEX"""
        text = text.strip()

        if not text:
            return IntentResult(
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                parameters={},
                original_text=text
            )

        # Check for explicit commands - PRIMARY INTERFACE
        words = text.split()
        if words:
            command = words[0].lower()

            if command in self.commands:
                intent_type = self.commands[command]
                args = " ".join(words[1:]) if len(words) > 1 else ""

                if intent_type == IntentType.IMAGE_GENERATION:
                    if not args:
                        # Command without prompt
                        return IntentResult(
                            intent_type=IntentType.UNKNOWN,
                            confidence=0.0,
                            parameters={"error": f"Command {command} requires a prompt"},
                            original_text=text
                        )

                    return IntentResult(
                        intent_type=IntentType.IMAGE_GENERATION,
                        confidence=1.0,  # Perfect confidence for explicit commands
                        parameters={"prompt": args},
                        original_text=text,
                        matched_pattern=command
                    )

                elif intent_type == IntentType.COMMAND:
                    return IntentResult(
                        intent_type=IntentType.COMMAND,
                        confidence=1.0,
                        parameters={"command": command[1:], "args": args},  # Remove / or !
                        original_text=text,
                        matched_pattern=command
                    )

        # Default to text chat for non-commands
        return IntentResult(
            intent_type=IntentType.TEXT_CHAT,
            confidence=0.9,
            parameters={"message": text},
            original_text=text
        )
    
    # REGEX PATTERN METHODS REMOVED - EXPLICIT COMMANDS ONLY
    
    def get_supported_intents(self) -> List[IntentType]:
        """Get supported intent types"""
        return [IntentType.TEXT_CHAT, IntentType.IMAGE_GENERATION, IntentType.COMMAND]

    def add_command(self, command: str, intent_type: IntentType) -> None:
        """Add custom explicit command"""
        self.commands[command.lower()] = intent_type
        self.logger.info(f"Added command: {command} -> {intent_type.value}")

    def get_available_commands(self) -> Dict[str, str]:
        """Get all available commands"""
        return {cmd: intent.value for cmd, intent in self.commands.items()}


class LLMIntentDetector:
    """
    Future LLM-based intent detector
    
    Placeholder for future implementation using LLM for intent analysis.
    Will implement the same IntentDetector protocol.
    """
    
    def __init__(self, llm_service_name: str = "llm"):
        self.llm_service = llm_service_name
        self.logger = logging.getLogger(__name__)
        self.logger.info("LLM intent detector initialized (not yet implemented)")
    
    def detect(self, text: str) -> IntentResult:
        """Detect intent using LLM (future implementation)"""
        # TODO: Implement LLM-based intent detection
        # This would send the text to an LLM service with a prompt like:
        # "Analyze this user message and determine if it's requesting:
        #  1. Text conversation
        #  2. Image generation  
        #  3. A command
        #  Return structured response with intent and parameters."
        
        raise NotImplementedError("LLM intent detection not yet implemented")
    
    def get_supported_intents(self) -> List[IntentType]:
        """Get supported intent types"""
        return [IntentType.TEXT_CHAT, IntentType.IMAGE_GENERATION, IntentType.COMMAND]


class IntentDetectorManager:
    """
    Manager for pluggable intent detection
    
    Allows switching between different detection implementations.
    """
    
    def __init__(self, default_detector: Optional[IntentDetector] = None):
        self.logger = logging.getLogger(__name__)

        # Use explicit command detector as default - NO REGEX
        self._detector = default_detector or ExplicitCommandDetector()
        self.logger.info(f"Intent detector initialized: {type(self._detector).__name__}")
    
    def set_detector(self, detector: IntentDetector) -> None:
        """Switch to a different intent detector"""
        old_detector = type(self._detector).__name__
        self._detector = detector
        new_detector = type(self._detector).__name__
        self.logger.info(f"Switched intent detector: {old_detector} -> {new_detector}")
    
    def detect_intent(self, text: str) -> IntentResult:
        """Detect intent using current detector"""
        try:
            result = self._detector.detect(text)
            self.logger.debug(f"Intent detected: {result.intent_type.value} "
                            f"(confidence: {result.confidence:.2f})")
            return result
        except Exception as e:
            self.logger.error(f"Intent detection failed: {e}")
            # Return safe fallback
            return IntentResult(
                intent_type=IntentType.TEXT_CHAT,
                confidence=0.5,
                parameters={"message": text},
                original_text=text
            )
    
    def get_detector_info(self) -> Dict[str, Any]:
        """Get information about current detector"""
        return {
            "type": type(self._detector).__name__,
            "supported_intents": [intent.value for intent in self._detector.get_supported_intents()]
        }


# Global intent detector instance
_global_detector: Optional[IntentDetectorManager] = None


def get_global_detector() -> IntentDetectorManager:
    """Get global intent detector instance"""
    global _global_detector
    
    if _global_detector is None:
        _global_detector = IntentDetectorManager()
    
    return _global_detector


def detect_intent(text: str) -> IntentResult:
    """Convenience function to detect intent using global detector"""
    return get_global_detector().detect_intent(text)
