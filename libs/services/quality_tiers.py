#!/usr/bin/env python3
"""
Quality Tier System

Defines three quality presets optimized for different use cases:
- draft: Fast iteration (social media, quick preview)
- standard: Balanced (social media + print, default)
- ultra: Maximum quality (gallery/print, cinema)
"""

from dataclasses import dataclass
from typing import Literal

QualityTier = Literal["draft", "standard", "ultra"]


@dataclass
class QualityConfig:
    """Configuration for a quality tier"""

    # Image generation
    inference_steps: int  # Diffusion steps (more = better quality, slower)
    num_candidates: int  # Generate N images, pick best
    guidance_scale: float  # Prompt adherence (7.5 = balanced)

    # Resolution
    generation_width: int  # Generation resolution
    generation_height: int  # Generation resolution
    output_width: int  # Final output resolution
    output_height: int  # Final output resolution

    # Video encoding
    crf: int  # H.264 quality (0-51, lower = better, 18-28 typical)
    audio_bitrate: str  # Audio quality (e.g., "128k", "192k")

    # Performance
    expected_time_per_image: float  # Seconds per image
    expected_gpu_memory: float  # GB
    expected_gpu_temp: float  # Celsius

    # Use cases
    use_cases: list  # What this tier is optimized for


# Quality Tier Definitions
QUALITY_TIERS = {
    "draft": QualityConfig(
        # Fast iteration - social media preview
        inference_steps=15,
        num_candidates=1,
        guidance_scale=7.5,
        generation_width=576,
        generation_height=1024,
        output_width=1080,
        output_height=1920,
        crf=28,
        audio_bitrate="128k",
        expected_time_per_image=3.0,
        expected_gpu_memory=6.0,
        expected_gpu_temp=65.0,
        use_cases=["social_media_preview", "quick_iteration"],
    ),
    "standard": QualityConfig(
        # Balanced - social media + print
        inference_steps=25,
        num_candidates=1,
        guidance_scale=7.5,
        generation_width=720,
        generation_height=1280,
        output_width=1080,
        output_height=1920,
        crf=20,
        audio_bitrate="192k",
        expected_time_per_image=5.0,
        expected_gpu_memory=8.0,
        expected_gpu_temp=70.0,
        use_cases=["social_media", "print_small", "web"],
    ),
    "ultra": QualityConfig(
        # Maximum quality - gallery/print + cinema
        # Realistic for RTX 5070 Ti: 40 steps at 864×1536
        inference_steps=40,
        num_candidates=2,
        guidance_scale=7.5,
        generation_width=864,
        generation_height=1536,
        output_width=1080,
        output_height=1920,
        crf=12,
        audio_bitrate="256k",
        expected_time_per_image=10.0,
        expected_gpu_memory=11.0,
        expected_gpu_temp=76.0,
        use_cases=["gallery", "print_large", "cinema", "archival"],
    ),
}


def get_quality_config(tier: QualityTier) -> QualityConfig:
    """Get configuration for a quality tier"""
    if tier not in QUALITY_TIERS:
        raise ValueError(
            f"Unknown quality tier: {tier}. Available: {list(QUALITY_TIERS.keys())}"
        )
    return QUALITY_TIERS[tier]


def describe_tier(tier: QualityTier) -> str:
    """Get human-readable description of a tier"""
    config = get_quality_config(tier)

    descriptions = {
        "draft": (
            "DRAFT - Fast iteration\n"
            f"  • {config.generation_width}×{config.generation_height} generation\n"
            f"  • {config.inference_steps} steps\n"
            f"  • ~{config.expected_time_per_image:.0f}s per image\n"
            f"  • Best for: Social media preview, quick iteration"
        ),
        "standard": (
            "STANDARD - Balanced quality (default)\n"
            f"  • {config.generation_width}×{config.generation_height} generation\n"
            f"  • {config.inference_steps} steps\n"
            f"  • ~{config.expected_time_per_image:.0f}s per image\n"
            f"  • Best for: Social media + small prints"
        ),
        "ultra": (
            "ULTRA - Maximum quality\n"
            f"  • {config.generation_width}×{config.generation_height} generation\n"
            f"  • {config.inference_steps} steps\n"
            f"  • ~{config.expected_time_per_image:.0f}s per image\n"
            f"  • Best for: Gallery, large prints, cinema"
        ),
    }

    return descriptions.get(tier, f"Unknown tier: {tier}")
