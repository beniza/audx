import pytest
from pathlib import Path
from unittest.mock import patch
from audx.ffmpeg import locate, FFmpegNotFound


def test_locate_finds_on_path():
    with patch('audx.ffmpeg.shutil.which', return_value='/usr/bin/ffmpeg'):
        result = locate()
    assert result == Path('/usr/bin/ffmpeg')

def test_locate_returns_path_object():
    with patch('audx.ffmpeg.shutil.which', return_value='/usr/bin/ffmpeg'):
        assert isinstance(locate(), Path)

def test_locate_missing_raises_ffmpegnotfound():
    with patch('audx.ffmpeg.shutil.which', return_value=None):
        with pytest.raises(FFmpegNotFound):
            locate()

def test_locate_missing_message_mentions_ffmpeg():
    with patch('audx.ffmpeg.shutil.which', return_value=None):
        with pytest.raises(FFmpegNotFound) as exc:
            locate()
    assert 'ffmpeg' in str(exc.value).lower()

def test_install_help_windows():
    with patch('audx.ffmpeg.shutil.which', return_value=None), \
         patch('audx.ffmpeg.platform.system', return_value='Windows'):
        with pytest.raises(FFmpegNotFound) as exc:
            locate()
    assert 'winget' in str(exc.value)

def test_install_help_macos():
    with patch('audx.ffmpeg.shutil.which', return_value=None), \
         patch('audx.ffmpeg.platform.system', return_value='Darwin'):
        with pytest.raises(FFmpegNotFound) as exc:
            locate()
    assert 'brew' in str(exc.value)

def test_install_help_linux():
    with patch('audx.ffmpeg.shutil.which', return_value=None), \
         patch('audx.ffmpeg.platform.system', return_value='Linux'):
        with pytest.raises(FFmpegNotFound) as exc:
            locate()
    assert 'apt' in str(exc.value)

def test_explicit_path_used(tmp_path):
    fake = tmp_path / 'ffmpeg'
    fake.write_bytes(b'')
    result = locate(ffmpeg_path=str(fake))
    assert result == fake

def test_explicit_path_missing_raises(tmp_path):
    with pytest.raises(FFmpegNotFound):
        locate(ffmpeg_path=str(tmp_path / 'nonexistent'))
