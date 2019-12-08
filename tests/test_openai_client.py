from types import SimpleNamespace

from ai_website_audit.openai_client import _extract_response_text, _supports_reasoning, _usage_to_dict


def test_supports_reasoning_for_gpt5_models():
    assert _supports_reasoning("gpt-5.5")
    assert _supports_reasoning("gpt-5.4-mini")
    assert not _supports_reasoning("gpt-4.1-mini")


def test_extract_response_text_from_output_text():
    response = SimpleNamespace(output_text=" Report text ")
    assert _extract_response_text(response) == " Report text "


def test_extract_response_text_from_output_items():
    response = SimpleNamespace(
        output=[
            SimpleNamespace(content=[SimpleNamespace(text="Part one."), SimpleNamespace(text="Part two.")])
        ]
    )
    assert _extract_response_text(response) == "Part one.\nPart two."


def test_usage_to_dict_from_plain_object():
    usage = SimpleNamespace(input_tokens=10, output_tokens=20, total_tokens=30)
    assert _usage_to_dict(usage) == {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30}
