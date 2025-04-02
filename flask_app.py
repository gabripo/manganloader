from flask import Flask, render_template, request, send_file, jsonify
import zipfile
import io
import os
import shutil

from manganloader.pages_downloader import Mangapage
from manganloader.docbuilder import batch_download_chapters
from manganloader.links import source_list

app = Flask(__name__)
options = {
    'manga': None,
    'source': None,
    'num_chapters_to_download': 1,
    'format': 'PDF',
    'gen_double_spread': False,
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
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
