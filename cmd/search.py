import logging
from tidmon.core.db import Database
from tidmon.core.config import Config
from tidmon.core.auth import get_session

logger = logging.getLogger(__name__)


class Search:
    """Handle artist/album/track search with interactive selection."""

    def __init__(self, config=None):
        self.config = config or Config()
        self.db = Database()
        self.session = get_session()
        self._api = None

    @property
    def api(self):
        if self._api is None:
            self._api = self.session.get_api()
        return self._api

    def search_artists(self, query: str, limit: int = 10):
        """Search for artists and optionally add to monitoring."""
        logger.info(f"Searching artists: {query}")

        results = self.api.search(query, search_type='ARTISTS', limit=limit)

        if not results or not results.artists or not results.artists.items:
            print(f"\n  No artists found for '{query}'\n")
            return

        artists = results.artists.items
        print("\n" + "=" * 60)
        print(f"  ARTIST RESULTS: {query}")
        print("=" * 60 + "\n")

        for i, artist in enumerate(artists, 1):
            monitored = self.db.get_artist(artist.id)
            status = "  ✓ [monitored]" if monitored else ""
            print(f"  {i:2}. {artist.name}{status}")
            print(f"      ID: {artist.id}")
            print()

        print("=" * 60)

        while True:
            try:
                choice = input("\n  Add to monitoring? (number or 0 to skip): ").strip()
                choice = int(choice)

                if choice == 0:
                    break

                if 1 <= choice <= len(artists):
                    artist = artists[choice - 1]
                    if self.db.get_artist(artist.id):
                        print(f"\n  Already monitoring {artist.name}\n")
                    else:
                        from tidmon.cmd.monitor import Monitor
                        m = Monitor()
                        m._add_artist(artist)
                    break
                else:
                    print("  Invalid choice.")
            except ValueError:
                print("  Enter a number.")
            except KeyboardInterrupt:
                print("\n")
                break

    def search_albums(self, query: str, limit: int = 10):
        """Search for albums."""
        logger.info(f"Searching albums: {query}")

        results = self.api.search(query, search_type='ALBUMS', limit=limit)

        if not results or not results.albums or not results.albums.items:
            print(f"\n  No albums found for '{query}'\n")
            return

        albums = results.albums.items
        print("\n" + "=" * 60)
        print(f"  ALBUM RESULTS: {query}")
        print("=" * 60 + "\n")

        for i, album in enumerate(albums, 1):
            artist_name = album.artist.name if album.artist else "Unknown"
            release = album.release_date.year if album.release_date else "?"
            explicit = " [E]" if album.explicit else ""
            print(f"  {i:2}. {album.title}{explicit}")
            print(f"      {artist_name}  |  {release}  |  ID: {album.id}")
            print()

        print("=" * 60 + "\n")

        while True:
            try:
                choice = input("  Download album? (number or 0 to skip): ").strip()
                choice = int(choice)
                if choice == 0:
                    break
                if 1 <= choice <= len(albums):
                    album = albums[choice - 1]
                    from tidmon.cmd.download import Download
                    Download().download_album(album.id)
                    break
                else:
                    print("  Invalid choice.")
            except ValueError:
                print("  Enter a number.")
            except KeyboardInterrupt:
                print("\n")
                break

    def search_tracks(self, query: str, limit: int = 10):
        """Search for tracks."""
        logger.info(f"Searching tracks: {query}")

        results = self.api.search(query, search_type='TRACKS', limit=limit)

        if not results or not results.tracks or not results.tracks.items:
            print(f"\n  No tracks found for '{query}'\n")
            return

        tracks = results.tracks.items
        print("\n" + "=" * 60)
        print(f"  TRACK RESULTS: {query}")
        print("=" * 60 + "\n")

        for i, track in enumerate(tracks, 1):
            artist_name = track.artist.name if track.artist else "Unknown"
            album_title = track.album.title if track.album else "Unknown Album"
            explicit = " [E]" if track.explicit else ""
            print(f"  {i:2}. {track.title}{explicit}")
            print(f"      {artist_name}  |  {album_title}  |  ID: {track.id}")
            print()

        print("=" * 60 + "\n")

        while True:
            try:
                choice = input("  Download track? (number or 0 to skip): ").strip()
                choice = int(choice)
                if choice == 0:
                    break
                if 1 <= choice <= len(tracks):
                    track = tracks[choice - 1]
                    from tidmon.cmd.download import Download
                    Download().download_track(track.id)
                    break
                else:
                    print("  Invalid choice.")
            except ValueError:
                print("  Enter a number.")
            except KeyboardInterrupt:
                print("\n")
                break