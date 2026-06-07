import os
import signal
import subprocess
import tempfile
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL   = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")

ALSA_DEVICE = "plughw:1,0"  # run 'arecord -l' on the Pi to list devices
SAMPLE_RATE = 16000
CHANNELS    = 1
MAX_SECONDS = 15  # safety cap for crank-driven recording


def record_while(is_active, max_seconds=MAX_SECONDS):
    """Record while is_active() stays True (or until max_seconds). Returns the WAV path."""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    cmd = ["arecord", "-D", ALSA_DEVICE, "-r", str(SAMPLE_RATE),
           "-f", "S16_LE", "-c", str(CHANNELS), tmp.name]
    proc = subprocess.Popen(cmd)
    start = time.time()
    try:
        while is_active() and time.time() - start < max_seconds:
            time.sleep(0.05)
    finally:
        proc.send_signal(signal.SIGINT)  # let arecord finalize the WAV header
        proc.wait()
    return tmp.name


def send_audio_to_api(wav_path):
    """POST the WAV to the CandyBot API and return the parsed JSON response."""
    with open(wav_path, "rb") as f:
        response = requests.post(
            API_URL,
            headers={"X-API-Token": API_TOKEN, "accept": "application/json"},
            files={"audio": (os.path.basename(wav_path), f, "audio/wav")},
            timeout=60,
        )
    if response.status_code == 200:
        return response.json()
    if response.status_code == 401:
        raise RuntimeError("Wrong API token")
    if response.status_code == 415:
        raise RuntimeError("Invalid audio format")
    if response.status_code == 422:
        return {"action": "nothing", "items": []}
    raise RuntimeError(f"API error {response.status_code}: {response.text}")


def record_and_send_while(is_active, max_seconds=MAX_SECONDS):
    """Record while is_active() is True, send to the API, clean up. Returns the response."""
    wav = record_while(is_active, max_seconds)
    try:
        return send_audio_to_api(wav)
    finally:
        os.remove(wav)
