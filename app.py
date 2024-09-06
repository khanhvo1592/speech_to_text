from flask import Flask, request, render_template, redirect, url_for, send_file, send_from_directory
import os
import json
from text_to_speech import text_to_speech_viettel, get_voices
from history import add_to_history, get_history, clean_old_files
from datetime import datetime, timedelta
import pandas as pd  
from openpyxl.styles import NamedStyle




app = Flask(__name__)
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


# Đọc file JSON chứa thông tin về chương trình có VOD
def load_programs_with_vod():
    json_path = os.path.join(os.path.dirname(__file__), 'static', 'programe_have_vod.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

PROGRAMS_WITH_VOD = load_programs_with_vod()

# URL mẫu cho video link
VOD_URL_TV = "https://60acee235f4d5.streamlock.net:443/VODHGTV/definst/VIDEO/mp4:"
VOD_URL_RADIO = "https://60acee235f4d5.streamlock.net:443/VODHGTV/definst/AUDIO/mp3:"


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


@app.route('/create_broadcast_schedule', methods=['GET', 'POST'])
def create_broadcast_schedule():
    if request.method == 'POST':
        date_input = request.form['date_input']
        program_type = request.form['program_type']
        input_data = request.form['input_data']

        # Xử lý ngày tháng
        current_year = datetime.now().year
        date = datetime.strptime(f"{date_input}{current_year}", "%d%m%Y")

        # Xử lý dữ liệu đầu vào
        schedule = process_input_data(input_data, date, program_type)

        # Tạo và lưu file Excel
        output_filename = f'lich_phat_song_{date.strftime("%d%m%Y")}.xlsx'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        save_schedule_to_excel(schedule, output_path)

        if os.path.exists(output_path):
            return send_file(output_path, as_attachment=True)
        else:
            return "Không thể tạo file lịch phát sóng", 500

    return render_template('create_broadcast_schedule.html')

def process_input_data(input_data, date, program_type):
    schedule = []
    lines = input_data.split('\n')
    for index, line in enumerate(lines, start=1):
        if line.strip():
            time, content = line.split(' ', 1)
            content = content.strip()
            video_link = generate_video_link(content, program_type, date)
            schedule.append({
                'STT': index,
                'Đài truyền hình': 2 if program_type == '2' else 1,  # 2 cho phát thanh, 1 cho truyền hình
                'Nội dung': content,
                'Danh mục': '',  # Để trống, có thể điền sau nếu cần
                'video_link': video_link,
                'ngày_giờ': f"{date.strftime('%Y-%m-%d')} {time}:00"
            })
    return schedule

def generate_video_link(content, program_type, date):
    current_date = date.strftime("%d%m%y")
    for program in PROGRAMS_WITH_VOD:
        if program['name'].lower() in content.lower():
            if program_type == '2':  # Phát thanh
                return f"{VOD_URL_RADIO}{program['shortname']}-{current_date}.mp3/playlist.m3u8"
            else:  # Truyền hình
                return f"{VOD_URL_TV}{program['shortname']}-{current_date}.mp4/playlist.m3u8"
    return ''  # Trả về chuỗi rỗng nếu không tìm thấy chương trình phù hợp

def save_schedule_to_excel(schedule, filename):
    df = pd.DataFrame(schedule)
    df = df[['STT', 'Đài truyền hình', 'Nội dung', 'Danh mục', 'video_link', 'ngày_giờ']]  # Sắp xếp lại các cột
    
    # Chuyển đổi cột 'ngày_giờ' sang định dạng datetime
    df['ngày_giờ'] = pd.to_datetime(df['ngày_giờ'])
    
    # Tạo một ExcelWriter object
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        # Lấy workbook và worksheet
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        
        # Định dạng các cột
        for col in ['A', 'B', 'D']:  # STT, Đài truyền hình, Danh mục
            worksheet.column_dimensions[col].width = 15
        worksheet.column_dimensions['C'].width = 50  # Nội dung
        worksheet.column_dimensions['E'].width = 100  # video_link
        worksheet.column_dimensions['F'].width = 20  # ngày_giờ
        
        # Định dạng cột ngày_giờ
        date_style = NamedStyle(name='datetime', number_format='YYYY-MM-DD HH:MM:SS')
        for cell in worksheet['F'][1:]:  # Skip header
            cell.style = date_style
        
    print(f"File saved to: {filename}")

if __name__ == '__main__':
    app.run(debug=True)