from pathlib import Path
from audx.command import build
from audx.jobs import Job
from audx.presets import Settings


def _job(inp='in.wav', out='out.mp3', fmt='mp3', is_video=False):
    return Job(Path(inp), Path(out), fmt, is_video)


def _settings(codec='libmp3lame', bitrate='192k', sample_rate=None, channels=None, note=None):
    return Settings(codec, bitrate, sample_rate, channels, note)


def test_basic_audio_command():
    cmd = build('ffmpeg', _job(), _settings())
    assert cmd == ['ffmpeg', '-y', '-i', 'in.wav', '-c:a', 'libmp3lame', '-b:a', '192k', 'out.mp3']

def test_video_input_adds_vn():
    cmd = build('ffmpeg', _job(inp='clip.mp4', is_video=True), _settings())
    assert '-vn' in cmd

def test_vn_comes_before_codec():
    cmd = build('ffmpeg', _job(inp='clip.mp4', is_video=True), _settings())
    assert cmd.index('-vn') < cmd.index('-c:a')

def test_lossless_format_no_bitrate_flag():
    cmd = build('ffmpeg', _job(out='out.flac', fmt='flac'), _settings(codec='flac', bitrate=None))
    assert '-b:a' not in cmd

def test_with_sample_rate():
    cmd = build('ffmpeg', _job(), _settings(sample_rate=44100))
    assert '-ar' in cmd
    assert cmd[cmd.index('-ar') + 1] == '44100'

def test_with_channels():
    cmd = build('ffmpeg', _job(), _settings(channels=1))
    assert '-ac' in cmd
    assert cmd[cmd.index('-ac') + 1] == '1'

def test_output_is_last_arg():
    cmd = build('ffmpeg', _job(out='out.mp3'), _settings())
    assert cmd[-1] == 'out.mp3'

def test_ffmpeg_path_as_string():
    cmd = build('/usr/bin/ffmpeg', _job(), _settings())
    assert cmd[0] == '/usr/bin/ffmpeg'

def test_ffmpeg_path_as_path_object():
    p = Path('/usr/bin/ffmpeg')
    cmd = build(p, _job(), _settings())
    assert cmd[0] == str(p)

def test_overwrite_flag_always_present():
    cmd = build('ffmpeg', _job(), _settings())
    assert '-y' in cmd
