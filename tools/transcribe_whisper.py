#!/usr/bin/env python3
"""Transcribe local media with Whisper and emit text + timestamps JSON.

Usage:
  python tools/transcribe_whisper.py \
    --input docs/sources/videos/raw/.../file.mp3 \
    --outdir docs/sources/videos/transcripts \
    --model medium
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Path to local audio/video file")
    p.add_argument("--outdir", default="docs/sources/videos/transcripts")
    p.add_argument("--model", default="medium", help="whisper model size")
    p.add_argument("--language", default=None, help="force language code, optional")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    in_path = Path(args.input)
    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path}")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    try:
        import whisper  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "Missing dependency: openai-whisper. Install with `pip install openai-whisper`."
        ) from exc

    model = whisper.load_model(args.model)
    result = model.transcribe(str(in_path), language=args.language)

    stem = in_path.stem
    txt_path = outdir / f"{stem}.txt"
    json_path = outdir / f"{stem}.segments.json"

    txt_path.write_text(result.get("text", "").strip() + "\n", encoding="utf-8")

    segments = []
    for seg in result.get("segments", []):
        segments.append(
            {
                "start": seg.get("start"),
                "end": seg.get("end"),
                "text": seg.get("text", "").strip(),
            }
        )
    json_path.write_text(
        json.dumps(
            {
                "source": str(in_path),
                "model": args.model,
                "language": result.get("language"),
                "segments": segments,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Wrote transcript: {txt_path}")
    print(f"Wrote segments:   {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
