FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md requirements.txt ./
COPY src ./src
COPY prompts ./prompts
RUN pip install --no-cache-dir -e .
ENTRYPOINT ["ai-website-audit"]
