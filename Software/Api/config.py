from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
PROMPT_PATH = "utils/system_prompt.txt"

def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default

@dataclass(frozen=True)
class Settings:
    google_stt_language: str
    gcp_project: str
    gcp_location: str
    stt_timeout_seconds: float
    llm_model: str
    llm_timeout_seconds: float
    max_audio_bytes: int
    prompt_path: Path
    api_token: str

def get_settings() -> Settings:
    prompt_path = Path(PROMPT_PATH)

    return Settings(
        google_stt_language="ca-ES",
        gcp_project=os.getenv("GCP_PROJECT", ""),
        gcp_location=os.getenv("GCP_LOCATION", "europe-west1"),
        stt_timeout_seconds=15.0,
        llm_model="gemini-2.5-flash",
        llm_timeout_seconds=20.0,
        max_audio_bytes=_get_int("MAX_AUDIO_BYTES", 5 * 1024 * 1024),
        prompt_path=prompt_path,
        api_token=os.getenv("API_TOKEN", ""),
    )

def validate_settings(settings: Settings) -> list[str]:
    missing: list[str] = []
    if not settings.api_token:
        missing.append("API_TOKEN (must be set in Env Vars for auth)")
    if not settings.prompt_path.exists():
        missing.append(f"PROMPT_PATH ({settings.prompt_path})")
    if settings.max_audio_bytes <= 0:
        missing.append("MAX_AUDIO_BYTES (must be > 0)")
    return missing