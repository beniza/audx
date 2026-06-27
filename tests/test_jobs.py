from pathlib import Path
from audx.jobs import expand, Job


# --- Single file ---

def test_single_audio_file(tmp_path):
    src = tmp_path / 'song.wav'
    src.write_bytes(b'fake')
    jobs = expand(str(src), fmt='mp3')
    assert len(jobs) == 1
    assert jobs[0].input_path == src
    assert jobs[0].output_path == src.with_suffix('.mp3')
    assert jobs[0].fmt == 'mp3'
    assert not jobs[0].is_video

def test_single_video_file(tmp_path):
    src = tmp_path / 'clip.mp4'
    src.write_bytes(b'fake')
    jobs = expand(str(src), fmt='mp3')
    assert len(jobs) == 1
    assert jobs[0].is_video

def test_mkv_is_video(tmp_path):
    src = tmp_path / 'clip.mkv'
    src.write_bytes(b'fake')
    assert expand(str(src), fmt='mp3')[0].is_video

def test_mov_is_video(tmp_path):
    src = tmp_path / 'clip.mov'
    src.write_bytes(b'fake')
    assert expand(str(src), fmt='mp3')[0].is_video

def test_explicit_output_file(tmp_path):
    src = tmp_path / 'song.wav'
    src.write_bytes(b'fake')
    out = tmp_path / 'result.mp3'
    jobs = expand(str(src), fmt='mp3', output=str(out))
    assert jobs[0].output_path == out


# --- Batch: directory ---

def test_directory_expands_audio_files(tmp_path):
    (tmp_path / 'a.wav').write_bytes(b'fake')
    (tmp_path / 'b.mp3').write_bytes(b'fake')
    (tmp_path / 'README.txt').write_bytes(b'ignore')
    jobs = expand(str(tmp_path), fmt='flac')
    assert len(jobs) == 2

def test_directory_output_is_directory(tmp_path):
    src_dir = tmp_path / 'src'
    src_dir.mkdir()
    out_dir = tmp_path / 'out'
    (src_dir / 'a.wav').write_bytes(b'fake')
    jobs = expand(str(src_dir), fmt='mp3', output=str(out_dir))
    assert jobs[0].output_path == out_dir / 'a.mp3'

def test_directory_non_recursive(tmp_path):
    (tmp_path / 'a.wav').write_bytes(b'fake')
    sub = tmp_path / 'sub'
    sub.mkdir()
    (sub / 'b.wav').write_bytes(b'fake')
    jobs = expand(str(tmp_path), fmt='mp3', recursive=False)
    assert len(jobs) == 1

def test_directory_recursive(tmp_path):
    (tmp_path / 'a.wav').write_bytes(b'fake')
    sub = tmp_path / 'sub'
    sub.mkdir()
    (sub / 'b.wav').write_bytes(b'fake')
    jobs = expand(str(tmp_path), fmt='mp3', recursive=True)
    assert len(jobs) == 2


# --- Overwrite ---

def test_existing_output_skipped_by_default(tmp_path):
    src = tmp_path / 'song.wav'
    src.write_bytes(b'fake')
    (tmp_path / 'song.mp3').write_bytes(b'exists')
    jobs = expand(str(src), fmt='mp3', overwrite=False)
    assert len(jobs) == 0

def test_existing_output_included_with_overwrite(tmp_path):
    src = tmp_path / 'song.wav'
    src.write_bytes(b'fake')
    (tmp_path / 'song.mp3').write_bytes(b'exists')
    jobs = expand(str(src), fmt='mp3', overwrite=True)
    assert len(jobs) == 1


# --- Glob ---

def test_glob_filters_non_audio_files(tmp_path):
    (tmp_path / 'song.wav').write_bytes(b'fake')
    (tmp_path / 'notes.txt').write_bytes(b'ignore')
    pattern = str(tmp_path / '*')
    jobs = expand(pattern, fmt='mp3')
    assert len(jobs) == 1
    assert jobs[0].input_path.name == 'song.wav'
