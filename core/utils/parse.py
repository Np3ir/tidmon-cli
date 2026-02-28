"""
Stream parsers — ported from tiddl/core/utils/parse.py with tidmon model names.
"""

from base64 import b64decode
from xml.etree.ElementTree import fromstring
from typing import Tuple, List
import json

from m3u8 import M3U8
from requests import Session

from tidmon.core.models.resources import TrackStream, VideoStream


def parse_manifest_XML(xml_content: str) -> Tuple[List[str], str]:
    """Parse DASH XML manifest (used for HI_RES_LOSSLESS tracks)."""

    NS = "{urn:mpeg:dash:schema:mpd:2011}"
    tree = fromstring(xml_content)

    representation = tree.find(
        f"{NS}Period/{NS}AdaptationSet/{NS}Representation"
    )
    if representation is None:
        raise ValueError("Representation element not found in DASH manifest")

    codecs = representation.get("codecs", "")

    segment_template = representation.find(f"{NS}SegmentTemplate")
    if segment_template is None:
        raise ValueError("SegmentTemplate element not found in DASH manifest")

    url_template = segment_template.get("media")
    if url_template is None:
        raise ValueError("No `media` attribute in SegmentTemplate")

    timeline_elements = segment_template.findall(f"{NS}SegmentTimeline/{NS}S")
    if not timeline_elements:
        raise ValueError("SegmentTimeline elements not found in DASH manifest")

    total = 0
    for element in timeline_elements:
        total += 1
        count = element.get("r")
        if count is not None:
            total += int(count)

    urls = [url_template.replace("$Number$", str(i)) for i in range(0, total + 1)]

    return urls, codecs


def parse_track_stream(track_stream: TrackStream) -> Tuple[List[str], str]:
    """
    Parse URLs and file extension from a TrackStream.

    Manifest types:
      application/vnd.tidal.bts  → JSON  (LOW / HIGH / LOSSLESS)
      application/dash+xml       → DASH XML  (HI_RES_LOSSLESS)

    Returns:
        (urls, extension)  where extension is one of '.flac', '.m4a'
    """
    decoded_manifest = b64decode(track_stream.manifest).decode()
    manifest_mime    = track_stream.manifest_mime_type

    if manifest_mime == "application/vnd.tidal.bts":
        manifest_data = json.loads(decoded_manifest)
        urls   = manifest_data.get("urls", [])
        codecs = manifest_data.get("codecs", "")

    elif manifest_mime == "application/dash+xml":
        urls, codecs = parse_manifest_XML(decoded_manifest)

    else:
        raise ValueError(f"Unknown manifest MIME type: {manifest_mime!r}")

    # Determine file extension from codec string
    if codecs == "flac":
        # HI_RES_LOSSLESS delivers FLAC inside an M4A container
        extension = ".m4a" if track_stream.audio_quality == "HI_RES_LOSSLESS" else ".flac"
    elif codecs.startswith("mp4"):
        extension = ".m4a"
    else:
        # FIX: raise instead of silently defaulting — unknown codec should be investigated
        raise ValueError(
            f"Unknown codec {codecs!r} for track stream "
            f"(quality={track_stream.audio_quality})"
        )

    return urls, extension


def parse_video_stream(video_stream: VideoStream) -> Tuple[List[str], str]:
    """
    Parse a VideoStream manifest and return the highest-quality HLS segment URLs.

    Tiddl approach (ported verbatim):
      1. Decode manifest → get master M3U8 URL
      2. Fetch master M3U8 → list of quality variants
      3. Pick last variant (highest bitrate)
      4. Fetch that variant M3U8 → individual segment URLs

    Returns:
        (segment_urls, '.mp4')
    """
    decoded_manifest = b64decode(video_stream.manifest).decode()

    class _VideoManifest:
        """Minimal model — manifest is a JSON with a 'urls' list."""
        def __init__(self, data: dict):
            self.urls: List[str] = data.get("urls", [])

    manifest_data = json.loads(decoded_manifest)
    manifest      = _VideoManifest(manifest_data)

    if not manifest.urls:
        raise ValueError("Video manifest contains no URLs")

    with Session() as s:
        # Step 1: Fetch master M3U8 (lists quality variants)
        req    = s.get(manifest.urls[0])
        master = M3U8(req.text)

        if not master.playlists:
            raise ValueError("Master M3U8 contains no quality variants")

        # Step 2: Pick the last playlist entry (highest quality / bitrate)
        uri = master.playlists[-1].uri
        if not uri:
            raise ValueError("Highest-quality M3U8 playlist has no URI")

        # Step 3: Fetch variant M3U8 → individual segment URLs
        req   = s.get(uri)
        video = M3U8(req.text)

    if not video.files:
        raise ValueError("Video M3U8 segment playlist is empty")

    urls = [url for url in video.files if url]
    return urls, ".mp4"