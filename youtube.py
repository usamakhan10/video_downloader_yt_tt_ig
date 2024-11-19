import yt_dlp
import os
from datetime import datetime
import re
from watermark import Watermark

def clean_title(folder_path):
    os.makedirs(folder_path, exist_ok=True)
    for file in os.listdir(folder_path):
        if file.endswith(".mp4"):
            title = file.replace(".mp4","")
            # Remove hashtags and associated words
            title = re.sub(r'#\w+', '', title)
            # Remove any special characters
            title = re.sub(r'[<>:"/\\|?*]', '', title)
            # Remove extra spaces and trim
            title = re.sub(r'\s+', ' ', title).strip()
            title = title + ".mp4"
            os.rename(os.path.join(folder_path, file), os.path.join(folder_path, title))
            

def download_channel_videos(channel_url,download_shorts=True,download_videos=True):
    # try:
    if "@" in channel_url:
        output_dir = "youtube_downloads/"+channel_url.split("@")[-1]
    else:
        output_dir = "youtube_downloads/"+channel_url.split("/")[-1]
    os.makedirs(output_dir, exist_ok=True)
    
    # Clean channel URL
    if not channel_url.startswith('https://'):
        channel_url = f'https://www.youtube.com/{channel_url}'
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestvideo[height>=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height>=720][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'ignoreerrors': True,
        'no_warnings': True,
        'extract_flat': True,
        'quiet': False,
        'progress': True,
        'playlistend': None,
        'extract_flat': 'in_playlist',
    }

    # First, get all videos from the channel
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        channel_info = ydl.extract_info(channel_url, download=False)
        if 'entries' in channel_info:
            shorts_urls = []
            if download_shorts:
                for entry in channel_info['entries'][1]["entries"]:
                    id = entry.get('id', '')
                    shorts_urls.append(f"https://www.youtube.com/watch?v={id}")
            if download_videos:
                for entry in channel_info['entries'][0]["entries"]:
                    id = entry.get('id', '')
                    shorts_urls.append(f"https://www.youtube.com/watch?v={id}")

    # Now download only the shorts
    ydl_opts['extract_flat'] = False
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(shorts_urls)

    print("Download completed!")
        
    # except Exception as e:
    #     print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    channel_url = "@Darklavia"
    download_channel_videos(channel_url,download_shorts=True,download_videos=False)
    watermark = Watermark()
    folder_path = "youtube_downloads/"+channel_url.replace("@","")
    watermark.process_videos_from_folder(folder_path,folder_path)
    clean_title(folder_path)