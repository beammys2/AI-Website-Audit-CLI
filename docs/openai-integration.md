# OpenAI Integration

This project uses OpenAI for the AI-assisted report layer. The deterministic extraction and scoring layers work without OpenAI.

## API interface

The integration uses the OpenAI Python SDK and the Responses API:

```python
from openai import OpenAI

client = OpenAI(api_key=settings.openai_api_key)
response = client.responses.create(
    model="gpt-5.5",
    instructions=SYSTEM_INSTRUCTIONS,
    input=prompt,
    max_output_tokens=6000,
    reasoning={"effort": "medium"},
    store=False,
)
```

The implementation lives in:

```text
src/ai_website_audit/openai_client.py
```

## Default model

The default model is:

```env
OPENAI_MODEL=gpt-5.5
```

This is intentionally current and high quality for strategy-heavy audits. Users can override it:

```bash
ai-website-audit audit https://example.com --model gpt-5.4-mini
```

## What is sent to OpenAI?

The prompt contains:

- public page metadata
- headings
- links summary
- image/form/CTA counts
- extracted readable text
- deterministic audit checks
- scores
- quick wins and risks

The prompt does **not** send:

- API keys
- `.env` contents
- cookies
- private browser sessions
- authentication headers
- local files

## Response storage

Default:

```env
OPENAI_STORE_RESPONSES=false
```

This is a privacy-first default. Users can opt in:

```bash
ai-website-audit audit https://example.com --store-response
```

## Usage metadata

When the SDK returns usage details, the CLI saves them in:

```text
reports/example-com-openai-response.json
```

The metadata includes:

- response ID
- model
- API endpoint name
- token usage when available
- latency
- reasoning effort
- max output tokens
- store setting

## Prompt design

The prompts are in:

```text
prompts/audit_prompt_en.md
prompts/audit_prompt_de.md
```

They instruct the model to avoid invented facts and to separate confirmed findings from manual-review items.
