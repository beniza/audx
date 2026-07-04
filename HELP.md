# audx — Command Reference

```
audx INPUT [-o OUTPUT] [-f FORMAT] [-q low|medium|high|lossless]
     [--bitrate 192k] [--sample-rate 44100] [--channels 1|2]
     [--ffmpeg-path PATH] [--recursive] [--overwrite]
     [--dry-run] [--script FILE] [-v/--verbose] [--version]
```

Run `audx --help` at any time to see this from the CLI itself.

## Arguments

### `INPUT` (required, positional)

A single file, a glob pattern (`*.wav`), or a directory.

- **File** — converts that one file.
- **Directory** — converts every supported audio/video file directly inside it.
  Add `--recursive` to also walk subdirectories.
- **Glob** (contains `*` or `?`) — converts every matching file. Non-matching
  extensions are filtered out even if the glob matches them.

Supported input extensions: `.mp3 .wav .flac .aac .m4a .ogg .opus` (audio),
`.mp4 .mkv .mov` (video — audio is extracted, video stream dropped).

### `-f, --format`

Output format/codec: `mp3`, `wav`, `flac`, `aac`, `m4a`, `ogg`, `opus`.

Required, unless `-o` is given with a filename that already ends in one of
these extensions — in that case the format is inferred from it.

### `-o, --output`

- **Single-file input:** path to the output file.
- **Batch input (directory/glob):** path to an output **directory**. Output
  filenames are derived from input filenames with the new extension. If
  `--recursive` is also used, the input's subfolder structure is mirrored
  under the output directory (e.g. `library/rock/song.wav` with
  `-o converted/` → `converted/rock/song.mp3`).
- **Omitted:** output is written next to each input file, same name, new extension.

### `-q, --quality`

Quality preset, default `medium`. Only affects **lossy** output formats
(mp3, aac, m4a, ogg, opus) — `wav` and `flac` are always full quality
regardless of preset.

| Preset | Lossy bitrate |
|--------|--------------|
| `low` | 96k |
| `medium` *(default)* | 192k |
| `high` | 320k |
| `lossless` | 320k, plus a printed note (see below) |

`lossless` on a lossy output format is **not** truly lossless — ffmpeg uses
that format's maximum sane bitrate, and audx prints a note suggesting `flac`
or `wav` if you need genuinely lossless output.

### `--bitrate`, `--sample-rate`, `--channels`

Explicit overrides, applied on top of the resolved preset:

- `--bitrate 256k` — overrides the preset's bitrate for lossy formats.
- `--sample-rate 44100` — resample (Hz).
- `--channels 1|2` — force mono or stereo.

### `--recursive`

When `INPUT` is a directory, also walk subdirectories. Ignored for
single-file or glob input (globs use their own `**` syntax for recursion).

### `--overwrite`

By default, if an output file already exists, that job is silently skipped
(reported in the final "no files to convert" message if it empties the whole
batch). `--overwrite` forces re-conversion.

### `--dry-run`

Print the resolved ffmpeg command(s), one per line, and exit without running
anything. Useful for sanity-checking a batch before committing to it.

### `--script FILE`

Write the resolved ffmpeg command(s) to `FILE` (one per line) instead of
running them — implies dry-run behavior (nothing is executed). Useful for
handing the job off to a scheduler, or as a teaching aid for what audx is
doing under the hood.

### `--ffmpeg-path PATH`

Use a specific ffmpeg binary instead of searching `PATH`.

### `-v, --verbose`

Print ffmpeg's own stdout/stderr for each conversion.

### `--version`

Print the installed audx version and exit.

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | All jobs succeeded |
| `1` | One or more jobs failed, or no files matched / all were skipped |
| `2` | ffmpeg not found (on `PATH` or at `--ffmpeg-path`) |

## Examples

```sh
# Convert a single file
audx song.wav -f mp3

# Explicit output file (format inferred from extension)
audx song.wav -o song-converted.mp3

# Extract audio from video at high quality
audx video.mp4 -f flac -q high

# Batch convert a directory, flat (top-level files only)
audx ./music/ -f mp3 -o ./converted/

# Batch convert recursively, custom bitrate, preserving subfolder structure
audx ./library/ -f mp3 -o ./converted/ --recursive --bitrate 256k

# Re-run and overwrite anything already converted
audx ./library/ -f mp3 --recursive --overwrite

# Preview commands without running them
audx ./music/ -f mp3 --dry-run

# Export commands to a script instead of running them
audx ./music/ -f mp3 --script convert.sh

# Force mono, 44.1kHz output
audx podcast.wav -f mp3 --channels 1 --sample-rate 44100

# Use a specific ffmpeg binary
audx song.wav -f mp3 --ffmpeg-path "C:\tools\ffmpeg\bin\ffmpeg.exe"
```

## Troubleshooting

**`ffmpeg not found on PATH`**
Install ffmpeg (see README) or pass `--ffmpeg-path` pointing directly at the
binary. Exit code `2`.

**`No files to convert`**
Either the input directory/glob had no supported audio/video files, or every
matching output already exists — re-run with `--overwrite` if you want to
replace them.

**A batch partly fails**
audx converts everything it can and reports per-file failures at the end
(`FAILED: <path>: <error>`), then exits `1`. Successful files are not rolled
back.
