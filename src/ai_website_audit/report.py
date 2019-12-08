from __future__ import annotations

import html
import json
from pathlib import Path

from .models import AuditContext, PageExtraction, SiteExtraction
from .utils import ensure_directory, slugify_url, utc_timestamp


def build_local_report(context: AuditContext, language: str) -> str:
    site = context.extraction
    audit = context.deterministic_audit
    page = site.primary_page
    labels = _labels(language)
    return f"""# {labels['title']}

**{labels['start_url']}:** {site.start_url}  
**{labels['final_url']}:** {page.final_url}  
**{labels['generated']}:** {utc_timestamp()}  
**{labels['pages_checked']}:** {len(site.pages)}  
**{labels['overall']}:** {audit.score.overall}/100

## {labels['scorecard']}

| {labels['area']} | Score |
|---|---:|
| SEO | {audit.score.seo}/100 |
| Content | {audit.score.content}/100 |
| UX & Conversion | {audit.score.ux}/100 |
| Accessibility | {audit.score.accessibility}/100 |
| Trust | {audit.score.trust}/100 |
| Performance | {audit.score.performance}/100 |

## {labels['quick_wins']}

{_markdown_list(audit.quick_wins, language)}

## {labels['opportunities']}

{_markdown_list(audit.opportunities, language)}

## {labels['automatic_checks']}

{_checks_table(audit.checks)}

## {labels['page_metadata']}

- Title: {page.title or labels['not_found']}
- Title length: {page.title_length}
- Meta description: {page.meta_description or labels['not_found']}
- Meta description length: {page.meta_description_length}
- Canonical URL: {page.canonical_url or labels['not_found']}
- Meta robots: {page.meta_robots or labels['not_found']}
- HTML lang: {page.html_lang or labels['not_found']}
- H1 count: {len(page.h1)}
- H2 count: {len(page.h2)}
- H3 count: {len(page.h3)}
- Word count: {page.word_count}
- Paragraphs: {page.paragraph_count}
- Text-to-HTML ratio: {page.text_to_html_ratio}%
- HTML response size: {round(page.page_size_bytes / 1024)} KB
- Initial HTML fetch: {page.load_time_ms or labels['not_found']} ms
- Images: {page.images_count}
- Images missing alt text: {page.images_missing_alt_count}
- Images without dimensions: {page.images_without_dimensions_count}
- Internal links: {len(page.internal_links)}
- External links: {len(page.external_links)}
- Broken/empty links: {page.broken_or_empty_links_count}
- Forms: {page.forms_count}
- Inputs: {page.inputs_count}
- Buttons: {page.buttons_count}
- Detected CTAs: {', '.join(page.detected_ctas[:10]) or labels['none']}
- Technology hints: {', '.join(page.technology_hints) or labels['none']}
- Schema types: {', '.join(page.schema_types) or labels['none']}

## H1

{_markdown_list(page.h1, language)}

## H2

{_markdown_list(page.h2, language)}

## {labels['sampled_pages']}

{_pages_table(site.pages)}

## {labels['text_preview']}

```text
{page.readable_text[:4500]}
```

> {labels['local_note']}
"""


