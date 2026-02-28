# tidmon

A powerful command-line tool for monitoring TIDAL artists, tracking new releases, and automating your music library management.

`tidmon` helps you keep your local music collection perfectly in sync with your favorite artists' discographies on TIDAL. It maintains a local database of artists you want to follow, checks for new albums, and provides a robust downloader to save them to your machine.

## Features

- **Artist & Playlist Monitoring**: Keep a list of your favorite artists and playlists to track for new releases.
- **Automatic Refresh**: Check for new albums and tracks with a single command.
- **High-Quality Downloads**: Download music in the highest quality available, including Hi-Res FLAC (MAX), with fallback to lower qualities.
- **Advanced Downloader**: Download by artist, album, track, or URL. Includes support for resuming interrupted downloads and forcing re-downloads.
- **Customizable File Organization**: Use powerful and flexible templates to define your folder structure and file naming conventions.
- **Robust and Resilient**: Handles token expiration automatically for long-running sessions and includes rate-limiting to respect the TIDAL API.
- **Local Database**: All monitored items and release history are stored locally, giving you full control over your data.

## Installation

1.  **Prerequisites**:
    *   **Python 3.10+**
    *   **FFmpeg**: Make sure `ffmpeg` is installed and available in your system's PATH. It is required for processing audio and video files.

2.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Np3ir/tidmon-cli.git
    cd tidmon
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Quick Start

1.  **Authenticate with TIDAL**:
    *   Run the interactive login process. This will open a browser window for you to authorize the application.
    ```bash
    python tidmon auth
    ```

2.  **Monitor an Artist**:
    *   Start tracking an artist by their name or TIDAL URL.
    ```bash
    python tidmon monitor add "Daft Punk"
    ```

3.  **Check for New Releases & Download**:
    *   `tidmon` will check for any new albums from your monitored artists and automatically download them.
    ```bash
    python tidmon refresh --download
    ```

## Command Reference

For a full list of all available commands, options, and advanced usage examples, please see the complete guide:

**[--> Full Command Reference (COMMANDS.md)](COMMANDS.md)**
