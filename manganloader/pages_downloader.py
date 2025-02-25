import os
import requests
import asyncio, aiohttp, aiofiles
import time
import re
from bs4 import BeautifulSoup
from manganloader.mloader_wrapper import MloaderWrapper

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
        
        output_folder = os.getcwd() if output_folder is None else output_folder
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
        if response is None or response.status_code != 200:
                print(f"Impossible to fetch images from {self.url} !")
                return
        soup = BeautifulSoup(response.text, 'html.parser')
        images_tags = soup.find_all('img')
        images_urls = [image['src'] for image in images_tags]
        return images_urls
    
    async def _write_images_from_urls(self, images_urls: list[str], output_folder: str):
        async with aiohttp.ClientSession() as session:
            tasks = [self._download_image(session, url, output_folder) for url in images_urls]
            img_paths = await asyncio.gather(*tasks)
            return img_paths

    async def _download_image(self, session: aiohttp.ClientSession, img_url: str, output_folder: str):
        img_name = os.path.basename(img_url)
        img_path = os.path.abspath(os.path.join(output_folder, img_name))

        async with session.get(img_url) as response:
            content = await response.read()

        async with aiofiles.open(img_path, "wb") as f:
            await f.write(content)
        print(f"Image stored from url {img_url} into {img_path} !")
        return img_path
    
    @staticmethod
    def _is_mangaplus_url(url: str):
        pattern = r'https://mangaplus\.shueisha\.co\.jp/viewer'
        return bool(re.search(pattern, url))