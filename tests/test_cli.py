import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from audx.cli import _parse_args, main
from audx.ffmpeg import FFmpegNotFound


# --- Arg parsing (pure, no I/O) ---

def test_format_inferred_from_output_extension():
    args = _parse_args(['input.wav', '-o', 'output.mp3'])
    assert args.format == 'mp3'

def test_explicit_format_takes_precedence():
    args = _parse_args(['input.wav', '-f', 'flac', '-o', 'output.mp3'])
    assert args.format == 'flac'

def test_quality_defaults_to_medium():
    args = _parse_args(['input.wav', '-f', 'mp3'])
    assert args.quality == 'medium'

def test_recursive_default_false():
    args = _parse_args(['input.wav', '-f', 'mp3'])
    assert args.recursive is False

def test_recursive_flag():
    args = _parse_args(['input/', '-f', 'mp3', '--recursive'])
    assert args.recursive is True

def test_overwrite_flag():
    args = _parse_args(['input.wav', '-f', 'mp3', '--overwrite'])
    assert args.overwrite is True

def test_dry_run_flag():
    args = _parse_args(['input.wav', '-f', 'mp3', '--dry-run'])
    assert args.dry_run is True

def test_script_flag():
    args = _parse_args(['input.wav', '-f', 'mp3', '--script', 'out.sh'])
    assert args.script == 'out.sh'

def test_missing_format_exits():
    with pytest.raises(SystemExit):
        _parse_args(['input.wav'])


# --- main() end-to-end with mocked deps ---

def test_dry_run_prints_command(tmp_path, capsys):
    src = tmp_path / 'song.wav'
    src.write_bytes(b'fake')
    with patch('audx.cli.locate', return_value=Path('ffmpeg')):
        with pytest.raises(SystemExit) as exc:
            main([str(src), '-f', 'mp3', '--dry-run'])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert 'ffmpeg' in out
    assert str(src) in out

def test_ffmpeg_missing_exits_2(tmp_path, capsys):
    src = tmp_path / 'song.wav'
    src.write_bytes(b'fake')
    with patch('audx.cli.locate', side_effect=FFmpegNotFound('not found\nwinget install ffmpeg')):
        with pytest.raises(SystemExit) as exc:
            main([str(src), '-f', 'mp3'])
    assert exc.value.code == 2

def test_no_jobs_exits_1(tmp_path):
    src = tmp_path / 'song.wav'
    src.write_bytes(b'fake')
    (tmp_path / 'song.mp3').write_bytes(b'exists')  # output already exists
    with patch('audx.cli.locate', return_value=Path('ffmpeg')):
        with pytest.raises(SystemExit) as exc:
            main([str(src), '-f', 'mp3'])
    assert exc.value.code == 1

def test_script_writes_file_and_exits_0(tmp_path):
    src = tmp_path / 'song.wav'
    src.write_bytes(b'fake')
    script = tmp_path / 'convert.sh'
    with patch('audx.cli.locate', return_value=Path('ffmpeg')):
        with pytest.raises(SystemExit) as exc:
            main([str(src), '-f', 'mp3', '--script', str(script)])
    assert exc.value.code == 0
    assert script.exists()
    assert 'ffmpeg' in script.read_text()

def test_successful_run_exits_0(tmp_path):
    src = tmp_path / 'song.wav'
    src.write_bytes(b'fake')
    mock_proc = MagicMock(returncode=0, stderr='')
    with patch('audx.cli.locate', return_value=Path('ffmpeg')), \
         patch('audx.runner.subprocess.run', return_value=mock_proc):
        with pytest.raises(SystemExit) as exc:
            main([str(src), '-f', 'mp3', '--overwrite'])
    assert exc.value.code == 0

def test_failed_run_exits_1(tmp_path, capsys):
    src = tmp_path / 'song.wav'
    src.write_bytes(b'fake')
    mock_proc = MagicMock(returncode=1, stderr='codec error')
    with patch('audx.cli.locate', return_value=Path('ffmpeg')), \
         patch('audx.runner.subprocess.run', return_value=mock_proc):
        with pytest.raises(SystemExit) as exc:
            main([str(src), '-f', 'mp3', '--overwrite'])
    assert exc.value.code == 1
    assert 'FAILED' in capsys.readouterr().err
