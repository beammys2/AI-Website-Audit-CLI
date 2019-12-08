import os

from ai_website_audit.config import get_settings


def test_default_openai_settings(monkeypatch):
    for key in [
        "OPENAI_MODEL",
        "OPENAI_MAX_OUTPUT_TOKENS",
        "OPENAI_REASONING_EFFORT",
        "OPENAI_STORE_RESPONSES",
        "OPENAI_SERVICE_TIER",
        "OPENAI_TEMPERATURE",
    ]:
        monkeypatch.delenv(key, raising=False)
    settings = get_settings()
    assert settings.openai_model == "gpt-5.5"
    assert settings.openai_max_output_tokens == 6000
    assert settings.openai_reasoning_effort == "medium"
    assert settings.openai_store_responses is False
    assert settings.openai_service_tier == "auto"
    assert settings.openai_temperature is None
