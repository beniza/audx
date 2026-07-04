import glob as _glob
from dataclasses import dataclass
from pathlib import Path

VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.mov'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.opus'}
_SUPPORTED = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS


@dataclass
class Job:
    input_path: Path
    output_path: Path
    fmt: str
    is_video: bool


def expand(
    input_str: str,
    fmt: str,
    output: str | None = None,
    recursive: bool = False,
    overwrite: bool = False,
) -> list[Job]:
    root = Path(input_str) if Path(input_str).is_dir() else None
    paths = _resolve_paths(input_str, recursive)
    jobs = []
    for p in paths:
        out = _derive_output(p, fmt, output, root)
        if out.exists() and not overwrite:
            continue
        jobs.append(Job(
            input_path=p,
            output_path=out,
            fmt=fmt,
            is_video=p.suffix.lower() in VIDEO_EXTENSIONS,
        ))
    return jobs


def _resolve_paths(input_str: str, recursive: bool) -> list[Path]:
    p = Path(input_str)
    if p.is_dir():
        pattern = '**/*' if recursive else '*'
        return sorted(
            f for f in p.glob(pattern)
            if f.is_file() and f.suffix.lower() in _SUPPORTED
        )
    if '*' in input_str or '?' in input_str:
        return sorted(
            Path(f) for f in _glob.glob(input_str, recursive=recursive)
            if Path(f).suffix.lower() in _SUPPORTED
        )
    return [p]


def _derive_output(input_path: Path, fmt: str, output: str | None, root: Path | None = None) -> Path:
    new_name = input_path.with_suffix(f'.{fmt}').name
    if output is None:
        return input_path.with_suffix(f'.{fmt}')
    out = Path(output)
    # Treat as directory if it already is one, or has no file extension
    if out.is_dir() or not out.suffix:
        if root is not None:
            out = out / input_path.parent.relative_to(root)
        return out / new_name
    return out
