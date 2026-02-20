#!/usr/bin/env bash
set -euo pipefail

# Download audio/video from YouTube for local research archiving.
# Requires: yt-dlp, ffmpeg (for audio extraction)
# Usage examples:
#   tools/fetch_youtube.sh "https://www.youtube.com/watch?v=..." --audio
#   tools/fetch_youtube.sh "https://www.youtube.com/watch?v=..." --video

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <youtube_url> --audio|--video [output_dir]" >&2
  exit 1
fi

URL="$1"
MODE="$2"
OUT_DIR="${3:-docs/sources/videos/raw}"
mkdir -p "$OUT_DIR"

if ! command -v yt-dlp >/dev/null 2>&1; then
  echo "yt-dlp is required. Install and retry." >&2
  exit 2
fi

case "$MODE" in
  --audio)
    yt-dlp \
      --extract-audio \
      --audio-format mp3 \
      --audio-quality 0 \
      --output "$OUT_DIR/%(uploader)s/%(upload_date>%Y-%m-%d)s__%(title).120B__[%(id)s].%(ext)s" \
      "$URL"
    ;;
  --video)
    yt-dlp \
      --format "bv*+ba/b" \
      --merge-output-format mp4 \
      --output "$OUT_DIR/%(uploader)s/%(upload_date>%Y-%m-%d)s__%(title).120B__[%(id)s].%(ext)s" \
      "$URL"
    ;;
  *)
    echo "Unknown mode: $MODE (expected --audio or --video)" >&2
    exit 3
    ;;
esac

echo "Saved to: $OUT_DIR"
