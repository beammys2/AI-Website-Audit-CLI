# Changelog

## 1.0.0

### Added

- Production-style OpenAI Responses API integration via `client.responses.create(...)`.
- Default OpenAI model set to `gpt-5.5`.
- Support for reasoning effort through `OPENAI_REASONING_EFFORT` and `--reasoning-effort`.
- Support for `OPENAI_MAX_OUTPUT_TOKENS` and `--max-output-tokens`.
- Privacy-first response storage control with `OPENAI_STORE_RESPONSES=false` and `--store-response/--no-store-response`.
- OpenAI response metadata JSON output.
- `docs/openai-integration.md`.
- `AGENTS.md` for Codex and AI coding agents.
- Dockerfile and Makefile.
- Stronger English and German prompt templates.

### Changed

- Version bumped from `0.3.0` to `1.0.0`.
- OpenAI dependency updated to `openai>=2.0.0`.
- README rewritten to emphasize real OpenAI API usage, MIT open source, deterministic checks and transparent artifacts.
- CLI now prints the OpenAI metadata output path when an AI report is generated.

## 0.3.0

### Added

- HTML report export.
- Performance score.
- Technology hints.
- `show-config` command.
- Additional extraction fields for load time, text-to-HTML ratio, image dimensions, forms and trust signals.

## 0.2.0

### Added

- Deterministic audit engine.
- Scorecard.
- `inspect` command.
- Conservative same-domain crawl.
- Expanded documentation.

## 0.1.0

### Added

- Initial public version.
- Website extraction.
- OpenAI-assisted Markdown report generation.
- German and English prompts.
