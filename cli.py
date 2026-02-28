"""
tidmon - TIDAL Release Monitor
CLI entry point (mirroring deemon's structure for TIDAL)
"""
import logging
import sys
import click
from pathlib import Path

# ── Logging setup ─────────────────────────────────────────────────────────────

def setup_logging(verbose: bool = False, debug: bool = False):
    level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s" if debug else "%(levelname)s: %(message)s"
    logging.basicConfig(level=level, format=fmt)

    # File handler for errors (optional)
    try:
        log_dir = Path.home() / ".tidmon" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "tidmon.log")
        file_handler.setLevel(logging.WARNING)  # Log warnings and errors to file
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        logging.getLogger().addHandler(file_handler)
    except Exception:
        # Logging to file is optional; do not crash if it fails (e.g., due to permissions)
        pass


# ── Root command ──────────────────────────────────────────────────────────────

@click.group()
@click.version_option("1.0.0", prog_name="tidmon")
@click.option('--verbose', '-v', is_flag=True, help='Show info messages.')
@click.option('--debug', '-d', is_flag=True, help='Show debug messages.')
@click.pass_context
def cli(ctx, verbose, debug):
    """tidmon — TIDAL Release Monitor\n\nTrack new releases from your favourite artists."""
    setup_logging(verbose, debug)
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['debug'] = debug


# ── auth ──────────────────────────────────────────────────────────────────────

@cli.command()
def auth():
    """Authenticate with TIDAL using device flow."""
    from tidmon.cmd.auth import Auth
    Auth().login()


@cli.command()
def logout():
    """Clear stored authentication tokens."""
    from tidmon.cmd.auth import Auth
    Auth().logout()


@cli.command()
def whoami():
    """Show current authentication status."""
    from tidmon.cmd.auth import Auth
    Auth().status()


# ── monitor ───────────────────────────────────────────────────────────────────

@cli.group()
def monitor():
    """Monitor artists and playlists for new releases."""
    pass


@monitor.command('add')
@click.argument('identifiers', nargs=-1, required=False)
@click.option('--file', '-f', 'from_file', type=click.Path(exists=True),
              help='Import from a file (artists or playlists, one per line).')
def monitor_add(identifiers, from_file):
    """Add artist(s) or playlist(s) to monitoring.

    Can accept artist names, IDs, artist URLs, or playlist URLs.
    When a playlist is added, all its artists are monitored.

    \b
    Examples:
      tidmon monitor add "Radiohead"
      tidmon monitor add 3528531
      tidmon monitor add https://tidal.com/browse/artist/3528531
      tidmon monitor add https://tidal.com/browse/playlist/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
      tidmon monitor add --file my_artists.txt
    """
    if not identifiers and not from_file:
        click.echo(click.get_current_context().get_help(), err=True)
        return

    from tidmon.cmd.monitor import Monitor
    m = Monitor()

    if from_file:
        m.add_from_file(from_file)

    if identifiers:
        for identifier in identifiers:
            from tidmon.core.utils.url import parse_url, TidalType
            parsed = parse_url(identifier)
            if parsed:
                if parsed.tidal_type == TidalType.ARTIST:
                    m.add_by_id(int(parsed.tidal_id))
                elif parsed.tidal_type == TidalType.PLAYLIST:
                    m.add_playlist(identifier)
            else:
                try:
                    m.add_by_id(int(identifier))
                except ValueError:
                    m.add_by_name(identifier)


@monitor.command('remove')
@click.argument('identifiers', nargs=-1, required=True)
def monitor_remove(identifiers):
    """Remove artist(s) from monitoring."""
    from tidmon.cmd.monitor import Monitor
    m = Monitor()
    for identifier in identifiers:
        m.remove_artist(identifier)

@monitor.command('clear')
@click.confirmation_option(prompt='Are you sure you want to remove all monitored artists?')
def monitor_clear():
    """Remove all monitored artists."""
    from tidmon.cmd.monitor import Monitor
    Monitor().clear_artists()


@monitor.command('list')
@click.option('--artists', 'target', flag_value='artists', default=True)
@click.option('--playlists', 'target', flag_value='playlists')
@click.option('--all', 'target', flag_value='all')
def monitor_list(target):
    """List monitored artists and/or playlists."""
    from tidmon.cmd.monitor import Monitor
    Monitor().list_items(target)


@monitor.group('playlist')
def monitor_playlist():
    """Monitor playlists for new tracks."""
    pass


@monitor_playlist.command('add')
@click.argument('url')
def playlist_add(url):
    """Add a playlist to monitoring."""
    from tidmon.cmd.monitor import Monitor
    Monitor().add_playlist(url)


@monitor_playlist.command('remove')
@click.argument('url')
def playlist_remove(url):
    """Remove a playlist from monitoring."""
    from tidmon.cmd.monitor import Monitor
    Monitor().remove_playlist(url)


@monitor_playlist.command('list')
def playlist_list():
    """List all monitored playlists."""
    from tidmon.cmd.monitor import Monitor
    Monitor().list_playlists()


