from flask import Flask, request, render_template, redirect, url_for
import requests
import os
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CONFIG_FILE = 'config.json'
HISTORY_FILE = 'history.json'  # File để lưu lịch sử

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_token():
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return config.get('token')

def write_token(token):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"token": token}, f)

def read_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def write_history(history):
    # Giới hạn lịch sử chỉ lưu lại 10 kết quả gần nhất
    if len(history) > 10:
        history = history[-10:]
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

@app.route('/', methods=['GET', 'POST'])
def upload_form():
    result_text = ""
    audio_file_url = None
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

                if response.status_code == 200:
                    response_data = response.json()
                    transcript = response_data.get('response', {}).get('result', [{}])[0].get('transcript', 'No transcript found')
                    result_text = transcript

                    # Lưu kết quả vào lịch sử
                    history = read_history()
                    history.append(transcript)
                    write_history(history)
                    
                    # Lưu đường dẫn file âm thanh để nghe thử
                    audio_file_url = url_for('uploaded_file', filename=file.filename)
                else:
                    result_text = 'Error in processing audio'

    history = read_history()
    history = [item.split('\n', 1)[0] for item in history]  # Chỉ lấy dòng đầu tiên của mỗi transcript
    return render_template('upload.html', result=result_text, history=history, audio_file_url=audio_file_url)

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        token = request.form['token']
        write_token(token)
        return redirect(url_for('upload_form'))
    return render_template('config.html', token=read_token())

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return redirect(url_for('static', filename=os.path.join('uploads', filename)))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)