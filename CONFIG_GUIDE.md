# `tidmon` Configuration Guide (`config.json`)

`tidmon` is highly customizable through a `config.json` file located in your user's data directory. This guide explains all available options.

- **Windows**: `C:\Users\YourUser\AppData\Roaming\tidmon\config.json`
- **Linux/macOS**: `~/.local/share/tidmon/config.json`

The file is created automatically the first time you run `tidmon`. You only need to add the keys you want to change — any missing key falls back to its documented default.

---

## Example `config.json`

Complete `config.json` with all available options and their defaults.

```json
{
  "version": "1.2.0",
  "user_id": null,
  "country_code": "US",
  "check_new_releases": true,
  "record_types": [
    "ALBUM",
    "EP",
    "SINGLE",
    "COMPILATION"
  ],
  "quality_order": [
    "MAX",
    "HI_RES_LOSSLESS",
    "LOSSLESS",
    "HIGH",
    "LOW"
  ],
  "save_cover": true,
  "embed_cover": true,
  "save_lrc": false,
  "save_video": true,
  "download_location": {
    "default": "/path/to/your/music",
    "video": "/path/to/your/videos"
  },
  "artist_separator": ", ",
  "concurrent_downloads": 3,
  "requests_per_minute": 50,
  "monitor_interval_hours": 24,
  "email_notifications": false,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_use_tls": true,
  "email_from": "",
  "email_to": "",
  "email_password": "",
  "debug_mode": false,
  "templates": {
    "default": "{artist_initials}/{album.artist}/({album.date:%Y-%m-%d}) {album.title} ({album.release})/{item.number:02}. {item.artists_with_features} - {item.title_version} {item.explicit:shortparens}",
    "video": "{artist_initials}/{album.artist}/({item.releaseDate:%Y-%m-%d}) {item.artists_with_features} - {item.title_version} {item.explicit:shortparens}",
    "playlist": "!playlists/{playlist.title}/{item.artists_with_features} - {item.title_version} {item.explicit:shortparens}"
  }
}
```

---

## Configuration Options

### General

| Key | Type | Default | Description |
|---|---|---|---|
| `user_id` | integer | `null` | Your TIDAL user ID. Set automatically by `tidmon auth`. |
| `country_code` | string | `"US"` | Your TIDAL country code. Set automatically by `tidmon auth`. |
| `check_new_releases` | bool | `true` | Whether `tidmon` tracks new releases for monitored artists. |
| `record_types` | list | `["ALBUM","EP","SINGLE","COMPILATION"]` | Album types to monitor. Types not in this list are ignored. |
| `monitor_interval_hours` | integer | `24` | Informational interval for scheduled refreshes. |
| `debug_mode` | bool | `false` | Enable verbose debug output. |

---

### Download Quality

- `quality_order`: list of strings
  - Preferred download qualities in order of preference. `tidmon` tries each in order, falling back to the next if unavailable.

| Value | Description |
|---|---|
| `"MAX"` | Hi-Res FLAC / MQA (best quality) |
| `"HI_RES_LOSSLESS"` | Standard Hi-Res FLAC |
| `"LOSSLESS"` | CD Quality FLAC (16-bit, 44.1 kHz) |
| `"HIGH"` | 320 kbps AAC |
| `"LOW"` | 96 kbps AAC |

---

### File and Metadata

| Key | Type | Default | Description |
|---|---|---|---|
| `save_cover` | bool | `true` | Save the album cover as `cover.jpg` in the album folder. |
| `embed_cover` | bool | `true` | Embed the album cover into the metadata of each audio file. |
| `save_lrc` | bool | `false` | Download synchronized lyrics in `.lrc` format (if available). |
| `save_video` | bool | `true` | Download music videos when fetching an artist's content. Also enables video detection during `tidmon refresh`. |
| `concurrent_downloads` | integer | `3` | Number of tracks downloaded simultaneously within an album. |

---

### Download Paths

- `download_location`: object
  - `"default"`: Base path for all audio downloads.
  - `"video"`: Base path for all video downloads. Ignored if the `video` template contains an absolute path.

**Note on absolute paths in templates:** If the `video` template starts with an absolute path (e.g., `G:/Artistas/{artist_initials}/...`), `tidmon` uses that path directly and ignores `download_location.video`. This lets you configure a different root per template without touching `download_location`.

---

### Concurrent Downloads & Rate Limiting

| Key | Type | Default | Description |
|---|---|---|---|
| `concurrent_downloads` | integer | `3` | Simultaneous track downloads per album. |
| `requests_per_minute` | integer | `50` | Maximum TIDAL API calls per minute. |