@monitor.command('export')
@click.option('--output', '-o', default='tidmon_export.txt', show_default=True,
              help='Output file path.')
def monitor_export(output):
    """Export monitored artists and playlists to a file."""
    from tidmon.cmd.monitor import Monitor
    Monitor().export_to_file(output)


# ── refresh ───────────────────────────────────────────────────────────────────

@cli.command()
@click.option('--artist', '-a', default=None, help='Refresh a specific artist by name.')
@click.option('--id', 'artist_id', default=None, type=int, help='Refresh a specific artist by ID.')
@click.option('--no-artists', 'skip_artists', is_flag=True, help='Skip artist refresh.')
@click.option('--no-playlists', 'skip_playlists', is_flag=True, help='Skip playlist refresh.')
@click.option('--download', '-D', is_flag=True, help='Auto-download new releases after refresh.')
@click.option('--since', default=None, help='Only refresh artists added since date (YYYY-MM-DD).')
@click.option('--until', default=None, help='Only refresh artists added until date (YYYY-MM-DD).')
@click.option('--album-since', default=None, help='Only process albums released after this date (YYYY-MM-DD).')
@click.option('--album-until', default=None, help='Only process albums released before this date (YYYY-MM-DD).')
def refresh(artist, artist_id, skip_artists, skip_playlists, download, since, until, album_since, album_until):
    """Check monitored artists for new releases."""
    from tidmon.cmd.refresh import Refresh
    Refresh().refresh(
        artist=artist,
        artist_id=artist_id,
        refresh_artists=not skip_artists,
        refresh_playlists=not skip_playlists,
        download=download,
        since=since,
        until=until,
        album_since=album_since,
        album_until=album_until,
    )


# ── download ──────────────────────────────────────────────────────────────────

@cli.group()
def download():
    """Download tracks, albums, artists, or playlists."""
    pass


@download.command('url')
@click.pass_context
@click.argument('url')
@click.option('--force', is_flag=True, default=False, help='Force re-download even if file exists.')
def download_url(ctx, url, force):
    """Download from a TIDAL URL (artist, album, track, video, playlist)."""
    from tidmon.cmd.download import Download
    Download(verbose=ctx.obj.get('verbose', False)).download_url(url, force=force)


@download.command('artist')
@click.pass_context
@click.argument('identifier')
@click.option('--force', is_flag=True, default=False, help='Force re-download even if file exists.')
def download_artist(ctx, identifier, force):
    """Download full discography for an artist (name or ID)."""
    from tidmon.cmd.download import Download
    dl = Download(verbose=ctx.obj.get('verbose', False))
    try:
        artist_id = int(identifier)
        dl.download_artist(artist_id=artist_id, force=force)
    except ValueError:
        dl.download_artist(artist_name=identifier, force=force)


@download.command('album')
@click.pass_context
@click.argument('album_id', type=int)
@click.option('--force', is_flag=True, default=False, help='Force re-download even if file exists.')
def download_album(ctx, album_id, force):
    """Download an album by ID."""
    from tidmon.cmd.download import Download
    Download(verbose=ctx.obj.get('verbose', False)).download_album(album_id, force=force)


@download.command('track')
@click.pass_context
@click.argument('track_id', type=int)
@click.option('--force', is_flag=True, default=False, help='Force re-download even if file exists.')
def download_track(ctx, track_id, force):
    """Download a track by ID."""
    from tidmon.cmd.download import Download
    Download(verbose=ctx.obj.get('verbose', False)).download_track(track_id, force=force)


@download.command('monitored')
@click.pass_context
@click.option('--force', is_flag=True, default=False, help='Force re-download even if file exists.')
@click.option('--since', default=None, help='Only albums released since date (YYYY-MM-DD).')
@click.option('--until', default=None, help='Only albums released until date (YYYY-MM-DD).')
@click.option('--dry-run', is_flag=True, default=False, help='Show what would be downloaded without actually downloading.')
@click.option('--export', default=None, metavar='FILE', help='Export album list to a .txt file (e.g. --export albums.txt).')
@click.option('--download', 'also_download', is_flag=True, default=False, help='Also download when --export is set (default: export only).')
def download_monitored(ctx, force, since, until, dry_run, export, also_download):
    """Download pending albums for all monitored artists."""
    from tidmon.cmd.download import Download
    Download(verbose=ctx.obj.get('verbose', False)).download_monitored(force=force, since=since, until=until, dry_run=dry_run, export=export, also_download=also_download)


@download.command('all')
@click.pass_context
@click.option('--force', is_flag=True, help='Force re-download of all albums, ignoring existing files.')
@click.option('--dry-run', is_flag=True, default=False, help='Show what would be downloaded without actually downloading.')
@click.option('--resume', is_flag=True, default=False, help='Resume an interrupted download, skipping completed albums.')
@click.option('--since', default=None, help='Only process albums released on or after this date (YYYY-MM-DD).')
@click.option('--until', default=None, help='Only process albums released on or before this date (YYYY-MM-DD).')
@click.option('--export', default=None, metavar='FILE', help='Export album list to a .txt file (e.g. --export albums.txt).')
@click.option('--download', 'also_download', is_flag=True, default=False, help='Also download when --export is set (default: export only).')
def download_all(ctx, force, dry_run, resume, since, until, export, also_download):
    """Download all albums from the database."""
    from tidmon.cmd.download import Download
    Download(verbose=ctx.obj.get('verbose', False)).download_all(force=force, dry_run=dry_run, resume=resume, since=since, until=until, export=export, also_download=also_download)


