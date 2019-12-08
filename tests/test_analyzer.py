from ai_website_audit.analyzer import run_deterministic_audit
from ai_website_audit.models import PageExtraction, SiteExtraction


def make_page(**overrides):
    data = dict(
        url="https://example.com",
        final_url="https://example.com",
        status_code=200,
        content_type="text/html",
        title="Example website audit landing page",
        title_length=34,
        meta_description="This is a useful example meta description for a website audit tool and its landing page.",
        meta_description_length=86,
        canonical_url="https://example.com",
        meta_robots=None,
        viewport="width=device-width, initial-scale=1",
        html_lang="en",
        h1=["Example Website Audit"],
        h2=["Features", "Pricing", "FAQ"],
        h3=[],
        internal_links=["https://example.com/about", "https://example.com/privacy", "https://example.com/terms"],
        external_links=[],
        broken_or_empty_links_count=0,
        images_count=2,
        images_missing_alt_count=0,
        images_with_lazy_loading_count=1,
        images_without_dimensions_count=0,
        forms_count=1,
        inputs_count=2,
        buttons_count=1,
        detected_ctas=["Get started"],
        open_graph={"og:title": "Example", "og:description": "Example", "og:image": "https://example.com/og.png"},
        twitter_cards={"twitter:card": "summary_large_image"},
        schema_types=["Organization"],
        email_mentions=["hello@example.com"],
        phone_mentions=[],
        word_count=500,
        paragraph_count=8,
        readable_text="Example content with FAQ, pricing and customer reviews.",
        text_to_html_ratio=12.0,
        page_size_bytes=120_000,
        load_time_ms=250,
        has_cookie_banner_signal=True,
        has_privacy_signal=True,
        has_terms_signal=True,
        has_pricing_signal=True,
        has_testimonial_signal=True,
        has_faq_signal=True,
        technology_hints=["next.js"],
    )
    data.update(overrides)
    return PageExtraction(**data)


def test_good_page_scores_high():
    site = SiteExtraction(start_url="https://example.com", pages=[make_page()])
    audit = run_deterministic_audit(site)
    assert audit.score.overall >= 85
    assert audit.score.performance >= 90
    assert not audit.risk_flags


def test_missing_h1_creates_fail():
    site = SiteExtraction(start_url="https://example.com", pages=[make_page(h1=[])])
    audit = run_deterministic_audit(site)
    ids = [check.id for check in audit.checks]
    assert "content.h1.missing" in ids
    assert audit.risk_flags


def test_missing_alt_text_reduces_accessibility_score():
    site = SiteExtraction(start_url="https://example.com", pages=[make_page(images_count=10, images_missing_alt_count=8)])
    audit = run_deterministic_audit(site)
    assert audit.score.accessibility < 100


def test_noindex_is_critical_risk():
    site = SiteExtraction(start_url="https://example.com", pages=[make_page(meta_robots="noindex,nofollow")])
    audit = run_deterministic_audit(site)
    assert "Page may be noindexed" in audit.risk_flags
    assert audit.score.seo < 90


def test_duplicate_titles_on_crawl_create_warning():
    page1 = make_page(final_url="https://example.com")
    page2 = make_page(url="https://example.com/about", final_url="https://example.com/about")
    site = SiteExtraction(start_url="https://example.com", pages=[page1, page2])
    audit = run_deterministic_audit(site)
    ids = [check.id for check in audit.checks]
    assert "seo.titles.duplicates" in ids