**Rate limiting behavior:**
- A fixed-interval gate serializes all requests (`60 / rpm` seconds per request) with per-request jitter to avoid burst patterns.
- An adaptive delay (`_rate_limit_delay`) self-tunes: +1 s on every HTTP 429 (max 5 s), −0.1 s on every success (floor 0 s).
- `requests_per_minute` is a ceiling — actual throughput self-adjusts.

| Value | Use case |
|---|---|
| `30` | Conservative — shared accounts or slow connections |
| `50` | Default — suits most TIDAL accounts |
| `80` | Aggressive — raise only if 429s never occur |

---

### Artist Separator

- `artist_separator`: string (default: `", "`)
  - The separator used between artist names in `{item.artists}`, `{item.features}`, and `{item.artists_with_features}`.

| Value | Result |
|---|---|
| `", "` | `The Weeknd, Daft Punk` |
| `" / "` | `The Weeknd / Daft Punk` |
| `"; "` | `The Weeknd; Daft Punk` |
| `" & "` | `The Weeknd & Daft Punk` |

---

### Email Notifications

Receive an email summary when `tidmon refresh` finds new releases.

| Key | Description |
|---|---|
| `email_notifications` | `true` to enable email on new releases. |
| `smtp_server` | SMTP server hostname (default: `smtp.gmail.com`). |
| `smtp_port` | SMTP port (default: `587`). |
| `smtp_use_tls` | Use STARTTLS (default: `true`). |
| `email_from` | Sender email address. |
| `email_to` | Recipient email address. |
| `email_password` | Sender password. If using Gmail with 2FA, use an **App Password**. |

---

## Path Templating System

The `templates` section controls the exact folder structure and filenames for your downloads.

| Key | Used for |
|---|---|
| `"default"` | Standard album track downloads. |
| `"video"` | Music video downloads. |
| `"playlist"` | Tracks downloaded from a monitored playlist. |

### Available Template Variables

**Track / Item variables:**

| Variable | Description | Example |
|---|---|---|
| `{item.title}` | Track title | `Starboy` |
| `{item.title_version}` | Track title with version/remix info | `Starboy (Remastered)` |
| `{item.artist}` | Main track artist | `The Weeknd` |
| `{item.artists}` | Main artists joined by `artist_separator` | `The Weeknd, Daft Punk` |
| `{item.features}` | Featured artists joined by `artist_separator` | `Daft Punk` |
| `{item.artists_with_features}` | All artists (main + featured) | `The Weeknd, Daft Punk` |
| `{item.number}` | Track number | `1` |
| `{item.number:02}` | Track number zero-padded | `01` |
| `{item.releaseDate}` | Track release date | `2016-11-25` |
| `{item.explicit}` | `Explicit` if explicit, empty otherwise | `Explicit` |
| `{item.explicit:short}` | Short explicit marker | `E` |
| `{item.explicit:shortparens}` | Short explicit in parentheses | `(E)` |

**Album variables** (available in `default` template):

| Variable | Description | Example |
|---|---|---|
| `{album.title}` | Album title | `Starboy` |
| `{album.artist}` | Main album artist | `The Weeknd` |
| `{album.artists}` | All album artists | `The Weeknd` |
| `{album.date}` | Album release date | `2016-11-25` |
| `{album.year}` | Album release year | `2016` |
| `{album.release}` | Release type | `ALBUM` |

**Shared variables:**

| Variable | Description | Example |
|---|---|---|
| `{artist_initials}` | First letter of the main artist name | `T` |

**Playlist variables** (available in `playlist` template):

| Variable | Description |
|---|---|
| `{playlist.title}` | Playlist title |

### Date Formatting

Any date variable supports Python `strftime` directives:

| Format | Output |
|---|---|
| `{album.date:%Y-%m-%d}` | `2016-11-25` |
| `{album.date:%Y}` | `2016` |
| `{album.date:%B %d, %Y}` | `November 25, 2016` |

### Template Examples

**Default — organized by artist initial, date, and album:**
```
{artist_initials}/{album.artist}/({album.date:%Y-%m-%d}) {album.title} ({album.release})/{item.number:02}. {item.artists_with_features} - {item.title_version} {item.explicit:shortparens}
```
Result: `T/The Weeknd/(2016-11-25) Starboy (ALBUM)/01. The Weeknd ft. Daft Punk - Starboy`

**Video — absolute path, organized by artist:**
```
G:/Artistas/{artist_initials}/{album.artist}/({item.releaseDate:%Y-%m-%d}) {item.artists_with_features} - {item.title_version} {item.explicit:shortparens}
```
Result: `G:/Artistas/T/The Weeknd/(2021-03-19) The Weeknd - Save Your Tears`

**Simple — artist / year - album / track:**
```
{album.artist}/{album.date:%Y} - {album.title}/{item.number:02}. {item.title}
```
Result: `The Weeknd/2016 - Starboy/01. Starboy`
