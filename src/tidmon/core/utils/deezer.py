"""
Deezer public API — genre enrichment via ISRC lookup.

No authentication required. Used as a fallback when TIDAL does not
provide genre information for a track.
"""

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_SESSION = requests.Session()
_SESSION.headers.update({"Accept": "application/json"})

DEEZER_API = "https://api.deezer.com"
TIMEOUT = 5  # seconds


def get_genre_from_deezer(isrc: str) -> Optional[str]:
    """
    Fetch the primary genre for a track using its ISRC via the Deezer public API.

    Flow:
      1. GET /track/isrc:{isrc}       → get album id
      2. GET /album/{album_id}        → get genre list
      3. Return the first genre name (most relevant)

    Returns None if the track is not found, the request fails, or no genre
    is associated with the album.
    """
    if not isrc:
        return None

    try:
        # Step 1: resolve ISRC → track → album id
        r = _SESSION.get(f"{DEEZER_API}/track/isrc:{isrc}", timeout=TIMEOUT)
        r.raise_for_status()
        track_data = r.json()

        if track_data.get("error") or "album" not in track_data:
            logger.debug(f"Deezer: track not found for ISRC {isrc}")
            return None

        album_id = track_data["album"].get("id")
        if not album_id:
            return None

        # Step 2: fetch album to get genres
        r2 = _SESSION.get(f"{DEEZER_API}/album/{album_id}", timeout=TIMEOUT)
        r2.raise_for_status()
        album_data = r2.json()

        genres = album_data.get("genres", {}).get("data", [])
        if genres:
            genre_name = genres[0].get("name")
            logger.debug(f"Deezer genre for ISRC {isrc}: {genre_name}")
            return genre_name

    except requests.RequestException as e:
        logger.debug(f"Deezer API request failed for ISRC {isrc}: {e}")
    except Exception as e:
        logger.debug(f"Unexpected error fetching Deezer genre for ISRC {isrc}: {e}")

    return None
