# `tidmon` Configuration Guide (`config.json`)

`tidmon` is highly customizable through a `config.json` file located in your user's data directory. This guide explains all the available options.

*   **Windows**: `C:\Users\YourUser\AppData\Local\tidmon\config.json`
*   **Linux/macOS**: `~/.local/share/tidmon/config.json` or `~/.config/tidmon/config.json`

The first time you run `tidmon`, this file will be created automatically with default values.

---

## Example `config.json`

Here is a complete `config.json` file with all default options. You can use this as a template.

```json
{
  "version": "1.0.0",
  "user_id": null,
  "country_code": "US",
  "check_new_releases": true,
  "record_types": [
    "ALBUM",
    "EP",
    "SINGLE"
  ],
  "quality_order": [
    "MAX",
    "HI_RES_LOSSLESS",
    "LOSSLESS",
    "HIGH",
    "LOW"
  ],
  "save_cover": true,
  "save_lrc": false,
  "save_video": true,
  "embed_cover": true,
  "email_notifications": false,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_use_tls": true,
  "email_from": "",
  "email_to": "",
  "email_password": "",
  "download_location": {
    "default": "/path/to/your/music/tidmon",
    "video": "/path/to/your/videos/tidmon"
  },
  "debug_mode": false,
  "monitor_interval_hours": 24,
  "templates": {
    "default": "{album.artist}/{album.date:%Y} - {album.title}/{item.number} - {item.title}",
    "video": "{album.artist}/Videos/{item.title} ({item.releaseDate:%Y})",
    "playlist": "Playlists/{playlist.title}/{item.number} - {item.title}"
  }
}
```

---

## Configuration Options Explained

### General

*   `user_id`, `country_code`
    *   Your TIDAL user ID and country code. These are set automatically during authentication.

*   `check_new_releases`: `true` | `false`
    *   (Not currently used, but planned for future features). Determines if `tidmon` should check for new releases.

*   `record_types`: `[string]`
    *   A list of album types to monitor and download. Any album type not in this list will be ignored.
    *   **Available Values**: `"ALBUM"`, `"EP"`, `"SINGLE"`, `"COMPILATION"`.

### Download Quality

*   `quality_order`: `[string]`
    *   Your preferred download qualities, listed in order of preference. `tidmon` will try to get the first quality on the list. If it's not available, it will try the next one, and so on.
    *   **Available Values**: 
        *   `"MAX"` (Hi-Res FLAC, MQA)
        *   `"HI_RES_LOSSLESS"` (Standard Hi-Res FLAC)
        *   `"LOSSLESS"` (CD Quality FLAC)
        *   `"HIGH"` (320 kbps AAC)
        *   `"LOW"` (96 kbps AAC)

### File and Metadata

*   `save_cover`: `true` | `false`
    *   If `true`, saves the album cover as a `cover.jpg` file in the album's folder.

*   `embed_cover`: `true` | `false`
    *   If `true`, embeds the album cover into the metadata of each audio file.

*   `save_lrc`: `true` | `false`
    *   If `true`, downloads the track lyrics in LRC format (if available), which is compatible with many music players for synchronized lyrics.

*   `save_video`: `true` | `false`
    *   If `true`, downloads music videos when fetching an artist's content.

### Download Paths

*   `download_location`: `{...}`
    *   An object specifying the root directories for your downloads.
    *   `"default"`: The base path for all audio downloads.
    *   `"video"`: The base path for all video downloads.

### Email Notifications

*   `email_notifications`: `true` | `false`
    *   Set to `true` to receive an email summary when `tidmon refresh` finds new releases.
*   `smtp_server`, `smtp_port`, `smtp_use_tls`
    *   Configuration for your SMTP (email) server. Defaults are for Gmail.
*   `email_from`, `email_to`, `email_password`
    *   Your email credentials. The `email_password` is often an "App Password" if you have 2-Factor Authentication enabled on your email account.

---

## Path Templating System

This is one of the most powerful features of `tidmon`. The `templates` section allows you to define the exact folder structure and filenames for your downloads.

*   `"default"`: The template for standard album track downloads.
*   `"video"`: The template for music video downloads.
*   `"playlist"`: The template for tracks downloaded from a playlist context.

### Available Template Variables

You can use properties of the `item` (the track or video being downloaded) and its associated `album` or `playlist`.

**Common Variables (available for `item`):**

*   `{item.title}`: The track title.
*   `{item.title_version}`: The version of the track (e.g., "Remastered", "Live").
*   `{item.artist}`: The main track artist.
*   `{item.artists}`: All track artists, comma-separated.
*   `{item.artists_with_features}`: Main artist plus any featured artists.
*   `{item.number}`: The track number.
*   `{item.releaseDate}`: The release date of the track/video.
*   `{item.explicit}`: The word "Explicit" if the track is explicit.
*   `{item.explicit:short}`: The letter "E".
*   `{item.explicit:shortparens}`: The letter "(E)".

**Album Variables (available for `album`):**

*   `{album.title}`: The album title.
*   `{album.artist}`: The main album artist.
*   `{album.artists}`: All album artists, comma-separated.
*   `{album.date}`: The release date of the album.
*   `{album.release}`: A formatted release string (e.g. "CD", "Deluxe").
*   `{album.year}`: The 4-digit year of the album's release.
*   `{artist_initials}`: The first letter of the main album artist's name (e.g., "D" for "Daft Punk"), useful for creating A-Z folders.

**Playlist Variables (available for `playlist`):**

*   `{playlist.title}`: The title of the playlist.

### Date Formatting

You can format any date variable (`album.date`, `item.releaseDate`) using standard Python `strftime` directives. 

*   `{album.date:%Y-%m-%d}` -> `2001-03-13`
*   `{album.date:%Y}` -> `2001`
*   `{album.date:%B %d, %Y}` -> `March 13, 2001`
