#!/usr/bin/env python3
"""
Sovereign Image Generation Module

Direct metal image generation without corporate wrapper bullshit.
Based on expert recommendations for RTX 5070 Ti with 16GB VRAM.

@llm-type service.image-gen
@llm-does sovereign image generation without corporate wrapper bullshit
"""

import torch
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging

try:
    from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
    from diffusers import StableDiffusionXLPipeline
    import safetensors.torch
    from PIL import Image
    import omegaconf
except ImportError as e:
    print(f"⚠️ Image generation dependencies not available: {e}")
    print("💡 Run: pip install -r build/requirements-image-gen-core.txt")

@dataclass
class ImageGenerationConfig:
    """Configuration for image generation."""
    model_name: str = "stabilityai/stable-diffusion-xl-base-1.0"
    model_path: Optional[Path] = None
    cache_dir: Path = Path.home() / ".cache" / "huggingface"
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    dtype: torch.dtype = torch.float16
    enable_xformers: bool = True
    enable_cpu_offload: bool = False
    enable_sequential_cpu_offload: bool = False
    enable_vae_slicing: bool = False
    enable_attention_slicing: bool = False
    scheduler_type: str = "DPMSolver++"
    
    # Default generation parameters
    default_steps: int = 25
    default_guidance_scale: float = 7.5
    default_width: int = 1024
    default_height: int = 1024

@dataclass
class GenerationRequest:
    """Request for image generation."""
    prompt: str
    negative_prompt: str = ""
    width: int = 1024
    height: int = 1024
    num_inference_steps: int = 25
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    batch_size: int = 1

@dataclass
class GenerationResult:
    """Result of image generation."""
    images: List[Image.Image]
    prompt: str
    negative_prompt: str
    parameters: Dict[str, Any]
    generation_time: float
    model_name: str
    seed: int

