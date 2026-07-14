"""Phase 3: synthesize a spoken-word script into audio using Gemini TTS."""
from __future__ import annotations

import base64
import wave
from pathlib import Path

from google import genai
from dotenv import load_dotenv
from ..audio import convert_wav_to_mp3

load_dotenv()

# Try 3.1 first (best quality); fall back to 2.5 if it returns a 500
_MODELS = [
    "gemini-3.1-flash-tts-preview",
    "gemini-2.5-flash-preview-tts",
]

# Sulafat = Warm. Full list: Zephyr, Puck, Kore, Aoede, Charon, Fenrir, etc.
VOICE = "Sulafat"

EPISODES_DIR = Path(__file__).resolve().parent.parent.parent / "episodes"


def _write_wav(path: Path, pcm: bytes) -> None:
    """Wrap raw 24kHz mono 16-bit PCM bytes in a WAV container."""
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)       # mono
        wf.setsampwidth(2)       # 16-bit = 2 bytes per sample
        wf.setframerate(24000)   # Gemini TTS outputs at 24,000 Hz
        wf.writeframes(pcm)


def synthesize(script: str, client: genai.Client | None = None, output_path: Path | None = None) -> Path:
    """
    Convert script text to audio. Returns the path of the saved .wav file.
    Tries gemini-3.1 first, falls back to gemini-2.5 on server errors.
    """
    client = client or genai.Client()
    EPISODES_DIR.mkdir(exist_ok=True)

    last_error = None
    for model in _MODELS:
        try:
            print(f"  Trying {model}...")
            interaction = client.interactions.create(
                model=model,
                input=script,
                response_format={"type": "audio"},
                generation_config={
                    "speech_config": [{"voice": VOICE}]
                },
            )
            pcm = base64.b64decode(interaction.output_audio.data)
            out = output_path or EPISODES_DIR / _default_filename()
            # _write_wav(out, pcm)
            # print(f"  Audio saved → {out}")
            _write_wav(out, pcm)

            mp3_path = convert_wav_to_mp3(out)

            print(f"  Audio saved → {mp3_path}")
            return mp3_path
            # return out
        except Exception as e:
            print(f"  {model} failed: {e}")
            last_error = e

    raise RuntimeError(f"All TTS models failed. Last error: {last_error}")


def _default_filename() -> str:
    from datetime import date
    return f"{date.today().isoformat()}.wav"


if __name__ == "__main__":
    from pathlib import Path
    script_file = Path(__file__).resolve().parent.parent.parent / "script.txt"
    if not script_file.exists():
        raise SystemExit("No script.txt found — run `python -m src.script_writer` first.")
    script = script_file.read_text().strip()
    print(f"Synthesizing {len(script.split())} words...")
    path = synthesize(script)
    print(f"Done: {path}")