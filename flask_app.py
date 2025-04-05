from flask import Flask, render_template, request, send_file, jsonify, redirect, send_from_directory, url_for
import os

from manganloader.flask_helpers import download_chapters, delete_folder

app = Flask(__name__)
options = {
    'manga': None,
    'source': None,
    'num_chapters_to_download': 1,
    'format': 'PDF',
    'device': 'KCC',
    'gen_double_spread': False,
}
OUTPUT_DIR = os.path.abspath(os.path.join(os.getcwd(), 'output'))
manga_names_mapping = {
    "onepiece_bw" : "One_Piece_",
    "onepiece_col" : "One_Piece_colored_",
    "dbs_bw" : "Dragon_Ball_Super_",
    "dbs_col" : "Dragon_Ball_Super_colored_",
    "hxh_col": "Hunter_x_Hunter_colored_",
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

    if options['format'] == 'epub':
        options['device'] = data.get('device')

    return jsonify({"status": "success"})

@app.route('/download', methods=['POST'])
def download():
    delete_folder(folder_path=OUTPUT_DIR)

    download_chapters(
        manga=manga_names_mapping.get(options['manga'], 'Manga'),
        source=options['source'],
        num_chapters=options['num_chapters_to_download'],
        format=options['format'],
        output_dir=OUTPUT_DIR,
        device=options['device'],
        gen_double_spread=options['gen_double_spread'],
        )

    return redirect(url_for('download_page'))
    
@app.route('/download_page', methods=['GET'])
def download_page():
    files = os.listdir(OUTPUT_DIR)
    return render_template('download_page.html', files=files)
    
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

@app.route('/back_to_main')
def back_to_main():
    delete_folder(folder_path=OUTPUT_DIR)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
