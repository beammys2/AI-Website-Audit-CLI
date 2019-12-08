from __future__ import annotations

from .models import AuditCheck, AuditScore, DeterministicAudit, PageExtraction, SiteExtraction


def run_deterministic_audit(site: SiteExtraction) -> DeterministicAudit:
    """Run deterministic checks that do not require an LLM.

    These checks are deliberately transparent. They are not a replacement for
    human SEO/UX judgment, but they create a useful baseline and high-signal
    context for the AI-generated report.
    """
    checks: list[AuditCheck] = []
    page = site.primary_page

    checks.extend([
        _title_check(page),
        _meta_description_check(page),
        _h1_check(page),
        _heading_depth_check(page),
        _viewport_check(page),
        _canonical_check(page),
        _robots_check(page),
        _alt_text_check(page),
        _image_dimension_check(page),
        _cta_check(page),
        _word_count_check(page),
        _paragraph_check(page),
        _og_check(page),
        _twitter_check(page),
        _schema_check(page),
        _contact_check(page),
        _trust_policy_check(page),
        _language_check(page),
        _performance_weight_check(page),
        _load_time_check(page),
        _text_ratio_check(page),
        _faq_check(page),
        _social_proof_check(page),
    ])

    if len(site.pages) > 1:
        checks.append(_multi_page_check(site))
        checks.extend(_cross_page_checks(site))

    score = _score(checks)
    quick_wins = _quick_wins(checks)
    risk_flags = [check.title for check in checks if check.severity in {"high", "critical"} and check.status == "fail"]
    opportunities = _opportunities(site, checks)
    return DeterministicAudit(score=score, checks=checks, quick_wins=quick_wins, risk_flags=risk_flags, opportunities=opportunities)


def _check(
    id: str,
    category: str,
    title: str,
    status: str,
    severity: str,
    message: str,
    recommendation: str,
    evidence: list[str] | None = None,
) -> AuditCheck:
    return AuditCheck(
        id=id,
        category=category,
        title=title,
        status=status,
        severity=severity,
        message=message,
        recommendation=recommendation,
        evidence=evidence or [],
    )


def _title_check(page: PageExtraction) -> AuditCheck:
    if not page.title:
        return _check("seo.title.missing", "SEO", "Missing page title", "fail", "high", "No <title> tag was found.", "Add a clear page title around 35-60 characters.")
    if page.title_length < 25:
        return _check("seo.title.short", "SEO", "Page title may be too short", "warn", "medium", f"Title length is {page.title_length} characters.", "Expand the title so it communicates offer, brand, and search intent.", [page.title])
    if page.title_length > 65:
        return _check("seo.title.long", "SEO", "Page title may be too long", "warn", "medium", f"Title length is {page.title_length} characters.", "Shorten the title to reduce truncation in search results.", [page.title])
    return _check("seo.title.ok", "SEO", "Page title is present", "pass", "low", f"Title length is {page.title_length} characters.", "Keep monitoring title relevance when content changes.", [page.title])


def _meta_description_check(page: PageExtraction) -> AuditCheck:
    if not page.meta_description:
        return _check("seo.meta.missing", "SEO", "Missing meta description", "fail", "high", "No meta description was found.", "Add a compelling 120-160 character meta description with a value proposition and CTA.")
    if page.meta_description_length < 80:
        return _check("seo.meta.short", "SEO", "Meta description may be too short", "warn", "medium", f"Meta description length is {page.meta_description_length} characters.", "Add more specific benefits and search context.", [page.meta_description])
    if page.meta_description_length > 170:
        return _check("seo.meta.long", "SEO", "Meta description may be too long", "warn", "medium", f"Meta description length is {page.meta_description_length} characters.", "Shorten it so the most important copy is not truncated.", [page.meta_description])
    return _check("seo.meta.ok", "SEO", "Meta description is present", "pass", "low", f"Meta description length is {page.meta_description_length} characters.", "Keep it aligned with the page promise.", [page.meta_description])


