# `tidmon` Command Guide

This is a reference guide for all available commands in `tidmon`.

---

## Main Commands

*   `tidmon [OPTIONS] COMMAND [ARGS]...`

**Global Options:**

*   `--version`: Show the version of `tidmon`.
*   `-v`, `--verbose`: Show detailed information messages (INFO).
*   `-d`, `--debug`: Show debugging messages (DEBUG).
*   `--help`: Show help for a command.

---

## `auth`: Authentication

Manages the connection and login with your TIDAL account.

*   **`tidmon auth`**: Starts the interactive authentication process through the browser.
*   **`tidmon logout`**: Deletes the saved authentication credentials.
*   **`tidmon whoami`**: Shows information about the current session (user, country, and token expiration time).

---

## `monitor`: Manage Artists and Playlists

The core of `tidmon`. Allows you to add, remove, and list the artists and playlists you want to supervise.

*   **`tidmon monitor add [IDENTIFIERS...] [-f FILE]`**: Adds one or more artists/playlists.
    *   Accepts artist names (e.g., "Daft Punk"), artist IDs, artist URLs, and playlist URLs.
    *   `--file, -f`: Imports a list of artists/playlists from a text file (one per line).
*   **`tidmon monitor remove [IDENTIFIERS...]`**: Removes artists from monitoring by name or ID.
*   **`tidmon monitor list`**: Shows a list of all monitored artists and playlists.
*   **`tidmon monitor clear`**: Removes **all** artists from monitoring (asks for confirmation).
*   **`tidmon monitor export -o [FILE]`**: Exports artist IDs and playlist URLs to a file.

---

## `refresh`: Search for New Releases

Checks TIDAL for new albums or tracks from the artists and playlists you are monitoring.

*   **`tidmon refresh [OPTIONS]`**

**Options:**

*   `-D`, `--download`: Automatically downloads the new releases found.
*   `--artist <NAME>`, `-a <NAME>`: Refreshes only a specific artist by name.
*   `--id <ID>`: Refreshes only a specific artist by ID.
*   `--since <YYYY-MM-DD>`: Refreshes only artists added *after* a date.
*   `--until <YYYY-MM-DD>`: Refreshes only artists added *before* a date.
*   `--album-since <YYYY-MM-DD>`: Processes only albums released *after* a date.
*   `--album-until <YYYY-MM-DD>`: Processes only albums released *before* a date.

---

## `download`: Download Music and Videos

The advanced download system of `tidmon`.

*   **`tidmon download album <ALBUM_ID> [--force]`**: Downloads a full album by its ID.
*   **`tidmon download artist [ID | "NAME"] [--force]`**: Downloads the complete discography of an artist.
*   **`tidmon download track <TRACK_ID> [--force]`**: Downloads a single track by its ID.
*   **`tidmon download url <TIDAL_URL> [--force]`**: Downloads from a TIDAL URL (album, artist, track, etc.).
*   **`tidmon download monitored [OPTIONS]`**: Downloads all pending albums from monitored artists.
    *   Options: `--force`, `--since <DATE>`, `--until <DATE>`, `--dry-run`
*   **`tidmon download all [OPTIONS]`**: Downloads **all** albums from the database, regardless of their status.
    *   Options: `--force`, `--dry-run`, `--resume`, `--since <DATE>`, `--until <DATE>`

**Common Download Options:**

*   `--force`: Redownloads the content even if the file already exists.
*   `--dry-run`: Shows what would be downloaded, but without performing the actual download.
*   `--resume`: Resumes a bulk download (`download all`), skipping already completed albums.
*   `--since <DATE>` / `--until <DATE>`: Filters the albums to be processed by their release date.

---

## `show`: Display Database Information

Lets you inspect the local database of artists and albums.

*   **`tidmon show artists`**: Lists all monitored artists.
*   **`tidmon show releases [--days <N> | --future]`**: Shows recent or upcoming releases.
    *   `--days <N>`: Show releases from the last N days (default: 7).
    *   `--future`: Show upcoming releases dated in the future.
*   **`tidmon show albums [OPTIONS]`**: Shows albums from the database with powerful filters.
    *   `--artist <NAME|ID>`: Filter by a specific artist.
    *   `--pending`: Show only albums that have not been downloaded yet.
    *   `--since <DATE>` / `--until <DATE>`: Filter albums by release date.
    *   `--export <FILE>`: Export the filtered list of album URLs to a text file, formatted for other tools like `tiddl`.

---

## `config`: Configuration

Allows you to view and modify the `tidmon` configuration.

*   **`tidmon config show`**: Shows the entire current configuration.
*   **`tidmon config get <KEY>`**: Gets the value of a specific key.
*   **`tidmon config set <KEY> <VALUE>`**: Sets a new value for a key.
*   **`tidmon config path`**: Shows the path to the `config.json` file.

---

## `backup`: Backup and Restore

Manages the creation and restoration of backups of your data (database and configuration).

*   **`tidmon backup create [-o FILE]`**: Creates a new backup archive.
*   **`tidmon backup restore <FILE>`**: Restores data from a backup file.
*   **`tidmon backup list`**: Lists all available backups in the default directory.
*   **`tidmon backup delete <FILE>`**: Deletes a specific backup file.
