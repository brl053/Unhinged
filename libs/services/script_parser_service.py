#!/usr/bin/env python3
"""
Script Parser Service

Parses text scripts into scenes/segments with timing and visual cues.
Prepares scripts for video generation pipeline.
"""

import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SceneSegment:
    """Represents a single scene/segment in a script"""

    id: int
    text: str
    duration: float  # Estimated duration in seconds
    visual_cue: str  # What to show visually
    emotion: str  # Tone/emotion (neutral, excited, calm, etc.)
    start_time: float
    end_time: float
    word_count: int


class ScriptParserService:
    """Parse scripts into scenes for video generation"""

    # Punctuation that indicates scene breaks
    SCENE_BREAKS = [".", "!", "?"]

    # Words per second for speech (average)
    WORDS_PER_SECOND = 2.5

    # Minimum scene duration (seconds)
    MIN_SCENE_DURATION = 1.0

    # Maximum scene duration (seconds)
    MAX_SCENE_DURATION = 5.0

    def __init__(self):
        logger.info("Script Parser Service initialized")

    def parse_script(self, script: str, target_duration: int | None = None) -> dict[str, Any]:
        """
        Parse script into scenes.

        Args:
            script: Text script to parse
            target_duration: Target video duration in seconds (optional)

        Returns:
            Dict with:
                - scenes: List of SceneSegment objects
                - total_duration: Estimated total duration
                - word_count: Total words in script
                - metadata: Additional metadata
        """
        logger.info(f"Parsing script ({len(script)} chars)")

        # Clean script
        script = script.strip()

        # Split into sentences
        sentences = self._split_into_sentences(script)
        logger.info(f"Found {len(sentences)} sentences")

        # Group sentences into scenes
        scenes = self._group_into_scenes(sentences)
        logger.info(f"Grouped into {len(scenes)} scenes")

        # Calculate timing
        scenes = self._calculate_timing(scenes)

        # If target duration specified, adjust pacing
        if target_duration:
            scenes = self._adjust_to_duration(scenes, target_duration)

        total_duration = scenes[-1].end_time if scenes else 0
        total_words = sum(s.word_count for s in scenes)

        return {
            "scenes": [asdict(s) for s in scenes],
            "total_duration": total_duration,
            "word_count": total_words,
            "scene_count": len(scenes),
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "avg_scene_duration": total_duration / len(scenes) if scenes else 0,
                "avg_words_per_scene": total_words / len(scenes) if scenes else 0,
            },
        }

    def _split_into_sentences(self, script: str) -> list[str]:
        """Split script into sentences"""
        # Split on sentence boundaries
        sentences = re.split(r"(?<=[.!?])\s+", script)
        # Clean up
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _group_into_scenes(self, sentences: list[str]) -> list[SceneSegment]:
        """Group sentences into scenes"""
        scenes = []
        current_scene_text = []
        scene_id = 0

        for sentence in sentences:
            current_scene_text.append(sentence)

            # Estimate duration for current scene
            word_count = len(" ".join(current_scene_text).split())
            estimated_duration = word_count / self.WORDS_PER_SECOND

            # Create scene if it's long enough or if it's the last sentence
            if estimated_duration >= self.MIN_SCENE_DURATION or sentence == sentences[-1]:
                scene_text = " ".join(current_scene_text)

                # Extract visual cue from text
                visual_cue = self._extract_visual_cue(scene_text)
                emotion = self._detect_emotion(scene_text)

                scene = SceneSegment(
                    id=scene_id,
                    text=scene_text,
                    duration=estimated_duration,
                    visual_cue=visual_cue,
                    emotion=emotion,
                    start_time=0,  # Will be calculated later
                    end_time=0,
                    word_count=word_count,
                )

                scenes.append(scene)
                current_scene_text = []
                scene_id += 1

        return scenes

    def _calculate_timing(self, scenes: list[SceneSegment]) -> list[SceneSegment]:
        """Calculate start/end times for each scene"""
        current_time = 0

        for scene in scenes:
            scene.start_time = current_time
            scene.end_time = current_time + scene.duration
            current_time = scene.end_time

        return scenes

    def _adjust_to_duration(
        self, scenes: list[SceneSegment], target_duration: int
    ) -> list[SceneSegment]:
        """Adjust scene durations to fit target duration"""
        current_total = scenes[-1].end_time if scenes else 0

        if current_total == 0:
            return scenes

        # Calculate scaling factor
        scale_factor = target_duration / current_total

        # Adjust each scene
        current_time = 0
        for scene in scenes:
            scene.duration *= scale_factor
            scene.start_time = current_time
            scene.end_time = current_time + scene.duration
            current_time = scene.end_time

        return scenes

    def _extract_visual_cue(self, text: str) -> str:
        """Extract visual cue from text"""
        # Look for visual keywords
        visual_keywords = {
            "show": "demonstration",
            "look": "visual",
            "see": "visual",
            "imagine": "abstract",
            "picture": "visual",
            "watch": "action",
            "amazing": "impressive",
            "beautiful": "scenic",
            "technology": "tech",
            "ai": "tech",
            "computer": "tech",
        }

        text_lower = text.lower()
        for keyword, cue in visual_keywords.items():
            if keyword in text_lower:
                return cue

        return "general"

    def _detect_emotion(self, text: str) -> str:
        """Detect emotion/tone from text"""
        text_lower = text.lower()

        if any(word in text_lower for word in ["!", "amazing", "awesome", "incredible"]):
            return "excited"
        elif any(word in text_lower for word in ["?", "wonder", "curious"]):
            return "curious"
        elif any(word in text_lower for word in ["calm", "peaceful", "serene"]):
            return "calm"
        else:
            return "neutral"
