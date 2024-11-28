from seleniumbase import SB
import time
import requests
from tqdm import tqdm
import re
import os       
import urllib.request
from watermark import Watermark


class TikTokScraper:
    def __init__(self, download_dir="tiktok_videos"):
        self.urls = []
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
    
        
    def get_video_urls(self, page_url: str):
        try:
            with SB(uc=True,headless=False) as sb:
                sb.get(page_url)
                sb.wait_for_element('a.css-1g95xhm-AVideoContainer',timeout=100)
                old_videos = []
                new_videos = sb.find_elements('a.css-1g95xhm-AVideoContainer')
                
                while len(old_videos)!=len(new_videos):
                    sb.execute_script("arguments[0].scrollIntoView();", new_videos[-1])
                    time.sleep(5)
                    old_videos = new_videos
                    new_videos = sb.find_elements('a.css-1g95xhm-AVideoContainer')
                urls = []
                names = []
                for video in new_videos:
                    urls.append(video.get_attribute('href'))
                    
                    #get the image alt attribute from the video by using innerHTML
                    inner_html = video.get_attribute("innerHTML")
                    if 'alt="' in inner_html:
                        start_index = inner_html.find('alt="') + 5
                        end_index = inner_html.find('"', start_index)
                        name = inner_html[start_index:end_index]
                        name = self.clean_filename(name)
                        names.append(name)
                    else:
                        names.append(None)
                        
            return urls, names
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    
      
    def play_and_download_video(self, urls: list,names: list):
        with SB(uc=True,headless=True) as sb:
            for index,url in enumerate(urls):
                try:
                    sb.get(url)
                    inner_html = ""
                    while "src=" not in inner_html:
                        # Get the video element's innerHTML
                        video_element = sb.find_element('video', timeout=30)
                        time.sleep(1)
                        inner_html = video_element.get_attribute("innerHTML")
                    # Extract the first source URL using string manipulation
                    if 'src="' in inner_html:
                        start_index = inner_html.find('src="') + 5
                        end_index = inner_html.find('"', start_index)
                        video_url = inner_html[start_index:end_index]
                        
                        # Decode HTML entities if present
                        video_url = video_url.replace('&amp;', '&')
                        
                        self.download_video(sb,url,names[index],video_url,index)
                    else:
                        print(f"{index}/{len(urls)} No video url found for {url}")
                        
                        
                except Exception as e:
                    print(f"{index}/{len(urls)} Error processing {url}: {e}")

    def clean_filename(self, name: str, max_length: int = 50) -> str:
        
        #remove hashtags and the word following it from name
        name = re.sub(r'#\S+', '', name)
        #remove any unallowed characters in filename from name
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        
        # Remove or replace other problematic characters
        name = name.replace('\n', ' ').replace('\r', '')
        
        # Truncate to max length while keeping the extension
        if len(name) > max_length:
            name = name[:max_length-4]
        
        return name.strip()

    def download_video(self,sb, url, name,video_url,index:int = 0):

        # Get cookies and user agent from selenium session
        cookies = sb.driver.get_cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        user_agent = sb.driver.execute_script("return navigator.userAgent")
                            
        # Set up headers
        headers = {
            'User-Agent': user_agent,
            'Referer': url,
            'Cookie': '; '.join([f'{k}={v}' for k, v in cookie_dict.items()]),
            'Accept': '*/*',
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Range': 'bytes=0-',
        }
        
        # Download with session and headers
        session = requests.Session()
        response = session.get(
            video_url,
            headers=headers,
            cookies=cookie_dict,
            stream=True
        )
        
        filename = name
        
        if response.status_code in [200, 206]:
            filepath = os.path.join(self.download_dir, f"{filename}.mp4")
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f, tqdm(
                desc=filename,
                total=total_size,
                unit='iB',
                unit_scale=True,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        size = f.write(chunk)
                        pbar.update(size)
            
            print(f"{index+1}- Successfully downloaded: {filename}")
            return True
        else:
            print(f"Failed to download. Status code: {response.status_code}")
            
            # Alternative method using urllib
            print("Trying alternative download method...")
            filepath = os.path.join(self.download_dir, f"{filename}.mp4")
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', user_agent)]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(video_url, filepath)
            print(f"Successfully downloaded using alternative method: {filename}")
            return True
    
    def generate_video_list(self,channel_name, videos_folder="tiktok_downloads/"):
        """Generate a text file listing all video titles in the videos folder"""
        video_files = [f for f in os.listdir(videos_folder) if f.endswith('.mp4')]
        os.makedirs(f"{videos_folder}", exist_ok=True)
        with open(f'{videos_folder}/video_list_{channel_name}.txt', 'w', encoding='utf-8') as f:
            for idx, video in enumerate(video_files, 1):
                # Remove .mp4 extension and format the line
                title = video.replace('.mp4', '')
                f.write(f"Day_{idx} {title}\n")
                os.rename(f"{videos_folder}/{video}", f"{videos_folder}/day_{idx}_{title}.mp4")
        
        print(f"Video list has been generated in video_list_{channel_name}.txt")
        
        
if __name__ == "__main__":
    url = "https://www.tiktok.com/@rankingdaily"
    channel_name = url.split('@')[1].replace('/', '')
    tiktok_scraper = TikTokScraper(download_dir="./tiktok_downloads/"+channel_name)
    tiktok_urls,video_names = tiktok_scraper.get_video_urls(url)
    print(f"Found {len(tiktok_urls)} videos")
    tiktok_scraper.play_and_download_video(tiktok_urls,video_names)
    watermark = Watermark()
    watermark.process_videos_from_folder("./tiktok_downloads/"+channel_name, "./tiktok_downloads/"+channel_name)
    tiktok_scraper.generate_video_list(channel_name, "./tiktok_downloads/"+channel_name)
