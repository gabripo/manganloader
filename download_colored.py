import requests
import asyncio
import os
from bs4 import BeautifulSoup
from manganloader.docbuilder import Document
from manganloader.pages_downloader import Mangapage

if __name__ == "__main__":
    # url = 'https://ww9.dbsmanga.com/manga/dragon-ball-super/'
    url = 'https://ww9.dbsmanga.com/manga/dragon-ball-super-colored/'
    response = Mangapage.fetch_webpage_response(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    links = [a.get('href') for a in soup.find_all('a', href=True)]

    base_url = 'https://ww9.dbsmanga.com/chapter/'
    seen = set()
    chapters_links = []
    for link in links:
        if base_url not in link:
            continue
        if link not in seen:
            seen.add(link)
            chapters_links.append(link)
    # chapters_links = chapters_links[-100:] # take it easy, man!

    for id, link in enumerate(chapters_links):
        chapter_name = "dragon_ball_super_colored_" + "{:05}".format(len(chapters_links)-id)
        d = Document(
            name=chapter_name,
            source_url=link,
            output_dir="output_kcc",
            document_type="epub",
        )
        d.set_working_dir(os.path.join(d.working_dir, chapter_name))
        d.set_kcc_option('--forcecolor')
        d.build_from_url()
        # d.clean_working_dir()