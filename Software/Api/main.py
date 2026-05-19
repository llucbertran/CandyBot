from __future__ import annotations
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile, status, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import ValidationError
from config import get_settings, validate_settings
from models import CandyBotResponse
from services.llm_client import generate_instruction_json
from services.parse_and_validate import parse_llm_response
from services.prompt_loader import load_system_prompt
from services.speech_to_text import transcribe_audio
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()
TRANSCRIPT_LOG_PATH = Path(__file__).resolve().parent / "transcripts.log"

@asynccontextmanager
async def lifespan(app: FastAPI):
    if missing := validate_settings(settings):
        raise RuntimeError(f"Missing settings: {', '.join(missing)}")
    app.state.system_prompt = load_system_prompt(settings.prompt_path)
    yield

app = FastAPI(title="CandyBot API", lifespan=lifespan)

@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "CandyBot API"}

api_key_header = APIKeyHeader(name="X-API-Token", auto_error=True)

def verify_token(api_key_header: str = Security(api_key_header)):
    if api_key_header != settings.api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Token",
        )
    return api_key_header

async def _process_audio(audio: UploadFile) -> str:
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or missing audio content type.")

    audio_bytes = await audio.read()
    if not audio_bytes or len(audio_bytes) > settings.max_audio_bytes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Audio file is empty or too large.")

    try:
        start_stt = time.perf_counter()
        transcript = transcribe_audio(audio_bytes, audio.content_type, settings)
        stt_duration = time.perf_counter() - start_stt
    except Exception as exc:
        logger.error(f"STT Error: {exc}")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Speech-to-text failed.") from exc

    transcript = transcript.strip()
    logger.info(f"[TIMING] Speech-to-Text completado en {stt_duration:.2f}s")
    return transcript

@app.post("/v1/command", response_model=CandyBotResponse, dependencies=[Depends(verify_token)])
async def command_from_audio(audio: UploadFile = File(...)) -> CandyBotResponse:
    start_total = time.perf_counter()
    transcript = await _process_audio(audio)

    if not transcript:
        logger.info("[INFO] Transcript buit, retornant nothing sense cridar el LLM")
        return CandyBotResponse(action="nothing", confidence=0.0, items=[])

    logger.info(f"[INFO] Transcript: {transcript}")

    try:
        start_llm = time.perf_counter()
        llm_text = await generate_instruction_json(app.state.system_prompt, transcript, settings)
        llm_duration = time.perf_counter() - start_llm
        logger.info(f"[INFO] LLM raw response: {llm_text}")
        result = parse_llm_response(llm_text)
        
        total_duration = time.perf_counter() - start_total
        logger.info(f"[TIMING] LLM Vertex AI completado en {llm_duration:.2f}s")
        logger.info(f"[TIMING] Peticion total completada en {total_duration:.2f}s")
        return result
    except (ValueError, ValidationError) as exc:
        logger.error(f"Validation Error: {exc}")
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "LLM response was invalid.") from exc
    except Exception as exc:
        logger.error(f"LLM Error: {exc}")
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "LLM request failed.") from exc
