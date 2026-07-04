from pathlib import Path
from unittest.mock import patch, MagicMock
from audx.runner import run, Result
from audx.jobs import Job


def _job():
    return Job(Path('in.wav'), Path('out.mp3'), 'mp3', False)


def test_run_success():
    mock_proc = MagicMock(returncode=0, stderr='')
    with patch('audx.runner.subprocess.run', return_value=mock_proc):
        result = run(['ffmpeg', '-i', 'in.wav', 'out.mp3'], _job())
    assert result.success is True
    assert result.error is None

def test_run_failure_nonzero_returncode():
    mock_proc = MagicMock(returncode=1, stderr='Error: codec not found')
    with patch('audx.runner.subprocess.run', return_value=mock_proc):
        result = run(['ffmpeg'], _job())
    assert result.success is False
    assert 'codec not found' in result.error

def test_run_result_contains_job():
    mock_proc = MagicMock(returncode=0, stderr='')
    with patch('audx.runner.subprocess.run', return_value=mock_proc):
        result = run(['ffmpeg'], _job())
    assert result.job.fmt == 'mp3'

def test_run_subprocess_exception_caught():
    with patch('audx.runner.subprocess.run', side_effect=FileNotFoundError('ffmpeg')):
        result = run(['ffmpeg'], _job())
    assert result.success is False
    assert result.error is not None

def test_run_uses_list_form_not_shell():
    """subprocess.run must be called with a list so PATH spaces are handled safely."""
    mock_proc = MagicMock(returncode=0, stderr='')
    with patch('audx.runner.subprocess.run', return_value=mock_proc) as mock_run:
        run(['ffmpeg', '-i', 'in.wav', 'out.mp3'], _job())
    assert isinstance(mock_run.call_args[0][0], list)


def test_run_parses_ffmpeg_speed_from_stderr():
    mock_proc = MagicMock(
        returncode=0,
        stderr='size=  256kB time=00:00:16.10 bitrate= 130.5kbits/s speed=25.3x',
    )
    with patch('audx.runner.subprocess.run', return_value=mock_proc):
        result = run(['ffmpeg'], _job())
    assert result.speed == 25.3


def test_run_speed_none_when_not_present():
    mock_proc = MagicMock(returncode=0, stderr='')
    with patch('audx.runner.subprocess.run', return_value=mock_proc):
        result = run(['ffmpeg'], _job())
    assert result.speed is None
