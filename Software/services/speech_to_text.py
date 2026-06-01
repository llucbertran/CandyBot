from dotenv import load_dotenv
import requests
import tempfile
import subprocess
import os
import json

load_dotenv()

# ==========================================================
# CONFIGURACIÓN
# API_URL y API_TOKEN se leen desde .env o variables de entorno
# El resto se configura aquí dentro del script
# ==========================================================
API_URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
ALSA_DEVICE = "plughw:1,0"
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_FORMAT = "S16_LE"
RECORD_SECONDS = 4


def validate_config():
    if not API_URL:
        raise RuntimeError("Falta API_URL en .env o en las variables de entorno")
    if not API_TOKEN:
        raise RuntimeError("Falta API_TOKEN en .env o en las variables de entorno")


def record_audio() -> str:
    validate_config()

    print(f"Gravant {RECORD_SECONDS} segons des de {ALSA_DEVICE}... parla ara!")

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()

    cmd = [
        "arecord",
        "-D", ALSA_DEVICE,
        "-r", str(SAMPLE_RATE),
        "-f", SAMPLE_FORMAT,
        "-c", str(CHANNELS),
        "-d", str(RECORD_SECONDS),
        tmp.name,
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        if os.path.exists(tmp.name):
            os.remove(tmp.name)
        raise RuntimeError(f"Error grabando audio con arecord: {e}") from e

    print("Gravació acabada.")
    return tmp.name


def send_audio_to_api(wav_path: str) -> dict:
    with open(wav_path, "rb") as f:
        files = {"audio": (os.path.basename(wav_path), f, "audio/wav")}
        headers = {
            "X-API-Token": API_TOKEN,
            "accept": "application/json",
        }
        response = requests.post(API_URL, headers=headers, files=files, timeout=60)

    if response.status_code == 200:
        return response.json()
    if response.status_code == 401:
        raise RuntimeError("❌ Token incorrecte")
    if response.status_code == 415:
        raise RuntimeError("❌ Àudio invàlid (no WAV)")
    if response.status_code == 422:
        return {"action": "nothing", "items": [], "note": "No s'ha detectat veu"}
    raise RuntimeError(f"❌ Error API {response.status_code}: {response.text}")


def main():
    wav_path = record_audio()

    try:
        print("\nEnviant audio a la API...")
        result = send_audio_to_api(wav_path)

        print("\n── Resposta API ──")
        print(f"device: {ALSA_DEVICE}")
        print(f"seconds: {RECORD_SECONDS}")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    finally:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)


if __name__ == "__main__":
    main()
