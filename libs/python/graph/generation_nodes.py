"""Generation nodes for content creation (text, image, audio, video).

@llm-type graph.generation
@llm-does provides GenerationNode base class and modality-specific subclasses

This module contains the GenerationNode abstract base class and its subclasses
for different content generation modalities. Each node type wraps a corresponding
service from libs.python.clients and provides template interpolation for prompts.

Node types:
- GenerationNode: Abstract base with template interpolation
- TextGenerationNode: Text/LLM generation via TextGenerationService
- ImageGenerationNode: Image generation via ImageGenerationService
- AudioGenerationNode: TTS/audio generation via TTSService
- VideoGenerationNode: Video generation via VideoGenerationService
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .nodes import GraphNode

if TYPE_CHECKING:
    from .context import SessionContext


class GenerationNode(GraphNode):
    """Abstract base for content generation nodes (text, image, audio, video).

    Provides common infrastructure for all generation modalities:
    - Template interpolation for prompts via {{session.*}}, {{node_id.*}}, {{input.*}}
    - Output directory management
    - Consistent output format with file_path, stdout, success keys

    Subclasses implement _generate() to call their specific service.

    Configuration:
    - prompt_template: Template string with {{...}} placeholders
    - output_dir: Directory for generated files (optional, uses service default)

    Output keys (subclasses may add more):
    - ``stdout``: Primary output (text or file path)
    - ``success``: Boolean indicating success
    - ``prompt``: The interpolated prompt used
    """

    def __init__(
        self,
        node_id: str,
        prompt_template: str = "{{input.topic}}",
        output_dir: str | None = None,
    ) -> None:
        super().__init__(node_id)
        self.prompt_template = prompt_template
        self.output_dir = output_dir
        self._session: SessionContext | None = None

    def set_session(self, session: SessionContext | None) -> None:
        """Set session context for template interpolation."""
        self._session = session

    def hydrate(self, input_data: dict[str, Any] | None = None) -> dict[str, str]:
        """Return the hydrated (interpolated) prompt without executing.

        Returns:
            Dict with 'prompt' key containing the interpolated prompt.
        """
        from libs.python.graph.template import interpolate

        input_data = input_data or {}
        prompt = interpolate(
            template=self.prompt_template,
            nodes=input_data,
            session=self._session,
        )
        return {"prompt": prompt}

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute generation with interpolated prompt.

        Calls _generate() which subclasses implement for their modality.
        """
        from libs.python.graph.template import interpolate

        input_data = input_data or {}

        # Interpolate prompt template
        prompt = interpolate(
            template=self.prompt_template,
            nodes=input_data,
            session=self._session,
        )

        try:
            result = await self._generate(prompt)
            result["prompt"] = prompt
            result["success"] = result.get("success", True)
            return result
        except Exception as exc:
            return {
                "stdout": "",
                "prompt": prompt,
                "error": str(exc),
                "success": False,
            }

    async def _generate(self, prompt: str) -> dict[str, Any]:
        """Subclasses implement this to call their generation service.

        Args:
            prompt: The interpolated prompt string.

        Returns:
            Dict with at least 'stdout' key. File-based outputs include 'file_path'.
        """
        raise NotImplementedError("Subclasses must implement _generate()")


