from __future__ import annotations

from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_float(name: str, default: float | None) -> float | None:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return float(value)


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    openai_max_output_tokens: int
    openai_reasoning_effort: str | None
    openai_temperature: float | None
    openai_store_responses: bool
    openai_service_tier: str | None
    request_timeout_seconds: int
    user_agent: str


def get_settings() -> Settings:
    """Load runtime settings from environment variables.

    The default AI model intentionally uses OpenAI's current flagship model so
    the project demonstrates a real modern Responses API integration. Users who
    need lower latency or cost can switch OPENAI_MODEL to a smaller model.
    """
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        openai_max_output_tokens=int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "6000")),
        openai_reasoning_effort=os.getenv("OPENAI_REASONING_EFFORT", "medium"),
        openai_temperature=_get_float("OPENAI_TEMPERATURE", None),
        openai_store_responses=_get_bool("OPENAI_STORE_RESPONSES", False),
        openai_service_tier=os.getenv("OPENAI_SERVICE_TIER", "auto"),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20")),
        user_agent=os.getenv(
            "USER_AGENT",
            "AIWebsiteAuditCLI/1.0.0 (+https://github.com/YOUR_USERNAME/ai-website-audit-cli)",
        ),
    )
