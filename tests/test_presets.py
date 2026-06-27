import pytest
from audx.presets import resolve, Settings


# --- Lossy formats ---

def test_mp3_medium():
    s = resolve('mp3', 'medium')
    assert s.codec == 'libmp3lame'
    assert s.bitrate == '192k'
    assert s.note is None

def test_mp3_low():
    s = resolve('mp3', 'low')
    assert s.bitrate == '96k'

def test_mp3_high():
    s = resolve('mp3', 'high')
    assert s.bitrate == '320k'

def test_aac_codec():
    assert resolve('aac', 'medium').codec == 'aac'

def test_m4a_codec():
    assert resolve('m4a', 'medium').codec == 'aac'

def test_ogg_codec():
    assert resolve('ogg', 'medium').codec == 'libvorbis'

def test_opus_codec():
    assert resolve('opus', 'medium').codec == 'libopus'


# --- Lossless formats — quality preset ignored ---

def test_wav_always_lossless():
    s = resolve('wav', 'low')
    assert s.codec == 'pcm_s16le'
    assert s.bitrate is None
    assert s.note is None

def test_flac_always_lossless():
    s = resolve('flac', 'high')
    assert s.codec == 'flac'
    assert s.bitrate is None
    assert s.note is None

def test_wav_lossless_preset_still_no_bitrate():
    s = resolve('wav', 'lossless')
    assert s.bitrate is None
    assert s.note is None


# --- lossless preset on lossy format ---

def test_lossless_preset_on_mp3_uses_max_bitrate():
    s = resolve('mp3', 'lossless')
    assert s.bitrate == '320k'

def test_lossless_preset_on_mp3_prints_note():
    s = resolve('mp3', 'lossless')
    assert s.note is not None
    note_lower = s.note.lower()
    assert 'flac' in note_lower or 'wav' in note_lower


# --- Overrides ---

def test_bitrate_override_takes_precedence():
    s = resolve('mp3', 'medium', bitrate='128k')
    assert s.bitrate == '128k'

def test_sample_rate_override():
    s = resolve('mp3', 'medium', sample_rate=44100)
    assert s.sample_rate == 44100

def test_channels_override():
    s = resolve('mp3', 'medium', channels=1)
    assert s.channels == 1

def test_no_overrides_default_to_none():
    s = resolve('mp3', 'medium')
    assert s.sample_rate is None
    assert s.channels is None