def _h1_check(page: PageExtraction) -> AuditCheck:
    if len(page.h1) == 0:
        return _check("content.h1.missing", "Content", "Missing H1", "fail", "high", "No H1 heading was found.", "Add one descriptive H1 that explains the page offer clearly.")
    if len(page.h1) > 1:
        return _check("content.h1.multiple", "Content", "Multiple H1 headings", "warn", "medium", f"Found {len(page.h1)} H1 headings.", "Use one primary H1 and structure subtopics with H2/H3 headings.", page.h1[:5])
    return _check("content.h1.ok", "Content", "Single H1 found", "pass", "low", f"H1: {page.h1[0]}", "Make sure the H1 matches the search and conversion intent.", page.h1[:1])


def _heading_depth_check(page: PageExtraction) -> AuditCheck:
    if page.h1 and not page.h2 and page.word_count > 400:
        return _check("content.headings.thin", "Content", "Content lacks H2 structure", "warn", "medium", "The page has substantial text but no H2 headings.", "Break long pages into scannable sections with descriptive H2 headings.")
    return _check("content.headings.ok", "Content", "Heading structure is usable", "pass", "low", f"Found {len(page.h1)} H1, {len(page.h2)} H2 and {len(page.h3)} H3 headings.", "Keep headings descriptive rather than decorative.")


def _viewport_check(page: PageExtraction) -> AuditCheck:
    if not page.viewport:
        return _check("ux.viewport.missing", "UX", "Missing viewport meta tag", "fail", "high", "No responsive viewport meta tag was found.", "Add <meta name='viewport' content='width=device-width, initial-scale=1'>.")
    return _check("ux.viewport.ok", "UX", "Viewport meta tag present", "pass", "low", page.viewport, "Keep testing mobile layouts on real devices.")


def _canonical_check(page: PageExtraction) -> AuditCheck:
    if not page.canonical_url:
        return _check("seo.canonical.missing", "SEO", "Missing canonical URL", "warn", "medium", "No canonical link was found.", "Add a canonical link to reduce duplicate-content ambiguity.")
    return _check("seo.canonical.ok", "SEO", "Canonical URL present", "pass", "low", page.canonical_url, "Ensure the canonical points to the intended indexable URL.", [page.canonical_url])


def _robots_check(page: PageExtraction) -> AuditCheck:
    if page.meta_robots and "noindex" in page.meta_robots.lower():
        return _check("seo.robots.noindex", "SEO", "Page may be noindexed", "fail", "critical", f"Meta robots contains: {page.meta_robots}", "Remove noindex if this page should appear in search results.")
    if page.meta_robots:
        return _check("seo.robots.present", "SEO", "Robots directive present", "pass", "low", f"Meta robots: {page.meta_robots}", "Verify the directive matches the intended indexing strategy.")
    return _check("seo.robots.default", "SEO", "No robots meta override", "pass", "low", "No page-level robots override was detected.", "No action required unless you need explicit indexing rules.")


def _alt_text_check(page: PageExtraction) -> AuditCheck:
    if page.images_count == 0:
        return _check("accessibility.images.none", "Accessibility", "No images detected", "pass", "low", "No image alt-text issues detected because no images were found.", "If images are added later, include meaningful alt text.")
    ratio = page.images_missing_alt_count / page.images_count
    if ratio > 0.5:
        return _check("accessibility.alt.many_missing", "Accessibility", "Many images missing alt text", "fail", "high", f"{page.images_missing_alt_count}/{page.images_count} images are missing alt text.", "Add descriptive alt text for meaningful images and empty alt for decorative images.")
    if page.images_missing_alt_count > 0:
        return _check("accessibility.alt.some_missing", "Accessibility", "Some images missing alt text", "warn", "medium", f"{page.images_missing_alt_count}/{page.images_count} images are missing alt text.", "Review image alt attributes and fix priority images first.")
    return _check("accessibility.alt.ok", "Accessibility", "Image alt text looks complete", "pass", "low", f"All {page.images_count} images include alt attributes.", "Keep alt text concise and useful.")


def _image_dimension_check(page: PageExtraction) -> AuditCheck:
    if page.images_count == 0:
        return _check("performance.images.none", "Performance", "No image dimension issues", "pass", "low", "No images detected.", "No action required.")
    if page.images_without_dimensions_count > page.images_count * 0.7:
        return _check("performance.images.dimensions", "Performance", "Most images lack dimensions", "warn", "medium", f"{page.images_without_dimensions_count}/{page.images_count} images have no width/height attributes.", "Add dimensions or CSS aspect-ratio to reduce layout shifts.")
    return _check("performance.images.dimensions_ok", "Performance", "Image dimensions look acceptable", "pass", "low", f"{page.images_without_dimensions_count}/{page.images_count} images lack explicit dimensions.", "Continue optimizing image layout stability.")


