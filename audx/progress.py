def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f'{h:02d}:{m:02d}:{s:02d}'


def format_line(
    completed: int,
    total: int,
    elapsed: float,
    speeds: list[float],
    current_name: str,
    width: int = 100,
) -> str:
    pct = (completed / total) if total else 0.0

    if completed and total > completed:
        eta = format_duration((elapsed / completed) * (total - completed))
    else:
        eta = '--:--:--'

    cur_speed = f'{speeds[-1]:.1f}x' if speeds else '--'
    avg_speed = f'{(sum(speeds) / len(speeds)):.1f}x' if speeds else '--'

    # core stats (progress/speed/ETA) always take priority over the bar and
    # filename, which are dropped/truncated first on narrow terminals
    core = (
        f'{completed}/{total} ({pct * 100:.1f}%) '
        f'| speed {cur_speed} (avg {avg_speed}) '
        f'| elapsed {format_duration(elapsed)} | ETA {eta}'
    )

    bar_width = 20
    filled = int(bar_width * pct)
    bar = '#' * filled + '-' * (bar_width - filled)
    with_bar = f'[{bar}] {core}'

    base = with_bar if (not width or len(with_bar) <= width) else core

    if current_name:
        room = (width - len(base) - 3) if width else None  # ' | '
        name = current_name
        if room is not None and len(name) > room:
            name = name[:max(0, room - 3)] + '...' if room > 3 else ''
        if name:
            base = f'{base} | {name}'

    if width and len(base) > width:
        base = base[:max(0, width - 3)] + '...'
    return base
