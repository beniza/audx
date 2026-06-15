# audx — Audio Converter CLI

**Date:** 2026-06-15
**Status:** Approved design, pre-implementation

## Summary

`audx` is a command-line audio converter built on top of `ffmpeg`. It converts
between common audio formats, extracts audio from video files, and runs on single
files or batches (glob / directory). It is distributed as a standalone `audx.exe`
via PyInstaller. `ffmpeg` is **not** bundled — it is located at runtime on `PATH`
or via `--ffmpeg-path`; if missing, `audx` prints OS-specific install instructions.

## Goals

- Convert between common audio formats: mp3, wav, flac, aac/m4a, ogg, opus.
- Extract audio from video containers: mp4, mkv, mov (auto-add `-vn`).
- Friendly quality presets (`low` / `medium` / `high` / `lossless`) with advanced
  per-setting overrides (bitrate, sample rate, channels).
- Single-file and batch (glob / directory, optional recursion) conversion.
- Ship as a single self-contained `audx.exe`.
- Zero third-party **runtime** dependencies (stdlib only) for a lean, reliable exe.

## Non-Goals (v1 / YAGNI)

- Multi audio-track selection (`--audio-stream N`) — deferred.
- Video→video transcoding, trimming, filters, normalization, metadata editing.
- Bundling ffmpeg into the exe or auto-downloading it.
- GUI.

## Architecture

Small modular package, stdlib-only. The module with real logic (mapping presets +
overrides → ffmpeg args) is pure and unit-testable; ffmpeg is only touched at the
edges.

Package layout: `audx/`

| Module | One job | Depends on |
|---|---|---|
| `cli.py` | Parse args, orchestrate the run, format output/errors, set exit code | all below |
| `ffmpeg.py` | Locate ffmpeg (PATH → `--ffmpeg-path`), version check, OS-specific install instructions if missing | stdlib `shutil`, `subprocess`, `platform` |
| `presets.py` | Map output format + quality preset → codec/bitrate defaults; pure data + lookup | none |
| `command.py` | Build the ffmpeg argument list from a resolved job | `presets` |
| `jobs.py` | Expand input (single / glob / dir) into a list of jobs; derive output paths | stdlib `pathlib`, `glob` |
| `runner.py` | Execute each ffmpeg command, capture result, report per-file outcome | `subprocess` |

`__main__.py` enables `python -m audx`; the console entry point is `audx`.

## CLI Surface (v1)

```
audx INPUT [-o OUTPUT] [-f FORMAT] [-q low|medium|high|lossless]
     [--bitrate 192k] [--sample-rate 44100] [--channels 1|2]
     [--ffmpeg-path PATH] [--recursive] [--overwrite]
     [--dry-run] [-v/--verbose] [--version]
```

- `INPUT` — a file, a glob (`*.wav`), or a directory.
- `-f/--format` — output format/codec: `mp3`, `wav`, `flac`, `aac`/`m4a`, `ogg`,
  `opus`. Inferred from `-o`'s extension if `-o` is given and `-f` omitted.
  Required if neither is present.
- `-q/--quality` — preset (default `medium`). Advanced flags override individual
  resolved preset values.
- `--bitrate`, `--sample-rate`, `--channels` — explicit overrides.
- Batch: when `INPUT` is a dir/glob, `-o` is treated as an output **directory**;
  output names derive from source names with the new extension. `--recursive`
  walks subdirectories.
- `--dry-run` — print the ffmpeg command(s) without executing.
- Video inputs automatically add `-vn` (drop video stream).

## Quality Presets

Presets resolve to a target bitrate for lossy output formats. Lossless formats
(wav, flac) ignore bitrate entirely — they are always full quality regardless of
preset. Indicative mapping for lossy targets (exact values finalized in
`presets.py` and asserted in tests):

| Preset | Lossy bitrate (mp3 / aac / ogg / opus) |
|---|---|
| low | ~96k |
| medium | ~192k (default) |
| high | ~256–320k |
| lossless | highest sane bitrate for the format, plus a printed note that true lossless requires a lossless format |

Rules:
- For **lossless output formats** (wav, flac), the `-q` preset is ignored; output
  is always full quality.
- For **lossy output formats**, `lossless` is not truly lossless — it maps to the
  format's highest sane bitrate and prints a note suggesting flac/wav for true
  lossless.

## Data Flow

`cli` →
`ffmpeg.locate()` (fail fast with install help if missing) →
`jobs.expand(input, recursive)` → list of jobs →
for each job: `presets.resolve(format, quality)` merged with overrides →
`command.build(job)` → `runner.run(cmd)` →
`cli` prints summary: *N succeeded, M failed*, with per-file errors.

## Error Handling

- **ffmpeg missing** → OS-specific install instructions (Windows: winget/choco;
  macOS: brew; Linux: apt/dnf), exit code `2`.
- **Bad input path / unsupported format** → validation error before any execution,
  non-zero exit.
- **Per-file ffmpeg failure in batch** → collect and continue; report all failures
  at the end; exit non-zero if any file failed.
- **Output already exists** → skip with a warning unless `--overwrite`.

### Exit Codes

- `0` — all jobs succeeded.
- `1` — one or more jobs failed (or validation error).
- `2` — ffmpeg not found / environment error.

## Testing Strategy

- **Unit (no ffmpeg needed):**
  - `presets` — preset → settings mapping, override precedence, lossless rules.
  - `command` — assert exact ffmpeg arg lists for representative jobs (audio↔audio,
    overrides, video input adds `-vn`).
  - `jobs` — single/glob/dir expansion, recursion, output-name/path derivation,
    overwrite/skip decisions.
  - `ffmpeg.locate` — PATH found / `--ffmpeg-path` / missing (mocked), install-text
    selection per OS.
- **Runner** — tested via `--dry-run` and mocked `subprocess`.
- **Integration (optional, skipped if ffmpeg absent)** — a real tiny conversion
  round-trip.

## Distribution

- PyInstaller `--onefile` → `dist/audx.exe`.
- `build.ps1` wraps the Windows build; README documents the equivalent one-liner
  for macOS/Linux.
- ffmpeg is not bundled; discovered at runtime.

## Repo Skeleton

```
audio-converter/
├── audx/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── ffmpeg.py
│   ├── presets.py
│   ├── command.py
│   ├── jobs.py
│   └── runner.py
├── tests/
│   ├── test_presets.py
│   ├── test_command.py
│   ├── test_jobs.py
│   └── test_ffmpeg.py
├── docs/superpowers/specs/2026-06-15-audx-audio-converter-design.md
├── pyproject.toml          # metadata + dev deps: pytest, pyinstaller
├── build.ps1
├── README.md
└── .gitignore
```