def _cta_check(page: PageExtraction) -> AuditCheck:
    if not page.detected_ctas and page.forms_count == 0:
        return _check("conversion.cta.missing", "Conversion", "No obvious CTA detected", "fail", "high", "No CTA-like button/link or form was detected.", "Add a clear primary CTA above the fold and repeat it near key decision points.")
    return _check("conversion.cta.ok", "Conversion", "CTA or form detected", "pass", "low", f"Detected CTAs: {', '.join(page.detected_ctas[:5]) or 'form present'}", "Make sure the primary CTA is visually prominent and benefit-oriented.", page.detected_ctas[:5])


def _word_count_check(page: PageExtraction) -> AuditCheck:
    if page.word_count < 150:
        return _check("content.word_count.low", "Content", "Very little readable content", "warn", "medium", f"Only about {page.word_count} words were extracted.", "Add clearer sections explaining the offer, benefits, trust proof, and next steps.")
    if page.word_count > 2500 and len(page.h2) < 4:
        return _check("content.word_count.dense", "Content", "Long page may need stronger structure", "warn", "medium", f"About {page.word_count} words were extracted but only {len(page.h2)} H2 headings were found.", "Add stronger sectioning, summaries, jump links, or conversion breaks.")
    return _check("content.word_count.ok", "Content", "Readable content found", "pass", "low", f"About {page.word_count} words were extracted.", "Keep copy scannable and focused.")


def _paragraph_check(page: PageExtraction) -> AuditCheck:
    if page.word_count > 300 and page.paragraph_count < 3:
        return _check("content.paragraphs.low", "Content", "Copy may not be paragraph-structured", "warn", "medium", f"Only {page.paragraph_count} paragraphs were detected.", "Use short paragraphs and bullets to improve scanning.")
    return _check("content.paragraphs.ok", "Content", "Paragraph structure detected", "pass", "low", f"Detected {page.paragraph_count} paragraphs.", "Keep paragraphs short and conversion-oriented.")


def _og_check(page: PageExtraction) -> AuditCheck:
    required = {"og:title", "og:description", "og:image"}
    missing = required - set(page.open_graph)
    if missing:
        return _check("social.og.incomplete", "Social", "Open Graph metadata incomplete", "warn", "medium", f"Missing: {', '.join(sorted(missing))}.", "Add Open Graph tags so shared links look credible on social platforms.")
    return _check("social.og.ok", "Social", "Open Graph metadata present", "pass", "low", "Core Open Graph tags were found.", "Keep social previews updated when positioning changes.")


def _twitter_check(page: PageExtraction) -> AuditCheck:
    if not page.twitter_cards:
        return _check("social.twitter.missing", "Social", "Twitter/X card metadata missing", "warn", "low", "No twitter:* meta tags were detected.", "Add Twitter/X card tags if social sharing matters for this page.")
    return _check("social.twitter.ok", "Social", "Twitter/X card metadata present", "pass", "low", f"Detected {len(page.twitter_cards)} Twitter card fields.", "Preview social cards after major content updates.")


def _schema_check(page: PageExtraction) -> AuditCheck:
    if not page.schema_types:
        return _check("seo.schema.missing", "SEO", "No structured data detected", "warn", "medium", "No JSON-LD schema types were detected.", "Consider adding Organization, WebSite, LocalBusiness, Product, FAQPage, or Article schema where relevant.")
    return _check("seo.schema.ok", "SEO", "Structured data detected", "pass", "low", f"Detected schema: {', '.join(page.schema_types[:8])}.", "Validate structured data after changes.", page.schema_types[:8])


def _contact_check(page: PageExtraction) -> AuditCheck:
    if page.email_mentions or page.phone_mentions or page.forms_count > 0:
        return _check("trust.contact.ok", "Trust", "Contact path detected", "pass", "low", "Email, phone, or form detected.", "Make contact options easy to find and connect them to the CTA path.")
    return _check("trust.contact.missing", "Trust", "No contact path detected", "warn", "medium", "No email, phone, or form was detected in extracted text.", "Add a clear contact path or dedicated contact CTA.")