# ── search ────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument('query')
@click.option('--type', '-t', 'search_type',
              type=click.Choice(['artists', 'albums', 'tracks'], case_sensitive=False),
              default='artists', show_default=True)
@click.option('--limit', '-l', default=10, show_default=True)
def search(query, search_type, limit):
    """Search TIDAL for artists, albums, or tracks."""
    from tidmon.cmd.search import Search
    s = Search()
    if search_type == 'artists':
        s.search_artists(query, limit=limit)
    elif search_type == 'albums':
        s.search_albums(query, limit=limit)
    elif search_type == 'tracks':
        s.search_tracks(query, limit=limit)


# ── show ──────────────────────────────────────────────────────────────────────

@cli.group()
def show():
    """Show monitored data (artists, releases, etc.)."""
    pass


@show.command('artists')
@click.option('--csv', 'export_csv', is_flag=True, help='Export as CSV.')
@click.option('--output', '-o', default=None, help='Output file path for CSV.')
def show_artists(export_csv, output):
    """Show all monitored artists."""
    from tidmon.cmd.show import Show
    Show().show_artists(export_csv=export_csv, export_path=output)


@show.command('releases')
@click.option('--days', '-d', default=30, show_default=True, help='Number of days to look back.')
@click.option('--future', '-f', is_flag=True, help='Show upcoming releases instead.')
def show_releases(days, future):
    """Show recent or upcoming releases."""
    from tidmon.cmd.show import Show
    Show().show_releases(days=days, future=future)


@show.command('albums')
@click.option('--artist', '-a', default=None, help='Filter by artist name or ID.')
@click.option('--pending', is_flag=True, help='Only show not yet downloaded.')
def show_albums(artist, pending):
    """Show albums in the database."""
    from tidmon.core.db import Database
    db = Database()
    artist_id = None
    if artist:
        try:
            artist_id = int(artist)
        except ValueError:
            row = db.get_artist_by_name(artist)
            if row:
                artist_id = row['artist_id']
            else:
                print(f"\n  Artist '{artist}' not found.\n")
                return

    albums = db.get_albums(artist_id=artist_id, include_downloaded=not pending)
    if not albums:
        print("\n  No albums found.\n")
        return

    print(f"\n  ALBUMS ({len(albums)})\n")
    for a in albums:
        dl = " [✓]" if a.get('downloaded') else ""
        print(f"  • {a['artist_name']} — {a['title']}{dl}")
        print(f"    Type: {a.get('album_type', '?')}  |  Released: {a.get('release_date', '?')[:10]}  |  ID: {a['album_id']}")
    print()


# ── config ────────────────────────────────────────────────────────────────────

@cli.group()
def config():
    """View and modify tidmon configuration."""
    pass


@config.command('show')
def config_show():
    """Show all configuration values."""
    from tidmon.cmd.config import ConfigCommand
    ConfigCommand().get_all()


@config.command('get')
@click.argument('key')
def config_get(key):
    """Get the value of a configuration key."""
    from tidmon.cmd.config import ConfigCommand
    ConfigCommand().get_key(key)


@config.command('set')
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """Set a configuration value."""
    from tidmon.cmd.config import ConfigCommand
    ConfigCommand().set_key(key, value)


@config.command('path')
def config_path():
    """Show the config file path."""
    from tidmon.cmd.config import ConfigCommand
    ConfigCommand().path()


# ── backup ────────────────────────────────────────────────────────────────────

@cli.group()
def backup():
    """Backup and restore tidmon data."""
    pass


@backup.command('create')
@click.option('--output', '-o', default=None, help='Output archive path.')
def backup_create(output):
    """Create a backup of the database and config."""
    from tidmon.cmd.backup import Backup
    Backup().create(output_path=output)


@backup.command('restore')
@click.argument('path')
def backup_restore(path):
    """Restore from a backup archive."""
    from tidmon.cmd.backup import Backup
    Backup().restore(path)


@backup.command('list')
def backup_list():
    """List available backups."""
    from tidmon.cmd.backup import Backup
    Backup().list_backups()


@backup.command('delete')
@click.argument('path', required=False)
@click.option('--keep', '-k', 'keep_last', default=None, type=int,
              help='Keep only the N most recent backups.')
def backup_delete(path, keep_last):
    """Delete a backup or trim old ones."""
    from tidmon.cmd.backup import Backup
    Backup().delete(backup_path=path, keep_last=keep_last)


# ── Entry point ───────────────────────────────────────────────────────────────

def run():
    cli(obj={})


if __name__ == '__main__':
    run()