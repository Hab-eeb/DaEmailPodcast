"""Audio file helpers."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def convert_wav_to_mp3(wav_path: Path, delete_wav: bool = True) -> Path:
    """Convert a WAV episode to a mono 64 kbps MP3 episode."""
    if not wav_path.exists():
        raise FileNotFoundError(f"WAV file not found: {wav_path}")

    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "FFmpeg is not installed or is not on your PATH. "
            "Install it with: brew install ffmpeg"
        )

    mp3_path = wav_path.with_suffix(".mp3")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(wav_path),
            "-vn",
            "-ac",
            "1",
            "-b:a",
            "64k",
            str(mp3_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    if delete_wav:
        wav_path.unlink()

    return mp3_path