class TextGenerationNode(GenerationNode):
    """Generation node for text/LLM output.

    Wraps TextGenerationService for graph-based text generation.
    Unlike LLMNode, this is designed for simple prompt-in/text-out generation
    without system prompts or complex configuration.

    Configuration:
    - prompt_template: Template with {{...}} placeholders
    - model: LLM model name (default: llama2)
    - provider: LLM provider (default: ollama)
    - max_tokens: Maximum tokens in response (default: 1024)
    - temperature: Sampling temperature (default: 0.7)

    Output keys:
    - ``stdout``: Generated text
    - ``text``: Same as stdout (alias)
    - ``prompt``: The interpolated prompt
    - ``model``: Model used
    - ``provider``: Provider used
    - ``success``: Boolean
    """

    def __init__(
        self,
        node_id: str,
        prompt_template: str = "{{input.topic}}",
        model: str = "llama2",
        provider: str = "ollama",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        output_dir: str | None = None,
    ) -> None:
        super().__init__(node_id, prompt_template, output_dir)
        self.model = model
        self.provider = provider
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def _generate(self, prompt: str) -> dict[str, Any]:
        """Generate text using TextGenerationService."""
        from libs.python.clients.text_generation_service import TextGenerationService

        service = TextGenerationService(model=self.model, provider=self.provider)
        text = service.generate(
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        return {
            "stdout": text,
            "text": text,
            "model": self.model,
            "provider": self.provider,
        }


class ImageGenerationNode(GenerationNode):
    """Generation node for image output.

    Wraps ImageGenerationService for graph-based image generation.

    Configuration:
    - prompt_template: Template with {{...}} placeholders
    - width: Image width in pixels (default: 512)
    - height: Image height in pixels (default: 512)
    - num_inference_steps: Diffusion steps (default: 20)
    - guidance_scale: Prompt adherence (default: 7.5)

    Output keys:
    - ``stdout``: Path to generated image (for piping)
    - ``file_path``: Same as stdout
    - ``prompt``: The interpolated prompt
    - ``success``: Boolean
    """

    def __init__(
        self,
        node_id: str,
        prompt_template: str = "{{input.topic}}",
        width: int = 512,
        height: int = 512,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        output_dir: str | None = None,
    ) -> None:
        super().__init__(node_id, prompt_template, output_dir)
        self.width = width
        self.height = height
        self.num_inference_steps = num_inference_steps
        self.guidance_scale = guidance_scale

    async def _generate(self, prompt: str) -> dict[str, Any]:
        """Generate image using ImageGenerationService."""
        from pathlib import Path

        from libs.python.clients.image_generation_service import ImageGenerationService

        output_path = Path(self.output_dir) if self.output_dir else None
        service = ImageGenerationService(output_dir=output_path)

        result = service.generate_image(
            prompt=prompt,
            width=self.width,
            height=self.height,
            num_inference_steps=self.num_inference_steps,
            guidance_scale=self.guidance_scale,
        )

        image_path = result.get("image_path", "")
        return {
            "stdout": image_path,
            "file_path": image_path,
            "metadata": result.get("metadata", {}),
        }


class AudioGenerationNode(GenerationNode):
    """Generation node for audio/TTS output.

    Wraps TTSService for graph-based text-to-speech generation.

    Configuration:
    - prompt_template: Template with {{...}} placeholders (text to speak)
    - voice: Voice to use (nova, echo, sage, shimmer) (default: nova)
    - speed: Speech speed 0.5-2.0 (default: 1.0)

    Output keys:
    - ``stdout``: Path to generated audio file (for piping)
    - ``file_path``: Same as stdout
    - ``duration``: Audio duration in seconds
    - ``prompt``: The interpolated text
    - ``success``: Boolean
    """

    def __init__(
        self,
        node_id: str,
        prompt_template: str = "{{input.topic}}",
        voice: str = "nova",
        speed: float = 1.0,
        output_dir: str | None = None,
    ) -> None:
        super().__init__(node_id, prompt_template, output_dir)
        self.voice = voice
        self.speed = speed

    async def _generate(self, prompt: str) -> dict[str, Any]:
        """Generate audio using TTSService."""
        from pathlib import Path

        from libs.python.clients.tts_service import TTSService

        output_path = Path(self.output_dir) if self.output_dir else None
        service = TTSService(output_dir=output_path)

        result = service.generate_voiceover(
            text=prompt,
            voice=self.voice,
            speed=self.speed,
        )

        audio_path = result.get("audio_path", "")
        return {
            "stdout": audio_path,
            "file_path": audio_path,
            "duration": result.get("duration", 0.0),
            "voice": self.voice,
        }


class VideoGenerationNode(GenerationNode):
    """Generation node for video output.

    Wraps VideoGenerationService for graph-based video generation.

    Configuration:
    - prompt_template: Template with {{...}} placeholders
    - approach: Generation approach (frame-interp, svd) (default: frame-interp)
    - duration: Video duration in seconds (default: 5)
    - fps: Frames per second (default: 24)
    - width: Video width in pixels (default: 512)
    - height: Video height in pixels (default: 512)

    Output keys:
    - ``stdout``: Path to generated video file (for piping)
    - ``file_path``: Same as stdout
    - ``duration``: Video duration in seconds
    - ``prompt``: The interpolated prompt
    - ``success``: Boolean
    """

    def __init__(
        self,
        node_id: str,
        prompt_template: str = "{{input.topic}}",
        approach: str = "frame-interp",
        duration: int = 5,
        fps: int = 24,
        width: int = 512,
        height: int = 512,
        output_dir: str | None = None,
    ) -> None:
        super().__init__(node_id, prompt_template, output_dir)
        self.approach = approach
        self.duration = duration
        self.fps = fps
        self.width = width
        self.height = height

    async def _generate(self, prompt: str) -> dict[str, Any]:
        """Generate video using VideoGenerationService."""
        from pathlib import Path

        from libs.python.clients.video_generation_service import VideoGenerationService

        output_path = Path(self.output_dir) if self.output_dir else None
        service = VideoGenerationService(output_dir=output_path)

        result = service.generate_video(
            prompt=prompt,
            approach=self.approach,
            duration=self.duration,
            fps=self.fps,
            width=self.width,
            height=self.height,
        )

        video_path = result.get("video_path", "")
        return {
            "stdout": video_path,
            "file_path": video_path,
            "duration": result.get("duration", 0.0),
            "approach": self.approach,
        }
