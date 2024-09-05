import requests
import time
from requests.exceptions import RequestException
import json

def speech_to_text_viettel(filepath, token, max_retries=3, timeout=30):
    url = "https://viettelai.vn/asr/recognize"
    payload = {'token': token}
    headers = {'accept': '*/*'}

    for attempt in range(max_retries):
        try:
            with open(filepath, 'rb') as audio_file:
                files = [('file', (filepath, audio_file, 'audio/wav'))]
                response = requests.request("POST", url, headers=headers, data=payload, files=files, timeout=timeout)

            print(f"Mã trạng thái: {response.status_code}")
            print("Phản hồi đầy đủ từ API:")
            print(response.text)

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    transcripts = [result.get('transcript', '') for result in response_data.get('response', {}).get('result', [])]
                    full_transcript = ' '.join(transcripts)
                    print(f"Độ dài transcript: {len(full_transcript)} ký tự")
                    return full_transcript
                except json.JSONDecodeError:
                    print("Lỗi: Không thể giải mã JSON từ phản hồi")
                    return None
            else:
                print(f"Lỗi API: {response.status_code}")
                return None

        except RequestException as e:
            print(f"Lỗi kết nối (lần thử {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Đợi 2 giây trước khi thử lại
            else:
                print("Đã vượt quá số lần thử lại tối đa.")
                return None

    return None