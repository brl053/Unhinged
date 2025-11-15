#!/usr/bin/env python3
"""
Image Generation Service

GPU-accelerated image generation using Stable Diffusion.
Smallest, fastest, least resource-intensive model for benchmarking.

Philosophy: Start with the smallest, fastest model (like running Doom on everything).
Then benchmark and allow users to choose larger models later.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import torch
from diffusers import StableDiffusionPipeline

logger = logging.getLogger(__name__)


class ImageGenerationService:
    """GPU-accelerated image generation using Stable Diffusion"""

    # Model configuration - smallest, fastest model
    MODEL_ID = "runwayml/stable-diffusion-v1-5"

    def __init__(self, output_dir: Path | None = None):
        """
        Initialize image generation service.

        Args:
            output_dir: Directory to save generated images.
                       Defaults to /build/tmp/generated_images/
        """
        self.output_dir = output_dir or Path.cwd() / "build" / "tmp" / "generated_images"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.gpu_available = torch.cuda.is_available()

        logger.info("Image Generation Service initialized")
        logger.info(f"Device: {self.device}")
        logger.info(f"GPU Available: {self.gpu_available}")
        logger.info(f"Output directory: {self.output_dir}")

        # Benchmark tracking
        self.generation_times = []
        self.total_generations = 0

    def _load_pipeline(self):
        """Load Stable Diffusion pipeline (lazy loading)"""
        if self.pipeline is None:
            logger.info(f"Loading Stable Diffusion model: {self.MODEL_ID}")

            try:
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    self.MODEL_ID,
                    torch_dtype=torch.float16 if self.gpu_available else torch.float32,
                    safety_checker=None,  # Disable safety checker for speed
                    requires_safety_checker=False,
                )

                self.pipeline = self.pipeline.to(self.device)

                # Enable memory optimization
                if self.gpu_available:
                    self.pipeline.enable_attention_slicing()
                    logger.info("Attention slicing enabled for memory optimization")

                logger.info("Stable Diffusion pipeline loaded successfully")

            except Exception as e:
                logger.error(f"Failed to load pipeline: {e}")
                raise

    def generate_image(
        self,
        prompt: str,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        height: int = 512,
        width: int = 512,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """
        Generate an image from a text prompt.

        Args:
            prompt: Text description of image to generate
            num_inference_steps: Number of inference steps (20-50, lower=faster)
            guidance_scale: How closely to follow prompt (7.5 is default)
            height: Image height in pixels (must be multiple of 8)
            width: Image width in pixels (must be multiple of 8)
            seed: Random seed for reproducibility

        Returns:
            Dict with:
                - image_path: Path to saved image
                - prompt: The prompt used
                - generation_time: Time taken in seconds
                - model: Model used
                - device: Device used (cuda/cpu)
                - metadata: Additional metadata
        """
        import time

        try:
            # Load pipeline if not already loaded
            self._load_pipeline()

            # Set seed for reproducibility
            if seed is not None:
                torch.manual_seed(seed)
                if self.gpu_available:
                    torch.cuda.manual_seed(seed)

            logger.info(f"Generating image: {prompt[:50]}...")
            start_time = time.time()

            # Generate image
            with torch.no_grad():
                result = self.pipeline(
                    prompt=prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    height=height,
                    width=width,
                )

            image = result.images[0]
            generation_time = time.time() - start_time

            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"generated_{timestamp}.png"
            image_path = self.output_dir / image_filename

            image.save(str(image_path))
            logger.info(f"Image saved: {image_path}")

            # Track benchmark data
            self.generation_times.append(generation_time)
            self.total_generations += 1

            return {
                "image_path": str(image_path),
                "image_filename": image_filename,
                "prompt": prompt,
                "generation_time": generation_time,
                "model": self.MODEL_ID,
                "device": self.device,
                "gpu_available": self.gpu_available,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "height": height,
                "width": width,
                "timestamp": timestamp,
                "metadata": {
                    "total_generations": self.total_generations,
                    "average_generation_time": sum(self.generation_times)
                    / len(self.generation_times)
                    if self.generation_times
                    else 0,
                },
            }

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise

    def get_benchmark_stats(self) -> dict[str, Any]:
        """Get benchmark statistics"""
        if not self.generation_times:
            return {
                "total_generations": 0,
                "average_generation_time": 0,
                "min_generation_time": 0,
                "max_generation_time": 0,
            }

        return {
            "total_generations": self.total_generations,
            "average_generation_time": sum(self.generation_times) / len(self.generation_times),
            "min_generation_time": min(self.generation_times),
            "max_generation_time": max(self.generation_times),
            "device": self.device,
            "gpu_available": self.gpu_available,
        }

    def cleanup(self):
        """Clean up GPU memory"""
        if self.pipeline is not None:
            del self.pipeline
            if self.gpu_available:
                torch.cuda.empty_cache()
            logger.info("Pipeline cleaned up, GPU memory freed")
