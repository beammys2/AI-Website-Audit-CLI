import pytest

from ai_website_audit.utils import dedupe_keep_order, normalize_url, same_domain, slugify_url, truncate_text


def test_normalize_url_adds_https():
    assert normalize_url("example.com") == "https://example.com"


def test_normalize_url_rejects_invalid_scheme():
    with pytest.raises(ValueError):
        normalize_url("ftp://example.com")


def test_normalize_url_rejects_missing_domain():
    with pytest.raises(ValueError):
        normalize_url("https://localhost")


def test_slugify_url():
    assert slugify_url("https://www.example.com/about/us") == "www-example-com-about-us"


def test_truncate_text():
    text = "hello world " * 100
    shortened = truncate_text(text, 50)
    assert len(shortened) < len(text)
    assert "Content truncated" in shortened


def test_same_domain_ignores_www():
    assert same_domain("https://example.com", "https://www.example.com/about")


def test_dedupe_keep_order():
    assert dedupe_keep_order(["A", "b", "a", "B", "c"]) == ["A", "b", "c"]
