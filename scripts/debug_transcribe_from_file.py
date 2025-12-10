#!/usr/bin/env python3

from pathlib import Path

from libs.python.clients.transcription_service import TranscriptionService


def main() -> None:
    wav_path = Path("/tmp/test.wav")
    if not wav_path.exists():
        print("[DEBUG] /tmp/test.wav does not exist")
        return

    data = wav_path.read_bytes()
    print(f"[DEBUG] Loaded test.wav, size={len(data)} bytes")

    service = TranscriptionService(model_size="base")
    try:
        text = service.transcribe_audio_data(data)
        print("[RESULT] Transcript:")
        print(text)
    except Exception as exc:
        print(f"[ERROR] transcribe_audio_data failed: {exc}")


if __name__ == "__main__":
    main()
