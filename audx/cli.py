import argparse
import sys
from pathlib import Path

from audx.ffmpeg import locate, FFmpegNotFound
from audx.jobs import expand
from audx.presets import resolve
from audx.command import build
from audx.runner import run


def main(argv=None):
    args = _parse_args(argv)

    try:
        ffmpeg_path = locate(args.ffmpeg_path)
    except FFmpegNotFound as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    jobs = expand(
        args.input,
        fmt=args.format,
        output=args.output,
        recursive=args.recursive,
        overwrite=args.overwrite,
    )

    if not jobs:
        print(
            "No files to convert (no supported audio files matched, or all outputs already exist — use --overwrite to replace).",
            file=sys.stderr,
        )
        sys.exit(1)

    commands = []
    for job in jobs:
        settings = resolve(
            job.fmt,
            args.quality,
            bitrate=args.bitrate,
            sample_rate=args.sample_rate,
            channels=args.channels,
        )
        if settings.note:
            print(settings.note)
        cmd = build(ffmpeg_path, job, settings)
        commands.append((job, cmd))

    # --script: write commands to file, exit without running
    if args.script:
        lines = [' '.join(str(a) for a in cmd) for _, cmd in commands]
        Path(args.script).write_text('\n'.join(lines) + '\n', encoding='utf-8')
        print(f"Commands written to {args.script}")
        sys.exit(0)

    # --dry-run: print commands, exit without running
    if args.dry_run:
        for _, cmd in commands:
            print(' '.join(str(a) for a in cmd))
        sys.exit(0)

    for job, cmd in commands:
        job.output_path.parent.mkdir(parents=True, exist_ok=True)
    results = [run(cmd, job, verbose=args.verbose) for job, cmd in commands]

    failures = [r for r in results if not r.success]
    for r in failures:
        print(f"FAILED: {r.job.input_path}: {r.error}", file=sys.stderr)

    succeeded = len(results) - len(failures)
    print(f"\n{succeeded} succeeded, {len(failures)} failed.")
    sys.exit(0 if not failures else 1)


def _parse_args(argv=None):
    p = argparse.ArgumentParser(prog='audx', description='Audio converter powered by ffmpeg')
    p.add_argument('input', help='Input file, glob pattern, or directory')
    p.add_argument('-o', '--output', help='Output file (single) or directory (batch)')
    p.add_argument(
        '-f', '--format',
        choices=['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg', 'opus'],
        help='Output format (inferred from -o extension if omitted)',
    )
    p.add_argument(
        '-q', '--quality',
        choices=['low', 'medium', 'high', 'lossless'],
        default='medium',
        help='Quality preset (default: medium)',
    )
    p.add_argument('--bitrate', help='Bitrate override, e.g. 192k')
    p.add_argument('--sample-rate', type=int, dest='sample_rate', metavar='HZ')
    p.add_argument('--channels', type=int, choices=[1, 2])
    p.add_argument('--ffmpeg-path', dest='ffmpeg_path', metavar='PATH')
    p.add_argument('--recursive', action='store_true')
    p.add_argument('--overwrite', action='store_true')
    p.add_argument('--dry-run', action='store_true', dest='dry_run')
    p.add_argument('--script', metavar='FILE', help='Write commands to FILE without executing')
    p.add_argument('-v', '--verbose', action='store_true')
    p.add_argument('--version', action='version', version='audx 0.1.0')

    args = p.parse_args(argv)

    # Infer format from -o extension if -f was not given
    if not args.format and args.output:
        ext = Path(args.output).suffix.lstrip('.')
        if ext in {'mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg', 'opus'}:
            args.format = ext

    if not args.format:
        p.error('-f/--format is required (or provide -o with a recognised audio extension)')

    return args
