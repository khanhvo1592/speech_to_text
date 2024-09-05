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
    history[type] = [{'input': input, 'output': output}] + history[type]
    history[type] = history[type][:MAX_HISTORY]
    save_history(history)

def get_history(type):
    history = load_history()
    return history.get(type, [])