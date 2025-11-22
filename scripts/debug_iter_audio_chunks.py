#!/usr/bin/env python3

import asyncio

from libs.python.services.mic_capture import iter_audio_chunks


async def main() -> None:
    print("[DEBUG] Starting iter_audio_chunks test...")
    idx = 0
    async for chunk in iter_audio_chunks(chunk_seconds=3, max_seconds=10):
        idx += 1
        print(f"[DEBUG] Chunk {idx}: {len(chunk)} bytes")
    print("[DEBUG] Done iter_audio_chunks test.")


if __name__ == "__main__":
    asyncio.run(main())