def _trust_policy_check(page: PageExtraction) -> AuditCheck:
    missing = []
    if not page.has_privacy_signal:
        missing.append("privacy")
    if not page.has_terms_signal:
        missing.append("legal/terms")
    if missing:
        return _check("trust.policies.missing", "Trust", "Legal/trust signals may be incomplete", "warn", "medium", f"Missing signals: {', '.join(missing)}.", "Add visible privacy/legal links, especially for business, SaaS, ecommerce, or lead-gen pages.")
    return _check("trust.policies.ok", "Trust", "Basic legal/trust links detected", "pass", "low", "Privacy and legal/terms-like signals were found.", "Keep trust links visible in footer and checkout/contact flows.")


def _language_check(page: PageExtraction) -> AuditCheck:
    if not page.html_lang:
        return _check("accessibility.lang.missing", "Accessibility", "Missing HTML language attribute", "warn", "medium", "The <html lang> attribute was not found.", "Set the page language, for example <html lang='en'> or <html lang='de'>.")
    return _check("accessibility.lang.ok", "Accessibility", "HTML language attribute present", "pass", "low", f"html lang='{page.html_lang}'.", "Ensure language switches are marked correctly on multilingual pages.")


def _performance_weight_check(page: PageExtraction) -> AuditCheck:
    if page.page_size_bytes > 1_500_000:
        return _check("performance.weight.large", "Performance", "HTML response is heavy", "warn", "medium", f"HTML response size is about {round(page.page_size_bytes / 1024)} KB.", "Reduce inline scripts/styles, remove unused markup, and defer non-critical resources.")
    return _check("performance.weight.ok", "Performance", "HTML response size is reasonable", "pass", "low", f"HTML response size is about {round(page.page_size_bytes / 1024)} KB.", "Audit full page weight with Lighthouse for assets not downloaded by this CLI.")


def _load_time_check(page: PageExtraction) -> AuditCheck:
    if page.load_time_ms is None:
        return _check("performance.timing.unknown", "Performance", "Fetch timing unavailable", "warn", "low", "No fetch timing was recorded.", "Run again or use Lighthouse/WebPageTest for deeper timing.")
    if page.load_time_ms > 2500:
        return _check("performance.timing.slow", "Performance", "Initial HTML fetch is slow", "warn", "medium", f"Initial HTML fetch took {page.load_time_ms} ms.", "Check hosting, caching, redirects, and server-side rendering latency.")
    return _check("performance.timing.ok", "Performance", "Initial HTML fetch looks acceptable", "pass", "low", f"Initial HTML fetch took {page.load_time_ms} ms.", "Use browser-based tools for full Core Web Vitals validation.")


def _text_ratio_check(page: PageExtraction) -> AuditCheck:
    if page.text_to_html_ratio < 3 and page.word_count < 250:
        return _check("content.text_ratio.low", "Content", "Low visible-text signal", "warn", "medium", f"Text-to-HTML ratio is {page.text_to_html_ratio}% with {page.word_count} words.", "Ensure important copy is server-rendered and visible to users/search engines.")
    return _check("content.text_ratio.ok", "Content", "Visible-text signal looks usable", "pass", "low", f"Text-to-HTML ratio is {page.text_to_html_ratio}%.", "Keep critical copy accessible without requiring complex client-side interactions.")


def _faq_check(page: PageExtraction) -> AuditCheck:
    if page.has_faq_signal:
        return _check("conversion.faq.ok", "Conversion", "FAQ signal detected", "pass", "low", "FAQ-like content or links were detected.", "Use FAQs to remove objections near conversion points.")
    return _check("conversion.faq.missing", "Conversion", "No FAQ signal detected", "warn", "low", "No FAQ-like signal was detected.", "Consider adding FAQs if visitors need reassurance before contacting or buying.")


def _social_proof_check(page: PageExtraction) -> AuditCheck:
    if page.has_testimonial_signal:
        return _check("trust.social_proof.ok", "Trust", "Social proof signal detected", "pass", "low", "Testimonials/reviews/reference-like signals were detected.", "Keep social proof specific, credible, and close to CTAs.")
    return _check("trust.social_proof.missing", "Trust", "No social proof signal detected", "warn", "low", "No testimonial/review/reference-like signal was detected.", "Add proof such as logos, results, testimonials, reviews, or case studies.")


