import requests

def speech_to_text_viettel(filepath, token):
    url = "https://viettelai.vn/asr/recognize"
    payload = {'token': token}
    headers = {'accept': '*/*'}

    with open(filepath, 'rb') as audio_file:
        files = [('file', (filepath, audio_file, 'audio/wav'))]
        response = requests.post(url, headers=headers, data=payload, files=files)

    if response.status_code == 200:
        response_data = response.json()
        transcript = response_data.get('response', {}).get('result', [{}])[0].get('transcript', 'Không tìm thấy transcript')
        return transcript
    else:
        return None