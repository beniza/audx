# audx

Audio converter CLI built on [ffmpeg](https://ffmpeg.org). Converts between
common audio formats and extracts audio from video files.

## Requirements

- [ffmpeg](https://ffmpeg.org/download.html) on PATH (or use `--ffmpeg-path`)

**Install ffmpeg:**
- Windows: `winget install ffmpeg`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

## Install

```sh
pip install -e .
```

Or use the pre-built `audx.exe` (Windows — see [Building](#building)).

## Usage

```
audx INPUT [-o OUTPUT] [-f FORMAT] [-q PRESET]
     [--bitrate RATE] [--sample-rate HZ] [--channels 1|2]
     [--ffmpeg-path PATH] [--recursive] [--overwrite]
     [--dry-run] [--script FILE] [-v] [--version]
```

### Examples

```sh
# Convert a single file
audx song.wav -f mp3

# Extract audio from video at high quality
audx video.mp4 -f flac -q high

# Batch convert a directory
audx ./music/ -f mp3 -o ./converted/

# Batch recursively with custom bitrate
audx ./library/ -f mp3 --recursive --bitrate 256k

# Preview commands without running
audx ./music/ -f mp3 --dry-run

# Save commands to a script file
audx ./music/ -f mp3 --script convert.sh
```

### Quality Presets

| Preset | Lossy bitrate | Lossless formats (wav/flac) |
|--------|--------------|------------------------------|
| `low` | 96k | always full quality |
| `medium` *(default)* | 192k | always full quality |
| `high` | 320k | always full quality |
| `lossless` | 320k + note† | always full quality |

†`lossless` on a lossy format uses maximum bitrate and prints a note recommending
flac or wav for true lossless output.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All jobs succeeded |
| `1` | One or more jobs failed, or validation error |
| `2` | ffmpeg not found |

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
