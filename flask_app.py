from flask import Flask, render_template, request, send_file, jsonify
import zipfile
import io
import os
import shutil

from manganloader.pages_downloader import Mangapage
from manganloader.docbuilder import batch_download_chapters

app = Flask(__name__)
options = {
    'manga': None,
    'source': None,
    'num_chapters_to_download': 1,
    'format': 'PDF',
    'gen_double_spread': False,
}
source_list = {
    'mangaplus': {
        'url': 'https://jumpg-webapi.tokyo-cdn.com/api/title_detailV3?title_id=100020',
        'base_url': None,
        'has_color': False,
        'reverse_order': True,
        'javascript_args_mainpage': {},
        'javascript_args_chapter': {},
        },
    'readonepiece': {
        'url': 'https://ww11.readonepiece.com/index.php/manga/one-piece-digital-colored-comics/',
        'base_url': 'https://ww11.readonepiece.com/index.php/chapter/',
        'has_color': True,
        'reverse_order': False,
        'javascript_args_mainpage': {},
        'javascript_args_chapter': {},
        },
    'dbsmanga_bw': {
        'url': 'https://ww9.dbsmanga.com/manga/dragon-ball-super/',
        'base_url': 'https://ww9.dbsmanga.com/chapter/',
        'has_color': False,
        'reverse_order': False,
        'javascript_args_mainpage': {},
        'javascript_args_chapter': {},
        },
    'dbsmanga_col': {
        'url': 'https://ww9.dbsmanga.com/manga/dragon-ball-super-colored/',
        'base_url': 'https://ww9.dbsmanga.com/chapter/',
        'has_color': True,
        'reverse_order': False,
        'javascript_args_mainpage': {},
        'javascript_args_chapter': {},
        },
    'weebcentral_dbs_col': {
        'url': 'https://weebcentral.com/series/01J76XYEWEQKT8DFAMV2S1Z883/Dragon-Ball-Super-Color',
        'base_url': 'https://weebcentral.com/chapters/',
        'has_color': True,
        'reverse_order': False,
        'javascript_args_mainpage': {
            'buttons': ['Show All Chapters'],
        },
        'javascript_args_chapter': {},
        },
    'mangatoto_dbs_col': {
        'url': 'https://mangatoto.net/title/86383',
        'base_url': 'https://mangatoto.net/title/86383-dragon-ball-super-digital-colored-official-tl-overlaid/',
        'has_color': True,
        'reverse_order': True,
        'javascript_args_mainpage': {
            'buttons_xpath': ['/html/body/div/main/div[3]/astro-island/div/div[1]/div[1]/span'],
        },
        'javascript_args_chapter': {
            'buttons': ['load all pages'],
        },
        },
    'mangareader_dbs_col': {
        'url': 'https://mangareader.to/dragon-ball-super-color-edition-55928',
        'base_url': 'https://mangareader.to/read/dragon-ball-super-color-edition-55928/en/chapter',
        'has_color': True,
        'reverse_order': True,
        'javascript_args_mainpage': {
            'dummy': [],
        },
        'javascript_args_chapter': {
            'buttons_xpath': ["/html/body/div[1]/div[4]/div/div[1]/div/div[3]/a[1]"],
            'scrolls': 3,
        },
        },
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_options', methods=['POST'])
def update_options():
    data = request.json
    options['manga'] = data.get('manga')
    options['source'] = data.get('source')
    options['num_chapters_to_download'] = int(data.get('numChaptersToDownload'))
    options['format'] = data.get('format')
    options['gen_double_spread'] = data.get('generateDoubleSpread')

    return jsonify({"status": "success"})

def DownloadBackend(
        manga: str,
        source: str,
        num_chapters: int,
        format: str,
        output_dir: str,
        gen_double_spread: bool,
        ):
    print(f"Manga: {manga}, Source: {source}, Num chapters to download: {num_chapters}, Format: {format}, Output folder: ")
    source_dict = source_list.get(source, None)
    if source_dict is None:
        print("Invalid source specified! Nothing will be downloaded.")
        return
    source_colored = source_dict.pop('has_color', False)
    reverse_order = source_dict.pop('reverse_order', False)
    javascript_args_chapter = source_dict.pop('javascript_args_chapter', {})
    
    chapters_links = Mangapage.fetch_latest_chapters_generic(**source_dict)
    if len(chapters_links) < num_chapters:
        print(f"Number of chapters to download is bigger than the available ones! Only {len(chapters_links)} will be downloaded.")
    elif reverse_order:
        chapters_links = chapters_links[-num_chapters:]
    else:
        chapters_links = chapters_links[:num_chapters]

    batch_download_chapters(
        chapters_links=chapters_links,
        use_color=source_colored,
        prefix=manga,
        output_dir=output_dir,
        output_format=format,
        gen_double_spread=gen_double_spread,
        javascript_args_chapter=javascript_args_chapter,
        )

@app.route('/download', methods=['POST'])
def download():
    output_dir = os.path.abspath(os.path.join(os.getcwd(), 'output'))
    shutil.rmtree(output_dir, ignore_errors=True)

    DownloadBackend(
        manga=options['manga'],
        source=options['source'],
        num_chapters=options['num_chapters_to_download'],
        format=options['format'],
        output_dir=output_dir,
        gen_double_spread=options['gen_double_spread'],
        )

    entries = os.listdir(output_dir)
    files = [os.path.join(output_dir, entry) for entry in entries if os.path.isfile(os.path.join(output_dir, entry))]
    if len(files) == 1:
        single_file = files[0]
        return send_file(
            single_file,
            as_attachment=True,
            download_name=os.path.basename(single_file),
        )
    else:
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zf.write(file_path, os.path.relpath(file_path, output_dir))
        memory_file.seek(0)

        zip_file_name = f"{options['manga']}_{options['num_chapters_to_download']}_{options['source']}_{options['format']}" + '.zip'
        return send_file(
            memory_file,
            as_attachment=True,
            download_name=zip_file_name,
            mimetype='application/zip'
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
