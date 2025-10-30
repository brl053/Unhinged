#!/usr/bin/env python3
"""
Image Generation Service

FastAPI service for sovereign image generation.
Integrates with the build system and provides REST API for image generation.

@llm-type service.image-generation
@llm-does REST API for sovereign image generation without corporate APIs
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.responses import FileResponse, JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("⚠️ FastAPI dependencies not available. Install with: pip install fastapi uvicorn")
    exit(1)

# Import our sovereign image generation module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "build"))

try:
    from modules.image_generation import (
        SovereignImageGenerator, 
        ImageGenerationConfig,
        GenerationRequest,
        GenerationResult
    )
except ImportError as e:
    print(f"⚠️ Image generation module not available: {e}")
    print("💡 Make sure the build system is set up correctly")

# Pydantic models for API
class ImageGenerationAPIRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    width: int = 1024
    height: int = 1024
    num_inference_steps: int = 25
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    batch_size: int = 1

class ImageGenerationAPIResponse(BaseModel):
    success: bool
    message: str
    images: List[str] = []  # File paths or base64 encoded images
    generation_time: float = 0.0
    parameters: Dict[str, Any] = {}
    seed: Optional[int] = None

class BatchGenerationRequest(BaseModel):
    prompts: List[str]
    negative_prompt: str = ""
    width: int = 1024
    height: int = 1024
    num_inference_steps: int = 25
    guidance_scale: float = 7.5

# Global generator instance
generator: Optional[SovereignImageGenerator] = None
output_dir = Path("/output/images")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup the image generator."""
    global generator
    
    # Startup
    logging.info("🚀 Starting Image Generation Service")
    
    try:
        # Initialize generator with production config
        config = ImageGenerationConfig(
            model_name="stabilityai/stable-diffusion-xl-base-1.0",
            device="cuda" if torch.cuda.is_available() else "cpu",
            dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            enable_xformers=torch.cuda.is_available(),
            cache_dir=Path.home() / ".cache" / "huggingface"
        )
        
        generator = SovereignImageGenerator(config)
        
        # Pre-load model for faster first generation
        if generator.load_model():
            logging.info("✅ Image generator initialized and model loaded")
        else:
            logging.warning("⚠️ Image generator initialized but model loading failed")
            
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
    except Exception as e:
        logging.error(f"❌ Failed to initialize image generator: {e}")
        generator = None
    
    yield
    
    # Shutdown
    logging.info("🛑 Shutting down Image Generation Service")
    if generator:
        generator.clear_cache()

# Create FastAPI app
app = FastAPI(
    title="Sovereign Image Generation API",
    description="Direct metal image generation without corporate wrapper bullshit",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Sovereign Image Generation API",
        "version": "1.0.0",
        "description": "Direct metal image generation - no middlemen",
        "status": "ready" if generator else "not_ready",
        "gpu_available": torch.cuda.is_available() if 'torch' in globals() else False
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not generator:
        raise HTTPException(status_code=503, detail="Image generator not initialized")
    
    stats = generator.get_stats()
    return {
        "status": "healthy",
        "generator_ready": generator.current_model is not None,
        "current_model": generator.current_model,
        "device": generator.device,
        "stats": stats
    }

@app.post("/generate", response_model=ImageGenerationAPIResponse)
async def generate_image(request: ImageGenerationAPIRequest, background_tasks: BackgroundTasks):
    """Generate a single image or batch of images."""
    if not generator:
        raise HTTPException(status_code=503, detail="Image generator not initialized")
    
    try:
        # Convert API request to internal request
        gen_request = GenerationRequest(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            seed=request.seed,
            batch_size=request.batch_size
        )
        
        # Generate image(s)
        result = generator.generate(gen_request)
        
        # Save images to disk
        saved_paths = generator.save_result(result, output_dir, "api_generated")
        
        # Return response
        return ImageGenerationAPIResponse(
            success=True,
            message=f"Generated {len(result.images)} image(s) successfully",
            images=[str(path) for path in saved_paths],
            generation_time=result.generation_time,
            parameters=result.parameters,
            seed=result.seed
        )
        
    except Exception as e:
        logging.error(f"❌ Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@app.post("/generate/batch")
async def generate_batch(request: BatchGenerationRequest):
    """Generate multiple images from multiple prompts."""
    if not generator:
        raise HTTPException(status_code=503, detail="Image generator not initialized")
    
    try:
        # Generate batch
        results = generator.generate_batch(
            request.prompts,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale
        )
        
        # Save all results
        all_paths = []
        total_time = 0.0
        
        for i, result in enumerate(results):
            saved_paths = generator.save_result(result, output_dir, f"batch_{i}")
            all_paths.extend(saved_paths)
            total_time += result.generation_time
        
        return {
            "success": True,
            "message": f"Generated {len(all_paths)} images from {len(request.prompts)} prompts",
            "images": [str(path) for path in all_paths],
            "total_generation_time": total_time,
            "average_time_per_image": total_time / len(all_paths) if all_paths else 0
        }
        
    except Exception as e:
        logging.error(f"❌ Batch generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")

@app.get("/image/{filename}")
async def get_image(filename: str):
    """Serve generated images."""
    image_path = output_dir / filename
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path)

@app.get("/stats")
async def get_stats():
    """Get generation statistics."""
    if not generator:
        raise HTTPException(status_code=503, detail="Image generator not initialized")
    
    return generator.get_stats()

@app.post("/clear-cache")
async def clear_cache():
    """Clear GPU memory cache."""
    if not generator:
        raise HTTPException(status_code=503, detail="Image generator not initialized")
    
    generator.clear_cache()
    return {"message": "Cache cleared successfully"}

@app.get("/models")
async def list_models():
    """List available models."""
    # In production, this would scan for available models
    return {
        "available_models": [
            "stabilityai/stable-diffusion-xl-base-1.0",
            "runwayml/stable-diffusion-v1-5",
            # Add more models as they become available
        ],
        "current_model": generator.current_model if generator else None
    }

# Development server
if __name__ == "__main__":
    import torch
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run server
    uvicorn.run(
        "image_gen_service:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
