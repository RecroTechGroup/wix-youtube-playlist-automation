import time
from wixv2 import *
from get_playlist import *
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

wix_save_file = 'wix_out.csv'
youtube_save_file = 'youtube_playlist.csv'
playlist_url = "https://www.youtube.com/watch?v=MORU93Ibwd0&list=PLhQVfDe_eNXoDyRUzjYUV9uVvPc3yucvB"


if __name__ == '__main__':
    while True:
        # run each hour
        ###################################################################################################################
        # Get videos from youtube
        ###################################################################################################################
        videos = get_playlist_videos(playlist_url)

        # Save to CSV
        if videos:
            save_to_csv(videos, filename=youtube_save_file)
            print("\nDone! Check youtube_playlist.csv for the results.")
        else:
            print("\nNo videos were extracted. Check the error messages above.")

        ###################################################################################################################
        # get contents from wix
        ###################################################################################################################
        ACCESS_TOKEN = os.getenv('WIX_ACCESS_TOKEN')
        SITE_ID = os.getenv('WIX_SITE_ID')

        # save wix data
        save_wix_data(wix_save_file)
        ###################################################################################################################
        # compare content and if video id is not found insert it in
        ###################################################################################################################

        df_youtube = pd.read_csv('youtube_playlist.csv')
        df_wix = pd.read_csv('wix_data.csv')
        wix_video_ids = df_wix['video_id']
        youtube_video_ids = df_youtube['video_id']
        set_youtube_ids = set(youtube_video_ids)
        set_wix_ids = set(wix_video_ids)
        diff_youtube_ids = set_youtube_ids - set_wix_ids

        if diff_youtube_ids:
            print('checking videos')
            for video_id in diff_youtube_ids:
                row = df_youtube[[df_youtube['video_id'] == video_id]]
                insert_youtube_video_to_wix(video_id=row['video_id'],
                                            title=row['title'],
                                            release_date=row['release_date'],
                                            url=row['url'],)
        else:
            print('no new video')

        time.sleep(60*60)  # sleep 1 hour
    