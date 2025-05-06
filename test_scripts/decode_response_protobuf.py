from requests import Session
# from mloader.response_pb2 import (
#     Response,
# )
import import_root_path
from manganloader.protobuf_lib.mangaplus_pb2 import (
    Response,
)

if __name__ == "__main__":
    session = Session()
    session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; "
                "rv:72.0) Gecko/20100101 Firefox/72.0"
            }
        )
    
    url = 'https://jumpg-webapi.tokyo-cdn.com/api/manga_viewer'
    params = {
        'chapter_id': '1001249', # from https://mangaplus.shueisha.co.jp/viewer/1001249?timestamp=1744143038719
        'split': 'yes',
        'img_quality': 'super_high',
        'clang': 'eng',
    }
    response = session.get(url=url, params=params)
    content = response.content
    viewer = Response.FromString(content).success.manga_viewer
    title_id = viewer.title_id