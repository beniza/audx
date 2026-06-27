import subprocess
from dataclasses import dataclass

from audx.jobs import Job


@dataclass
class Result:
    job: Job
    success: bool
    error: str | None


def run(cmd: list[str], job: Job, verbose: bool = False) -> Result:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            return Result(job=job, success=True, error=None)
        return Result(
            job=job,
            success=False,
            error=proc.stderr.strip() or f"exit code {proc.returncode}",
        )
    except Exception as e:
        return Result(job=job, success=False, error=str(e))
