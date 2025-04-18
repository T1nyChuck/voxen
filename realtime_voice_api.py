import os
import time
import requests
import json
import base64
import sqlite3
import re
import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from instructions_voice import VOICE_AI_INSTRUCTIONS

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HEADERS_JSON = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
DB_PATH = "data.db"

conversation_log = []
payment_progress = {}

REQUIRED_FIELDS = ["name", "address", "card_number", "expiry_date", "cvv"]

HALLUCINATIONS = [
    "thank you", "thank you.", "you", "you.", "okay", "okay.",
    "subs by www.zeoranger.co.uk",
    "this program is brought to you", "brought to you by",
    "transcribed by", "sponsored by",
    "go to beadaholique.com for all of your beading supply needs!"
]

def validate_payment_field(field, value):
    if not value or not isinstance(value, str): return False
    value = value.strip()

    if field == "name":
        return len(value.split()) >= 2 and value.replace(" ", "").isalpha()
    elif field == "address":
        return len(value) > 5 and any(char.isdigit() for char in value)
    elif field == "card_number":
        digits = re.sub(r"\D", "", value)
        return digits.isdigit() and 13 <= len(digits) <= 19
    elif field == "expiry_date":
        try:
            if re.match(r"\d{2}/\d{2,4}", value):
                month, year = map(int, value.split("/"))
                if year < 100: year += 2000
                return datetime.datetime(year, month, 1) > datetime.datetime.now()
        except:
            return False
    elif field == "cvv":
        return re.fullmatch(r"\d{3}", value) is not None
    return False

def insert_payment_info(**kwargs):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, address TEXT,
            card_number TEXT, expiry_date TEXT, cvv TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        INSERT INTO payments (name, address, card_number, expiry_date, cvv)
        VALUES (:name, :address, :card_number, :expiry_date, :cvv)
    """, kwargs)
    conn.commit()
    conn.close()
    print(f"💾 Stored in DB: {kwargs}")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('connected', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('start_session')
def handle_start_session():
    print("Session started")
    conversation_log.clear()
    payment_progress.clear()
    emit('session_started', {"status": "ready"})

@socketio.on('audio_input')
def handle_audio_input(data):
    print("Received audio input")
    base64_audio = data.get("audio")
    audio_bytes = base64.b64decode(base64_audio.split(',')[1])
    with open("temp_audio.webm", "wb") as f:
        f.write(audio_bytes)

    # Whisper
    with open("temp_audio.webm", "rb") as f:
        transcription_resp = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers=HEADERS_JSON,
            files={"file": ("audio.webm", f, "audio/webm")},
            data={"model": "whisper-1", "language": "en"}
        )

    if not transcription_resp.ok:
        print("Whisper error:", transcription_resp.text)
        emit('error', {"message": "Whisper failed"})
        return

    transcript = transcription_resp.json().get("text", "").strip()
    print("Transcript:", transcript)

    if not transcript or transcript.lower() in HALLUCINATIONS or (
        len(transcript.split()) < 3 and any(h in transcript.lower() for h in HALLUCINATIONS)
    ):
        print("🧠 Filtered hallucinated or empty transcript:", transcript)
        fallback = "Sorry, I didn’t catch that. Could you try again?"
        conversation_log.append({"role": "assistant", "content": fallback})
        respond_with_tts(fallback)
        return

    emit("transcript", {"text": transcript})
    conversation_log.append({"role": "user", "content": transcript})

    # ChatGPT
    chat_resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={**HEADERS_JSON, "Content-Type": "application/json"},
        json={
            "model": "gpt-4",
            "messages": [{"role": "system", "content": VOICE_AI_INSTRUCTIONS}] + conversation_log,
            "functions": [
                {
                    "name": "store_payment_info",
                    "description": "Collect and store payment info",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "address": {"type": "string"},
                            "card_number": {"type": "string"},
                            "expiry_date": {"type": "string"},
                            "cvv": {"type": "string"}
                        }
                    }
                }
            ],
            "function_call": "auto"
        }
    )

    choice = chat_resp.json()["choices"][0]
    message = choice["message"]

    if "function_call" in message:
        args = json.loads(message["function_call"].get("arguments", "{}"))
        response = ""
        for field, value in args.items():
            if validate_payment_field(field, value):
                payment_progress[field] = value
                response += f"Got your {field.replace('_', ' ')}. "
            else:
                response += f"Hmm, \"{value}\" doesn’t look like a valid {field.replace('_', ' ')}. Could you try again? "
                break
        if all(field in payment_progress for field in REQUIRED_FIELDS):
            insert_payment_info(**payment_progress)
            response += "Perfect, you’re all set. You’ll receive confirmation by mail in a few business days."
    else:
        response = message.get("content", "(no response)")

    conversation_log.append({"role": "assistant", "content": response})
    respond_with_tts(response)

def respond_with_tts(text):
    print("Sending TTS...")
    tts_resp = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={**HEADERS_JSON, "Content-Type": "application/json"},
        json={
            "model": "tts-1",
            "input": text,
            "voice": "shimmer",
            "response_format": "mp3"
        }
    )
    if not tts_resp.ok:
        emit("error", {"message": "TTS failed"})
        return
    audio_b64 = base64.b64encode(tts_resp.content).decode("utf-8")
    emit("audio_response", {"text": text, "audio": audio_b64})

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5002)
