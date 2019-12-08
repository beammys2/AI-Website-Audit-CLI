.PHONY: install test inspect demo clean

install:
	python -m pip install -e . pytest

test:
	pytest

inspect:
	ai-website-audit inspect https://example.com --html

demo:
	ai-website-audit audit https://example.com --no-ai --html --output reports/demo

clean:
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info reports/demo
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