def _multi_page_check(site: SiteExtraction) -> AuditCheck:
    return _check("crawl.multi_page.ok", "Crawl", "Multiple pages sampled", "pass", "low", f"Sampled {len(site.pages)} pages from the same domain.", "Use this sample to find repeated template-level issues.")


def _cross_page_checks(site: SiteExtraction) -> list[AuditCheck]:
    checks: list[AuditCheck] = []
    titles = [p.title for p in site.pages if p.title]
    if len(titles) != len(set(titles)):
        checks.append(_check("seo.titles.duplicates", "SEO", "Duplicate titles across sampled pages", "warn", "medium", "At least two sampled pages share the same title.", "Make titles unique by matching each page's intent.", titles))
    descriptions = [p.meta_description for p in site.pages if p.meta_description]
    if len(descriptions) != len(set(descriptions)):
        checks.append(_check("seo.meta.duplicates", "SEO", "Duplicate meta descriptions across sampled pages", "warn", "medium", "At least two sampled pages share the same meta description.", "Write unique descriptions for important pages.", descriptions[:5]))
    if site.crawl_errors:
        checks.append(_check("crawl.errors", "Crawl", "Some pages failed during crawl", "warn", "low", f"{len(site.crawl_errors)} crawl errors were recorded.", "Review crawl errors to find blocked or broken internal pages.", site.crawl_errors[:5]))
    return checks


def _score(checks: list[AuditCheck]) -> AuditScore:
    weights = {"critical": 28, "high": 18, "medium": 9, "low": 3}
    category_penalties = {
        "SEO": 0,
        "Content": 0,
        "UX": 0,
        "Accessibility": 0,
        "Trust": 0,
        "Conversion": 0,
        "Social": 0,
        "Crawl": 0,
        "Performance": 0,
    }
    for check in checks:
        if check.status == "fail":
            category_penalties[check.category] = category_penalties.get(check.category, 0) + weights[check.severity]
        elif check.status == "warn":
            category_penalties[check.category] = category_penalties.get(check.category, 0) + weights[check.severity] // 2

    def cat_score(*cats: str) -> int:
        penalty = sum(category_penalties.get(cat, 0) for cat in cats)
        return max(0, min(100, 100 - penalty))

    seo = cat_score("SEO", "Social")
    content = cat_score("Content")
    ux = cat_score("UX", "Conversion")
    accessibility = cat_score("Accessibility")
    trust = cat_score("Trust")
    performance = cat_score("Performance")
    overall = round((seo * 0.24) + (content * 0.18) + (ux * 0.20) + (accessibility * 0.12) + (trust * 0.14) + (performance * 0.12))
    return AuditScore(overall=overall, seo=seo, content=content, ux=ux, accessibility=accessibility, trust=trust, performance=performance)


def _quick_wins(checks: list[AuditCheck]) -> list[str]:
    priority = [c for c in checks if c.status in {"fail", "warn"}]
    priority.sort(key=lambda c: {"critical": 0, "high": 1, "medium": 2, "low": 3}[c.severity])
    return [f"{c.title}: {c.recommendation}" for c in priority[:10]]


def _opportunities(site: SiteExtraction, checks: list[AuditCheck]) -> list[str]:
    page = site.primary_page
    opportunities: list[str] = []
    if not page.has_pricing_signal:
        opportunities.append("Clarify pricing, packages, or next-step expectations if this is a commercial page.")
    if not page.has_faq_signal:
        opportunities.append("Add an FAQ section to address common objections and improve long-tail search coverage.")
    if not page.schema_types:
        opportunities.append("Add structured data that matches the page type, such as Organization, LocalBusiness, Product, FAQPage, or Article.")
    if page.forms_count > 0 and not page.has_privacy_signal:
        opportunities.append("Add visible privacy/GDPR reassurance near forms to improve trust.")
    failed_high = [c for c in checks if c.status == "fail" and c.severity in {"high", "critical"}]
    if failed_high:
        opportunities.append("Fix high-severity technical basics before spending time on small copy improvements.")
    return opportunities[:8]
