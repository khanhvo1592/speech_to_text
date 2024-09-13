import os
import json
from datetime import datetime, time
import pandas as pd
from openpyxl.styles import NamedStyle
import re

# Đọc file JSON chứa thông tin về chương trình có VOD
def load_programs_with_vod():
    json_path = os.path.join(os.path.dirname(__file__), 'static', 'programe_with_vod.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

PROGRAMS_WITH_VOD = load_programs_with_vod()

# URL mẫu cho video link
VOD_URL_TV = "https://60acee235f4d5.streamlock.net:443/VODHGTV/definst/VIDEO/mp4:"
VOD_URL_RADIO = "https://60acee235f4d5.streamlock.net:443/VODHGTV/definst/AUDIO/mp3:"

def parse_custom_time(time_string):
    # Xử lý các định dạng thời gian khác nhau
    patterns = [
        r'(\d{2})h(\d{2})',  # 00h00
        r'(\d{2}):(\d{2})',  # 00:00
        r'(\d{2})h(\d{2})\s*',  # 00h00 (có thể có khoảng trắng)
    ]
    
    for pattern in patterns:
        match = re.match(pattern, time_string)
        if match:
            hour, minute = map(int, match.groups())
            return time(hour, minute)
    
    raise ValueError(f"Không thể phân tích chuỗi thời gian: {time_string}")

def process_input_data(input_data, date, program_type):
    schedule = []
    lines = input_data.split('\n')
    for index, line in enumerate(lines, start=1):
        if line.strip():
            try:
                # Tìm thời gian ở đầu dòng
                time_match = re.match(r'(\d{2}[h:]\d{2})\s*(.*)', line.strip())
                if time_match:
                    time_part, content = time_match.groups()
                else:
                    raise ValueError("Không tìm thấy thời gian hợp lệ")

                parsed_time = parse_custom_time(time_part)
                content = content.strip()
                video_link = generate_video_link(content, program_type, date)
                
                # Kết hợp ngày và giờ
                full_datetime = datetime.combine(date, parsed_time)
                
                schedule.append({
                    'STT': index,
                    'Đài truyền hình': 2 if program_type == '2' else 1,
                    'Nội dung': content,
                    'Danh mục': '',
                    'video_link': video_link,
                    'ngày_giờ': full_datetime.strftime('%Y-%m-%d %H:%M:%S')
                })
            except ValueError as e:
                print(f"Lỗi xử lý dòng {index}: {str(e)}")
    return schedule

def generate_video_link(content, program_type, date):
    current_date = date.strftime("%d%m%y")
    for program in PROGRAMS_WITH_VOD:
        if program['name'].lower() in content.lower():
            if program_type == '2':  # Phát thanh
                return f"{VOD_URL_RADIO}{program['shortname']}-{current_date}.mp3/playlist.m3u8"
            else:  # Truyền hình
                return f"{VOD_URL_TV}{program['shortname']}-{current_date}.mp4/playlist.m3u8"
    return ''

# Cập nhật hàm save_schedule_to_excel
def save_schedule_to_excel(schedule, filename):
    df = pd.DataFrame(schedule)
    df = df[['STT', 'Đài truyền hình', 'Nội dung', 'Danh mục', 'video_link', 'ngày_giờ']]
    
    # Chuyển đổi cột 'ngày_giờ' thành datetime nếu nó chưa phải là datetime
    if not pd.api.types.is_datetime64_any_dtype(df['ngày_giờ']):
        df['ngày_giờ'] = pd.to_datetime(df['ngày_giờ'])
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        worksheet = writer.sheets['Sheet1']
        
        for col in ['A', 'B', 'D']:
            worksheet.column_dimensions[col].width = 15
        worksheet.column_dimensions['C'].width = 50
        worksheet.column_dimensions['E'].width = 100
        worksheet.column_dimensions['F'].width = 20
        
        date_style = NamedStyle(name='datetime', number_format='YYYY-MM-DD HH:MM:SS')
        for cell in worksheet['F'][1:]:
            cell.style = date_style
    
    print(f"File saved to: {filename}")
def create_broadcast_schedule(date_input, program_type, input_data, upload_folder):
    try:
        current_year = datetime.now().year
        date = datetime.strptime(f"{date_input}{current_year}", "%d%m%Y")
    except ValueError:
        print(f"Lỗi: Không thể chuyển đổi '{date_input}' thành ngày tháng hợp lệ.")
        return None

    schedule = process_input_data(input_data, date, program_type)

    if not schedule:
        print("Không có dữ liệu hợp lệ để tạo lịch phát sóng.")
        return None

    output_filename = f'lich_phat_song_{date.strftime("%d%m%Y")}.xlsx'
    output_path = os.path.join(upload_folder, output_filename)
    save_schedule_to_excel(schedule, output_path)

    return output_path if os.path.exists(output_path) else None
