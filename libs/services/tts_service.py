#!/usr/bin/env python3
"""
Text-to-Speech Service

Generates AI voiceovers from text with multiple voice options.
Integrates with local TTS engines (gTTS, pyttsx3) and cloud services.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech voiceover generation"""

    VOICES = {
        "nova": {"gender": "female", "accent": "american", "speed": 1.0},
        "echo": {"gender": "male", "accent": "american", "speed": 1.0},
        "sage": {"gender": "male", "accent": "american", "speed": 0.95},
        "shimmer": {"gender": "female", "accent": "british", "speed": 1.0},
    }

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize TTS service.

        Args:
            output_dir: Directory to save audio files
        """
        self.output_dir = output_dir or Path.cwd() / "build" / "tmp" / "generated"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("TTS Service initialized")
        logger.info(f"Output directory: {self.output_dir}")

    def generate_voiceover(
        self,
        text: str,
        voice: str = "nova",
        speed: float = 1.0,
        emotion: str = "neutral",
    ) -> Dict[str, Any]:
        """
        Generate voiceover from text.

        Args:
            text: Text to convert to speech
            voice: Voice to use (nova, echo, sage, shimmer)
            speed: Speech speed (0.5-2.0)
            emotion: Emotion/tone (neutral, excited, calm, sad)

        Returns:
            Dict with:
                - audio_path: Path to generated audio file
                - duration: Audio duration in seconds
                - word_count: Number of words
                - metadata: Additional metadata
        """
        if voice not in self.VOICES:
            raise ValueError(
                f"Unknown voice: {voice}. Available: {list(self.VOICES.keys())}"
            )

        logger.info(f"Generating voiceover: {len(text)} chars, voice={voice}")

        try:
            # Use gTTS (Google Text-to-Speech)
            from gtts import gTTS
            import soundfile as sf

            # Create TTS object
            tts = gTTS(text=text, lang="en", slow=speed < 1.0)

            # Generate audio
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"voiceover_{timestamp}.mp3"
            audio_path = self.output_dir / audio_filename

            tts.save(str(audio_path))

            # Calculate duration (rough estimate: 150 words per minute)
            word_count = len(text.split())
            duration = (word_count / 150) * 60 / speed

            logger.info(f"Voiceover generated: {audio_path}")

            return {
                "audio_path": str(audio_path),
                "audio_filename": audio_filename,
                "text": text,
                "voice": voice,
                "speed": speed,
                "emotion": emotion,
                "duration": duration,
                "word_count": word_count,
                "timestamp": timestamp,
                "metadata": {
                    "voice_info": self.VOICES.get(voice, {}),
                    "format": "mp3",
                    "sample_rate": 24000,
                },
            }

        except ImportError:
            logger.error("gTTS not installed. Run: pip install gtts")
            raise
        except Exception as e:
            logger.error(f"Voiceover generation failed: {e}")
            raise

    def generate_batch_voiceovers(
        self,
        scenes: list,
        voice: str = "nova",
        speed: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Generate voiceovers for multiple scenes.

        Args:
            scenes: List of scene dicts with 'text' key
            voice: Voice to use
            speed: Speech speed

        Returns:
            Dict with list of generated voiceovers
        """
        logger.info(f"Generating {len(scenes)} voiceovers")

        voiceovers = []
        total_duration = 0

        for i, scene in enumerate(scenes):
            logger.info(f"Generating voiceover {i + 1}/{len(scenes)}")

            result = self.generate_voiceover(
                text=scene.get("text", ""),
                voice=voice,
                speed=speed,
                emotion=scene.get("emotion", "neutral"),
            )

            voiceovers.append(result)
            total_duration += result["duration"]

        return {
            "voiceovers": voiceovers,
            "total_duration": total_duration,
            "count": len(voiceovers),
            "timestamp": datetime.now().isoformat(),
        }
