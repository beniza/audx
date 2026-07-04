# audx

A command-line audio converter built on [ffmpeg](https://ffmpeg.org). Converts
between common audio formats, extracts audio from video files, and handles
single files or whole directory trees in one batch — powered entirely by
Python's standard library (no third-party runtime dependencies).

## Features

- Convert between mp3, wav, flac, aac/m4a, ogg, opus
- Extract audio from video (mp4, mkv, mov) — video stream is dropped automatically
- Friendly quality presets (`low` / `medium` / `high` / `lossless`) or explicit
  bitrate/sample-rate/channel overrides
- Batch convert a whole folder, optionally `--recursive`, preserving subfolder
  structure in the output
- `--dry-run` / `--script` to preview or export the ffmpeg commands without running them
- Ships as a single standalone `audx.exe` — nothing to install but ffmpeg

## Requirements

- [ffmpeg](https://ffmpeg.org/download.html) on `PATH` (or pass `--ffmpeg-path`)

**Install ffmpeg:**
- Windows: `winget install ffmpeg`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

## Install

Download the latest `audx.exe` from [Releases](../../releases) — no Python required.

Or, from source:
```sh
pip install -e .
```

## Quick start

```sh
# Convert a single file
audx song.wav -f mp3

# Extract audio from video at high quality
audx video.mp4 -f flac -q high

# Batch convert a whole folder into another folder, recursively
audx ./library/ -f mp3 -o ./converted/ --recursive

# Preview the ffmpeg commands without running them
audx ./music/ -f mp3 --dry-run
```

See **[HELP.md](HELP.md)** for the full command reference, every flag, and troubleshooting.

## Building

**Windows (`audx.exe`):**
```powershell
pip install pyinstaller
.\build.ps1
# Output: dist\audx.exe
```

**macOS / Linux:**
```sh
pip install pyinstaller
pyinstaller --onefile --name audx audx/__main__.py
# Output: dist/audx
```

Pushing a tag like `v0.2.1` runs [`.github/workflows/release.yml`](.github/workflows/release.yml),
which builds `audx.exe` and publishes it as a GitHub Release automatically.
