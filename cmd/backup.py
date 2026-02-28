"""
Backup and restore functionality for tidmon.
Backs up the database and config file into a tar.gz archive.
"""
import tarfile
import logging
from pathlib import Path
from datetime import datetime
from tidmon.core.config import Config
from tidmon.core.utils.startup import get_appdata_dir, get_db_file, get_config_file

logger = logging.getLogger(__name__)


class Backup:
    """Handle backup and restore of tidmon data."""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.appdata_dir = get_appdata_dir()
        self.backups_dir = self.appdata_dir / "backups"
        self.backups_dir.mkdir(exist_ok=True)

    def close(self) -> None:
        """Close the database connection."""
        self.db.close()

    def __enter__(self) -> "Backup":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def create(self, output_path: str = None) -> bool:
        """Create a backup archive of config + database."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"tidmon_backup_{timestamp}.tar.gz"

        if output_path:
            backup_file = Path(output_path)
        else:
            backup_file = self.backups_dir / default_name

        db_file = get_db_file()
        config_file = get_config_file()

        sources = []
        if db_file.exists():
            sources.append(db_file)
        if config_file.exists():
            sources.append(config_file)

        if not sources:
            print("\n  ✗ Nothing to backup (no db or config found).\n")
            return False

        try:
            with tarfile.open(backup_file, 'w:gz') as tar:
                for source in sources:
                    tar.add(source, arcname=source.name)
                    logger.debug(f"Added to backup: {source.name}")

            size_kb = backup_file.stat().st_size // 1024
            print(f"\n  ✓ Backup created: {backup_file}")
            print(f"    Size: {size_kb} KB")
            print(f"    Contains: {', '.join(s.name for s in sources)}\n")
            return True

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            print(f"\n  ✗ Backup failed: {e}\n")
            return False

    def restore(self, backup_path: str) -> bool:
        """Restore from a backup archive."""
        backup_file = Path(backup_path)

        if not backup_file.exists():
            print(f"\n  ✗ Backup file not found: {backup_path}\n")
            return False

        if not tarfile.is_tarfile(backup_file):
            print(f"\n  ✗ Not a valid tar archive: {backup_path}\n")
            return False

        # Confirm before overwriting
        print(f"\n  RESTORE from: {backup_file.name}")
        print("  This will overwrite your current database and config.")
        confirm = input("  Continue? (yes/no): ").strip().lower()
        if confirm not in ('yes', 'y'):
            print("  Cancelled.\n")
            return False

        try:
            with tarfile.open(backup_file, 'r:gz') as tar:
                members = tar.getmembers()
                print(f"\n  Restoring {len(members)} file(s)...")

                for member in members:
                    # Determine destination
                    if member.name == get_db_file().name:
                        dest = get_db_file().parent
                    elif member.name == get_config_file().name:
                        dest = get_config_file().parent
                    else:
                        dest = self.appdata_dir

                    tar.extract(member, path=dest)
                    print(f"  ✓ Restored: {member.name}")

            print(f"\n  ✓ Restore complete.\n")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            print(f"\n  ✗ Restore failed: {e}\n")
            return False

    def list_backups(self):
        """List available backups."""
        backups = sorted(self.backups_dir.glob("tidmon_backup_*.tar.gz"), reverse=True)

        if not backups:
            print("\n  No backups found.\n")
            print(f"  Backup directory: {self.backups_dir}\n")
            return

        print(f"\n  AVAILABLE BACKUPS  ({self.backups_dir})")
        print("  " + "=" * 50)

        for i, backup in enumerate(backups, 1):
            size_kb = backup.stat().st_size // 1024
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            print(f"  {i:2}. {backup.name}")
            print(f"      Size: {size_kb} KB  |  Date: {mtime.strftime('%Y-%m-%d %H:%M')}")
            print()

    def delete(self, backup_path: str = None, keep_last: int = None):
        """Delete a specific backup or keep only the N most recent."""
        if backup_path:
            target = Path(backup_path)
            if not target.is_absolute():
                target = self.backups_dir / target.name
            if target.exists():
                target.unlink()
                print(f"\n  ✓ Deleted: {target.name}\n")
            else:
                print(f"\n  ✗ Not found: {backup_path}\n")

        elif keep_last is not None:
            backups = sorted(self.backups_dir.glob("tidmon_backup_*.tar.gz"), reverse=True)
            to_delete = backups[keep_last:]
            if not to_delete:
                print(f"\n  Nothing to delete (only {len(backups)} backup(s) exist).\n")
                return
            for b in to_delete:
                b.unlink()
                print(f"  ✓ Deleted: {b.name}")
            print()
        else:
            print("  Specify a file path or --keep N.\n")