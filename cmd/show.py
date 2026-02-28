import logging
import csv
from pathlib import Path
from tidmon.core.db import Database

logger = logging.getLogger(__name__)


class Show:
    """Display information about artists, releases, etc."""
    
    def __init__(self):
        self.db = Database()
    
    def show_artists(self, export_csv: bool = False, export_path: str = None):
        """Show all monitored artists"""
        artists = self.db.get_all_artists()
        
        if not artists:
            print("\nNo artists being monitored.\n")
            return
        
        if export_csv:
            self._export_artists_csv(artists, export_path)
            return
        
        print("\n" + "="*60)
        print("  MONITORED ARTISTS")
        print("="*60 + "\n")
        
        for artist in artists:
            # Count albums
            albums = self.db.get_artist_albums(artist['artist_id'])
            album_count = len(albums)
            
            last_checked = artist.get('last_checked', 'Never')
            if last_checked and last_checked != 'Never':
                last_checked = last_checked.split('T')[0]
            
            print(f"  • {artist['artist_name']}")
            print(f"    ID: {artist['artist_id']}")
            print(f"    Albums in DB: {album_count}")
            print(f"    Added: {artist['added_date'].split('T')[0]}")
            print(f"    Last checked: {last_checked}")
            print()
        
        print("="*60 + "\n")
        print(f"Total: {len(artists)} artists\n")
    
    def _export_artists_csv(self, artists: list, export_path: str = None):
        """Export artists to CSV"""
        if not export_path:
            export_path = Path.cwd() / "tidmon_artists.csv"
        else:
            export_path = Path(export_path)
        
        try:
            with open(export_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Artist ID', 'Artist Name', 'Added Date', 'Last Checked'])
                
                for artist in artists:
                    writer.writerow([
                        artist['artist_id'],
                        artist['artist_name'],
                        artist['added_date'],
                        artist.get('last_checked', '')
                    ])
            
            logger.info(f"✓ Exported {len(artists)} artists to {export_path}")
            print(f"\n✓ Exported to: {export_path}\n")
        
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
    
    def show_releases(self, days: int = 7, future: bool = False):
        """Show recent or future releases"""
        if future:
            releases = self.db.get_future_releases()
            title = "UPCOMING RELEASES"
        else:
            releases = self.db.get_recent_releases(days)
            title = f"RELEASES (LAST {days} DAYS)"
        
        if not releases:
            print(f"\nNo {'upcoming' if future else 'recent'} releases found.\n")
            return
        
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60 + "\n")
        
        for release in releases:
            explicit = " [EXPLICIT]" if release.get('explicit') else ""
            
            print(f"  • {release['title']}{explicit}")
            print(f"    Artist: {release['artist_name']}")
            print(f"    Type: {release.get('album_type', 'ALBUM')}")
            print(f"    Release: {release.get('release_date', 'Unknown')}")
            print(f"    Tracks: {release.get('number_of_tracks', 'N/A')}")
            print(f"    Album ID: {release['album_id']}")
            print()
        
        print("="*60 + "\n")
        print(f"Total: {len(releases)} release(s)\n")