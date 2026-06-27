import math
import shutil
import struct
import wave
import pytest
from pathlib import Path
from audx.cli import main

pytestmark = pytest.mark.skipif(
    shutil.which('ffmpeg') is None,
    reason="ffmpeg not on PATH",
)


def _make_wav(path: Path):
    """Write a valid 1-second 440 Hz sine WAV at 8kHz mono."""
    rate = 8000
    samples = [
        int(32767 * math.sin(2 * math.pi * 440 * t / rate))
        for t in range(rate)
    ]
    with wave.open(str(path), 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(struct.pack(f'<{len(samples)}h', *samples))


def test_wav_to_mp3(tmp_path):
    src = tmp_path / 'tone.wav'
    _make_wav(src)
    out = tmp_path / 'tone.mp3'
    with pytest.raises(SystemExit) as exc:
        main([str(src), '-f', 'mp3', '-o', str(out)])
    assert exc.value.code == 0
    assert out.exists() and out.stat().st_size > 0


def test_wav_to_flac(tmp_path):
    src = tmp_path / 'tone.wav'
    _make_wav(src)
    out = tmp_path / 'tone.flac'
    with pytest.raises(SystemExit) as exc:
        main([str(src), '-f', 'flac', '-o', str(out)])
    assert exc.value.code == 0
    assert out.exists() and out.stat().st_size > 0


def test_batch_directory(tmp_path):
    src_dir = tmp_path / 'src'
    src_dir.mkdir()
    out_dir = tmp_path / 'out'
    _make_wav(src_dir / 'a.wav')
    _make_wav(src_dir / 'b.wav')
    with pytest.raises(SystemExit) as exc:
        main([str(src_dir), '-f', 'mp3', '-o', str(out_dir)])
    assert exc.value.code == 0
    assert len(list(out_dir.glob('*.mp3'))) == 2
