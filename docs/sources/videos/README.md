# Video sources (reproducible pipeline)

This folder is the canonical layout for collecting video-based research artifacts.

## Directory layout

- `raw/` — downloaded original media (audio/video), grouped by uploader/date.
- `transcripts/` — plain text transcripts and timestamped segments JSON.
- `mapping/` — manual concept maps from timestamps to strategy concepts.

## Recommended workflow

1. Fetch source media:
   - `tools/fetch_youtube.sh "<url>" --audio`
2. Transcribe:
   - `python tools/transcribe_whisper.py --input <media_file> --outdir docs/sources/videos/transcripts`
3. Fill mapping template (see `docs/COURSE_LOGIC_SPEC.md`, section "Video → concept mapping").

## Transcript naming convention

For media file `YYYY-MM-DD__Title__[videoid].mp3`:
- transcript text: `YYYY-MM-DD__Title__[videoid].txt`
- timestamped segments: `YYYY-MM-DD__Title__[videoid].segments.json`

## Timestamp schema (segments JSON)

```json
{
  "source": "docs/sources/videos/raw/.../file.mp3",
  "model": "medium",
  "language": "ru",
  "segments": [
    {"start": 12.34, "end": 18.77, "text": "..."}
  ]
}
```
