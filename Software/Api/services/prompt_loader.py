from __future__ import annotations
from pathlib import Path

def load_system_prompt(prompt_path: Path) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")
