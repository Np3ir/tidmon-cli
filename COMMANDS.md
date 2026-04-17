# `tidmon` Command Guide

Complete reference for all available commands in `tidmon`.

---

## Global Options

```
tidmon [OPTIONS] COMMAND [ARGS]...
```

| Option | Description |
|---|---|
| `--version` | Show the installed version of `tidmon`. |
| `-v`, `--verbose` | Show detailed info messages (INFO level). |
| `-d`, `--debug` | Show full debug messages (DEBUG level). |
| `--help` | Show help for any command or subcommand. |

---

## `auth` — Authentication

Manage the connection to your TIDAL account.

| Command | Description |
|---|---|
| `tidmon auth` | Start the interactive browser-based authentication flow. |
| `tidmon logout` | Delete stored authentication credentials. |
| `tidmon whoami` | Show the current session (user, country, token expiration). |
| `tidmon auth-refresh [OPTIONS]` | Manually refresh the TIDAL access token. |

**`auth-refresh` options:**

| Option | Description |
|---|---|
| `--force`, `-f` | Refresh even if the token is still valid. |
| `--early-expire`, `-e SECONDS` | Treat the token as expired N seconds before its actual expiry. |

---

## `monitor` — Manage Artists and Playlists

Add, remove, and inspect the artists and playlists you want to track.

### Artist commands

| Command | Description |
|---|---|
| `tidmon monitor add [IDENTIFIERS...] [-f FILE]` | Add one or more artists or playlists. Accepts names, IDs, TIDAL URLs, or a file. |
| `tidmon monitor remove [IDENTIFIERS...]` | Remove artists from monitoring by name or ID. |
| `tidmon monitor clear` | Remove **all** monitored artists (requires confirmation). |
| `tidmon monitor export [-o FILE]` | Export the full list of monitored artists and playlists to a file. |

**`monitor add` options:**

| Option | Description |
|---|---|
| `--file`, `-f PATH` | Import from a text file (one artist/playlist per line). |

**Examples:**
```bash
tidmon monitor add "Daft Punk"
tidmon monitor add 3528531
tidmon monitor add "https://tidal.com/browse/artist/3528531"
tidmon monitor add --file my_artists.txt
```

### Playlist subcommands

| Command | Description |
|---|---|
| `tidmon monitor playlist add <URL>` | Add a TIDAL playlist to monitoring (imports all its artists). |
| `tidmon monitor playlist remove <URL>` | Remove a playlist from monitoring. |
| `tidmon monitor playlist list` | List all currently monitored playlists. |

---

## `refresh` — Check for New Releases

Checks TIDAL for new albums and videos from your monitored artists and playlists.

```
tidmon refresh [OPTIONS]
```

| Option | Description |
|---|---|
| `-D`, `--download` | Auto-download new releases and videos found during refresh. |
| `--videos-only` | With `--download`, download only new videos (skip albums). |
| `--artist`, `-a NAME` | Refresh only a specific artist by name. |
| `--id ID` | Refresh only a specific artist by ID. |
| `--no-artists` | Skip artist refresh. |
| `--no-playlists` | Skip playlist refresh. |
| `--since YYYY-MM-DD` | Only refresh artists added *after* this date. |
| `--until YYYY-MM-DD` | Only refresh artists added *before* this date. |
| `--album-since YYYY-MM-DD` | Only process albums released *after* this date. |
| `--album-until YYYY-MM-DD` | Only process albums released *before* this date. |

**Notes:**
- Videos are detected automatically when `save_video: true` in `config.json`.
- New videos are shown in the refresh summary alongside new album releases.
- `--videos-only` is useful if you only want to catch up on videos without re-processing albums.

**Examples:**
```bash
# Full refresh and download everything new
tidmon refresh --download

# Check for new releases in the last 30 days, download only
tidmon refresh --album-since 2026-01-01 --download

# Download only new videos from all monitored artists
tidmon refresh --download --videos-only

# Refresh a single artist
tidmon refresh --artist "Rosalía"
```

---

## `download` — Download Music and Videos

Downloads music and videos from TIDAL. Audio tracks are fully completed (audio → lyrics → metadata → cover) before moving to the next.

### Subcommands

| Command | Description |
|---|---|
| `tidmon download url <URL>` | Download from a TIDAL URL (artist, album, track, video, or playlist). |
| `tidmon download artist <ID\|NAME>` | Download the complete discography of an artist (albums + videos). |
| `tidmon download album <ALBUM_ID>` | Download a full album by its ID. |
| `tidmon download track <TRACK_ID>` | Download a single track by its ID. |
| `tidmon download video <VIDEO_ID>` | Download a single video by its ID. |
| `tidmon download monitored` | Download all pending albums from monitored artists. |
| `tidmon download all` | Download **all** albums from the database regardless of status. |

### Common options

| Option | Applies to | Description |
|---|---|---|
| `--force` | all | Re-download even if the file already exists on disk or is marked as downloaded in the DB. |
| `--dry-run` | `monitored`, `all` | Show what would be downloaded without actually downloading. |
| `--resume` | `all` | Skip albums already marked as downloaded in the DB. |
| `--since YYYY-MM-DD` | `monitored`, `all` | Only process albums released on or after this date. |
| `--until YYYY-MM-DD` | `monitored`, `all` | Only process albums released on or before this date. |

