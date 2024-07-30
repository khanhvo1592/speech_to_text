from flask import Flask, request, render_template, redirect, url_for
import requests
import os
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CONFIG_FILE = 'config.json'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_token():
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return config.get('token')

def write_token(token):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"token": token}, f)
@app.route('/', methods=['GET', 'POST'])
def upload_form():
    result_text = ""
    if request.method == 'POST':
        if 'file' not in request.files:
            result_text = 'No file part'
        else:
            file = request.files['file']
            if file.filename == '' or not allowed_file(file.filename):
                result_text = 'No selected file or file type not allowed'
            else:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)

                token = read_token()
                url = "https://viettelai.vn/asr/recognize"
                payload = {'token': token}
                headers = {'accept': '*/*'}

                with open(filepath, 'rb') as audio_file:
                    files = [('file', (file.filename, audio_file, 'audio/wav'))]
                    response = requests.post(url, headers=headers, data=payload, files=files)

                os.remove(filepath)

                if response.status_code == 200:
                    response_data = response.json()
                    # Trích xuất transcript
                    transcript = response_data.get('response', {}).get('result', [{}])[0].get('transcript', 'No transcript found')
                    result_text = transcript
                else:
                    result_text = 'Error in processing audio'

    return render_template('upload.html', result=result_text)
@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        token = request.form['token']
        write_token(token)
        return redirect(url_for('upload_form'))
    return render_template('config.html', token=read_token())

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)