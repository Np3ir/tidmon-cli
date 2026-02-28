import logging
import csv
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.rule import Rule
from rich import box

from tidmon.core.db import Database

logger = logging.getLogger(__name__)
console = Console()


def _export_tiddl(albums: list, path: Path) -> None:
    """Escribe un archivo .txt con comandos tiddl download url."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"tiddl download url https://tidal.com/album/{a['album_id']}" for a in albums]
    path.write_text("\n".join(lines), encoding="utf-8")
    console.print(f"[green]📄 Exported {len(lines)} album(s) to[/] {path}")


def _export_csv(albums: list, path: Path) -> None:
    """Escribe un archivo .csv con todos los campos del álbum."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["album_id", "artist_name", "title", "album_type", "release_date",
              "number_of_tracks", "downloaded"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(albums)
    console.print(f"[green]📄 Exported {len(albums)} album(s) to[/] {path}")


def _auto_export(albums: list, export_path: str) -> None:
    """Detecta formato por extensión: .csv → CSV, cualquier otro → tiddl txt."""
    path = Path(export_path)
    if path.suffix.lower() == ".csv":
        _export_csv(albums, path)
    else:
        _export_tiddl(albums, path)


class Show:
    """Display information about artists, releases and albums."""

    def __init__(self):
        self.db = Database()

    # ── Artists ──────────────────────────────────────────────────────────────

    def show_artists(self, export_csv: bool = False, export_path: str = None,
                     target: str = "artists"):
        """
        Show monitored artists and/or playlists.

        Args:
            export_csv:  Write results to a CSV file instead of printing.
            export_path: Destination path for the CSV file.
            target:      What to display — 'artists', 'playlists', or 'all'.
        """
        if target in ("artists", "all"):
            artists = self.db.get_all_artists()

            if export_csv:
                self._export_artists_csv(artists or [], export_path)
                # Fall through to playlists only if target == 'all'
                if target != "all":
                    return

            if artists:
                counts = self.db.get_album_counts_per_artist()
                table = Table(
                    box=box.SIMPLE_HEAVY,
                    show_header=True,
                    header_style="bold cyan",
                    show_edge=False,
                    pad_edge=False,
                )
                table.add_column("Artist", style="bold", min_width=25)
                table.add_column("ID", style="dim", justify="right")
                table.add_column("Albums", justify="right")
                table.add_column("Added", style="dim")
                table.add_column("Last checked", style="dim")

                for a in artists:
                    album_count = counts.get(a["artist_id"], 0)
                    added   = (a.get("added_date") or "")[:10]
                    checked = (a.get("last_checked") or "Never")[:10]
                    table.add_row(
                        a["artist_name"],
                        str(a["artist_id"]),
                        str(album_count),
                        added,
                        checked,
                    )

                console.print()
                console.print(Rule("[bold]Monitored Artists", style="cyan"))
                console.print(table)
                console.print(f"[dim]Total: {len(artists)} artist(s)[/]\n")
            else:
                console.print("[yellow]No artists being monitored.[/]")

        if target in ("playlists", "all"):
            playlists = self.db.get_monitored_playlists()

            if playlists:
                table = Table(
                    box=box.SIMPLE_HEAVY,
                    show_header=True,
                    header_style="bold cyan",
                    show_edge=False,
                    pad_edge=False,
                )
                table.add_column("Name", style="bold", min_width=30)
                table.add_column("UUID", style="dim")
                table.add_column("Added", style="dim")

                for p in playlists:
                    added = (p.get("added_date") or "")[:10]
                    table.add_row(p.get("name", ""), p.get("uuid", ""), added)

                console.print()
                console.print(Rule("[bold]Monitored Playlists", style="cyan"))
                console.print(table)
                console.print(f"[dim]Total: {len(playlists)} playlist(s)[/]\n")
            else:
                console.print("[yellow]No playlists being monitored.[/]")

    def _export_artists_csv(self, artists: list, export_path: str = None):
        """Export artists to CSV with UTF-8 BOM for Excel compatibility."""
        path = Path(export_path) if export_path else Path.cwd() / "tidmon_artists.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Artist ID", "Artist Name", "Added Date", "Last Checked"])
                for a in artists:
                    writer.writerow([
                        a["artist_id"],
                        a["artist_name"],
                        a.get("added_date", ""),
                        a.get("last_checked", ""),
                    ])
            console.print(f"[green]📄 Exported {len(artists)} artist(s) to[/] {path}")
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            console.print(f"[red]❌ Export failed:[/] {e}")

    # ── Releases ─────────────────────────────────────────────────────────────

    def show_releases(self, days: int = 30, future: bool = False,
                      export: str = None):
        """Show recent or upcoming releases."""
        if future:
            releases = self.db.get_future_releases()
            title    = "Upcoming Releases"
        else:
            releases = self.db.get_recent_releases(days)
            title    = f"Releases — last {days} day(s)"

        if not releases:
            label = "upcoming" if future else "recent"
            console.print(f"[yellow]No {label} releases found.[/]")
            return

        if export:
            _auto_export(releases, export)
            return

        table = Table(
            box=box.SIMPLE_HEAVY,
            show_header=True,
            header_style="bold cyan",
            show_edge=False,
            pad_edge=False,
        )
        table.add_column("Artist", style="bold", min_width=20)
        table.add_column("Title", min_width=25)
        table.add_column("Type", style="dim")
        table.add_column("Released", style="dim")
        table.add_column("Tracks", justify="right", style="dim")
        table.add_column("ID", style="dim", justify="right")

        for r in releases:
            title_cell = r["title"]
            if r.get("explicit"):
                title_cell += " [dim][E][/]"
            table.add_row(
                r["artist_name"],
                title_cell,
                r.get("album_type", "ALBUM"),
                (r.get("release_date") or "")[:10],
                str(r.get("number_of_tracks", "?")),
                str(r["album_id"]),
            )

        console.print()
        console.print(Rule(f"[bold]{title}", style="cyan"))
        console.print(table)
        console.print(f"[dim]Total: {len(releases)} release(s)[/]\n")

    # ── Albums ───────────────────────────────────────────────────────────────

    def show_albums(self, artist: Optional[str] = None, pending: bool = False,
                    since: str = None, until: str = None, export: str = None):
        """Show albums in the database."""
        artist_id = None

        if artist:
            try:
                artist_id = int(artist)
            except ValueError:
                row = self.db.get_artist_by_name(artist)
                if row:
                    artist_id = row["artist_id"]
                else:
                    console.print(f"[red]❌ Artist '{artist}' not found.[/]")
                    return

        albums = self.db.get_albums(
            artist_id=artist_id,
            include_downloaded=not pending,
            since=since,
            until=until,
        )

        if not albums:
            console.print("[yellow]No albums found.[/]")
            return

        # Export mode — write file and return, no table printed
        if export:
            _auto_export(albums, export)
            return

        filter_label = ""
        if artist:
            filter_label = f" — {artist}"
        if pending:
            filter_label += " [pending only]"
        if since or until:
            date_range = f" [{since or ''}→{until or 'now'}]"
            filter_label += date_range

        table = Table(
            box=box.SIMPLE_HEAVY,
            show_header=True,
            header_style="bold cyan",
            show_edge=False,
            pad_edge=False,
        )
        table.add_column("Artist", style="bold", min_width=20)
        table.add_column("Title", min_width=25)
        table.add_column("Type", style="dim")
        table.add_column("Released", style="dim")
        table.add_column("ID", style="dim", justify="right")
        table.add_column("DL", justify="center")

        for a in albums:
            dl_mark = "[green]✓[/]" if a.get("downloaded") else "[dim]·[/]"
            table.add_row(
                a["artist_name"],
                a["title"],
                a.get("album_type", "?"),
                (a.get("release_date") or "")[:10],
                str(a["album_id"]),
                dl_mark,
            )

        console.print()
        console.print(Rule(f"[bold]Albums{filter_label}", style="cyan"))
        console.print(table)
        console.print(f"[dim]Total: {len(albums)} album(s)[/]\n")