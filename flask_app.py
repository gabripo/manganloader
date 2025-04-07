from flask import Flask, render_template, request, send_file, jsonify, redirect, send_from_directory, url_for
import os
import secrets

from manganloader.flask_helpers import download_chapters, delete_folder, determine_output_folder

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) # needed for sessions management
options = {
    'manga': None,
    'source': None,
    'num_chapters_to_download': 1,
    'format': 'PDF',
    'device': 'KCC',
    'gen_double_spread': False,
}
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
    output_dir = determine_output_folder()
    delete_folder(folder_path=output_dir)

    download_chapters(
        manga=manga_names_mapping.get(options['manga'], 'Manga'),
        source=options['source'],
        num_chapters=options['num_chapters_to_download'],
        format=options['format'],
        output_dir=output_dir,
        device=options['device'],
        gen_double_spread=options['gen_double_spread'],
        )

    return redirect(url_for('download_page'))
    
@app.route('/download_page', methods=['GET'])
def download_page():
    output_dir = determine_output_folder()
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        if files:
            for file in files:
                print(f"File {file} found in folder {output_dir}")
    else:
        files = []
        print(f"No files found in folder {output_dir} !")
    return render_template('download_page.html', files=files)
    
@app.route('/download/<filename>')
def download_file(filename):
    output_dir = determine_output_folder()
    return send_from_directory(output_dir, filename, as_attachment=True)

@app.route('/back_to_main')
def back_to_main():
    output_dir = determine_output_folder()
    delete_folder(folder_path=output_dir)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
