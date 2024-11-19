import instaloader
import os
from watermark import Watermark

def download_instagram_profile(username):
    try:
        # Create an Instaloader instance
        L = instaloader.Instaloader(
            download_pictures=True,    # Download photos
            download_videos=True,      # Download videos
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False
        )
        download_path = "instagram_downloads/"
        # Create download directory if it doesn't exist
        os.makedirs(download_path, exist_ok=True)
        os.chdir(download_path)

        # Get profile
        profile = instaloader.Profile.from_username(L.context, username)
        
        print(f"Starting download for profile: {username}")
        print(f"Total posts to download: {profile.mediacount}")

        # Download all posts
        for post in profile.get_posts():
            try:
                print(f"Downloading post from {post.date}")
                L.download_post(post, target=username)
            except Exception as e:
                print(f"Error downloading post: {e}")
                continue

        print("Download completed!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace with the Instagram username you want to download from
    target_username = "xzio.th"
    download_instagram_profile(target_username)
    watermark = Watermark()
    os.chdir("..")
    watermark.process_videos_from_folder("./instagram_downloads/"+target_username, "./instagram_downloads/"+target_username)