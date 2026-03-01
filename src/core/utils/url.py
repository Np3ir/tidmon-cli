import re
from enum import Enum
from typing import Optional
from dataclasses import dataclass

@dataclass
class TidalUrl:
    tidal_type: 'TidalType'
    tidal_id: str
    country_code: Optional[str] = None

class TidalType(Enum):
    ARTIST = "artist"
    ALBUM = "album"
    TRACK = "track"
    VIDEO = "video"
    PLAYLIST = "playlist"
    MIX = "mix"

def parse_url(url: str) -> Optional["TidalUrl"]:
    """
    Parse Tidal URL and return a TidalUrl object.
    Supports:
    - https://tidal.com/browse/artist/Name/12345
    - https://tidal.com/browse/album/12345
    - https://tidal.com/browse/track/12345
    - https://tidal.com/artist/12345
    - https://listen.tidal.com/album/12345
    """
    if not url:
        return None

    # Standardize URL
    url = url.strip()

    # Extract country code if present. The original code did not parse this,
    # so it's added to align with the expected TidalUrl object structure.
    country_code_match = re.search(r"[?&]countryCode=([A-Z]{2})", url, re.IGNORECASE)
    country_code = country_code_match.group(1).upper() if country_code_match else None

    # Artist/Album/Track/Video (Numeric IDs)
    # https://tidal.com/browse/artist/The-Weeknd/3528531
    # https://tidal.com/browse/artist/3528531

    numeric_types = ['artist', 'album', 'track', 'video']
    for type_str in numeric_types:
        # Match .../type/12345 or .../type/Name/12345
        # We look for the type followed by slash, maybe some text and slash, then digits at the end or before ?
        pattern = f"/{type_str}/(?:[^/]+/)?(\\d+)"
        match = re.search(pattern, url)
        if match:
            return TidalUrl(TidalType(type_str), match.group(1), country_code)

    # Playlist/Mix (UUIDs)
    # https://tidal.com/browse/playlist/50937748-912b-4261-8451-24756a655848
    uuid_types = ['playlist', 'mix']
    for type_str in uuid_types:
        pattern = f"/{type_str}/([0-9a-fA-F-]{{36}})"
        match = re.search(pattern, url)
        if match:
            return TidalUrl(TidalType(type_str), match.group(1), country_code)

    return None
