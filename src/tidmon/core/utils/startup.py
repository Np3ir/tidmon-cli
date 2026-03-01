import logging
import os
import platform
import sys
from pathlib import Path
import shutil

FFMPEG_HELP_URL = "https://ffmpeg.org/download.html"
FFMPEG_MISSING_MESSAGE = f"""
[bold red]Error: FFmpeg not found.[/bold red]

FFmpeg is an essential requirement for processing downloaded audio and video files.

[bold yellow]Solution:[/bold yellow]
1.  **Install FFmpeg** on your system. You can download it from: [blue underline]{FFMPEG_HELP_URL}[/blue underline]
2.  Make sure the FFmpeg executable (`ffmpeg.exe` on Windows) is in a folder included in your system's **PATH**.

Once installed, run this command again.
"""


def check_external_dependencies():
    """Checks for required external command-line tools."""
    if not shutil.which("ffmpeg"):
        from rich import print
        print(FFMPEG_MISSING_MESSAGE)
        sys.exit(1)

logger = logging.getLogger(__name__)


def get_appdata_dir() -> Path:
    """
    Get the application data directory.

    Priority order:
      1. PyInstaller frozen exe  → <exe_dir>/data   (portable, always)
      2. Env var TIDMON_DATA_DIR → custom path       (power users / CI)
      3. Standard OS path        → platform-specific (normal pip install)
         - Windows : %APPDATA%/tidmon
         - macOS   : ~/Library/Application Support/tidmon
         - Linux   : ~/.local/share/tidmon
    """
    # 1. PyInstaller frozen executable
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent / "data"
        app_dir.mkdir(exist_ok=True)
        return app_dir

    # 2. Override via environment variable
    env_override = os.environ.get("TIDMON_DATA_DIR")
    if env_override:
        app_dir = Path(env_override)
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir

    # 3. OS-standard location (pip install / dev)
    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        # Linux / other POSIX - respect XDG spec
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    app_dir = base / "tidmon"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_config_file() -> Path:
    """Get the configuration file path"""
    return get_appdata_dir() / "config.json"


def get_db_file() -> Path:
    """Get the database file path"""
    return get_appdata_dir() / "tidmon.db"


def get_log_file() -> Path:
    """Get the log file path"""
    log_dir = get_appdata_dir() / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir / "tidmon.log"


def init_appdata_dir(appdata_path: Path):
    """Initialize application data directory"""
    try:
        appdata_path.mkdir(parents=True, exist_ok=True)
        (appdata_path / "logs").mkdir(exist_ok=True)
        (appdata_path / "backups").mkdir(exist_ok=True)

        logger.info(f"Application directory initialized at {appdata_path}")

        print(f"\n✓ tidmon initialized!")
        print(f"  Config: {get_config_file()}")
        print(f"  Database: {get_db_file()}")
        print(f"  Logs: {get_log_file()}")
        print("\nNext steps:")
        print("  1. Authenticate with TIDAL: tidmon auth")
        print('  2. Add artists to monitor: tidmon monitor add "Artist Name"')
        print("  3. Refresh for new releases: tidmon refresh\n")

        return True

    except Exception as e:
        logger.error(f"Failed to initialize app directory: {e}")
        return False


def check_setup():
    """Check if application is set up"""
    appdata = get_appdata_dir()
    if not (appdata / "config.json").exists():
        init_appdata_dir(appdata)
