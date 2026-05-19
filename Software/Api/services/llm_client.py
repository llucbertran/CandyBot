from __future__ import annotations
import vertexai
from vertexai.generative_models import GenerativeModel
from config import Settings

_MODEL_INSTANCE = None

def _get_model(system_prompt: str, settings: Settings) -> GenerativeModel:
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        vertexai.init(project=settings.gcp_project, location=settings.gcp_location)
        _MODEL_INSTANCE = GenerativeModel(
            model_name=settings.llm_model,
            system_instruction=[system_prompt]
        )
    return _MODEL_INSTANCE

async def generate_instruction_json(system_prompt: str, user_text: str, settings: Settings) -> str:
    model = _get_model(system_prompt, settings)
    
    response = await model.generate_content_async(
        contents=[user_text],
        generation_config={
            "response_mime_type": "application/json",
        }
    )

    if not response.text:
        raise ValueError("LLM response did not contain text")
    
    return response.text.strip()