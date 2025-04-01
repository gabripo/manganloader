import os
import requests
import urllib
import asyncio, aiohttp, aiofiles
import time
import re
import base64
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException
from manganloader.mloader_wrapper import MloaderWrapper

VALID_RESPONSE_STATUS = 200
MAX_RETRIES = 5
MANGAPLUS_OP_URL = "https://jumpg-webapi.tokyo-cdn.com/api/title_detailV3?title_id=100020"
SELENIUM_LOAD_TIME_S = 1
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

    def fetch_images(self, output_folder: str = None, javascript_args_chapter: dict = {}):
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
            if javascript_args_chapter != {}:
                # webpage scraping with Javascript
                try:
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_experimental_option("prefs", {
                        "download.default_directory": output_folder,
                        "download.prompt_for_download": False,
                        "download.directory_upgrade": True,
                        "safebrowsing.enabled": True,
                        "profile.default_content_setting_values.automatic_downloads": 1,
                        "profile.default_content_setting_values.popups": 0,
                    })
                    driver = webdriver.Chrome(
                            service=ChromeService(ChromeDriverManager().install()),
                            options=chrome_options,
                        )
                    
                    driver.get(self.url)
                    time.sleep(SELENIUM_LOAD_TIME_S)

                    if 'buttons' in javascript_args_chapter.keys():
                        buttons_to_press = javascript_args_chapter['buttons']
                        for button_name in buttons_to_press:
                            button = driver.find_element(
                                By.XPATH,
                                f"//button[contains(text(), '{button_name}')]",
                            )
                            button.click()
                            time.sleep(SELENIUM_LOAD_TIME_S)

                    images_selenium = driver.find_elements(By.TAG_NAME, 'img')
                    seen = set()
                    images_urls = []
                    for img_selenium in images_selenium:
                        img_url = img_selenium.get_attribute('src')
                        if img_url in seen:
                            continue
                        images_urls.append(img_url)
                        seen.add(img_url)

                    for index, img_url in enumerate(images_urls):
                        if img_url:
                            driver.get(img_url)
                            time.sleep(SELENIUM_LOAD_TIME_S)

                            img_elements = driver.find_elements(By.TAG_NAME, "img")
                            if img_elements:
                                img_element = img_elements[0]
                                img_width = driver.execute_script("return arguments[0].naturalWidth", img_element)
                                img_height = driver.execute_script("return arguments[0].naturalHeight", img_element)

                                img_data = driver.execute_script(f"""
                                var canvas = document.createElement('canvas');
                                var context = canvas.getContext('2d');
                                var img = arguments[0];
                                canvas.width = {img_width};
                                canvas.height = {img_height};
                                context.drawImage(img, 0, 0);
                                return canvas.toDataURL('image/png').substring(22);
                                """, img_element)

                                img_path = os.path.join(output_folder, f"image_{index}.png")
                                with open(img_path, 'wb') as img_file:
                                    img_file.write(base64.b64decode(img_data))
                            else:
                                print(f"No images were found at the url {img_url} ! Maybe a cloud protection was active?")
                except Exception as exc:
                    print(f"Impossible to fetch images from the url {self.url} : {exc}")
                    self.images = []
                finally:
                    driver.quit()
            else:
                # static webpage scraping
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
    def fetch_webpage_response(url: str, max_retries: int = MAX_RETRIES):
        response = None
        retry = 1
        while response is None and retry <= max_retries:
            try:
                response = requests.get(
                    url,
                    verify=False, # we do not care about SSL
                    headers=Mangapage._build_session_headers(url)
                    )
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
        if Mangapage._is_mangaplus_url(url):
            url_split = url.split('/')
            return int(url_split[-1])
        else:
            print(f"The url {url} is not a valid Mangaplus one! The url of the latest chapter will be used!")
            return Mangapage.fetch_id_latest_chapter()

    @staticmethod
    def fetch_num_latest_chapter():
        latest_chapters = Mangapage.fetch_latest_chapters()
        return max(latest_chapters.keys())

    @staticmethod
    def fetch_id_latest_chapter():
        latest_chapters = Mangapage.fetch_latest_chapters()
        return latest_chapters[Mangapage.fetch_num_latest_chapter()]
    
    @staticmethod
    def build_url_from_id_chapter(id_chapter: str):
        return f"https://mangaplus.shueisha.co.jp/viewer/{id_chapter}"
    
    @staticmethod
    def fetch_url_latest_chapter():
        id_latest_chapter = Mangapage.fetch_id_latest_chapter()
        return Mangapage.build_url_from_id_chapter(id_latest_chapter)
    
    @staticmethod
    def fetch_latest_chapters():
        url = MANGAPLUS_OP_URL
        response = Mangapage.fetch_webpage_response(url=url)
        if response.status_code != 200:
            print(f"Response of the url {url} is invalid! The latest chapters were not fetched!")
            return {}
        chapter_nums = re.findall("#(\\d+)", response.text)
        chapter_ids = re.findall("chapter/(\\d+)/chapter_thumbnail", response.text)
        chapters = {ch_num: ch_id for ch_num, ch_id in zip(chapter_nums, chapter_ids)}
        return chapters
    
    @staticmethod
    def fetch_latest_chapters_generic(
        url: str = None,
        base_url: str = None,
        javascript_args_mainpage: dict = {},
        ):
        if base_url is None and url == MANGAPLUS_OP_URL:
            print("Fetching the latest One Piece chapters from Mangaplus...")
            chapters_num_id = Mangapage.fetch_latest_chapters()
            chapters_links = [Mangapage.build_url_from_id_chapter(ch_id) for ch_id in chapters_num_id.values()]
            return chapters_links
        if url is None or base_url is None:
            print(f"Invalid combination of url and base url specified: impossible to fetch the latest chapters. Fallback to One Piece colored.")
            url = 'https://ww11.readonepiece.com/index.php/manga/one-piece-digital-colored-comics/'
            base_url = 'https://ww11.readonepiece.com/index.php/chapter/'

        if javascript_args_mainpage:
            # rendering with Javascript
            try:
                driver = webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()),
                )
                driver.get(url)
                time.sleep(SELENIUM_LOAD_TIME_S)

                if 'buttons' in javascript_args_mainpage.keys():
                    buttons_to_press = javascript_args_mainpage['buttons']
                    for button_name in buttons_to_press:
                        button = driver.find_element(
                            By.XPATH,
                            f"//button[contains(text(), '{button_name}')]",
                        )
                        button.click()
                        time.sleep(SELENIUM_LOAD_TIME_S)
                
                if 'buttons_xpath' in javascript_args_mainpage.keys():
                    buttons_xpath_to_press = javascript_args_mainpage['buttons_xpath']
                    for button_xpath in buttons_xpath_to_press:
                        button = driver.find_element(
                            By.XPATH,
                            button_xpath,
                        )
                        button.click()
                        time.sleep(SELENIUM_LOAD_TIME_S)
                
                links_selenium = driver.find_elements(By.TAG_NAME, 'a')
                links = [l.get_attribute('href') for l in links_selenium]
            except Exception as exc:
                print(f"Impossible to fetch links from the url {url} : {exc}")
                links = []
            finally:
                driver.quit()
        else:
            # static rendering without Javascript
            response = Mangapage.fetch_webpage_response(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [a.get('href') for a in soup.find_all('a', href=True)]

        seen = set()
        chapters_links = []
        for link in links:
            if link is None:
                continue
            if base_url not in link:
                continue
            if link not in seen:
                seen.add(link)
                chapters_links.append(link)
        return chapters_links
    
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
            tasks = [
                self._download_image(session, url, output_folder, id)
                for id, url in enumerate(images_urls)
                ]
            img_paths = await asyncio.gather(*tasks)
            return img_paths

    async def _download_image(
            self,
            session: aiohttp.ClientSession,
            img_url: str,
            output_folder: str,
            image_id: int,
            max_retries: int = MAX_RETRIES,
            wait_time_s: float = 1.0):
        img_name = "{:05}".format(image_id) + "_" + os.path.basename(img_url)
        img_path = os.path.abspath(os.path.join(output_folder, img_name))

        session.headers.update(self._build_session_headers(img_url))
        attempts = 0
        while attempts < max_retries:
            async with session.get(img_url) as response:
                content = await response.read()

            if not content or response.status != VALID_RESPONSE_STATUS:
                attempts += 1
                if attempts == max_retries:
                    print(f"Impossible to download image from url {img_url} !")
                    return ''   
                print(f"Impossible to download image from url {img_url} ! Retry for the {attempts}-th time after {wait_time_s} seconds...")
                time.sleep(wait_time_s)
            else:
                break

        async with aiofiles.open(img_path, "wb") as f:
            await f.write(content)
        print(f"Image stored from url {img_url} into {img_path} !")
        return img_path
    
    @staticmethod
    def _build_session_headers(url: str) -> dict:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }
        if 'imgur' in url:
            headers["Referer"] = "https://imgur.com/"
        if 'lastation' in url:
            headers = {
                "Host" : "scans.lastation.us",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:136.0) Gecko/20100101 Firefox/136.0",
                "Accept" : "image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5",
                "Accept-Language" : "en-GB,en;q=0.5",
                "Accept-Encoding" : "gzip, deflate, br, zstd",
                "Referer" : "https://weebcentral.com/",
                "Sec-Fetch-Dest" : "image",
                "Sec-Fetch-Mode" : "no-cors",
                "Sec-Fetch-Site" : "cross-site",
                "Connection" : "keep-alive",
            }
        return headers
    
    @staticmethod
    def _is_mangaplus_url(url: str):
        pattern = r'https://mangaplus\.shueisha\.co\.jp/viewer'
        return bool(re.search(pattern, url))