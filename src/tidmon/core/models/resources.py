"""
Pydantic models for TIDAL API resources.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any, Literal
from datetime import datetime
from enum import Enum


# MediaMetadata MUST be defined before Album/Track
class MediaMetadata(BaseModel):
    tags: Optional[List[str]] = None


class Artist(BaseModel):
    id: int
    name: str
    type: Optional[str] = None
    picture: Optional[str] = None
    popularity: Optional[int] = None


class Album(BaseModel):
    id: int
    title: str
    duration: Optional[int] = None
    number_of_tracks: Optional[int] = Field(None, alias='numberOfTracks')
    number_of_videos: Optional[int] = Field(None, alias='numberOfVideos')
    number_of_volumes: Optional[int] = Field(None, alias='numberOfVolumes')
    release_date: Optional[datetime] = Field(None, alias='releaseDate')
    copyright: Optional[str] = None
    type: Optional[str] = None
    version: Optional[str] = None
    url: Optional[str] = None
    cover: Optional[str] = None
    explicit: Optional[bool] = None
    audio_quality: Optional[str] = Field(None, alias='audioQuality')
    artist: Optional[Artist] = None
    artists: List[Artist] = []
    media_metadata: Optional[MediaMetadata] = Field(None, alias='mediaMetadata')
    genre: Optional[str] = None

    @validator('release_date', pre=True)
    def parse_release_date(cls, v):
        if isinstance(v, str):
            # The API can return just a year, or year-month, or year-month-day
            # We pad it to be a full date to avoid errors
            if len(v) == 4: # YYYY
                v += '-01-01'
            elif len(v) == 7: # YYYY-MM
                v += '-01'
            return datetime.strptime(v, '%Y-%m-%d')
        return v


    class Config:
        allow_population_by_field_name = True


class Track(BaseModel):
    id: int
    title: str
    duration: Optional[int] = None
    replay_gain: Optional[float] = Field(None, alias='replayGain')
    peak: Optional[float] = None
    track_number: Optional[int] = Field(None, alias='trackNumber')
    volume_number: Optional[int] = Field(None, alias='volumeNumber')
    version: Optional[str] = None
    isrc: Optional[str] = None
    explicit: Optional[bool] = None
    audio_quality: Optional[str] = Field(None, alias='audioQuality')
    copyright: Optional[str] = Field(None, alias='copyright')
    bpm: Optional[int] = None
    album: Optional[Album] = None
    artist: Optional[Artist] = None
    artists: List[Artist] = []
    media_metadata: Optional[MediaMetadata] = Field(None, alias='mediaMetadata')
    release_date: Optional[datetime] = Field(None, alias='releaseDate')
    stream_start_date: Optional[datetime] = Field(None, alias='streamStartDate')
    allow_streaming: Optional[bool] = Field(True, alias='allowStreaming')

    @validator('release_date', 'stream_start_date', pre=True)
    def parse_dates(cls, v):
        if isinstance(v, str):
            if len(v) == 4: # YYYY
                v += '-01-01'
            elif len(v) == 7: # YYYY-MM
                v += '-01'
            
            if 'T' in v and v.endswith('Z'):
                # Handle ISO 8601 format like '2021-03-19T10:00:00.000Z'
                try:
                    return datetime.fromisoformat(v.replace('.000Z', '+00:00'))
                except ValueError:
                    # Fallback for different ISO 8601 format without milliseconds
                    return datetime.fromisoformat(v.replace('Z', '+00:00'))

            try:
                return datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                return v # return original value if parsing fails
        return v

    class Config:
        allow_population_by_field_name = True


class Video(BaseModel):
    id: int
    title: str
    duration: Optional[int] = None
    image_id: Optional[str] = Field(None, alias='imageId')
    track_number: Optional[int] = Field(None, alias='trackNumber')
    volume_number: Optional[int] = Field(None, alias='volumeNumber')
    explicit: Optional[bool] = None
    artist: Optional[Artist] = None
    artists: List[Artist] = []
    album: Optional[Album] = None
    release_date: Optional[datetime] = Field(None, alias='releaseDate')
    stream_start_date: Optional[datetime] = Field(None, alias='streamStartDate')
    quality: Optional[str] = None
    allow_streaming: Optional[bool] = Field(True, alias='allowStreaming')

    @validator('release_date', 'stream_start_date', pre=True)
    def parse_dates(cls, v):
        if isinstance(v, str):
            if len(v) == 4: # YYYY
                v += '-01-01'
            elif len(v) == 7: # YYYY-MM
                v += '-01'
            
            if 'T' in v and v.endswith('Z'):
                # Handle ISO 8601 format like '2021-03-19T10:00:00.000Z'
                try:
                    return datetime.fromisoformat(v.replace('.000Z', '+00:00'))
                except ValueError:
                    # Fallback for different ISO 8601 format without milliseconds
                    return datetime.fromisoformat(v.replace('Z', '+00:00'))

            try:
                return datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                return v # return original value if parsing fails
        return v

    class Config:
        allow_population_by_field_name = True


class Playlist(BaseModel):
    uuid: str
    title: str
    number_of_tracks: int = Field(..., alias='numberOfTracks')
    number_of_videos: int = Field(..., alias='numberOfVideos')
    description: Optional[str] = None
    duration: int
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')
    created: Optional[datetime] = None
    type: str
    public: Optional[bool] = Field(None, alias='publicPlaylist')
    url: Optional[str] = None
    image: Optional[str] = None
    popularity: Optional[int] = None

    @validator('last_updated', 'created', pre=True)
    def parse_dates(cls, v):
        if isinstance(v, str):
            if 'T' in v and v.endswith('Z'):
                # Handle ISO 8601 format like '2021-03-19T10:00:00.000Z'
                try:
                    return datetime.fromisoformat(v.replace('.000Z', '+00:00'))
                except ValueError:
                    # Fallback for different ISO 8601 format without milliseconds
                    return datetime.fromisoformat(v.replace('Z', '+00:00'))
            try:
                return datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                return v # return original value if parsing fails
        return v

    class Config:
        allow_population_by_field_name = True


class Contributor(BaseModel):
    name: str
    role: Optional[str] = None


class TrackCredits(BaseModel):
    track_id: Optional[int] = Field(None, alias='trackId')
    source: Optional[str] = None
    contributors: List[Contributor] = []

    class Config:
        allow_population_by_field_name = True


class TrackMix(BaseModel):
    id: str


class ArtistBio(BaseModel):
    source: Optional[str] = None
    last_updated: Optional[datetime] = Field(None, alias='lastUpdated')
    text: Optional[str] = None
    summary: Optional[str] = None

    @validator('last_updated', pre=True)
    def parse_dates(cls, v):
        if isinstance(v, str):
            if 'T' in v and v.endswith('Z'):
                # Handle ISO 8601 format like '2021-03-19T10:00:00.000Z'
                try:
                    return datetime.fromisoformat(v.replace('.000Z', '+00:00'))
                except ValueError:
                    # Fallback for different ISO 8601 format without milliseconds
                    return datetime.fromisoformat(v.replace('Z', '+00:00'))
            try:
                return datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                return v # return original value if parsing fails
        return v

    class Config:
        allow_population_by_field_name = True


class ArtistLinks(BaseModel):
    source: Optional[str] = None
    url: Optional[str] = None


class ArtistTopTracks(BaseModel):
    limit: int
    offset: int
    total_number_of_items: int = Field(..., alias='totalNumberOfItems')
    items: List[Track] = []

    class Config:
        allow_population_by_field_name = True


class TrackQuality(str, Enum):
    LOW = "LOW"
    HIGH = "HIGH"
    LOSSLESS = "LOSSLESS"
    HI_RES_LOSSLESS = "HI_RES_LOSSLESS"


class StreamVideoQuality(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TrackStream(BaseModel):
    track_id: int = Field(..., alias='trackId')
    audio_quality: str = Field(..., alias='audioQuality')
    audio_mode: Optional[str] = Field(None, alias='audioMode')
    manifest: str
    manifest_mime_type: str = Field(..., alias='manifestMimeType')
    bit_depth: Optional[int] = Field(None, alias='bitDepth')
    sample_rate: Optional[int] = Field(None, alias='sampleRate')

    class Config:
        allow_population_by_field_name = True


class VideoStream(BaseModel):
    video_id: int = Field(..., alias='videoId')
    video_quality: str = Field(..., alias='videoQuality')
    manifest: str
    manifest_mime_type: str = Field(..., alias='manifestMimeType')

    class Config:
        allow_population_by_field_name = True


TRACK_QUALITY_LITERAL = Literal["low", "normal", "high", "max"]
VIDEO_QUALITY_LITERAL = Literal["sd", "hd", "fhd"]

track_qualities: dict = {
    "low": TrackQuality.LOW,
    "normal": TrackQuality.HIGH,
    "high": TrackQuality.LOSSLESS,
    "max": TrackQuality.HI_RES_LOSSLESS,
}

video_qualities: dict = {
    "sd": StreamVideoQuality.LOW,
    "hd": StreamVideoQuality.MEDIUM,
    "fhd": StreamVideoQuality.HIGH,
}

# AudioQualityEnum / VideoQualityEnum aliases
AudioQualityEnum = TrackQuality
VideoQualityEnum = StreamVideoQuality
AlbumTypeEnum = Literal["ALBUM", "EP", "SINGLE", "COMPILATION"]
