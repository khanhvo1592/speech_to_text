import json
import os

HISTORY_FILE = 'history.json'
MAX_HISTORY = 10

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {'speech_to_text': [], 'text_to_speech': []}
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {'speech_to_text': [], 'text_to_speech': []}

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def add_to_history(type, input, output):
    history = load_history()
    if type not in history:
        history[type] = []
    history[type].insert(0, {
        'input': input,
        'output': output.replace('\\', '/')
    })
    history[type] = history[type][:MAX_HISTORY]
    save_history(history)

def get_history(type):
    history = load_history()
    return history.get(type, [])
def clean_old_files(type, current_files):
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    for filename in os.listdir(uploads_dir):
        if filename.startswith(f"{type}_"):
            file_path = os.path.join(uploads_dir, filename)
            if filename not in current_files:
                os.remove(file_path)