**Notes on video downloads:**
- Videos require `save_video: true` in `config.json`.
- `tidmon download artist` downloads both albums and videos for the artist.
- `tidmon download url <tidal-video-url>` also works for individual videos.
- Downloaded videos are tracked in the local database — already-downloaded videos are automatically skipped on future runs unless `--force` is used.

**Examples:**
```bash
tidmon download url "https://tidal.com/browse/album/123456"
tidmon download url "https://tidal.com/browse/video/987654"
tidmon download artist "Rosalía"
tidmon download video 987654
tidmon download album 123456
tidmon download monitored --since 2026-01-01
tidmon download all --resume
```

---

## `show` — Inspect the Database

Inspect your local database of monitored artists, albums, and releases.

| Command | Description |
|---|---|
| `tidmon show artists [OPTIONS]` | List monitored artists and/or playlists. |
| `tidmon show releases [OPTIONS]` | Show recent or upcoming releases. |
| `tidmon show albums [OPTIONS]` | Show albums in the database with filters. |
| `tidmon show report [OPTIONS]` | Per-artist summary: album count and total track count. |
| `tidmon show discography [OPTIONS]` | Export full A–Z artist discographies to files. |

### `show artists` options

| Option | Description |
|---|---|
| `--artists` | Show monitored artists (default). |
| `--playlists` | Show monitored playlists instead. |
| `--all` | Show both artists and playlists. |
| `--csv` | Export the list as a CSV file. |
| `--output`, `-o FILE` | Output file path for the CSV export. |

### `show releases` options

| Option | Description |
|---|---|
| `--days`, `-d N` | Number of days to look back (default: 30). |
| `--future`, `-f` | Show upcoming releases instead of recent ones. |
| `--export FILE` | Export to file: `.csv` for spreadsheet, any other extension for tiddl-compatible URL list. |

### `show albums` options

| Option | Description |
|---|---|
| `--artist`, `-a NAME\|ID` | Filter by a specific artist. |
| `--pending` | Show only albums not yet downloaded. |
| `--since YYYY-MM-DD` | Only albums released on or after this date. |
| `--until YYYY-MM-DD` | Only albums released on or before this date. |
| `--export FILE` | Export to file: `.csv` for spreadsheet, any other extension for tiddl-compatible URL list. |

### `show report` options

Displays a Rich table in the console with: Artist ID, Artist Name, Albums, Songs, and a totals footer row.

| Option | Description |
|---|---|
| `--export FILE` | Export to `.csv` (UTF-8 BOM, Excel-compatible) or `.html` (dark-themed table). |

> Artists with `Albums = 0` were added to monitoring but have not been refreshed yet.

### `show discography` options

Generates one file per letter (A–Z and `#`) for each requested format, containing all artists and their albums sorted by release date.

| Option | Description |
|---|---|
| `--format`, `-f [csv\|txt\|html]` | Output format(s). Can be specified multiple times (default: `csv txt html`). |
| `--output`, `-o DIR` | Directory where files will be saved (default: current directory). |

**Example:**
```bash
tidmon show discography --format csv --format html -o ~/Music/catalog
```

---

## `search` — Search TIDAL

```
tidmon search <QUERY> [OPTIONS]
```

| Option | Description |
|---|---|
| `--type`, `-t [artists\|albums\|tracks]` | Type of content to search (default: `artists`). |
| `--limit`, `-l N` | Maximum number of results to return (default: 10). |

**Examples:**
```bash
tidmon search "Rosalía"
tidmon search "Motomami" --type albums
tidmon search "Con Altura" --type tracks --limit 5
```

---

## `config` — Configuration

View and modify `tidmon` configuration values.

| Command | Description |
|---|---|
| `tidmon config show` | Show the full current configuration. |
| `tidmon config get <KEY>` | Get the value of a specific configuration key. |
| `tidmon config set <KEY> <VALUE>` | Set a new value for a configuration key. |
| `tidmon config path` | Show the path to the `config.json` file. |

**Examples:**
```bash
tidmon config set save_lrc true
tidmon config set save_video true
tidmon config set monitor_interval_hours 12
tidmon config set quality_order '["MAX", "HI_RES_LOSSLESS", "LOSSLESS"]'
```

---

## `backup` — Backup and Restore

Create and restore backups of your database and configuration.

| Command | Description |
|---|---|
| `tidmon backup create [-o FILE]` | Create a new backup archive. Defaults to the `tidmon` data directory. |
| `tidmon backup restore <FILE>` | Restore data from a backup file. |
| `tidmon backup list` | List all available backups. |
| `tidmon backup delete [FILE\|--keep N]` | Delete a specific backup, or keep only the N most recent. |

---

## `reset` — Reset the Database

Remove all monitored artists, albums, and download history from the database.

```
tidmon reset [OPTIONS]
```

| Option | Description |
|---|---|
| *(none)* | Reset the entire database (artists, albums, playlists). Requires confirmation. |
| `--artists` | Remove only monitored artists and their albums. |
| `--db` | Explicitly reset the full database (same as no option). |

> ⚠️ This action is irreversible. Use `tidmon backup create` before resetting if you want to preserve your data.
