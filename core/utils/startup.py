import logging
import platform
import sys
from pathlib import Path
import shutil

FFMPEG_HELP_URL = "https://ffmpeg.org/download.html"
FFMPEG_MISSING_MESSAGE = f"""
[bold red]Error: FFmpeg no encontrado.[/bold red]

FFmpeg es un requisito indispensable para procesar los archivos de audio y vídeo descargados.

[bold yellow]Solución:[/bold yellow]
1.  **Instala FFmpeg** en tu sistema. Puedes descargarlo desde: [blue underline]{FFMPEG_HELP_URL}[/blue underline]
2.  Asegúrate de que el ejecutable de FFmpeg (`ffmpeg.exe` en Windows) esté en una carpeta incluida en el **PATH** de tu sistema.

Una vez instalado, vuelve a ejecutar este comando.
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
    Portable Mode: Uses 'data' folder next to the executable if it exists.
    Standard Mode: Uses OS standard AppData location.
    """
    # Check if we are running as a frozen executable (PyInstaller)
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        # Development mode - use current working directory or script location
        base_dir = Path(__file__).parent.parent.parent

    # Check for portable 'data' folder
    portable_data = base_dir / "data"
    
    # If 'data' folder exists next to exe, use it (Portable Mode)
    if portable_data.exists():
        return portable_data
        
    # Otherwise, create it there to FORCE portable mode by default for new installs
    # or fall back to system AppData if you prefer hybrid.
    # User request: "installation portable easy to move" -> FORCE PORTABLE
    
    portable_data.mkdir(exist_ok=True)
    return portable_data

    # Legacy AppData fallback (commented out for forced portability)
    # system = platform.system()
    # if system == "Windows": ...



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
        # Create main directory
        appdata_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (appdata_path / "logs").mkdir(exist_ok=True)
        (appdata_path / "backups").mkdir(exist_ok=True)
        
        logger.info(f"Application directory initialized at {appdata_path}")
        
        print(f"\n✓ tidmon initialized!")
        print(f"  Config: {get_config_file()}")
        print(f"  Database: {get_db_file()}")
        print(f"  Logs: {get_log_file()}")
        print("\nNext steps:")
        print("  1. Authenticate with TIDAL: tidmon auth")
        print("  2. Add artists to monitor: tidmon monitor add \"Artist Name\"")
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
