#!/usr/bin/env python3
"""
Unhinged Generate CLI - Headless generation commands

Provides CLI interface for image and video generation.
Designed to be layered with GTK4 UI later.

Usage:
  unhinged generate image stable-diffusion "a beautiful landscape"
  unhinged generate image sdxl "high quality portrait" --steps 40 --guidance 7.5
  unhinged generate video stable-diffusion "sunset over ocean" --duration 30
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "libs"))

try:
    from libs.services import (
        ImageGenerationService,
        YOLOAnalysisService,
        VideoGenerationService,
        ScriptParserService,
        TTSService,
        ShortFormVideoService,
    )
except ImportError as e:
    ImageGenerationService = None
    YOLOAnalysisService = None
    VideoGenerationService = None
    ScriptParserService = None
    TTSService = None
    ShortFormVideoService = None
    IMPORT_ERROR = str(e)


class GenerateCLI:
    """CLI for generation commands"""

    def __init__(self):
        self.project_root = PROJECT_ROOT

    def generate_image(
        self,
        model: str,
        prompt: str,
        quality: str = "standard",
        steps: Optional[int] = None,
        guidance: Optional[float] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
        seed: Optional[int] = None,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """Generate image using specified model"""

        if ImageGenerationService is None:
            print(f"❌ Dependencies not installed: {IMPORT_ERROR}", file=sys.stderr)
            print("   Run: pip install torch diffusers transformers", file=sys.stderr)
            sys.exit(1)

        print(f"🎨 Generating image with {model}...")
        print(f"   Prompt: {prompt}")
        print(f"   Quality: {quality}")
        if steps:
            print(f"   Steps: {steps}")
        if guidance:
            print(f"   Guidance: {guidance}")
        if height and width:
            print(f"   Resolution: {width}x{height}")

        try:
            service = ImageGenerationService(model=model)

            result = service.generate_image(
                prompt=prompt,
                quality=quality,
                num_inference_steps=steps,
                guidance_scale=guidance,
                height=height,
                width=width,
                seed=seed,
            )

            # Format output
            if output_format == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                print(f"✅ Image generated: {result['image_path']}")
                print(f"   Generation time: {result['generation_time']:.1f}s")
                print(f"   Model: {result['model']}")
                print(f"   Device: {result['device']}")

            return result

        except Exception as e:
            print(f"❌ Image generation failed: {e}", file=sys.stderr)
            sys.exit(1)

    def generate_video(
        self,
        approach: str,
        prompt: str,
        duration: int = 30,
        fps: int = 24,
        width: int = 512,
        height: int = 512,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """Generate video using specified approach"""

        if VideoGenerationService is None:
            print(f"❌ Dependencies not installed: {IMPORT_ERROR}", file=sys.stderr)
            print("   Run: pip install imageio imageio-ffmpeg", file=sys.stderr)
            sys.exit(1)

        print(f"🎬 Generating video with {approach}...")
        print(f"   Prompt: {prompt}")
        print(f"   Duration: {duration}s, FPS: {fps}")
        print(f"   Resolution: {width}x{height}")

        try:
            service = VideoGenerationService()

            result = service.generate_video(
                prompt=prompt,
                approach=approach,
                duration=duration,
                fps=fps,
                width=width,
                height=height,
            )

            # Format output
            if output_format == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                print(f"✅ Video generated: {result['video_path']}")
                print(f"   Generation time: {result['generation_time']:.1f}s")
                print(f"   Approach: {result['approach']}")
                print(f"   Duration: {result['duration']}s @ {result['fps']}fps")
                print(f"   Resolution: {result['width']}x{result['height']}")

            return result

        except Exception as e:
            print(f"❌ Video generation failed: {e}", file=sys.stderr)
            sys.exit(1)

    def analyze_screenshot(
        self,
        image_path: str,
        model_size: str = "m",
        confidence: float = 0.5,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """Analyze screenshot for GUI elements"""

        if YOLOAnalysisService is None:
            print(f"❌ Dependencies not installed: {IMPORT_ERROR}", file=sys.stderr)
            print(
                "   Run: pip install ultralytics opencv-python pillow", file=sys.stderr
            )
            sys.exit(1)

        print(f"🔍 Analyzing screenshot with YOLOv8{model_size}...")
        print(f"   Image: {image_path}")
        print(f"   Confidence: {confidence}")

        try:
            service = YOLOAnalysisService(model_size=model_size)
            result = service.analyze_screenshot(image_path, confidence=confidence)

            # Format output
            if output_format == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                print(
                    f"✅ Analysis complete: {result['total_detections']} elements detected"
                )
                print(f"   Analysis time: {result['analysis_time']:.2f}s")
                print(f"   Annotated image: {result['annotated_image_path']}")
                print(f"   Element counts: {result['element_counts']}")

            return result

        except Exception as e:
            print(f"❌ Analysis failed: {e}", file=sys.stderr)
            sys.exit(1)

    def generate_shortform_video(
        self,
        script: str,
        platform: str = "tiktok",
        voice: str = "nova",
        style: str = "cinematic",
        quality: str = "standard",
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """Generate studio-grade short-form video from script"""

        if ShortFormVideoService is None:
            print(f"❌ Dependencies not installed: {IMPORT_ERROR}", file=sys.stderr)
            sys.exit(1)

        print("🎬 Generating short-form video...")
        print(f"   Platform: {platform}")
        print(f"   Voice: {voice}")
        print(f"   Style: {style}")
        print(f"   Quality: {quality}")
        print(f"   Script length: {len(script)} chars")

        try:
            service = ShortFormVideoService()
            result = service.generate_from_script(
                script=script,
                platform=platform,
                voice=voice,
                style=style,
                quality=quality,
            )

            # Format output
            if output_format == "json":
                print(json.dumps(result, indent=2, default=str))
            else:
                print(f"✅ Video generated: {result['video_path']}")
                print(f"   Duration: {result['duration']:.1f}s")
                print(f"   Scenes: {result['scenes']}")
                print(f"   Generation time: {result['generation_time']:.1f}s")
                print(f"   Platform: {result['platform']}")

            return result

        except Exception as e:
            print(f"❌ Video generation failed: {e}", file=sys.stderr)
            import traceback

            traceback.print_exc()
            sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Unhinged Generation CLI - Headless image, video, and short-form content generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  unhinged generate image stable-diffusion "a beautiful landscape"
  unhinged generate image sdxl "high quality portrait" --steps 40 --quality ultra
  unhinged generate video frame-interp "sunset over ocean" --duration 30
  unhinged generate video svd "dancing figure" --duration 30 --fps 30
  unhinged generate analyze /path/to/screenshot.png
  unhinged generate shortform "Hey everyone! Check this out." --platform tiktok --voice nova --style cinematic
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Generation command")

    # Image generation command
    image_parser = subparsers.add_parser("image", help="Generate images")
    image_parser.add_argument(
        "model",
        choices=["stable-diffusion", "sdxl"],
        help="Model to use for generation",
    )
    image_parser.add_argument("prompt", help="Image generation prompt")
    image_parser.add_argument(
        "--quality",
        choices=["draft", "standard", "high", "ultra"],
        default="standard",
        help="Quality preset (default: standard)",
    )
    image_parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Override inference steps (uses quality preset if not set)",
    )
    image_parser.add_argument(
        "--guidance",
        type=float,
        default=None,
        help="Override guidance scale (uses quality preset if not set)",
    )
    image_parser.add_argument(
        "--height", type=int, default=None, help="Override image height in pixels"
    )
    image_parser.add_argument(
        "--width", type=int, default=None, help="Override image width in pixels"
    )
    image_parser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducibility"
    )
    image_parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )

    # Video generation command
    video_parser = subparsers.add_parser("video", help="Generate videos")
    video_parser.add_argument(
        "approach", choices=["frame-interp", "svd"], help="Video generation approach"
    )
    video_parser.add_argument("prompt", help="Video generation prompt")
    video_parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Video duration in seconds (default: 30)",
    )
    video_parser.add_argument(
        "--fps", type=int, default=24, help="Frames per second (default: 24)"
    )
    video_parser.add_argument(
        "--width", type=int, default=512, help="Video width in pixels (default: 512)"
    )
    video_parser.add_argument(
        "--height", type=int, default=512, help="Video height in pixels (default: 512)"
    )
    video_parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )

    # Screenshot analysis command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze screenshots for GUI elements"
    )
    analyze_parser.add_argument("image_path", help="Path to screenshot image")
    analyze_parser.add_argument(
        "--model-size",
        choices=["n", "s", "m", "l", "x"],
        default="m",
        help="YOLO model size (default: m)",
    )
    analyze_parser.add_argument(
        "--confidence",
        type=float,
        default=0.5,
        help="Detection confidence threshold (default: 0.5)",
    )
    analyze_parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )

    # Short-form video generation command
    shortform_parser = subparsers.add_parser(
        "shortform", help="Generate studio-grade short-form videos"
    )
    shortform_parser.add_argument("script", help="Text script for the video")
    shortform_parser.add_argument(
        "--platform",
        choices=["tiktok", "reels", "shorts"],
        default="tiktok",
        help="Target platform (default: tiktok)",
    )
    shortform_parser.add_argument(
        "--voice",
        choices=["nova", "echo", "sage", "shimmer"],
        default="nova",
        help="Voice for voiceover (default: nova)",
    )
    shortform_parser.add_argument(
        "--style",
        choices=["cinematic", "minimal", "vibrant", "abstract"],
        default="cinematic",
        help="Visual style (default: cinematic)",
    )
    shortform_parser.add_argument(
        "--quality",
        choices=["draft", "standard", "ultra"],
        default="standard",
        help="Quality tier (default: standard)\n"
        "  draft: Fast (~3s/image), social media\n"
        "  standard: Balanced (~6s/image), social + print\n"
        "  ultra: Maximum (~25s/image), gallery + cinema",
    )
    shortform_parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cli = GenerateCLI()

    if args.command == "image":
        cli.generate_image(
            model=args.model,
            prompt=args.prompt,
            quality=args.quality,
            steps=args.steps,
            guidance=args.guidance,
            height=args.height,
            width=args.width,
            seed=args.seed,
            output_format=args.format,
        )
    elif args.command == "video":
        cli.generate_video(
            approach=args.approach,
            prompt=args.prompt,
            duration=args.duration,
            fps=args.fps,
            width=args.width,
            height=args.height,
            output_format=args.format,
        )
    elif args.command == "analyze":
        cli.analyze_screenshot(
            image_path=args.image_path,
            model_size=args.model_size,
            confidence=args.confidence,
            output_format=args.format,
        )
    elif args.command == "shortform":
        cli.generate_shortform_video(
            script=args.script,
            platform=args.platform,
            voice=args.voice,
            style=args.style,
            quality=args.quality,
            output_format=args.format,
        )


if __name__ == "__main__":
    main()
