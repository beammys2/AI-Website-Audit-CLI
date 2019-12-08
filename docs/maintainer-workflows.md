# Maintainer Workflows

This document describes how maintainers can keep the project healthy.

## Weekly maintenance

- Review new issues
- Label bugs, docs, enhancement, good first issue
- Check dependency updates
- Review open PRs
- Update roadmap when priorities change

## Release process

1. Merge completed changes into main
2. Update `CHANGELOG.md`
3. Update version in `pyproject.toml` and `__init__.py`
4. Create GitHub release
5. Tag release, e.g. `v0.1.1`

## Issue labels

Recommended labels:

- `bug`
- `documentation`
- `enhancement`
- `good first issue`
- `prompt`
- `security`
- `help wanted`
- `needs reproduction`

## AI-assisted maintainer workflows

Maintainers can use coding assistants to help with:

- generating tests for utility functions
- reviewing pull requests
- improving prompt templates
- detecting unsafe code paths
- generating release notes
- summarizing issues
- converting feature ideas into implementation plans
- writing docs for new modules

## Prompt review workflow

Prompt updates should be reviewed carefully because prompt changes affect report behavior.

Checklist:

- Is the prompt specific?
- Does it avoid unsupported claims?
- Does it request actionable output?
- Does it remain useful across industries?
- Does it work in both English and German where relevant?
- Does it avoid legal, medical, or financial overclaiming?
