import os
import requests
import urllib
import asyncio, aiohttp, aiofiles
import time
import re
from bs4 import BeautifulSoup
from manganloader.mloader_wrapper import MloaderWrapper

VALID_RESPONSE_STATUS = 200
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://imgur.com/",
    }
class Mangapage:
    def __init__(self, manga_url: str = None):
        self.url = None
        self.content = None
        self.images = None
        self.set_url(manga_url)

    def set_url(self, url: str) -> None:
        if not self.is_valid_url(url):
            print(f"Invalid url {url} !")
            return
        self.url = url

    def fetch_images(self, output_folder: str = None):
        if self.url is None:
            print("Invalid url, impossible to fetch images!")
            return
        output_folder = os.getcwd() if None else output_folder
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        if self._is_mangaplus_url(self.url):
            mloader = MloaderWrapper(output_directory=output_folder)
            chapter_number = self.get_chapter_id(self.url)
            self.images = mloader.download_chapters(chapter_number)
        else:
            # fallback to normal webpage scraping
            response = self.fetch_webpage_response(self.url)
            images_urls = self._extract_images_urls(response)
            self.images = asyncio.run(self._write_images_from_urls(images_urls, output_folder))
        return self.images

    @staticmethod
    def is_valid_url(url: str) -> bool:
        # django url validation regex - https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45
        regex = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None
    
    @staticmethod
    def fetch_webpage_response(url: str):
        response = None
        MAX_RETRIES = 10
        retry = 1
        while response is None and retry <= MAX_RETRIES:
            try:
                response = requests.get(url, verify=False) # we do not care about SSL
                return response
            except Exception as exc:
                retry += 1
                print(f"We were greedy pirates: the site {url} does not want to give us treasures...")
                sleep_time_s = 5
                print(f"Waiting {sleep_time_s} seconds before looting again...")
                time.sleep(sleep_time_s)
                print("Let's loot again! ARRRWWW!")
        return response
    
    @staticmethod
    def get_chapter_id(url: str):
        # TODO intelligent search for non-Mangaplus urls
        url_split = url.split('/')
        return int(url_split[-1])
    
    def _extract_images_urls(self, response):
        if response is None or response.status_code != VALID_RESPONSE_STATUS:
                print(f"Impossible to fetch images from {self.url} !")
                return
        soup = BeautifulSoup(response.text, 'html.parser')
        images_tags = soup.find_all('img')
        images_urls = [
            self._clean_image_url(image['src'])
            for image in images_tags
            ]
        images_urls = self._exclude_outlier_urls(images_urls)
        return images_urls
    
    @staticmethod
    def _clean_image_url(img_url: str) -> str:
        image_formats = {'.jpg', '.jpeg', '.png'}
        img_url_parsed = urllib.parse.urlparse(img_url)
        img_name, img_ext = os.path.splitext(img_url_parsed.path)
        if img_ext not in image_formats:
            return ''
        return urllib.parse.urlunparse((
            img_url_parsed.scheme,
            img_url_parsed.netloc,
            img_url_parsed.path,
            '',
            '',
            '',
            ))
    
    def _exclude_outlier_urls(self, urls: list[str]) -> list[str]:
        urls_netloc = [urllib.parse.urlparse(url).netloc for url in urls]
        common_netloc = self._commonest_values(urls_netloc)
        common_netloc = common_netloc[0] # prevent unlucky scenario with 2 netlocs with same frequencies
        urls = [url for url in urls if common_netloc in url]
        return urls
    
    @staticmethod
    def _commonest_values(arr: list):
        val_freq = {}
        for val in arr:
            val_freq[val] = val_freq.get(val, 0) + 1
        max_freq = max(val_freq.values())
        return [val for val, freq in val_freq.items() if freq == max_freq]


    async def _write_images_from_urls(self, images_urls: list[str], output_folder: str):
        async with aiohttp.ClientSession() as session:
            tasks = [self._download_image(session, url, output_folder) for url in images_urls]
            img_paths = await asyncio.gather(*tasks)
            return img_paths

    async def _download_image(self, session: aiohttp.ClientSession, img_url: str, output_folder: str):
        img_name = os.path.basename(img_url)
        img_path = os.path.abspath(os.path.join(output_folder, img_name))

        session.headers.update(HEADERS)
        async with session.get(img_url) as response:
            content = await response.read()

        if not content or response.status != VALID_RESPONSE_STATUS:
            print(f"Impossible to download image from url {img_url} !")
            return ''

        async with aiofiles.open(img_path, "wb") as f:
            await f.write(content)
        print(f"Image stored from url {img_url} into {img_path} !")
        return img_path
    
    @staticmethod
    def _is_mangaplus_url(url: str):
        pattern = r'https://mangaplus\.shueisha\.co\.jp/viewer'
        return bool(re.search(pattern, url))