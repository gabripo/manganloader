import os
import requests
import urllib
import asyncio, aiohttp, aiofiles
import time
import re
import base64
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from manganloader.selenium_manager import SeleniumManager, SELENIUM_LOAD_TIME_SHORT_S, SELENIUM_LOAD_TIME_LONG_S
from manganloader.mloader_wrapper import MloaderWrapper

VALID_RESPONSE_STATUS = 200
MAX_RETRIES = 5
MANGAPLUS_OP_URL = "https://jumpg-webapi.tokyo-cdn.com/api/title_detailV3?title_id=100020"
MANGAPLUS_OP_BASEURL = "https://mangaplus.shueisha.co.jp/viewer/"
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
                self.images = []
                try:
                    selenium_manager = SeleniumManager(driver_type="chrome")
                    if os.getenv("APP_IN_DOCKER") == "Yes":
                        print("DOCKER EXECUTION DETECTED")
                        selenium_manager.generate_driver_options({
                            'download_directory': output_folder,
                            'unlimited_downloads': True,
                            'disable_cors': True,
                            'headless_mode': True,
                            'docker_support': True,
                        })
                    else:
                        selenium_manager.generate_driver_options({
                            'download_directory': output_folder,
                            'unlimited_downloads': True,
                            'disable_cors': True,
                        })
                    selenium_manager.create_driver()
                    driver = selenium_manager.get_driver()
                    
                    driver.get(self.url)
                    time.sleep(SELENIUM_LOAD_TIME_SHORT_S)

                    SeleniumManager.javascript_actions(
                        driver=driver,
                        javascript_args=javascript_args_chapter,
                        )

                    time.sleep(SELENIUM_LOAD_TIME_LONG_S)
                    images_selenium = selenium_manager.find_images()
                    images_urls = set()
                    images_selenium_unique = []
                    for img_selenium in images_selenium:
                        img_url = img_selenium.get_attribute('src')
                        if img_url in images_urls:
                            continue
                        images_selenium_unique.append(img_selenium)
                        images_urls.add(img_url)

                    for index, img_element in enumerate(images_selenium_unique):
                        img_url = img_selenium.get_attribute('src')
                        if img_url:
                            img_path = SeleniumManager.save_image_element_with_driver(
                                driver=driver,
                                img_element=img_element,
                                output_folder=output_folder,
                                filename=f"image_{index:05}.png",
                            )
                            if img_path:
                                print(f"Image {img_path} generated from url {img_url}")
                                self.images.append(img_path)
                        else:
                            print(f"No images were found at the url {img_url} ! Maybe a cloud protection was active?")
                except Exception as exc:
                    print(f"Impossible to fetch images from the url {self.url} : {exc}")
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
    def fetch_num_latest_chapter(url = MANGAPLUS_OP_URL):
        latest_chapters = Mangapage.fetch_latest_chapters(url=url)
        return max(latest_chapters.keys())

    @staticmethod
    def fetch_id_latest_chapter(url = MANGAPLUS_OP_URL):
        latest_chapters = Mangapage.fetch_latest_chapters(url=url)
        latest_chapter_num = max(latest_chapters.keys())
        return latest_chapters[latest_chapter_num]
    
    @staticmethod
    def fetch_url_latest_chapter(url = MANGAPLUS_OP_URL, base_url: str = MANGAPLUS_OP_BASEURL):
        id_latest_chapter = Mangapage.fetch_id_latest_chapter(url=url)
        return id_latest_chapter + base_url
    
    @staticmethod
    def fetch_latest_chapters(url = MANGAPLUS_OP_URL):
        response = Mangapage.fetch_webpage_response(url=url)
        if response.status_code != 200:
            print(f"Response of the url {url} is invalid! The latest chapters were not fetched!")
            return {}
        if url == MANGAPLUS_OP_URL:
            chapter_nums = re.findall("#(\\d+)", response.text)
            chapter_ids = re.findall("chapter/(\\d+)/chapter_thumbnail", response.text)
            chapters = {ch_num: ch_id for ch_num, ch_id in zip(chapter_nums, chapter_ids)}
            return chapters
        else:
            return {}
    
    @staticmethod
    def fetch_latest_chapters_generic(
        url: str = None,
        base_url: str = None,
        javascript_args_mainpage: dict = {},
        naming_strategy: dict = None,
        ):
        if base_url is None and url == MANGAPLUS_OP_URL:
            print("Fetching the latest One Piece chapters from Mangaplus...")
            chapters_num_id = Mangapage.fetch_latest_chapters(url=MANGAPLUS_OP_URL)
            chapters_links = [MANGAPLUS_OP_BASEURL + ch_id for ch_id in chapters_num_id.values()]
            return chapters_links
        if url is None or base_url is None:
            print(f"Invalid combination of url and base url specified: impossible to fetch the latest chapters. Fallback to One Piece colored.")
            url = 'https://ww11.readonepiece.com/index.php/manga/one-piece-digital-colored-comics/'
            base_url = 'https://ww11.readonepiece.com/index.php/chapter/'

        if javascript_args_mainpage:
            # rendering with Javascript
            try:
                selenium_manager = SeleniumManager(driver_type="chrome")
                if os.getenv("APP_IN_DOCKER") == "Yes":
                    print("DOCKER EXECUTION DETECTED")
                    selenium_manager.generate_driver_options({
                        'headless_mode': True,
                        'docker_support': True,
                    })
                selenium_manager.create_driver()
                driver = selenium_manager.get_driver()

                driver.get(url)
                time.sleep(SELENIUM_LOAD_TIME_SHORT_S)

                SeleniumManager.javascript_actions(
                    driver=driver,
                    javascript_args=javascript_args_mainpage,
                )
                
                links_selenium = selenium_manager.find_links()
                links = [l.get_attribute('href') for l in links_selenium]
            except Exception as exc:
                print(f"Impossible to fetch links from the url {url} : {exc}")
                links = []
            finally:
                if naming_strategy is not None and naming_strategy.get('strategy', None) == 'from_webpage':
                    # if we want to use the webpage to extract the chapter number we need to keep the driver open
                    pass
                else:
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
        
        if links_selenium:
            seen = set()
            links_selenium_cleaned = []
            for link_selenium in links_selenium:
                link = link_selenium.get_attribute('href')
                if base_url not in link:
                    continue
                if link not in seen:
                    seen.add(link)
                    links_selenium_cleaned.append(link_selenium)
            links_selenium = links_selenium_cleaned

        if naming_strategy is not None:
            strategy = naming_strategy.get('strategy', None)
            if strategy == 'url_removal':
                url_to_remove = naming_strategy.get('url_to_remove', '')
                for id, link in enumerate(chapters_links):
                    chapter_num = Mangapage._naming_strategy_url_removal(link, url_to_remove)
                    chapters_links[id] = {'link': link, 'num': chapter_num}
            elif strategy == 'from_substring':
                start_substring = naming_strategy.get('start_substring', '')
                for id, link in enumerate(chapters_links):
                    start_index = link.find(start_substring)
                    chapter_num = link[start_index:]
                    chapters_links[id] = {'link': link, 'num': chapter_num}
            elif strategy == 'from_webpage':
                if 'selenium_manager' not in locals() or not selenium_manager.is_driver_running():
                    print(f"Invalid driver! Impossible to extract chapter numbers from the webpage {url}!")
                else:
                    css_to_find = naming_strategy.get('css_selector', None)
                    if css_to_find is None:
                        print(f"Invalid css selector specified for webpage {url}: no chapter numbers will be extracted!")
                    else:
                        for id, link_selenium in enumerate(links_selenium):
                            # assuming the same order of links and links_selenium
                            chapter_num = Mangapage._naming_strategy_from_webpage(link_selenium, css_to_find)
                            chapters_links[id] = {'link': link_selenium.get_attribute('href'), 'num': chapter_num}
                    driver.quit()
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
    def _naming_strategy_url_removal(link: str, url_to_remove: str) -> int | float | str:
        chapter_num_str = link.replace(url_to_remove, '').strip('/')
        if Mangapage._string_is_number(chapter_num_str):
            try:
                chapter_num = int(chapter_num_str)
            except:
                chapter_num = float(chapter_num_str)
        else:
            chapter_num = chapter_num_str
        return chapter_num
    
    @staticmethod
    def _naming_strategy_from_webpage(link_selenium, css_selector: str) -> str:
        span_element = link_selenium.find_element(By.CSS_SELECTOR, css_selector)
        chapter_num = span_element.text.strip()
        return chapter_num
    
    @staticmethod
    def _string_is_number(num_str: str) -> bool:
        pattern = r'^-?\d+(\.\d+)?$'
        return re.match(pattern, num_str)
    
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