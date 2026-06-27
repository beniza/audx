from pathlib import Path
from audx.jobs import Job
from audx.presets import Settings


def build(ffmpeg_path, job: Job, settings: Settings) -> list[str]:
    cmd = [ffmpeg_path.as_posix() if isinstance(ffmpeg_path, Path) else str(ffmpeg_path), '-y', '-i', str(job.input_path)]
    if job.is_video:
        cmd.append('-vn')
    cmd += ['-c:a', settings.codec]
    if settings.bitrate is not None:
        cmd += ['-b:a', settings.bitrate]
    if settings.sample_rate is not None:
        cmd += ['-ar', str(settings.sample_rate)]
    if settings.channels is not None:
        cmd += ['-ac', str(settings.channels)]
    cmd.append(str(job.output_path))
    return cmd
