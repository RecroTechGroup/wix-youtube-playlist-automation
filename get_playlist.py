import yt_dlp
import csv
from datetime import datetime
import sys
import io


def get_playlist_videos(playlist_url):
    """
    Extract video information from a YouTube playlist including release dates.

    Args:
        playlist_url: URL of the YouTube playlist

    Returns:
        List of dictionaries containing video information
    """
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,  # Changed to False to get full video info
        'force_generic_extractor': False,
        'ignoreerrors': True,
        'no_color': True,
        'socket_timeout': 30,
    }

    videos = []

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Fetching playlist information...")
            playlist_info = ydl.extract_info(playlist_url, download=False)

            if 'entries' in playlist_info:
                total = len([e for e in playlist_info['entries'] if e])
                print(f"Found {total} videos in playlist\n")

                for idx, video in enumerate(playlist_info['entries'], 1):
                    if video:  # Some entries might be None
                        video_data = {
                            'video_id': video.get('id', 'N/A'),
                            'title': video.get('title', 'N/A'),
                            'url': video.get('webpage_url', f"https://www.youtube.com/watch?v={video.get('id', '')}"),
                            'release_date': video.get('upload_date', 'N/A'),
                            'view_count': video.get('view_count', 'N/A'),
                            'duration': video.get('duration', 'N/A')
                        }

                        # Format date from YYYYMMDD to YYYY-MM-DD
                        if video_data['release_date'] != 'N/A':
                            try:
                                date_obj = datetime.strptime(video_data['release_date'], '%Y%m%d')
                                video_data['release_date'] = date_obj.strftime('%Y-%m-%d')
                            except:
                                pass

                        # Format duration from seconds to HH:MM:SS
                        if video_data['duration'] != 'N/A' and isinstance(video_data['duration'], (int, float)):
                            duration_sec = int(video_data['duration'])
                            hours = duration_sec // 3600
                            minutes = (duration_sec % 3600) // 60
                            seconds = duration_sec % 60
                            if hours > 0:
                                video_data['duration'] = f"{hours}:{minutes:02d}:{seconds:02d}"
                            else:
                                video_data['duration'] = f"{minutes}:{seconds:02d}"

                        videos.append(video_data)
                        print(f"[{idx}/{total}] {video_data['video_id']} - {video_data['release_date']} - {video_data['title']}")
            else:
                print("No entries found in playlist")

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

    return videos


def save_to_csv(videos, filename='youtube_playlist.csv'):
    """
    Save video information to a CSV file.

    Args:
        videos: List of video dictionaries
        filename: Output CSV filename
    """
    if not videos:
        print("No videos to save!")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['video_id', 'title', 'url', 'release_date', 'view_count', 'duration']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for video in videos:
            writer.writerow(video)

    print(f"\nSaved {len(videos)} videos to {filename}")



if __name__ == "__main__":

    # Your playlist URL
    playlist_url = "https://www.youtube.com/watch?v=MORU93Ibwd0&list=PLhQVfDe_eNXoDyRUzjYUV9uVvPc3yucvB"

    # Get videos
    videos = get_playlist_videos(playlist_url)

    # Save to CSV
    if videos:
        save_to_csv(videos)
        print("\nDone! Check youtube_playlist.csv for the results.")
    else:
        print("\nNo videos were extracted. Check the error messages above.")
