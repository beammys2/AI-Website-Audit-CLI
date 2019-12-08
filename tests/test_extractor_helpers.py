from bs4 import BeautifulSoup

from ai_website_audit.extractor import _detect_ctas, _extract_schema_types, _technology_hints


def test_detect_ctas_from_links_and_buttons():
    soup = BeautifulSoup('<a href="/contact">Contact us</a><button>Get started</button>', 'html.parser')
    assert _detect_ctas(soup) == ["Contact us", "Get started"]


def test_extract_schema_types_from_json_ld():
    html = '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization"}</script>'
    soup = BeautifulSoup(html, 'html.parser')
    assert _extract_schema_types(soup) == ["Organization"]


def test_technology_hints_detect_nextjs():
    assert "next.js" in _technology_hints('<script src="/_next/static/app.js"></script>')