def build_html_report(markdown_report: str, context: AuditContext) -> str:
    """Create a lightweight standalone HTML report from the markdown string.

    This is intentionally dependency-free. The HTML is not a full Markdown
    renderer; it preserves the report in a readable <pre> and adds a styled
    score header for quick client/internal review.
    """
    score = context.deterministic_audit.score
    page = context.extraction.primary_page
    escaped_report = html.escape(markdown_report)
    title = html.escape(page.title or context.extraction.start_url)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Website Audit - {title}</title>
  <style>
    :root {{ color-scheme: light dark; --bg:#0f172a; --card:#111827; --text:#e5e7eb; --muted:#9ca3af; --line:#334155; }}
    body {{ margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; background:var(--bg); color:var(--text); }}
    header {{ padding:40px 24px; border-bottom:1px solid var(--line); background:linear-gradient(135deg,#111827,#1e293b); }}
    main {{ max-width:1100px; margin:0 auto; padding:28px 20px 60px; }}
    .kicker {{ color:var(--muted); text-transform:uppercase; letter-spacing:.12em; font-size:12px; }}
    h1 {{ margin:.25rem 0 1rem; font-size:clamp(28px,4vw,48px); }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:14px; margin-top:22px; }}
    .card {{ background:rgba(255,255,255,.04); border:1px solid var(--line); border-radius:18px; padding:18px; }}
    .num {{ font-size:34px; font-weight:800; }}
    .label {{ color:var(--muted); font-size:13px; }}
    pre {{ white-space:pre-wrap; word-break:break-word; line-height:1.55; background:#020617; border:1px solid var(--line); border-radius:18px; padding:22px; overflow:auto; }}
    a {{ color:#93c5fd; }}
  </style>
</head>
<body>
<header>
  <div class="kicker">AI Website Audit CLI</div>
  <h1>{title}</h1>
  <div class="grid">
    <div class="card"><div class="num">{score.overall}</div><div class="label">Overall</div></div>
    <div class="card"><div class="num">{score.seo}</div><div class="label">SEO</div></div>
    <div class="card"><div class="num">{score.ux}</div><div class="label">UX & Conversion</div></div>
    <div class="card"><div class="num">{score.performance}</div><div class="label">Performance</div></div>
  </div>
</header>
<main>
  <pre>{escaped_report}</pre>
</main>
</body>
</html>
"""


def save_report(content: str, output_dir: str | Path, url: str) -> Path:
    directory = ensure_directory(output_dir)
    filename = f"{slugify_url(url)}-audit.md"
    path = directory / filename
    path.write_text(content, encoding="utf-8")
    return path


def save_html_report(content: str, output_dir: str | Path, url: str) -> Path:
    directory = ensure_directory(output_dir)
    filename = f"{slugify_url(url)}-audit.html"
    path = directory / filename
    path.write_text(content, encoding="utf-8")
    return path


def save_json(data: dict, output_dir: str | Path, url: str, suffix: str) -> Path:
    directory = ensure_directory(output_dir)
    filename = f"{slugify_url(url)}-{suffix}.json"
    path = directory / filename
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def save_extraction_json(extraction: SiteExtraction | PageExtraction, output_dir: str | Path, url: str) -> Path:
    if isinstance(extraction, SiteExtraction):
        return save_json(extraction.to_dict(), output_dir, url, "extraction")
    return save_json(extraction.to_dict(), output_dir, url, "extraction")


def _labels(language: str) -> dict[str, str]:
    if language == "de":
        return {
            "title": "Lokaler Website-Audit",
            "start_url": "Start-URL",
            "final_url": "Finale URL",
            "generated": "Generiert",
            "pages_checked": "Seiten geprüft",
            "overall": "Gesamtscore",
            "scorecard": "Scorecard",
            "area": "Bereich",
            "quick_wins": "Wichtigste Quick Wins",
            "opportunities": "Weitere Chancen",
            "automatic_checks": "Automatische Checks",
            "page_metadata": "Seiten-Metadaten",
            "sampled_pages": "Geprüfte Seiten",
            "text_preview": "Extrahierter Textauszug",
            "not_found": "Nicht gefunden",
            "none": "Keine",
            "local_note": "Hinweis: Dieser lokale Report nutzt deterministische Checks. Für einen vollwertigen, priorisierten Audit mit Textanalyse starte das Tool ohne --no-ai.",
        }
    return {
        "title": "Local Website Audit",
        "start_url": "Start URL",
        "final_url": "Final URL",
        "generated": "Generated",
        "pages_checked": "Pages checked",
        "overall": "Overall score",
        "scorecard": "Scorecard",
        "area": "Area",
        "quick_wins": "Top Quick Wins",
        "opportunities": "Additional Opportunities",
        "automatic_checks": "Automatic Checks",
        "page_metadata": "Page Metadata",
        "sampled_pages": "Sampled Pages",
        "text_preview": "Extracted Text Preview",
        "not_found": "Not found",
        "none": "None",
        "local_note": "Note: This local report uses deterministic checks only. For a full prioritized audit with copy and UX analysis, run without --no-ai.",
    }


def _markdown_list(items: list[str], language: str = "en") -> str:
    if not items:
        return "- Keine gefunden" if language == "de" else "- None found"
    return "\n".join(f"- {item}" for item in items)


def _checks_table(checks) -> str:
    rows = ["| Status | Severity | Category | Check | Evidence | Recommendation |", "|---|---|---|---|---|---|"]
    for check in checks:
        evidence = "; ".join(str(item).replace("|", "\\|") for item in check.evidence[:3])
        rows.append(f"| {check.status} | {check.severity} | {check.category} | {check.title} | {evidence or '-'} | {check.recommendation} |")
    return "\n".join(rows)


def _pages_table(pages: list[PageExtraction]) -> str:
    rows = ["| URL | Status | Title | Words | H1 |", "|---|---:|---|---:|---:|"]
    for page in pages:
        title = (page.title or "-").replace("|", "\\|")
        rows.append(f"| {page.final_url} | {page.status_code} | {title} | {page.word_count} | {len(page.h1)} |")
    return "\n".join(rows)
