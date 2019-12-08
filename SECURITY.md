# Security Policy

## Supported versions

Security fixes are applied to the latest released version.

## Reporting a vulnerability

Please open a private security advisory on GitHub or contact the maintainer directly.

Do not publicly disclose vulnerabilities that could expose secrets, leak private data, or enable abuse before maintainers have had a reasonable chance to respond.

## Security principles

This tool should:

- audit only public websites provided by the user
- never bypass authentication
- never scrape private dashboards or logged-in pages
- never overload target websites
- never collect unnecessary personal data
- never store API keys in reports
- never send `.env` files to OpenAI
- never send cookies or private headers to OpenAI
- never run remote code from audited websites
- never include hidden telemetry

## OpenAI API keys

Never commit `.env` files or API keys.

Use `.env.example` as a template:

```env
OPENAI_API_KEY=sk-your-key
```

The CLI reads the key from environment variables and does not print it in `show-config`.

## OpenAI response storage

Default:

```env
OPENAI_STORE_RESPONSES=false
```

This means the CLI asks the OpenAI API not to store generated response objects unless the user opts in.

## What data is sent to OpenAI?

Only the audit context generated from a public URL:

- extracted public HTML metadata
- headings and readable public text
- link/image/form/CTA summaries
- deterministic checks and scores

The tool should not send:

- API keys
- cookies
- private files
- private browser sessions
- authentication headers
- unpublished content

## Responsible use

Respect target websites. Keep crawls small, use a clear user agent, and do not use the tool for aggressive scanning.
