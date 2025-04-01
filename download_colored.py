import requests
import asyncio
import os
from bs4 import BeautifulSoup
from manganloader.docbuilder import Document, batch_download_chapters
from manganloader.pages_downloader import Mangapage

USE_JAVASCRIPT = True

if __name__ == "__main__":
    if USE_JAVASCRIPT:
        url = 'https://mangaberri.com/dbs-colored-manga'
        base_url = 'https://mangaberri.com/dbs-colored-manga/'
        javascript_args_mainpage = {
            'dummy': [],
        }
        javascript_args_chapter = {}
    else:
        # url = 'https://ww9.dbsmanga.com/manga/dragon-ball-super/'
        url = 'https://ww9.dbsmanga.com/manga/dragon-ball-super-colored/'
        base_url = 'https://ww9.dbsmanga.com/chapter/'
        javascript_args_mainpage = {}
        javascript_args_chapter = {}

    chapters_links = Mangapage.fetch_latest_chapters_generic(
        url=url,
        base_url=base_url,
        javascript_args_mainpage=javascript_args_mainpage,
    )
    # chapters_links = chapters_links[-100:] # take it easy, man!

    batch_download_chapters(
        chapters_links=chapters_links,
        use_color=True,
        prefix='dragon_ball_super_colored_',
        output_dir="output_kcc",
        output_format="epub",
        javascript_args_chapter=javascript_args_chapter,
    )