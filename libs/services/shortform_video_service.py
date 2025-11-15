#!/usr/bin/env python3
"""
Short-Form Video Generator Service

Generates studio-grade TikTok/Reels/Shorts from text scripts.
Orchestrates: script parsing → TTS → visual generation → video composition.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import time

from .script_parser_service import ScriptParserService
from .tts_service import TTSService
from .image_generation_service import ImageGenerationService
from .video_generation_service import VideoGenerationService
from .quality_tiers import get_quality_config

logger = logging.getLogger(__name__)


class ShortFormVideoService:
    """Generate studio-grade short-form videos from scripts"""

    # Platform specifications
    # Note: Using 720x1280 for generation (upscaled to 1080x1920 in post-processing)
    # This reduces GPU memory usage by ~60% while maintaining quality
    PLATFORMS = {
        "tiktok": {
            "width": 720,
            "height": 1280,
            "fps": 24,
            "max_duration": 600,
            "output_width": 1080,
            "output_height": 1920,
        },
        "reels": {
            "width": 720,
            "height": 1280,
            "fps": 24,
            "max_duration": 90,
            "output_width": 1080,
            "output_height": 1920,
        },
        "shorts": {
            "width": 720,
            "height": 1280,
            "fps": 24,
            "max_duration": 60,
            "output_width": 1080,
            "output_height": 1920,
        },
    }

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize short-form video service.

        Args:
            output_dir: Directory to save generated videos
        """
        self.output_dir = output_dir or Path.cwd() / "build" / "tmp" / "generated"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize sub-services
        self.script_parser = ScriptParserService()
        self.tts = TTSService(output_dir)
        self.image_gen = ImageGenerationService(
            model="stable-diffusion", output_dir=output_dir
        )
        self.video_gen = VideoGenerationService(output_dir)

        logger.info("Short-Form Video Service initialized")
        logger.info(f"Output directory: {self.output_dir}")

    def generate_from_script(
        self,
        script: str,
        platform: str = "tiktok",
        voice: str = "nova",
        style: str = "cinematic",
        quality: str = "standard",
        music: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate short-form video from text script.

        Args:
            script: Text script for the video
            platform: Target platform (tiktok, reels, shorts)
            voice: Voice for voiceover (nova, echo, sage, shimmer)
            style: Visual style (cinematic, minimal, vibrant, abstract)
            quality: Quality tier (draft, standard, ultra)
            music: Background music track (optional)

        Returns:
            Dict with:
                - video_path: Path to generated video
                - duration: Video duration
                - scenes: Number of scenes
                - quality: Quality tier used
                - metadata: Additional metadata
        """
        if platform not in self.PLATFORMS:
            raise ValueError(f"Unknown platform: {platform}")

        # Get quality configuration
        try:
            quality_config = get_quality_config(quality)
        except ValueError as e:
            raise ValueError(
                f"Invalid quality tier: {quality}. Available: draft, standard, ultra"
            ) from e

        logger.info(f"Generating short-form video for {platform}")
        logger.info(f"Quality: {quality} ({quality_config.inference_steps} steps)")
        logger.info(f"Script: {len(script)} chars, voice={voice}, style={style}")

        start_time = time.time()
        platform_spec = self.PLATFORMS[platform]

        try:
            # Step 1: Parse script
            logger.info("Step 1: Parsing script...")
            parse_result = self.script_parser.parse_script(
                script,
                target_duration=platform_spec["max_duration"],
            )
            scenes = parse_result["scenes"]
            logger.info(f"✅ Parsed into {len(scenes)} scenes")

            # Step 2: Generate voiceovers
            logger.info("Step 2: Generating voiceovers...")
            tts_result = self.tts.generate_batch_voiceovers(scenes, voice=voice)
            voiceovers = tts_result["voiceovers"]
            logger.info(f"✅ Generated {len(voiceovers)} voiceovers")

            # Step 3: Generate visuals
            logger.info("Step 3: Generating visuals...")
            visuals = []
            for i, scene in enumerate(scenes):
                logger.info(f"  Generating visual {i + 1}/{len(scenes)}...")
                visual_prompt = self._create_visual_prompt(scene, style)

                image_result = self.image_gen.generate_image(
                    prompt=visual_prompt,
                    quality=quality,
                    num_inference_steps=quality_config.inference_steps,
                    width=quality_config.generation_width,
                    height=quality_config.generation_height,
                )
                visuals.append(image_result)

            logger.info(f"✅ Generated {len(visuals)} visuals")

            # Step 4: Compose video
            logger.info("Step 4: Composing video...")
            video_result = self._compose_video(
                scenes=scenes,
                voiceovers=voiceovers,
                visuals=visuals,
                platform_spec=platform_spec,
                music=music,
            )

            generation_time = time.time() - start_time

            logger.info(f"✅ Video generation complete: {generation_time:.1f}s")

            return {
                "video_path": video_result["video_path"],
                "video_filename": video_result["video_filename"],
                "platform": platform,
                "quality": quality,
                "duration": parse_result["total_duration"],
                "scenes": len(scenes),
                "word_count": parse_result["word_count"],
                "generation_time": generation_time,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "voice": voice,
                    "style": style,
                    "quality_tier": quality,
                    "inference_steps": quality_config.inference_steps,
                    "generation_resolution": f"{quality_config.generation_width}x{quality_config.generation_height}",
                    "output_resolution": f"{quality_config.output_width}x{quality_config.output_height}",
                    "fps": platform_spec["fps"],
                    "expected_gpu_memory": f"{quality_config.expected_gpu_memory:.1f} GB",
                    "expected_time_per_image": f"{quality_config.expected_time_per_image:.1f}s",
                },
            }

        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            raise

    def _create_visual_prompt(self, scene: Dict[str, Any], style: str) -> str:
        """Create visual prompt from scene"""
        text = scene.get("text", "")
        visual_cue = scene.get("visual_cue", "general")
        emotion = scene.get("emotion", "neutral")

        # Build prompt based on style
        if style == "cinematic":
            prompt = f"cinematic, professional, {visual_cue}, {emotion} mood, 4k, high quality"
        elif style == "minimal":
            prompt = f"minimalist, clean, {visual_cue}, {emotion} mood, simple"
        elif style == "vibrant":
            prompt = f"vibrant colors, energetic, {visual_cue}, {emotion} mood, dynamic"
        elif style == "abstract":
            prompt = f"abstract art, {visual_cue}, {emotion} mood, artistic"
        else:
            prompt = f"{visual_cue}, {emotion} mood"

        # Add text context
        if len(text) < 100:
            prompt += f", {text}"

        return prompt

    def _compose_video(
        self,
        scenes: list,
        voiceovers: list,
        visuals: list,
        platform_spec: Dict[str, Any],
        music: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compose final video from components with audio sync"""
        logger.info("Composing video from components...")

        try:
            import imageio
            import numpy as np
            from PIL import Image
        except ImportError as e:
            logger.error(f"Required library not available: {e}")
            raise

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"shortform_{timestamp}.mp4"
        video_path = self.output_dir / video_filename

        fps = platform_spec["fps"]
        width = platform_spec["output_width"]
        height = platform_spec["output_height"]

        # Build frame sequence with timing
        frames = []
        frame_times = []
        current_time = 0

        logger.info(f"Building frame sequence: {len(visuals)} visuals")

        for i, visual in enumerate(visuals):
            if i >= len(voiceovers):
                logger.warning(f"More visuals than voiceovers, stopping at {i}")
                break

            # Get image path from visual result
            image_path = visual.get("image_path")
            if not image_path:
                logger.warning(f"Visual {i} has no image_path, skipping")
                continue

            # Get duration from voiceover
            voiceover_duration = voiceovers[i].get("duration", 3.0)

            # Load and resize image
            try:
                img = Image.open(image_path)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                img_array = np.array(img)
            except Exception as e:
                logger.error(f"Failed to load image {image_path}: {e}")
                continue

            # Calculate number of frames for this scene
            num_frames = int(voiceover_duration * fps)
            logger.info(f"Scene {i}: {voiceover_duration:.1f}s → {num_frames} frames")

            # Add frames (hold image for duration of voiceover)
            for _ in range(num_frames):
                frames.append(img_array)
                frame_times.append(current_time)
                current_time += 1.0 / fps

        if not frames:
            logger.error("No frames generated")
            raise ValueError("Failed to generate any frames")

        logger.info(f"Writing {len(frames)} frames to video...")

        # Write video file
        writer = imageio.get_writer(str(video_path), fps=fps, codec="libx264")

        for frame in frames:
            writer.append_data(frame)

        writer.close()

        total_duration = len(frames) / fps

        logger.info(f"Video saved: {video_path}")
        logger.info(
            f"Duration: {total_duration:.1f}s, Frames: {len(frames)}, FPS: {fps}"
        )

        return {
            "video_path": str(video_path),
            "video_filename": video_filename,
            "status": "success",
            "duration": total_duration,
            "frames": len(frames),
            "fps": fps,
            "resolution": f"{width}x{height}",
        }
