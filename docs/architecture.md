# Architecture

`ai-website-audit-cli` is intentionally split into simple layers.

## 1. CLI layer

File:

```text
src/ai_website_audit/cli.py
```

Responsibilities:

- parse command-line arguments
- load settings
- call extraction
- call deterministic audit
- optionally call OpenAI
- save Markdown, HTML and JSON artifacts
- print score tables and quick wins

## 2. Configuration layer

File:

```text
src/ai_website_audit/config.py
```

Responsibilities:

- read `.env` and environment variables
- expose OpenAI model/settings
- expose request timeout and user agent
- keep secrets out of reports and logs

## 3. Extraction layer

File:

```text
src/ai_website_audit/extractor.py
```

Responsibilities:

- fetch public HTML
- parse metadata, headings, links, forms, images and text
- detect basic trust, pricing, FAQ and technology signals
- optionally sample a small number of same-domain pages

The extraction layer stores facts, not opinions.

## 4. Data model layer

File:

```text
src/ai_website_audit/models.py
```

Responsibilities:

- define dataclasses for page extraction, site extraction, audit checks, scores and contexts
- provide `.to_dict()` methods for JSON output and prompt construction

## 5. Deterministic audit layer

File:

```text
src/ai_website_audit/analyzer.py
```

Responsibilities:

- convert extracted facts into transparent checks
- calculate score categories
- create quick wins and risk flags
- detect multi-page issues such as duplicate titles or meta descriptions

This layer is testable and works without OpenAI.

## 6. Prompt layer

Files:

```text
src/ai_website_audit/prompts.py
prompts/audit_prompt_en.md
prompts/audit_prompt_de.md
```

Responsibilities:

- load language-specific prompt templates
- inject the audit context JSON
- keep prompt wording separate from code

## 7. OpenAI layer

File:

```text
src/ai_website_audit/openai_client.py
```

Responsibilities:

- call the OpenAI Responses API
- use the configured model, reasoning effort and output token limit
- keep system instructions explicit
- return the AI report plus metadata
- avoid leaking secrets

## 8. Report layer

File:

```text
src/ai_website_audit/report.py
```

Responsibilities:

- save Markdown reports
- save JSON artifacts
- build a lightweight standalone HTML report

## Data flow

```text
URL
 ↓
extract_site()
 ↓
SiteExtraction JSON
 ↓
run_deterministic_audit()
 ↓
DeterministicAudit JSON
 ↓                         ↘
build_audit_prompt()        build_local_report()
 ↓
OpenAI Responses API
 ↓
Markdown report + OpenAI metadata
 ↓
Optional HTML report
```

## Design principles

- Keep extraction and AI separate.
- Save the raw evidence.
- Make checks deterministic and testable.
- Keep OpenAI calls centralized.
- Do not invent facts in prompts or local reports.
- Keep the project small enough for contributors to understand quickly.
