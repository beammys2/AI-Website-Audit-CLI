from __future__ import annotations

from dataclasses import asdict, dataclass
import time
from typing import Any

from .config import Settings

SYSTEM_INSTRUCTIONS = """You are a senior website auditor, technical SEO analyst, UX strategist,
accessibility reviewer, performance analyst, and conversion copywriter.

You receive structured extraction data and deterministic checks from a CLI tool.
Write a practical Markdown report grounded only in that evidence.

Rules:
- Do not invent facts that are not visible in the provided extraction.
- Separate confirmed findings from items requiring manual review.
- Prioritize recommendations by likely business impact and implementation effort.
- Include concrete copy/UX examples when the page text supports them.
- Be direct, specific, and useful for developers, freelancers, agencies, and SMBs.
- Avoid generic SEO advice unless it clearly applies to the extracted data.
"""

REASONING_MODEL_PREFIXES = ("gpt-5", "o1", "o3", "o4")


@dataclass(frozen=True)
class OpenAIReport:
    """AI report content plus call metadata saved for transparent audits."""

    content: str
    response_id: str | None
    model: str
    api: str
    usage: dict[str, Any]
    latency_ms: int
    reasoning_effort: str | None
    max_output_tokens: int
    store: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def generate_audit_with_openai(
    prompt: str,
    settings: Settings,
    model: str | None = None,
    reasoning_effort: str | None = None,
    max_output_tokens: int | None = None,
    store: bool | None = None,
) -> OpenAIReport:
    """Generate the AI audit report with OpenAI's Responses API.

    The Responses API is OpenAI's current unified interface for text generation,
    tool use, stateful responses, structured outputs, and reasoning-capable
    models. This function keeps the integration small and explicit so the repo
    is easy to audit and maintain.
    """
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file or run with --no-ai.")

    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("The openai package is not installed. Run: pip install -e .") from exc

    chosen_model = model or settings.openai_model
    chosen_reasoning = reasoning_effort if reasoning_effort is not None else settings.openai_reasoning_effort
    chosen_max_output = max_output_tokens or settings.openai_max_output_tokens
    chosen_store = settings.openai_store_responses if store is None else store

    client = OpenAI(api_key=settings.openai_api_key)
    request: dict[str, Any] = {
        "model": chosen_model,
        "instructions": SYSTEM_INSTRUCTIONS,
        "input": prompt,
        "max_output_tokens": chosen_max_output,
        "store": chosen_store,
        "metadata": {"project": "ai-website-audit-cli", "purpose": "website_audit"},
    }

    if settings.openai_service_tier:
        request["service_tier"] = settings.openai_service_tier

    if settings.openai_temperature is not None:
        request["temperature"] = settings.openai_temperature

    if _supports_reasoning(chosen_model) and chosen_reasoning:
        request["reasoning"] = {"effort": chosen_reasoning}

    start = time.perf_counter()
    response = client.responses.create(**request)
    latency_ms = int((time.perf_counter() - start) * 1000)

    content = _extract_response_text(response)
    if not content:
        raise RuntimeError("OpenAI returned an empty response")

    return OpenAIReport(
        content=content.strip(),
        response_id=getattr(response, "id", None),
        model=str(getattr(response, "model", chosen_model)),
        api="responses.create",
        usage=_usage_to_dict(getattr(response, "usage", None)),
        latency_ms=latency_ms,
        reasoning_effort=chosen_reasoning if _supports_reasoning(chosen_model) else None,
        max_output_tokens=chosen_max_output,
        store=chosen_store,
    )


def _supports_reasoning(model: str) -> bool:
    normalized = model.lower()
    return normalized.startswith(REASONING_MODEL_PREFIXES)


def _extract_response_text(response: Any) -> str:
    """Extract text from SDK response objects across minor SDK variations."""
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    chunks: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if isinstance(text, str):
                chunks.append(text)
    return "\n".join(chunks)


def _usage_to_dict(usage: Any) -> dict[str, Any]:
    if usage is None:
        return {}
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if hasattr(usage, "to_dict"):
        return usage.to_dict()
    if isinstance(usage, dict):
        return usage
    result: dict[str, Any] = {}
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        value = getattr(usage, key, None)
        if value is not None:
            result[key] = value
    return result
