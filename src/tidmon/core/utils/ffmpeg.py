"""
FFmpeg utilities from tiddl
Code extracted from tiddl/core/utils/ffmpeg.py
"""

import subprocess
from pathlib import Path


def run(cmd: list[str]):
    """Run process without printing to terminal"""
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def is_ffmpeg_installed() -> bool:
    """Checks if `ffmpeg` is installed."""
    try:
        run(["ffmpeg", "-version"])
        return True
    except FileNotFoundError:
        return False


def convert_to_mp4(source: Path) -> Path:
    """Convert .ts to .mp4"""
    output_path = source.with_suffix(".mp4")
    
    run(["ffmpeg", "-y", "-i", str(source), "-c", "copy", str(output_path)])
    
    source.unlink()
    
    return output_path


def extract_flac(source: Path) -> Path:
    """
    Extracts FLAC audio from MP4 container
    For HI_RES_LOSSLESS
    """
    
    tmp = source.with_suffix(".tmp.flac")
    dest = source.with_suffix(".flac")
    
    run(["ffmpeg", "-y", "-i", str(source), "-c", "copy", str(tmp)])
    
    tmp.replace(dest)
    
    # Delete source if it's different
    if source != dest:
        try:
            source.unlink()
        except OSError:
            pass
    
    return dest


def fix_mp4_faststart(source: Path) -> Path:
    """
    Remuxes MP4/M4A to move 'moov' atom to the beginning
    Fixes corrupt/fragmented files
    """
    tmp = source.with_name(source.stem + ".fixed" + source.suffix)
    
    run(["ffmpeg", "-y", "-i", str(source), "-c", "copy", "-movflags", "+faststart", str(tmp)])
    
    # Replace original if tmp was created
    if tmp.exists():
        tmp.replace(source)
    
    return source
