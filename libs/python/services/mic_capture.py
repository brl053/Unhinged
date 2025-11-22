"""Microphone capture helpers for local transcription.

@llm-type library.services.mic_capture
@llm-does provide async helpers that yield raw audio chunks via subprocess

This module does not know anything about Whisper or transcription. It simply
executes an external command expected to record a single audio chunk and write
it to stdout. The command is provided explicitly or via the
UNHINGED_MIC_CHUNK_CMD environment variable.
"""

from __future__ import annotations

import asyncio
import os
import shlex
import shutil
from collections.abc import AsyncIterator, Sequence


class MicCaptureError(RuntimeError):
    """Raised when microphone capture fails or is misconfigured."""


async def iter_audio_chunks(
    *,
    chunk_seconds: int,
    max_seconds: int | None = None,
    cmd: Sequence[str] | None = None,
) -> AsyncIterator[bytes]:
    """Yield raw audio chunks produced by an external recorder command.

    The command is expected to record approximately ``chunk_seconds`` of audio
    and write a complete audio file (e.g. WAV) to stdout on each invocation.

    Args:
        chunk_seconds: Logical duration of each chunk in seconds (used by
            callers for timing; this function does not enforce duration).
        max_seconds: Optional maximum total duration. If provided, at most
            ``max_seconds // chunk_seconds`` chunks will be recorded.
        cmd: Explicit command to execute for each chunk. If ``None``, the
            UNHINGED_MIC_CHUNK_CMD environment variable must be set.

    Yields:
        Bytes for each recorded audio chunk.
    """

    if cmd is None:
        # 1) Explicit env override, if present
        env_cmd = os.getenv("UNHINGED_MIC_CHUNK_CMD")
        if env_cmd:
            cmd = shlex.split(env_cmd)
        else:
            # 2) Prefer ALSA arecord, which supports fixed-duration WAV chunks
            if shutil.which("arecord"):
                cmd = [
                    "arecord",
                    "-q",
                    "-d",
                    str(chunk_seconds),
                    "-f",
                    "cd",  # 16-bit, 44.1kHz, stereo
                    "-t",
                    "wav",  # proper WAV header
                    "-",  # stdout
                ]
            else:
                raise MicCaptureError(
                    "No suitable mic recorder found. Install 'arecord' (alsa-utils) "
                    "or set UNHINGED_MIC_CHUNK_CMD to a command that records "
                    "one WAV chunk to stdout."
                )

    max_chunks: int | None = None
    if max_seconds is not None and max_seconds > 0:
        # Ensure at least one chunk
        max_chunks = max(1, max_seconds // chunk_seconds)

    chunk_index = 0

    while max_chunks is None or chunk_index < max_chunks:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await proc.communicate()
        except asyncio.CancelledError:
            proc.kill()
            await proc.wait()
            raise

        if proc.returncode != 0:
            raise MicCaptureError(
                f"Mic command failed with exit code {proc.returncode}: "
                f"{stderr.decode('utf-8', errors='replace').strip()}"
            )

        if not stdout:
            # No audio produced; treat as end-of-stream
            break

        yield stdout
        chunk_index += 1
