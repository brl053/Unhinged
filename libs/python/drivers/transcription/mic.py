"""Microphone-based transcription driver.

@llm-type library.drivers.transcription.mic
@llm-does adapt mic capture + streaming transcription into a Driver API
"""

from __future__ import annotations

from contextlib import suppress
from typing import Any

from libs.python.audio.mic_capture import MicCaptureError, iter_audio_chunks
from libs.python.audio.streaming_transcription import (
    new_session,
    stream_transcription_from_chunks,
)
from libs.python.drivers.base import Driver, DriverCapability, DriverError
from libs.python.models.transcription.schema import TranscriptionMode, TranscriptionSession


class MicTranscriptionDriver(Driver):
    """Driver that records from microphone and returns a transcription session.

    This driver is gRPC-free and purely local. It expects an external recorder
    command (configured explicitly or via UNHINGED_MIC_CHUNK_CMD) that
    records a single chunk of audio to stdout per invocation.
    """

    def __init__(self, driver_id: str = "audio.mic") -> None:
        super().__init__(driver_id)

    def get_capabilities(self) -> list[DriverCapability]:
        return [DriverCapability.READ, DriverCapability.STREAM]

    async def execute(self, operation: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        params = params or {}

        try:
            if operation == "mic_stream":
                session = await self._run_mic_stream(params)
                return {
                    "success": True,
                    "data": {
                        "session": session,
                    },
                }

            return {
                "success": False,
                "error": f"Unsupported operation: {operation}",
            }

        except MicCaptureError as exc:
            raise DriverError(str(exc), driver_name=self.driver_id) from exc
        except DriverError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise DriverError(str(exc), driver_name=self.driver_id) from exc

    async def _run_mic_stream(self, params: dict[str, Any]) -> TranscriptionSession:
        chunk_seconds = int(params.get("chunk_seconds", 5))
        max_seconds = params.get("max_seconds")
        model_size = str(params.get("model_size", "base"))
        cmd = params.get("cmd")  # Optional explicit command (sequence of args)
        on_segment = params.get("on_segment")  # Optional callback for streaming UX

        session = new_session(
            mode=TranscriptionMode.MIC,
            model_size=model_size,
            chunk_seconds=chunk_seconds,
        )

        async def _audio_iter():
            async for chunk in iter_audio_chunks(
                chunk_seconds=chunk_seconds,
                max_seconds=max_seconds,
                cmd=cmd,
            ):
                yield chunk

        async for segment in stream_transcription_from_chunks(
            _audio_iter(),
            model_size=model_size,
            chunk_seconds=chunk_seconds,
            mode=TranscriptionMode.MIC,
        ):
            session.segments.append(segment)

            # Optional per-segment callback for real-time consumers (e.g., CLI)
            if callable(on_segment):  # type: ignore[call-arg]
                # Best-effort: ignore callback errors so recording continues
                with suppress(Exception):
                    on_segment(segment)

        return session
