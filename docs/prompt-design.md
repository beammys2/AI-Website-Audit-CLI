# Prompt Design

The project uses prompt templates instead of hard-coded prompt strings.

## Goals

The prompt should produce a report that is:

- grounded in extracted data
- specific, not generic
- useful for implementation
- honest about unknowns
- structured as Markdown
- suitable for developers, founders, freelancers, and small agencies

## Input structure

The model receives one JSON object called `AuditContext` containing:

- extracted website facts
- deterministic audit checks
- scores
- risk flags
- quick wins

## Anti-hallucination rules

The prompt explicitly tells the model not to invent:

- traffic numbers
- revenue
- search rankings
- conversion rates
- Core Web Vitals
- competitor claims
- legal conclusions

If something is not visible in the extraction, the model should mark it as "Needs manual review".

## Language support

Current prompt templates:

- `audit_prompt_en.md`
- `audit_prompt_de.md`

Future templates could include:

- agency-style report
- founder landing-page report
- technical SEO report
- accessibility-focused report
- ecommerce report
- SaaS landing-page report
