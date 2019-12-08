# CLI Reference

## Install

```bash
pip install -e .
```

## Global options

```bash
ai-website-audit --version
ai-website-audit --help
```

## `inspect`

Runs extraction and deterministic checks only. No OpenAI API key required.

```bash
ai-website-audit inspect URL [OPTIONS]
```

Options:

| Option | Default | Description |
|---|---|---|
| `--output`, `-o` | `reports` | Output directory |
| `--max-chars` | `12000` | Maximum readable text characters per page |
| `--crawl` | false | Sample same-domain internal links |
| `--max-pages` | `3` | Max pages when crawling |
| `--html` | false | Also save a standalone HTML report |

Example:

```bash
ai-website-audit inspect https://example.com --html
```

## `audit`

Runs the full audit. Uses OpenAI unless `--no-ai` is passed.

```bash
ai-website-audit audit URL [OPTIONS]
```

Options:

| Option | Default | Description |
|---|---|---|
| `--language`, `-l` | `en` | Report language: `en` or `de` |
| `--output`, `-o` | `reports` | Output directory |
| `--model` | `OPENAI_MODEL` | OpenAI model override |
| `--reasoning-effort` | `OPENAI_REASONING_EFFORT` | Reasoning effort for supported models |
| `--max-output-tokens` | `OPENAI_MAX_OUTPUT_TOKENS` | Max OpenAI output tokens |
| `--store-response/--no-store-response` | `OPENAI_STORE_RESPONSES` | Whether OpenAI may store the response object |
| `--max-chars` | `12000` | Maximum readable text characters per page |
| `--crawl` | false | Sample same-domain internal links |
| `--max-pages` | `3` | Max pages when crawling |
| `--no-ai` | false | Generate local deterministic Markdown instead of OpenAI report |
| `--html` | false | Also save a standalone HTML report |
| `--verbose`, `-v` | false | Print debug details |

Examples:

```bash
ai-website-audit audit https://example.com --language en --html
```

```bash
ai-website-audit audit https://example.com \
  --language de \
  --crawl \
  --max-pages 5 \
  --model gpt-5.5 \
  --reasoning-effort medium \
  --max-output-tokens 6000 \
  --html
```

```bash
ai-website-audit audit https://example.com --no-ai --html
```

## `show-config`

Prints runtime settings without exposing secrets.

```bash
ai-website-audit show-config
```

Shows:

- OpenAI model
- OpenAI API interface
- max output tokens
- reasoning effort
- response storage setting
- service tier
- request timeout
- user agent
- whether an API key is configured
