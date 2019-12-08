from __future__ import annotations

import json
from pathlib import Path

from .models import AuditContext

ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR = ROOT / "prompts"


def load_prompt_template(language: str) -> str:
    language = language.lower()
    if language not in {"en", "de"}:
        raise ValueError("Supported languages are 'en' and 'de'")
    path = PROMPTS_DIR / f"audit_prompt_{language}.md"
    return path.read_text(encoding="utf-8")


def build_audit_prompt(context: AuditContext, language: str) -> str:
    template = load_prompt_template(language)
    data = json.dumps(context.to_dict(), ensure_ascii=False, indent=2)
    return template.replace("{{AUDIT_CONTEXT_JSON}}", data)
