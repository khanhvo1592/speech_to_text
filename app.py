from flask import Flask, request, render_template, redirect, url_for, send_file, send_from_directory
import os
import json
from speech_to_text import speech_to_text_viettel
from text_to_speech import text_to_speech_viettel, get_voices
from history import add_to_history, get_history, clean_old_files

app = Flask(__name__)
# Định nghĩa UPLOAD_FOLDER
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a'}
CONFIG_FILE = 'config.json'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_token():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config.get('token')
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def write_token(token):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"token": token}, f)
    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/speech-to-text', methods=['GET', 'POST'])
def speech_to_text_page():
    token = read_token()
    if not token:
        return redirect(url_for('config'))
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
        voice = request.form.get('voice', 'hcm-leyen')
        speed = float(request.form.get('speed', 1))
        
        audio_file = text_to_speech_viettel(text, voice, speed, read_token(), UPLOAD_FOLDER)
        
        if audio_file:
            add_to_history('text_to_speech', text, audio_file)
            return send_file(os.path.join(UPLOAD_FOLDER, audio_file), 
                             as_attachment=True, 
                             download_name='speech.mp3',
                             mimetype='audio/mpeg')
        else:
            return 'Lỗi khi chuyển đổi văn bản thành giọng nói', 500
    
    voices = get_voices()
    history = get_history('text_to_speech')
    print("History:", history)  # Thêm dòng này để kiểm tra
    # Lấy danh sách các tệp âm thanh hiện tại trong lịch sử
    current_files = [item['output'] for item in history if item['output'].endswith('.mp3')]
    
    # Xóa các tệp âm thanh cũ không còn trong lịch sử
    clean_old_files('tts', current_files)
    return render_template('text_to_speech.html', voices=voices, history=history)

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        token = request.form['token']
        write_token(token)
        return redirect(url_for('home'))
    return render_template('config.html', token=read_token())

@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, 
                               as_attachment=True, 
                               mimetype='audio/mpeg')
if __name__ == '__main__':
    app.run(debug=True)