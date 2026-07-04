import re
import subprocess
from dataclasses import dataclass

from audx.jobs import Job

_SPEED_RE = re.compile(r'speed=\s*([\d.]+)x')


@dataclass
class Result:
    job: Job
    success: bool
    error: str | None
    speed: float | None = None


def run(cmd: list[str], job: Job, verbose: bool = False) -> Result:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        speed = _parse_speed(proc.stderr)
        if proc.returncode == 0:
            return Result(job=job, success=True, error=None, speed=speed)
        return Result(
            job=job,
            success=False,
            error=proc.stderr.strip() or f"exit code {proc.returncode}",
            speed=speed,
        )
    except Exception as e:
        return Result(job=job, success=False, error=str(e))


def _parse_speed(stderr: str) -> float | None:
    matches = _SPEED_RE.findall(stderr or '')
    return float(matches[-1]) if matches else None
