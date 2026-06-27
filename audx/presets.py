from dataclasses import dataclass

LOSSLESS_FORMATS = {'wav', 'flac'}

_CODECS = {
    'mp3':  'libmp3lame',
    'aac':  'aac',
    'm4a':  'aac',
    'ogg':  'libvorbis',
    'opus': 'libopus',
    'wav':  'pcm_s16le',
    'flac': 'flac',
}

_BITRATES = {'low': '96k', 'medium': '192k', 'high': '320k', 'lossless': '320k'}

_LOSSLESS_NOTE = (
    "Note: '{fmt}' is a lossy format. Preset 'lossless' uses {br} bitrate. "
    "Use --format flac or --format wav for true lossless output."
)


@dataclass
class Settings:
    codec: str
    bitrate: str | None
    sample_rate: int | None
    channels: int | None
    note: str | None


def resolve(
    fmt: str,
    quality: str,
    bitrate: str | None = None,
    sample_rate: int | None = None,
    channels: int | None = None,
) -> Settings:
    codec = _CODECS[fmt]

    if fmt in LOSSLESS_FORMATS:
        final_bitrate = None
        note = None
    else:
        default_br = _BITRATES[quality]
        final_bitrate = bitrate if bitrate else default_br
        if quality == 'lossless' and bitrate is None:
            note = _LOSSLESS_NOTE.format(fmt=fmt, br=final_bitrate)
        else:
            note = None

    return Settings(
        codec=codec,
        bitrate=final_bitrate,
        sample_rate=sample_rate,
        channels=channels,
        note=note,
    )
