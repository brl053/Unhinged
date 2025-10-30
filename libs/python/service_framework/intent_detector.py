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


class RegexIntentDetector:
    """
    Regex-based intent detector
    
    Current implementation using pattern matching.
    Designed to be replaced by LLM intent parser in the future.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Image generation patterns (from existing implementation)
        self.image_patterns = [
            (r"generate image of (.+)", 0.95),
            (r"create image (.+)", 0.95),
            (r"draw (.+)", 0.90),
            (r"/image (.+)", 1.0),  # Explicit command
            (r"make an image of (.+)", 0.95),
            (r"show me (.+)", 0.70),  # Lower confidence - could be text request
            (r"picture of (.+)", 0.85),
            (r"generate (.+) image", 0.90),
            (r"can you draw (.+)", 0.85),
            (r"create a picture of (.+)", 0.95)
        ]
        
        # Command patterns
        self.command_patterns = [
            (r"^/(\w+)(?:\s+(.*))?", 1.0),  # Explicit commands like /help, /status
            (r"^!(\w+)(?:\s+(.*))?", 1.0),  # Alternative command syntax
        ]
        
        # Compile patterns for efficiency
        self._compiled_image_patterns = [
            (re.compile(pattern, re.IGNORECASE), confidence)
            for pattern, confidence in self.image_patterns
        ]
        
        self._compiled_command_patterns = [
            (re.compile(pattern, re.IGNORECASE), confidence)
            for pattern, confidence in self.command_patterns
        ]
    
    def detect(self, text: str) -> IntentResult:
        """Detect intent from text using regex patterns"""
        text = text.strip()
        
        if not text:
            return IntentResult(
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                parameters={},
                original_text=text
            )
        
        # Check for explicit commands first (highest priority)
        command_result = self._detect_command(text)
        if command_result.confidence > 0.8:
            return command_result
        
        # Check for image generation
        image_result = self._detect_image_generation(text)
        if image_result.confidence > 0.7:
            return image_result
        
        # Default to text chat
        return IntentResult(
            intent_type=IntentType.TEXT_CHAT,
            confidence=0.9,  # High confidence for text chat as fallback
            parameters={"message": text},
            original_text=text
        )
    
    def _detect_command(self, text: str) -> IntentResult:
        """Detect explicit commands"""
        for pattern, confidence in self._compiled_command_patterns:
            match = pattern.match(text)
            if match:
                command = match.group(1).lower()
                args = match.group(2) if match.lastindex > 1 else ""
                
                return IntentResult(
                    intent_type=IntentType.COMMAND,
                    confidence=confidence,
                    parameters={
                        "command": command,
                        "args": args.strip() if args else ""
                    },
                    original_text=text,
                    matched_pattern=pattern.pattern
                )
        
        return IntentResult(
            intent_type=IntentType.UNKNOWN,
            confidence=0.0,
            parameters={},
            original_text=text
        )
    
    def _detect_image_generation(self, text: str) -> IntentResult:
        """Detect image generation requests"""
        for pattern, confidence in self._compiled_image_patterns:
            match = pattern.search(text)
            if match:
                prompt = match.group(1).strip()
                
                # Adjust confidence based on prompt quality
                adjusted_confidence = self._adjust_image_confidence(prompt, confidence)
                
                return IntentResult(
                    intent_type=IntentType.IMAGE_GENERATION,
                    confidence=adjusted_confidence,
                    parameters={
                        "prompt": prompt,
                        "type": "image_generation"
                    },
                    original_text=text,
                    matched_pattern=pattern.pattern
                )
        
        return IntentResult(
            intent_type=IntentType.UNKNOWN,
            confidence=0.0,
            parameters={},
            original_text=text
        )
    
    def _adjust_image_confidence(self, prompt: str, base_confidence: float) -> float:
        """Adjust confidence based on prompt characteristics"""
        # Very short prompts are less likely to be image requests
        if len(prompt.strip()) < 3:
            return base_confidence * 0.5
        
        # Prompts with question words might be text questions
        question_words = ["what", "how", "why", "when", "where", "who"]
        if any(word in prompt.lower() for word in question_words):
            return base_confidence * 0.7
        
        # Prompts with visual descriptors are more likely to be image requests
        visual_words = ["color", "bright", "dark", "beautiful", "style", "realistic", "artistic"]
        if any(word in prompt.lower() for word in visual_words):
            return min(1.0, base_confidence * 1.1)
        
        return base_confidence
    
    def get_supported_intents(self) -> List[IntentType]:
        """Get supported intent types"""
        return [IntentType.TEXT_CHAT, IntentType.IMAGE_GENERATION, IntentType.COMMAND]
    
    def add_image_pattern(self, pattern: str, confidence: float = 0.9) -> None:
        """Add custom image generation pattern"""
        self.image_patterns.append((pattern, confidence))
        self._compiled_image_patterns.append((re.compile(pattern, re.IGNORECASE), confidence))
        self.logger.info(f"Added image pattern: {pattern}")
    
    def add_command_pattern(self, pattern: str, confidence: float = 1.0) -> None:
        """Add custom command pattern"""
        self.command_patterns.append((pattern, confidence))
        self._compiled_command_patterns.append((re.compile(pattern, re.IGNORECASE), confidence))
        self.logger.info(f"Added command pattern: {pattern}")


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
        
        # Use regex detector as default
        self._detector = default_detector or RegexIntentDetector()
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
