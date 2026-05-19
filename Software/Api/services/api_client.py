
# Software/Api/services/api_client.py
from dotenv import load_dotenv
import requests
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
import os
load_dotenv()

API_URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")

print("DEBUG API_URL:", API_URL)
print("DEBUG API_TOKEN:", API_TOKEN)

SAMPLE_RATE = 44100
CHANNELS = 1


# ─────────────────────────────────────────────
# 🎤 GRAVAR AUDIO
# ─────────────────────────────────────────────

def record_audio(seconds: int = 4) -> str:
    print(f"Gravant {seconds} segons... parla ara!")

    audio = sd.rec(
        int(seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16"
    )

    sd.wait()
    print("Gravació acabada.")

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

def record_and_send(seconds: int = 4) -> dict:
    wav_path = record_audio(seconds)

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
