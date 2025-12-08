"""Driver wrapping TextGenerationService for graph/APINode usage.

@llm-type library.drivers.llm.text
@llm-does provide text generation operations for graphs and workflows
"""

from __future__ import annotations

from typing import Any

from libs.python.drivers.base import Driver, DriverCapability, DriverError
from libs.services.text_generation_service import TextGenerationService


class LLMTextGenerationDriver(Driver):
    """Driver that exposes TextGenerationService via the driver registry.

    Supported operations:

    - generate_summary: params={prompt: str, max_tokens?: int, temperature?: float}
    """

    def __init__(self, driver_id: str = "llm.text") -> None:
        super().__init__(driver_id)

    def get_capabilities(self) -> list[DriverCapability]:
        return [DriverCapability.READ]

    async def execute(self, operation: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = params or {}

        try:
            if operation == "generate_summary":
                prompt = params.get("prompt")
                if not prompt:
                    return {"success": False, "error": "Missing required param: prompt"}

                max_tokens = int(params.get("max_tokens", 512))
                temperature = float(params.get("temperature", 0.5))
                model = str(params.get("model", "llama2"))
                provider = str(params.get("provider", "ollama"))

                service = TextGenerationService(model=model, provider=provider)
                text = service.generate(prompt=prompt, max_tokens=max_tokens, temperature=temperature)

                return {
                    "success": True,
                    "data": {
                        "text": text,
                        "model": model,
                        "provider": provider,
                    },
                }

            return {"success": False, "error": f"Unsupported operation: {operation}"}

        except Exception as exc:  # pragma: no cover - defensive
            raise DriverError(str(exc), driver_name=self.driver_id) from exc
