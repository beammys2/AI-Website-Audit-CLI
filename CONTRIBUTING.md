# Contributing

Thanks for considering a contribution.

AI Website Audit CLI is meant to be a practical open-source tool, not a toy example. Contributions should make the tool more useful, more accurate, easier to maintain, or easier to understand.

## Good first issues

Good starter contributions:

- add a deterministic check in `analyzer.py`
- add tests for existing checks
- improve German or English prompt wording
- improve README examples
- add a sample report
- add extraction for another metadata type
- improve OpenAI response metadata handling
- add another report format
- improve error handling
- document a limitation clearly

## Development setup

```bash
git clone https://github.com/YOUR_USERNAME/ai-website-audit-cli.git
cd ai-website-audit-cli
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest
```

Run tests:

```bash
pytest
```

Run local smoke test without OpenAI:

```bash
python -m ai_website_audit audit https://example.com --no-ai --verbose
```

Run OpenAI smoke test:

```bash
cp .env.example .env
# add OPENAI_API_KEY
python -m ai_website_audit audit https://example.com --model gpt-5.4-mini --max-output-tokens 3000
```

## Project principles

1. **Ground reports in evidence**  
   Do not add checks or prompts that encourage invented claims.

2. **Keep OpenAI usage explicit**  
   OpenAI calls belong in `src/ai_website_audit/openai_client.py`.

3. **Keep the CLI usable**  
   Avoid adding too many mandatory parameters.

4. **Prefer structured data**  
   Extract facts first, then let AI reason over those facts.

5. **Make failures understandable**  
   Error messages should help users fix the problem.

6. **Tests matter**  
   Add or update tests when changing scoring, URL handling, extraction behavior, prompts or OpenAI metadata handling.

## Pull request checklist

Before opening a PR:

- [ ] Code runs locally
- [ ] Tests pass
- [ ] README/docs updated if needed
- [ ] New behavior is covered by tests when practical
- [ ] No secrets or API keys committed
- [ ] Output remains useful and non-hallucinatory
- [ ] OpenAI usage remains centralized and transparent

## Prompt contributions

Prompt changes are welcome, but they should follow these rules:

- keep reports specific
- discourage hallucinations
- ask for evidence from extraction
- include manual review sections
- preserve English and German quality
- avoid claims based on traffic, rankings, revenue or analytics unless explicitly provided by the user

## Security

Do not submit vulnerabilities publicly if they could expose secrets or enable abuse. See `SECURITY.md`.
