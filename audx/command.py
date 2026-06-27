from pathlib import Path
from audx.jobs import Job
from audx.presets import Settings


def build(ffmpeg_path, job: Job, settings: Settings) -> list[str]:
    # Convert ffmpeg_path to string, preserving forward slashes if it's a Path
    if isinstance(ffmpeg_path, Path):
        ffmpeg_str = ffmpeg_path.as_posix()
    else:
        ffmpeg_str = str(ffmpeg_path)

    cmd = [ffmpeg_str, '-y', '-i', str(job.input_path)]
    if job.is_video:
        cmd.append('-vn')
    cmd += ['-c:a', settings.codec]
    if settings.bitrate:
        cmd += ['-b:a', settings.bitrate]
    if settings.sample_rate:
        cmd += ['-ar', str(settings.sample_rate)]
    if settings.channels:
        cmd += ['-ac', str(settings.channels)]
    cmd.append(str(job.output_path))
    return cmd
