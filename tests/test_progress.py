from audx.progress import format_duration, format_line


# --- format_duration ---

def test_format_duration_zero():
    assert format_duration(0) == '00:00:00'

def test_format_duration_seconds_only():
    assert format_duration(45) == '00:00:45'

def test_format_duration_hours_minutes_seconds():
    assert format_duration(3725) == '01:02:05'


# --- format_line ---

def test_format_line_shows_completed_and_total():
    line = format_line(completed=0, total=930, elapsed=0, speeds=[], current_name='')
    assert '0/930' in line

def test_format_line_shows_percentage():
    line = format_line(completed=93, total=930, elapsed=60, speeds=[10.0], current_name='a.mp3')
    assert '10.0%' in line

def test_format_line_shows_current_filename():
    line = format_line(completed=1, total=10, elapsed=5, speeds=[20.0], current_name='CHPTR3.mp3', width=200)
    assert 'CHPTR3.mp3' in line

def test_format_line_shows_last_and_average_speed():
    line = format_line(completed=2, total=10, elapsed=10, speeds=[10.0, 30.0], current_name='x.mp3')
    assert '30.0x' in line   # most recent
    assert '20.0x' in line   # average

def test_format_line_no_speed_data_yet():
    line = format_line(completed=0, total=10, elapsed=0, speeds=[], current_name='')
    assert '--' in line

def test_format_line_eta_extrapolates_from_average_job_time():
    # 1 job done in 10s, 9 remaining -> ETA ~90s -> 00:01:30
    line = format_line(completed=1, total=10, elapsed=10, speeds=[5.0], current_name='x.mp3', width=200)
    assert '00:01:30' in line

def test_format_line_truncates_to_width():
    line = format_line(
        completed=1, total=10, elapsed=1, speeds=[1.0],
        current_name='a-very-long-filename-that-should-get-cut-off.mp3',
        width=40,
    )
    assert len(line) <= 40

def test_format_line_is_ascii_safe_when_truncated():
    # Windows OEM codepages (cp437/cp850) crash on non-ASCII chars in print();
    # a truncated progress line must not kill a long batch mid-run.
    line = format_line(
        completed=1, total=10, elapsed=1, speeds=[1.0],
        current_name='a-very-long-filename-that-should-get-cut-off.mp3',
        width=40,
    )
    line.encode('cp437')  # raises UnicodeEncodeError if a non-ASCII char slipped in
