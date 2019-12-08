from __future__ import annotations

import json
import re
import time
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .config import Settings
from .models import PageExtraction, SiteExtraction
from .utils import dedupe_keep_order, normalize_url, same_domain, truncate_text

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s()./-]{7,}\d)")
WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)
CTA_HINTS = (
    "contact", "book", "demo", "start", "buy", "shop", "subscribe", "sign up", "get started",
    "try", "quote", "pricing", "call", "download", "learn more", "kontakt", "anfragen", "buchen",
    "demo", "starten", "kaufen", "abo", "termin", "angebot", "preise", "kostenlos", "mehr erfahren",
)
PRIVACY_HINTS = ("privacy", "datenschutz", "gdpr", "dsgvo")
TERMS_HINTS = ("terms", "agb", "impressum", "legal", "imprint")
PRICING_HINTS = ("pricing", "preise", "plans", "pakete", "angebote", "kosten")
TESTIMONIAL_HINTS = ("testimonial", "review", "bewertungen", "kunden", "referenzen", "case study")
FAQ_HINTS = ("faq", "frequently asked", "häufige fragen", "fragen")
COOKIE_HINTS = ("cookie", "cookies", "consent", "einwilligung")

TECH_HINTS = {
    "wordpress": ("wp-content", "wp-json", "woocommerce"),
    "shopify": ("cdn.shopify.com", "shopify"),
    "webflow": ("webflow.js", "webflow"),
    "wix": ("wixstatic.com", "wix.com"),
    "squarespace": ("squarespace",),
    "next.js": ("__next", "next/static"),
    "react": ("react", "react-dom"),
    "gtm": ("googletagmanager.com", "gtm.js"),
    "google-analytics": ("google-analytics.com", "gtag/js"),
}


