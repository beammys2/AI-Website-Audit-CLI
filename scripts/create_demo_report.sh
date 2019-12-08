#!/usr/bin/env bash
set -euo pipefail
python -m ai_website_audit audit https://example.com --no-ai --output reports --verbose
