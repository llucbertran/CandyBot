
# Software/services/api_client.py
from dotenv import load_dotenv
import requests
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import tempfile
import time
import os
load_dotenv()

API_URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")

print("DEBUG API_URL:", API_URL)
print("DEBUG API_TOKEN:", API_TOKEN)

SAMPLE_RATE = 44100
CHANNELS = 1
MAX_SECONDS = 8          # límit dur de gravació

# Microphone input device (Electret Mic Breakout via USB audio adapter).
# None = system default; or an int index / name substring.
# List devices: python -c "import sounddevice; print(sounddevice.query_devices())"
MIC_DEVICE = None


# ─────────────────────────────────────────────
# 🎤 GRAVAR AUDIO
#    Grava fins que arribi un senyal de parada (stop_event)
#    o fins a max_seconds, el que passi abans.
# ─────────────────────────────────────────────

def record_audio(max_seconds: int = MAX_SECONDS, stop_event=None) -> str:
    print(f"Gravant (max {max_seconds}s)... parla ara!")

    chunks = []

    def _callback(indata, frames, time_info, status):
        chunks.append(indata.copy())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        device=MIC_DEVICE,
        callback=_callback,
    ):
        start = time.time()
        while time.time() - start < max_seconds:
            if stop_event is not None and stop_event.is_set():
                break
            sd.sleep(50)  # ms

    print("Gravacio acabada.")

    if chunks:
        audio = np.concatenate(chunks, axis=0)
    else:
        audio = np.zeros((1, CHANNELS), dtype="int16")

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wav.write(tmp.name, SAMPLE_RATE, audio)

    return tmp.name


# ─────────────────────────────────────────────
# 🌐 ENVIAR A LA API
# ─────────────────────────────────────────────

def send_audio_to_api(wav_path: str) -> dict:
    print("Enviant àudio a la API...")

    with open(wav_path, "rb") as f:
        files = {
            "audio": (os.path.basename(wav_path), f, "audio/wav")
        }

        headers = {
            "X-API-Token": API_TOKEN,
            "accept": "application/json",
        }

        response = requests.post(
            API_URL,
            headers=headers,
            files=files,
            timeout=60
        )

    if response.status_code == 200:
        print(f"✅ Resposta OK ({response.status_code})")
        return response.json()

    elif response.status_code == 401:
        raise RuntimeError("❌ Token incorrecte")

    elif response.status_code == 415:
        raise RuntimeError("❌ Àudio invàlid (no WAV)")
    elif response.status_code == 422:

        print("⚠️ No s'ha detectat veu. Torna-ho a provar.")

        return {"action": "nothing", "items": []}


# ─────────────────────────────────────────────
# 🔄 PIPELINE COMPLET (TIPUS README)
# ─────────────────────────────────────────────

def record_and_send(max_seconds: int = MAX_SECONDS, stop_event=None) -> dict:
    wav_path = record_audio(max_seconds, stop_event)

    try:
        result = send_audio_to_api(wav_path)
    finally:
        os.remove(wav_path)

    return result


# ─────────────────────────────────────────────
# 🧪 TEST DIRECTE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    result = record_and_send(4)

    print("\n── Resposta API ──")
    print(f"action: {result.get('action')}")
    print(f"items: {result.get('items')}")
