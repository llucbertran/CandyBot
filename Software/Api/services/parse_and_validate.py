from __future__ import annotations
import json
from Software.Api.models import CandyBotResponse

def parse_llm_response(raw_text: str) -> CandyBotResponse:
    if not raw_text:
        raise ValueError("LLM returned empty response")

    cleaned = raw_text.strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("LLM response did not contain JSON")

    json_text = cleaned[start : end + 1]
    data = json.loads(json_text)

    return CandyBotResponse.model_validate(data)
