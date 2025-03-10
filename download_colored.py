import requests
import asyncio
from bs4 import BeautifulSoup
from manganloader.docbuilder import Document
from manganloader.pages_downloader import Mangapage

if __name__ == "__main__":
    url = 'https://ww11.readonepiece.com/index.php/manga/one-piece-digital-colored-comics/'
    response = Mangapage.fetch_webpage_response(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    links = [a.get('href') for a in soup.find_all('a', href=True)]

    base_url = 'https://ww11.readonepiece.com/index.php/chapter/'
    seen = set()
    chapters_links = []
    for link in links:
        if base_url not in link:
            continue
        if link not in seen:
            seen.add(link)
            chapters_links.append(link)
    chapters_links = chapters_links[-100:] # take it easy, man!

    for id, link in enumerate(chapters_links):
        d = Document(
            name="one_piece_colored_" + "{:05}".format(id),
            source_url=link,
            output_dir="output_raw",
            document_type="raw",
        )
        d.build_from_url()