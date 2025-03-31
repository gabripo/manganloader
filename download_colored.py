import requests
import asyncio
import os
from bs4 import BeautifulSoup
from manganloader.docbuilder import Document, batch_download_chapters
from manganloader.pages_downloader import Mangapage

if __name__ == "__main__":
    # url = 'https://ww9.dbsmanga.com/manga/dragon-ball-super/'
    url = 'https://ww9.dbsmanga.com/manga/dragon-ball-super-colored/'
    base_url = 'https://ww9.dbsmanga.com/chapter/'
    chapters_links = Mangapage.fetch_latest_chapters_generic(
        url=url,
        base_url=base_url,
    )
    # chapters_links = chapters_links[-100:] # take it easy, man!

    batch_download_chapters(
        chapters_links=chapters_links,
        use_color=True,
        prefix='dragon_ball_super_colored_',
        output_dir="output_kcc",
        output_format="epub"
    )