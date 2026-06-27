import platform
import shutil
from pathlib import Path

_INSTALL_HELP = {
    'Windows': (
        "Install ffmpeg:\n"
        "  winget install ffmpeg\n"
        "  or: choco install ffmpeg\n"
        "  or download from https://ffmpeg.org/download.html"
    ),
    'Darwin': (
        "Install ffmpeg:\n"
        "  brew install ffmpeg"
    ),
    'Linux': (
        "Install ffmpeg:\n"
        "  sudo apt install ffmpeg\n"
        "  or: sudo dnf install ffmpeg"
    ),
}


class FFmpegNotFound(Exception):
    pass


def locate(ffmpeg_path: str | None = None) -> Path:
    if ffmpeg_path is not None:
        p = Path(ffmpeg_path)
        if p.is_file():
            return p
        raise FFmpegNotFound(f"ffmpeg not found at: {ffmpeg_path}\n{_install_help()}")

    found = shutil.which('ffmpeg')
    if found:
        return Path(found)

    raise FFmpegNotFound(f"ffmpeg not found on PATH.\n{_install_help()}")


def _install_help() -> str:
    return _INSTALL_HELP.get(
        platform.system(),
        "Please install ffmpeg: https://ffmpeg.org/download.html",
    )
