from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PageExtraction:
    """Structured facts extracted from one public webpage.

    The model intentionally stores raw, boring website facts instead of opinions.
    Reports and AI prompts are generated from this structured layer so users can
    inspect what the tool actually saw before trusting recommendations.
    """

    url: str
    final_url: str
    status_code: int
    content_type: str | None
    title: str | None
    title_length: int
    meta_description: str | None
    meta_description_length: int
    canonical_url: str | None
    meta_robots: str | None
    viewport: str | None
    html_lang: str | None
    h1: list[str] = field(default_factory=list)
    h2: list[str] = field(default_factory=list)
    h3: list[str] = field(default_factory=list)
    internal_links: list[str] = field(default_factory=list)
    external_links: list[str] = field(default_factory=list)
    broken_or_empty_links_count: int = 0
    images_count: int = 0
    images_missing_alt_count: int = 0
    images_with_lazy_loading_count: int = 0
    images_without_dimensions_count: int = 0
    forms_count: int = 0
    inputs_count: int = 0
    buttons_count: int = 0
    detected_ctas: list[str] = field(default_factory=list)
    open_graph: dict[str, str] = field(default_factory=dict)
    twitter_cards: dict[str, str] = field(default_factory=dict)
    schema_types: list[str] = field(default_factory=list)
    email_mentions: list[str] = field(default_factory=list)
    phone_mentions: list[str] = field(default_factory=list)
    word_count: int = 0
    paragraph_count: int = 0
    readable_text: str = ""
    text_to_html_ratio: float = 0.0
    page_size_bytes: int = 0
    load_time_ms: int | None = None
    has_cookie_banner_signal: bool = False
    has_privacy_signal: bool = False
    has_terms_signal: bool = False
    has_pricing_signal: bool = False
    has_testimonial_signal: bool = False
    has_faq_signal: bool = False
    technology_hints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SiteExtraction:
    """A collection of one or more extracted pages from the same website."""

    start_url: str
    pages: list[PageExtraction]
    crawl_errors: list[str] = field(default_factory=list)

    @property
    def primary_page(self) -> PageExtraction:
        if not self.pages:
            raise ValueError("SiteExtraction contains no pages")
        return self.pages[0]

    @property
    def total_word_count(self) -> int:
        return sum(page.word_count for page in self.pages)

    @property
    def unique_schema_types(self) -> list[str]:
        seen: list[str] = []
        for page in self.pages:
            for schema_type in page.schema_types:
                if schema_type not in seen:
                    seen.append(schema_type)
        return seen

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_url": self.start_url,
            "pages": [page.to_dict() for page in self.pages],
            "crawl_errors": self.crawl_errors,
            "total_word_count": self.total_word_count,
            "unique_schema_types": self.unique_schema_types,
        }


@dataclass
class AuditCheck:
    id: str
    category: str
    title: str
    status: str
    severity: str
    message: str
    recommendation: str
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuditScore:
    overall: int
    seo: int
    content: int
    ux: int
    accessibility: int
    trust: int
    performance: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass
class DeterministicAudit:
    score: AuditScore
    checks: list[AuditCheck]
    quick_wins: list[str]
    risk_flags: list[str]
    opportunities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score.to_dict(),
            "checks": [check.to_dict() for check in self.checks],
            "quick_wins": self.quick_wins,
            "risk_flags": self.risk_flags,
            "opportunities": self.opportunities,
        }


@dataclass
class AuditContext:
    extraction: SiteExtraction
    deterministic_audit: DeterministicAudit

    def to_dict(self) -> dict[str, Any]:
        return {
            "extraction": self.extraction.to_dict(),
            "deterministic_audit": self.deterministic_audit.to_dict(),
        }
