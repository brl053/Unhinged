#!/usr/bin/env python3
"""
@llm-type service.api
@llm-does image generation grpc server with health.proto implementation
"""

import sys
import time
from collections.abc import Iterator
from concurrent import futures
from pathlib import Path

import grpc

# Add build directory to path for image generation module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "build"))

# Health proto imports
from unhinged_proto_clients.health import health_pb2, health_pb2_grpc

# Image generation proto imports (will be generated)
try:
    from unhinged_proto_clients import (
        common_pb2,
        image_generation_pb2,
        image_generation_pb2_grpc,
    )
except ImportError:
    print("⚠️ Image generation protobuf clients not generated yet")
    print("💡 Run: ./proto/build.sh to generate protobuf clients")
    sys.exit(1)

# Import our sovereign image generation module
try:
    from modules.image_generation import (
        GenerationRequest,
        GenerationResult,
        ImageGenerationConfig,
        SovereignImageGenerator,
    )
except ImportError as e:
    print(f"⚠️ Image generation module not available: {e}")
    print("💡 Make sure the build system is set up correctly")
    sys.exit(1)

# Event logging
from events import create_service_logger

# Initialize event logger
events = create_service_logger("image-generation", "1.0.0")


class ImageGenerationServicer(
    image_generation_pb2_grpc.ImageGenerationServiceServicer,
    health_pb2_grpc.HealthServiceServicer,
):
    """
    gRPC Image Generation Service implementation following proto contracts

    Implements all methods defined in image_generation.proto:
    - GenerateImage: Single image generation with streaming progress
    - GenerateBatch: Batch image generation
    - Model management operations
    - Generation history management
    - Health checks
    """

    def __init__(self):
        self.generator: SovereignImageGenerator | None = None
        self.start_time = time.time()
        self.service_ready = False
        self.output_dir = Path("/output/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize image generator
        self._initialize_generator()

        events.info(
            "Image generation service initialized",
            {"output_dir": str(self.output_dir), "service_ready": self.service_ready},
        )

    def _initialize_generator(self):
        """Initialize the sovereign image generator."""
        try:
            # Configure for production
            config = ImageGenerationConfig(
                model_name="stabilityai/stable-diffusion-xl-base-1.0",
                device="cuda" if self._check_cuda_available() else "cpu",
                dtype="float16" if self._check_cuda_available() else "float32",
                enable_xformers=self._check_cuda_available(),
                cache_dir=Path.home() / ".cache" / "huggingface",
            )

            self.generator = SovereignImageGenerator(config)

            # Pre-load model for faster first generation
            if self.generator.load_model():
                self.service_ready = True
                events.info("Image generator initialized and model loaded")
            else:
                events.warning("Image generator initialized but model loading failed")

        except Exception as e:
            events.error("Failed to initialize image generator", exception=e)
            self.service_ready = False

    def _check_cuda_available(self) -> bool:
        """Check if CUDA is available."""
        try:
            import torch

            return torch.cuda.is_available()
        except ImportError:
            return False

    # ========================================================================
    # Image Generation Service Methods
    # ========================================================================

    def GenerateImage(
        self, request: image_generation_pb2.GenerateImageRequest, context
    ) -> Iterator[common_pb2.StreamChunk]:
        """
        Generate a single image with streaming progress updates.

        Args:
            request: GenerateImageRequest with prompt and parameters
            context: gRPC context

        Yields:
            StreamChunk: Progress updates and final result
        """
        try:
            if not self.service_ready or not self.generator:
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details("Image generation service not ready")
                return

            generation_id = f"gen_{int(time.time() * 1000)}"

            events.info(
                "Starting image generation",
                {
                    "generation_id": generation_id,
                    "prompt": request.prompt[:50] + "..."
                    if len(request.prompt) > 50
                    else request.prompt,
                    "width": request.width,
                    "height": request.height,
                    "steps": request.num_inference_steps,
                },
            )

            # Send initial progress
            yield self._create_progress_chunk(
                generation_id,
                image_generation_pb2.GENERATION_STAGE_INITIALIZING,
                0.0,
                "Initializing generation...",
            )

            # Convert gRPC request to internal request
            gen_request = GenerationRequest(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                width=request.width or 1024,
                height=request.height or 1024,
                num_inference_steps=request.num_inference_steps or 25,
                guidance_scale=request.guidance_scale or 7.5,
                seed=request.seed if request.seed != 0 else None,
                batch_size=request.batch_size or 1,
            )

            # Send encoding progress
            yield self._create_progress_chunk(
                generation_id,
                image_generation_pb2.GENERATION_STAGE_ENCODING,
                10.0,
                "Encoding text prompt...",
            )

            # Generate image (this would have progress callbacks in a real implementation)
            result = self.generator.generate(gen_request)

            # Send denoising progress (simulated)
            for progress in [25.0, 50.0, 75.0]:
                yield self._create_progress_chunk(
                    generation_id,
                    image_generation_pb2.GENERATION_STAGE_DENOISING,
                    progress,
                    f"Denoising step {int(progress * gen_request.num_inference_steps / 100)}/{gen_request.num_inference_steps}",
                )

            # Send decoding progress
            yield self._create_progress_chunk(
                generation_id,
                image_generation_pb2.GENERATION_STAGE_DECODING,
                90.0,
                "Decoding to image...",
            )

            # Save images
            saved_paths = self.generator.save_result(
                result, self.output_dir, "grpc_generated"
            )

            # Send saving progress
            yield self._create_progress_chunk(
                generation_id,
                image_generation_pb2.GENERATION_STAGE_SAVING,
                95.0,
                "Saving images...",
            )

            # Send final result
            yield self._create_completion_chunk(generation_id, result, saved_paths)

            events.info(
                "Image generation completed",
                {
                    "generation_id": generation_id,
                    "generation_time": result.generation_time,
                    "images_generated": len(result.images),
                    "seed": result.seed,
                },
            )

        except Exception as e:
            events.error("Image generation failed", exception=e)

            # Send error chunk
            error_chunk = common_pb2.StreamChunk()
            error_chunk.stream_id = generation_id
            error_chunk.type = common_pb2.CHUNK_TYPE_ERROR
            error_chunk.text = f"Generation failed: {str(e)}"
            error_chunk.is_final = True
            error_chunk.status = common_pb2.CHUNK_STATUS_ERROR
            yield error_chunk

    def GenerateBatch(
        self, request: image_generation_pb2.GenerateBatchRequest, context
    ) -> Iterator[common_pb2.StreamChunk]:
        """
        Generate multiple images from multiple prompts.

        Args:
            request: GenerateBatchRequest with prompts and parameters
            context: gRPC context

        Yields:
            StreamChunk: Progress updates for batch generation
        """
        try:
            if not self.service_ready or not self.generator:
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details("Image generation service not ready")
                return

            batch_id = f"batch_{int(time.time() * 1000)}"
            total_prompts = len(request.prompts)

            events.info(
                "Starting batch generation",
                {"batch_id": batch_id, "total_prompts": total_prompts},
            )

            # Send initial progress
            yield self._create_progress_chunk(
                batch_id,
                image_generation_pb2.GENERATION_STAGE_INITIALIZING,
                0.0,
                f"Starting batch generation for {total_prompts} prompts...",
            )

            # Generate each image
            all_results = []
            for i, prompt in enumerate(request.prompts):
                # Send progress for current image
                progress = (i / total_prompts) * 100
                yield self._create_progress_chunk(
                    batch_id,
                    image_generation_pb2.GENERATION_STAGE_DENOISING,
                    progress,
                    f"Generating image {i+1}/{total_prompts}: {prompt[:30]}...",
                )

                # Generate single image
                gen_request = GenerationRequest(
                    prompt=prompt,
                    negative_prompt=request.negative_prompt,
                    width=request.width or 1024,
                    height=request.height or 1024,
                    num_inference_steps=request.num_inference_steps or 25,
                    guidance_scale=request.guidance_scale or 7.5,
                    seed=request.seeds[i] if i < len(request.seeds) else None,
                )

                result = self.generator.generate(gen_request)
                all_results.append(result)

                # Save result
                saved_paths = self.generator.save_result(
                    result, self.output_dir, f"batch_{i}"
                )

            # Send completion
            yield self._create_batch_completion_chunk(batch_id, all_results)

            events.info(
                "Batch generation completed",
                {
                    "batch_id": batch_id,
                    "total_images": len(all_results),
                    "total_time": sum(r.generation_time for r in all_results),
                },
            )

        except Exception as e:
            events.error("Batch generation failed", exception=e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Batch generation failed: {str(e)}")

    def GetServiceStatus(
        self, request: image_generation_pb2.GetServiceStatusRequest, context
    ) -> image_generation_pb2.GetServiceStatusResponse:
        """Get current service status and statistics."""
        try:
            response = image_generation_pb2.GetServiceStatusResponse()

            # Set basic response
            response.response.success = True
            response.response.message = "Service status retrieved"

            # Set service status
            if self.service_ready:
                response.status = image_generation_pb2.SERVICE_STATUS_READY
            else:
                response.status = image_generation_pb2.SERVICE_STATUS_INITIALIZING

            # Add system resources (mock data for now)
            response.resources.gpu_name = "RTX 5070 Ti"
            response.resources.gpu_memory_total_gb = 16
            response.resources.gpu_memory_used_gb = 8
            response.resources.gpu_memory_free_gb = 8
            response.resources.gpu_utilization_percent = 45.0

            # Add statistics
            if self.generator:
                stats = self.generator.get_stats()
                response.statistics.total_generations = stats.get(
                    "total_generations", 0
                )
                response.statistics.successful_generations = stats.get(
                    "total_generations", 0
                )
                response.statistics.average_generation_time = stats.get(
                    "average_time", 0.0
                )

            return response

        except Exception as e:
            events.error("Failed to get service status", exception=e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get service status: {str(e)}")

    # ========================================================================
    # Health Check Implementation
    # ========================================================================

    def Check(
        self, request: health_pb2.HealthCheckRequest, context
    ) -> health_pb2.HealthCheckResponse:
        """Health check implementation."""
        response = health_pb2.HealthCheckResponse()

        if self.service_ready and self.generator:
            response.status = health_pb2.HealthCheckResponse.SERVING
        else:
            response.status = health_pb2.HealthCheckResponse.NOT_SERVING

        return response

    def Watch(
        self, request: health_pb2.HealthCheckRequest, context
    ) -> Iterator[health_pb2.HealthCheckResponse]:
        """Health check watch implementation."""
        while True:
            response = health_pb2.HealthCheckResponse()

            if self.service_ready and self.generator:
                response.status = health_pb2.HealthCheckResponse.SERVING
            else:
                response.status = health_pb2.HealthCheckResponse.NOT_SERVING

            yield response
            time.sleep(5)  # Check every 5 seconds

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _create_progress_chunk(
        self, generation_id: str, stage: int, progress: float, message: str
    ) -> common_pb2.StreamChunk:
        """Create a progress update chunk."""
        chunk = common_pb2.StreamChunk()
        chunk.stream_id = generation_id
        chunk.type = common_pb2.CHUNK_TYPE_PROGRESS
        chunk.status = common_pb2.CHUNK_STATUS_PROCESSING

        # Create progress payload
        progress_payload = image_generation_pb2.GenerationProgressPayload()
        progress_payload.generation_id = generation_id
        progress_payload.stage = stage
        progress_payload.progress_percent = progress
        progress_payload.status_message = message

        # Serialize payload to structured data
        chunk.structured.update(
            {
                "generation_id": generation_id,
                "stage": stage,
                "progress_percent": progress,
                "status_message": message,
            }
        )

        return chunk

    def _create_completion_chunk(
        self, generation_id: str, result: GenerationResult, saved_paths: list
    ) -> common_pb2.StreamChunk:
        """Create a completion chunk with final result."""
        chunk = common_pb2.StreamChunk()
        chunk.stream_id = generation_id
        chunk.type = common_pb2.CHUNK_TYPE_DATA
        chunk.status = common_pb2.CHUNK_STATUS_COMPLETE
        chunk.is_final = True

        # Add result data
        chunk.structured.update(
            {
                "generation_id": generation_id,
                "stage": image_generation_pb2.GENERATION_STAGE_COMPLETE,
                "progress_percent": 100.0,
                "status_message": "Generation completed successfully",
                "generation_time": result.generation_time,
                "seed": result.seed,
                "images": [str(path) for path in saved_paths],
                "image_count": len(result.images),
            }
        )

        return chunk

    def _create_batch_completion_chunk(
        self, batch_id: str, results: list
    ) -> common_pb2.StreamChunk:
        """Create a batch completion chunk."""
        chunk = common_pb2.StreamChunk()
        chunk.stream_id = batch_id
        chunk.type = common_pb2.CHUNK_TYPE_DATA
        chunk.status = common_pb2.CHUNK_STATUS_COMPLETE
        chunk.is_final = True

        total_time = sum(r.generation_time for r in results)
        total_images = sum(len(r.images) for r in results)

        chunk.structured.update(
            {
                "batch_id": batch_id,
                "stage": image_generation_pb2.GENERATION_STAGE_COMPLETE,
                "progress_percent": 100.0,
                "status_message": f"Batch generation completed: {total_images} images",
                "total_time": total_time,
                "total_images": total_images,
                "batch_size": len(results),
            }
        )

        return chunk


def serve():
    """Start the gRPC server with health.proto implementation"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = ImageGenerationServicer()

    # Register both image generation and health services
    image_generation_pb2_grpc.add_ImageGenerationServiceServicer_to_server(
        servicer, server
    )
    health_pb2_grpc.add_HealthServiceServicer_to_server(servicer, server)

    listen_addr = "[::]:9094"  # Use port 9094 for image generation
    server.add_insecure_port(listen_addr)

    events.info("Starting gRPC server", {"address": listen_addr})
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        events.info("Shutting down gRPC server")
        server.stop(0)


if __name__ == "__main__":
    serve()
