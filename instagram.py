from seleniumbase import SB
from time import sleep
import instaloader
import os
from watermark import Watermark
from datetime import datetime

def scroll_and_get_reel_links(sb, username):
    # Set to store unique reel links
    reel_links = set()
    
    # Initial scroll height
    last_height = sb.execute_script("return document.body.scrollHeight")
    tries = 0
    while True:
        # Get all reel links on current view
        links = sb.find_elements(f'a[href^="/{username}/reel/"]')
        for link in links:
            href = link.get_attribute('href')
            if href:
                reel_links.add(href)
        
        # Scroll down
        sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)  # Wait for content to load
        
        # Calculate new scroll height
        new_height = sb.execute_script("return document.body.scrollHeight")
        
        # Break if we've reached the bottom
        if new_height == last_height:
            tries += 1
            if tries > 10:
                break
        else:
            tries = 0
        last_height = new_height
        
    return reel_links

        
def download_reels(reel_links):
    L = instaloader.Instaloader(
        download_videos=True,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
        )
    for index, link in enumerate(reel_links,start=1):
        shortcode = link.split("/")[-2]
        L.download_post(instaloader.Post.from_shortcode(L.context, shortcode),target="reels")
        print(f"downloaded {index} of {len(reel_links)}")
        
        
def generate_video_list(username, reels_folder="reels/"):
    """Generate a text file listing all video titles in the reels folder"""
    video_files = [f for f in os.listdir(reels_folder) if f.endswith('.mp4')]
    os.makedirs(f"{reels_folder}", exist_ok=True)
    with open(f'{reels_folder}/video_list_{username}.txt', 'w', encoding='utf-8') as f:
        for idx, video in enumerate(video_files, 1):
            # Remove .mp4 extension and format the line
            title = video.replace('.mp4', '')
            f.write(f"Day_{idx} {title}\n")
            os.rename(f"{reels_folder}/{video}", f"{reels_folder}/day_{idx}_{title}.mp4")
    
    print(f"Video list has been generated in video_list_{username}.txt")

def main():
    # Instagram credentials
    USERNAME = "usama62263"
    PASSWORD = "a1n2e3w4p5a6s7s8w9o10r11d12"
    TARGET_USERNAME = "alphaissance"  # The account to scrape
    
    # Use undetected-chromedriver mode
    with SB(uc=True,headless=False) as sb:
        # Login to Instagram
        sb.open("https://www.instagram.com/")
        sleep(5)  # Wait for page to load
        
        # Fill login form
        sb.type('input[name="username"]', USERNAME)
        sb.type('input[name="password"]', PASSWORD)
        sb.click('button[type="submit"]')
        sleep(5)  # Wait for login
        
        # Handle potential "Save Login Info" popup
        try:
            sb.click('button:contains("Not Now")', timeout=5)
        except:
            pass
            
        # Handle potential notifications popup
        try:
            sb.click('button:contains("Not Now")', timeout=5)
        except:
            pass
        
        # Navigate to target user's reels
        reels_url = f"https://www.instagram.com/{TARGET_USERNAME}/reels/"
        sb.open(reels_url)
        sleep(5)  # Wait for page to load
        
        # Scroll and collect reel links
        reel_links = scroll_and_get_reel_links(sb, TARGET_USERNAME)
        
    # Print all collected links
    print(f"\nTotal Reels Found: {len(reel_links)}")
    download_reels(reel_links)
    watermark = Watermark()
    watermark.process_videos_from_folder("reels/", f"reels/{TARGET_USERNAME}")
    generate_video_list(username=TARGET_USERNAME, reels_folder=f"reels/{TARGET_USERNAME}")

if __name__ == "__main__":
    main()