def fetch_html(url: str, settings: Settings) -> tuple[str, str, int, str | None, int | None, int]:
    normalized = normalize_url(url)
    started = time.perf_counter()
    response = requests.get(
        normalized,
        timeout=settings.request_timeout_seconds,
        headers={"User-Agent": settings.user_agent, "Accept": "text/html,application/xhtml+xml"},
        allow_redirects=True,
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    response.raise_for_status()
    return (
        response.text,
        response.url,
        response.status_code,
        response.headers.get("content-type"),
        elapsed_ms,
        len(response.content),
    )


def extract_site(
    url: str,
    settings: Settings,
    *,
    max_chars: int = 12000,
    crawl: bool = False,
    max_pages: int = 1,
) -> SiteExtraction:
    """Extract one website. If crawl=True, follow a small number of same-domain links.

    The crawler is intentionally conservative: breadth-first, same-domain only,
    no asset downloads, no form submission, and a small max_pages default.
    """
    start = normalize_url(url)
    to_visit = [start]
    visited: set[str] = set()
    pages: list[PageExtraction] = []
    crawl_errors: list[str] = []

    while to_visit and len(pages) < max(1, max_pages):
        current = urldefrag(to_visit.pop(0))[0]
        if current in visited:
            continue
        visited.add(current)
        try:
            page = extract_page(current, settings, max_chars=max_chars)
        except Exception as exc:  # keep crawl useful even when one page fails
            crawl_errors.append(f"{current}: {exc}")
            continue
        pages.append(page)

        if crawl:
            for link in _rank_internal_links(page.internal_links):
                clean = urldefrag(link)[0]
                if clean not in visited and clean not in to_visit and same_domain(start, clean):
                    to_visit.append(clean)

    if not pages:
        joined = "; ".join(crawl_errors) or "No pages could be fetched."
        raise RuntimeError(joined)

    return SiteExtraction(start_url=start, pages=pages, crawl_errors=crawl_errors)


def extract_page(url: str, settings: Settings, max_chars: int = 12000) -> PageExtraction:
    html, final_url, status_code, content_type, load_time_ms, page_size_bytes = fetch_html(url, settings)
    soup = BeautifulSoup(html, "html.parser")

    html_tag = soup.find("html")
    html_lang = html_tag.get("lang", "").strip() if html_tag else None

    title = soup.title.string.strip() if soup.title and soup.title.string else None
    meta_description = _meta_content(soup, name="description")
    canonical_url = _canonical_url(soup, final_url)
    meta_robots = _meta_content(soup, name="robots")
    viewport = _meta_content(soup, name="viewport")
    open_graph = _meta_map(soup, attr="property", prefix="og:")
    twitter_cards = _meta_map(soup, attr="name", prefix="twitter:")
    schema_types = _extract_schema_types(soup)

    headings = {
        "h1": _clean_list([h.get_text(" ", strip=True) for h in soup.find_all("h1")]),
        "h2": _clean_list([h.get_text(" ", strip=True) for h in soup.find_all("h2")]),
        "h3": _clean_list([h.get_text(" ", strip=True) for h in soup.find_all("h3")]),
    }

    internal_links, external_links, broken_or_empty = _extract_links(soup, final_url)
    images = soup.find_all("img")
    missing_alt = [img for img in images if not (img.get("alt") or "").strip()]
    lazy_images = [img for img in images if (img.get("loading") or "").lower() == "lazy"]
    images_without_dimensions = [img for img in images if not img.get("width") or not img.get("height")]
    forms_count = len(soup.find_all("form"))
    inputs_count = len(soup.find_all(["input", "textarea", "select"]))
    buttons_count = len(soup.find_all(["button"]))
    detected_ctas = _detect_ctas(soup)
    technology_hints = _technology_hints(html)

    html_lower = html.lower()
    has_cookie_banner_signal = any(hint in html_lower for hint in COOKIE_HINTS)
    link_text_blob = " ".join(a.get_text(" ", strip=True).lower() for a in soup.find_all("a"))
    full_signal_blob = f"{html_lower} {link_text_blob}"

    for tag in soup(["script", "style", "noscript", "svg", "canvas", "iframe", "template"]):
        tag.decompose()

    readable_text = _readable_text(soup)
    emails = dedupe_keep_order(EMAIL_RE.findall(readable_text))[:20]
    phones = dedupe_keep_order([m.strip() for m in PHONE_RE.findall(readable_text)])[:20]
    words = WORD_RE.findall(readable_text)
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p") if p.get_text(" ", strip=True)]
    truncated_text = truncate_text(readable_text, max_chars)
    text_ratio = round((len(readable_text) / max(len(html), 1)) * 100, 2)

    return PageExtraction(
        url=normalize_url(url),
        final_url=final_url,
        status_code=status_code,
        content_type=content_type,
        title=title,
        title_length=len(title or ""),
        meta_description=meta_description,
        meta_description_length=len(meta_description or ""),
        canonical_url=canonical_url,
        meta_robots=meta_robots,
        viewport=viewport,
        html_lang=html_lang,
        h1=headings["h1"],
        h2=headings["h2"],
        h3=headings["h3"],
        internal_links=internal_links[:300],
        external_links=external_links[:300],
        broken_or_empty_links_count=broken_or_empty,
        images_count=len(images),
        images_missing_alt_count=len(missing_alt),
        images_with_lazy_loading_count=len(lazy_images),
        images_without_dimensions_count=len(images_without_dimensions),
        forms_count=forms_count,
        inputs_count=inputs_count,
        buttons_count=buttons_count,
        detected_ctas=detected_ctas,
        open_graph=open_graph,
        twitter_cards=twitter_cards,
        schema_types=schema_types,
        email_mentions=emails,
        phone_mentions=phones,
        word_count=len(words),
        paragraph_count=len(paragraphs),
        readable_text=truncated_text,
        text_to_html_ratio=text_ratio,
        page_size_bytes=page_size_bytes,
        load_time_ms=load_time_ms,
        has_cookie_banner_signal=has_cookie_banner_signal,
        has_privacy_signal=any(hint in full_signal_blob for hint in PRIVACY_HINTS),
        has_terms_signal=any(hint in full_signal_blob for hint in TERMS_HINTS),
        has_pricing_signal=any(hint in full_signal_blob for hint in PRICING_HINTS),
        has_testimonial_signal=any(hint in full_signal_blob for hint in TESTIMONIAL_HINTS),
        has_faq_signal=any(hint in full_signal_blob for hint in FAQ_HINTS),
        technology_hints=technology_hints,
    )


def extract_website(url: str, settings: Settings, max_chars: int = 12000) -> PageExtraction:
    """Backward-compatible single-page extraction."""
    return extract_page(url, settings, max_chars=max_chars)


def _rank_internal_links(links: list[str]) -> list[str]:
    priority_words = ("about", "service", "pricing", "contact", "case", "blog", "faq", "leistungen", "preise", "kontakt", "referenz")

    def score(link: str) -> tuple[int, int, str]:
        lower = link.lower()
        priority = 0 if any(word in lower for word in priority_words) else 1
        depth = urlparse(link).path.count("/")
        return priority, depth, link

    return sorted(links, key=score)


def _meta_content(soup: BeautifulSoup, *, name: str) -> str | None:
    tag = soup.find("meta", attrs={"name": re.compile(f"^{re.escape(name)}$", re.I)})
    content = tag.get("content", "").strip() if tag else ""
    return content or None


def _canonical_url(soup: BeautifulSoup, base_url: str) -> str | None:
    tag = soup.find("link", rel=lambda value: value and "canonical" in value)
    href = tag.get("href", "").strip() if tag else ""
    return urljoin(base_url, href) if href else None


def _meta_map(soup: BeautifulSoup, *, attr: str, prefix: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for tag in soup.find_all("meta"):
        key = (tag.get(attr) or "").strip()
        content = (tag.get("content") or "").strip()
        if key.lower().startswith(prefix) and content:
            values[key] = content
    return values


def _extract_schema_types(soup: BeautifulSoup) -> list[str]:
    types: list[str] = []
    for script in soup.find_all("script", attrs={"type": re.compile("ld\\+json", re.I)}):
        raw = script.string or script.get_text() or ""
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        _collect_schema_types(data, types)
    return dedupe_keep_order(types)[:30]


def _collect_schema_types(data: object, types: list[str]) -> None:
    if isinstance(data, dict):
        value = data.get("@type")
        if isinstance(value, str):
            types.append(value)
        elif isinstance(value, list):
            types.extend(str(v) for v in value)
        for child in data.values():
            _collect_schema_types(child, types)
    elif isinstance(data, list):
        for item in data:
            _collect_schema_types(item, types)


def _extract_links(soup: BeautifulSoup, base_url: str) -> tuple[list[str], list[str], int]:
    internal: list[str] = []
    external: list[str] = []
    broken_or_empty = 0
    base_domain = urlparse(base_url).netloc.lower().removeprefix("www.")

    for anchor in soup.find_all("a"):
        href = (anchor.get("href") or "").strip()
        if not href or href == "#" or href.lower().startswith(("javascript:", "mailto:", "tel:")):
            broken_or_empty += 1 if not href or href == "#" or href.lower().startswith("javascript:") else 0
            continue
        absolute = urljoin(base_url, href)
        absolute = urldefrag(absolute)[0]
        domain = urlparse(absolute).netloc.lower().removeprefix("www.")
        if not domain:
            broken_or_empty += 1
        elif domain == base_domain:
            internal.append(absolute)
        else:
            external.append(absolute)
    return dedupe_keep_order(internal), dedupe_keep_order(external), broken_or_empty


def _detect_ctas(soup: BeautifulSoup) -> list[str]:
    candidates: list[str] = []
    for tag in soup.find_all(["a", "button"]):
        text = tag.get_text(" ", strip=True)
        if not text or len(text) > 90:
            continue
        lower = text.lower()
        href = (tag.get("href") or "").lower()
        if any(hint in lower or hint in href for hint in CTA_HINTS):
            candidates.append(text)
    return dedupe_keep_order(candidates)[:30]


def _technology_hints(html: str) -> list[str]:
    lower = html.lower()
    found: list[str] = []
    for name, hints in TECH_HINTS.items():
        if any(hint in lower for hint in hints):
            found.append(name)
    return found


def _readable_text(soup: BeautifulSoup) -> str:
    text = soup.get_text("\n", strip=True)
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def _clean_list(items: list[str]) -> list[str]:
    return dedupe_keep_order([re.sub(r"\s+", " ", item).strip() for item in items if item.strip()])
