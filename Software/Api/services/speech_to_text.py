from __future__ import annotations
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from Software.Api.config import Settings, get_settings

from Software.Api.utils.audio_utils import ensure_mono_wav

WAV_CONTENT_TYPE = "audio/wav"
_SPEECH_CLIENT = None

def _get_speech_client() -> SpeechClient:
    global _SPEECH_CLIENT
    if _SPEECH_CLIENT is None:
        _SPEECH_CLIENT = SpeechClient()
    return _SPEECH_CLIENT

def transcribe_audio(
    audio_bytes: bytes,
    content_type: str,
    settings: Settings | None = None,
) -> str:
    if content_type != WAV_CONTENT_TYPE:
        raise ValueError(f"Unsupported audio content type: {content_type}. Use {WAV_CONTENT_TYPE}.")

    settings = settings or get_settings()

    audio_bytes = ensure_mono_wav(audio_bytes)

    client = _get_speech_client()
    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=[settings.google_stt_language],
        model="latest_short",
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{settings.gcp_project}/locations/global/recognizers/_",
        config=config,
        content=audio_bytes,
    )

    response = client.recognize(request=request, timeout=settings.stt_timeout_seconds)

    if not response.results:
        return ""

    chunks = [result.alternatives[0].transcript for result in response.results if result.alternatives]
    return " ".join(chunks).strip()