class SovereignImageGenerator:
    """
    Direct metal image generation - no middlemen.
    
    What you're actually running when you strip away all BS:
    1. Load weights (the actual model)
    2. Text → embeddings (CLIP encoding)
    3. Iterative denoising (UNet + scheduler)
    4. Decode to image (VAE decoder)
    
    That's it. No cloud, no service fees, no API keys.
    Just matrix multiplication on your GPU.
    """
    
    def __init__(self, config: Optional[ImageGenerationConfig] = None):
        self.config = config or ImageGenerationConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Pipeline state
        self.pipe = None
        self.current_model = None
        self.device = self.config.device
        
        # Performance tracking
        self.generation_stats = {
            "total_generations": 0,
            "total_time": 0.0,
            "average_time": 0.0,
            "cache_hits": 0
        }
        
        self.logger.info(f"🎨 Initialized SovereignImageGenerator")
        self.logger.info(f"   Device: {self.device}")
        self.logger.info(f"   Model: {self.config.model_name}")
        self.logger.info(f"   Cache: {self.config.cache_dir}")
    
    def load_model(self, model_name: Optional[str] = None) -> bool:
        """
        Load model weights directly from disk or HuggingFace.
        
        Args:
            model_name: Model to load, defaults to config model
            
        Returns:
            True if loaded successfully
        """
        model_name = model_name or self.config.model_name
        
        if self.current_model == model_name and self.pipe is not None:
            self.logger.debug(f"Model {model_name} already loaded")
            return True
        
        self.logger.info(f"🔄 Loading model: {model_name}")
        start_time = time.time()
        
        try:
            # Configure for RTX 5070 Ti's 16GB VRAM
            if "xl" in model_name.lower():
                self.pipe = StableDiffusionXLPipeline.from_pretrained(
                    model_name,
                    torch_dtype=self.config.dtype,  # Half precision for speed
                    use_safetensors=True,
                    cache_dir=self.config.cache_dir,
                    variant="fp16" if self.config.dtype == torch.float16 else None
                )
            else:
                self.pipe = DiffusionPipeline.from_pretrained(
                    model_name,
                    torch_dtype=self.config.dtype,
                    use_safetensors=True,
                    cache_dir=self.config.cache_dir
                )
            
            # Move to device
            self.pipe = self.pipe.to(self.device)
            
            # Apply optimizations for RTX 5070 Ti
            self._apply_optimizations()
            
            # Set scheduler
            self._configure_scheduler()
            
            self.current_model = model_name
            load_time = time.time() - start_time
            
            self.logger.info(f"✅ Model loaded in {load_time:.2f}s")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load model {model_name}: {e}")
            return False
    
    def _apply_optimizations(self):
        """Apply optimizations for RTX 5070 Ti's 16GB VRAM."""
        if self.pipe is None:
            return
        
        # Enable xformers memory efficient attention (critical for performance)
        if self.config.enable_xformers:
            try:
                self.pipe.enable_xformers_memory_efficient_attention()
                self.logger.debug("✅ Enabled xformers memory efficient attention")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not enable xformers: {e}")
        
        # CPU offloading (not needed with 16GB VRAM but available)
        if self.config.enable_cpu_offload:
            self.pipe.enable_model_cpu_offload()
            self.logger.debug("✅ Enabled model CPU offload")
        
        if self.config.enable_sequential_cpu_offload:
            self.pipe.enable_sequential_cpu_offload()
            self.logger.debug("✅ Enabled sequential CPU offload")
        
        # VAE optimizations (not needed with 16GB VRAM)
        if self.config.enable_vae_slicing:
            self.pipe.enable_vae_slicing()
            self.logger.debug("✅ Enabled VAE slicing")
        
        if self.config.enable_attention_slicing:
            self.pipe.enable_attention_slicing()
            self.logger.debug("✅ Enabled attention slicing")
    
    def _configure_scheduler(self):
        """Configure the diffusion scheduler."""
        if self.pipe is None:
            return
        
        if self.config.scheduler_type == "DPMSolver++":
            # Use faster scheduler (2-3x faster than DDIM)
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config
            )
            self.logger.debug("✅ Configured DPMSolver++ scheduler")
    
    def generate(self, request: Union[GenerationRequest, str]) -> GenerationResult:
        """
        Raw generation - no UI, no bullshit.
        
        Args:
            request: Generation request or simple prompt string
            
        Returns:
            GenerationResult with images and metadata
        """
        # Handle simple string prompt
        if isinstance(request, str):
            request = GenerationRequest(prompt=request)
        
        # Ensure model is loaded
        if not self.load_model():
            raise RuntimeError("Failed to load model")
        
        self.logger.info(f"🎨 Generating: '{request.prompt[:50]}...'")
        start_time = time.time()
        
        # Set seed for reproducibility
        if request.seed is not None:
            torch.manual_seed(request.seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(request.seed)
            generator_seed = request.seed
        else:
            generator_seed = torch.randint(0, 2**32, (1,)).item()
            torch.manual_seed(generator_seed)
        
        # Direct generation with parameters
        try:
            result = self.pipe(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                num_inference_steps=request.num_inference_steps,
                width=request.width,
                height=request.height,
                guidance_scale=request.guidance_scale,
                num_images_per_prompt=request.batch_size
            )
            
            generation_time = time.time() - start_time
            
            # Update stats
            self.generation_stats["total_generations"] += 1
            self.generation_stats["total_time"] += generation_time
            self.generation_stats["average_time"] = (
                self.generation_stats["total_time"] / 
                self.generation_stats["total_generations"]
            )
            
            self.logger.info(f"✅ Generated {len(result.images)} image(s) in {generation_time:.2f}s")
            
            return GenerationResult(
                images=result.images,
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                parameters={
                    "width": request.width,
                    "height": request.height,
                    "num_inference_steps": request.num_inference_steps,
                    "guidance_scale": request.guidance_scale,
                    "batch_size": request.batch_size
                },
                generation_time=generation_time,
                model_name=self.current_model,
                seed=generator_seed
            )
            
        except Exception as e:
            self.logger.error(f"❌ Generation failed: {e}")
            raise
    
    def generate_batch(self, prompts: List[str], **kwargs) -> List[GenerationResult]:
        """
        Batch processing for efficiency.
        
        Args:
            prompts: List of prompts to generate
            **kwargs: Additional parameters for GenerationRequest
            
        Returns:
            List of GenerationResults
        """
        self.logger.info(f"🎨 Batch generating {len(prompts)} images")
        
        results = []
        for i, prompt in enumerate(prompts):
            self.logger.info(f"📸 Generating {i+1}/{len(prompts)}: {prompt[:30]}...")
            
            request = GenerationRequest(prompt=prompt, **kwargs)
            result = self.generate(request)
            results.append(result)
        
        total_time = sum(r.generation_time for r in results)
        self.logger.info(f"✅ Batch completed: {len(results)} images in {total_time:.2f}s")
        
        return results
    
    def save_result(self, result: GenerationResult, output_dir: Path, 
                   filename_prefix: str = "generated") -> List[Path]:
        """
        Save generation result to disk.
        
        Args:
            result: GenerationResult to save
            output_dir: Directory to save images
            filename_prefix: Prefix for filenames
            
        Returns:
            List of saved file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_paths = []
        
        for i, image in enumerate(result.images):
            # Create filename with metadata
            timestamp = int(time.time())
            filename = f"{filename_prefix}_{timestamp}_{result.seed}_{i:02d}.png"
            filepath = output_dir / filename
            
            # Save image
            image.save(filepath)
            saved_paths.append(filepath)
            
            # Save metadata
            metadata = {
                "prompt": result.prompt,
                "negative_prompt": result.negative_prompt,
                "parameters": result.parameters,
                "generation_time": result.generation_time,
                "model_name": result.model_name,
                "seed": result.seed,
                "timestamp": timestamp
            }
            
            metadata_path = filepath.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        self.logger.info(f"💾 Saved {len(saved_paths)} images to {output_dir}")
        return saved_paths
    
    def get_stats(self) -> Dict[str, Any]:
        """Get generation statistics."""
        return {
            **self.generation_stats,
            "current_model": self.current_model,
            "device": self.device,
            "config": {
                "model_name": self.config.model_name,
                "dtype": str(self.config.dtype),
                "optimizations": {
                    "xformers": self.config.enable_xformers,
                    "cpu_offload": self.config.enable_cpu_offload,
                    "vae_slicing": self.config.enable_vae_slicing
                }
            }
        }
    
    def clear_cache(self):
        """Clear GPU memory cache."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            self.logger.info("🗑️ Cleared GPU memory cache")

# Convenience functions for quick usage
def generate_image(prompt: str, **kwargs) -> GenerationResult:
    """Quick image generation function."""
    generator = SovereignImageGenerator()
    request = GenerationRequest(prompt=prompt, **kwargs)
    return generator.generate(request)

def generate_images(prompts: List[str], **kwargs) -> List[GenerationResult]:
    """Quick batch image generation function."""
    generator = SovereignImageGenerator()
    return generator.generate_batch(prompts, **kwargs)
