from flask import Flask, request, render_template, redirect, url_for, send_file
import os
import json
from speech_to_text import speech_to_text_viettel
from text_to_speech import text_to_speech_viettel
from history import add_to_history, get_history

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a'}
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

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/speech-to-text', methods=['GET', 'POST'])
def speech_to_text_page():
    result_text = ""
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = file.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                result_text = speech_to_text_viettel(filepath, read_token())
                
                os.remove(filepath)
                
                if result_text:
                    add_to_history('speech_to_text', filename, result_text)
                else:
                    result_text = "Lỗi trong quá trình xử lý âm thanh"
            else:
                result_text = "File không hợp lệ"
    
    history = get_history('speech_to_text')
    return render_template('speech_to_text.html', result=result_text, history=history)

@app.route('/text-to-speech', methods=['GET', 'POST'])
def text_to_speech_page():
    if request.method == 'POST':
        if 'text' not in request.form:
            return 'Không có văn bản để chuyển đổi', 400
        
        text = request.form['text']
        voice = request.form.get('voice', 'hcm-diemmy')
        speed = float(request.form.get('speed', 1))
        
        audio_file = text_to_speech_viettel(text, voice, speed, read_token())
        
        if audio_file:
            add_to_history('text_to_speech', text, audio_file)
            return send_file(audio_file, as_attachment=True, download_name='speech.mp3')
        else:
            return 'Lỗi khi chuyển đổi văn bản thành giọng nói', 500
    
    history = get_history('text_to_speech')
    return render_template('text_to_speech.html', history=history)

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        token = request.form['token']
        write_token(token)
        return redirect(url_for('home'))
    return render_template('config.html', token=read_token())

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)