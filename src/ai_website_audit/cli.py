from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__
from .analyzer import run_deterministic_audit
from .config import get_settings
from .extractor import extract_site
from .models import AuditContext
from .openai_client import OpenAIReport, generate_audit_with_openai
from .prompts import build_audit_prompt
from .report import build_html_report, build_local_report, save_extraction_json, save_html_report, save_json, save_report
from .utils import normalize_url

app = typer.Typer(
    help="Generate AI-powered website audit reports from public URLs.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"ai-website-audit-cli {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(None, "--version", callback=_version_callback, is_eager=True, help="Show version and exit."),
) -> None:
    """AI Website Audit CLI."""


@app.command()
def audit(
    url: str = typer.Argument(..., help="Public website URL to audit."),
    language: str = typer.Option("en", "--language", "-l", help="Report language: en or de."),
    output: Path = typer.Option(Path("reports"), "--output", "-o", help="Output directory."),
    model: str | None = typer.Option(None, "--model", help="OpenAI model override. Defaults to OPENAI_MODEL, usually gpt-5.5."),
    reasoning_effort: str | None = typer.Option(None, "--reasoning-effort", help="Reasoning effort for supported models: none, low, medium, high, xhigh."),
    max_output_tokens: int | None = typer.Option(None, "--max-output-tokens", help="Maximum OpenAI output tokens for the AI report."),
    store_response: bool | None = typer.Option(None, "--store-response/--no-store-response", help="Whether OpenAI may store this response. Defaults to OPENAI_STORE_RESPONSES=false."),
    max_chars: int = typer.Option(12000, "--max-chars", help="Maximum extracted text characters per page."),
    crawl: bool = typer.Option(False, "--crawl", help="Sample internal links from the same domain."),
    max_pages: int = typer.Option(3, "--max-pages", help="Maximum pages to sample when --crawl is enabled."),
    no_ai: bool = typer.Option(False, "--no-ai", help="Skip OpenAI and generate deterministic local report."),
    html_report: bool = typer.Option(False, "--html", help="Also save a standalone HTML report."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Print debug details."),
) -> None:
    """Audit a public website and save Markdown + JSON artifacts."""
    settings = get_settings()
    normalized_url = _validate_url_and_language(url, language)

    console.print(Panel.fit(f"[bold]AI Website Audit CLI[/bold]\n{normalized_url}", border_style="cyan"))

    try:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task("Fetching, extracting, and scoring website content...", total=None)
            extraction = extract_site(
                normalized_url,
                settings,
                max_chars=max_chars,
                crawl=crawl,
                max_pages=max_pages if crawl else 1,
            )
            deterministic = run_deterministic_audit(extraction)
            context = AuditContext(extraction=extraction, deterministic_audit=deterministic)

        extraction_path = save_extraction_json(extraction, output, normalized_url)
        audit_json_path = save_json(deterministic.to_dict(), output, normalized_url, "deterministic-audit")

        _print_score_table(context)
        _print_quick_wins(context)

        if verbose:
            _print_debug_details(context, extraction_path, audit_json_path)

        if no_ai:
            report = build_local_report(context, language.lower())
        else:
            prompt = build_audit_prompt(context, language.lower())
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                progress.add_task("Generating AI audit report with OpenAI Responses API...", total=None)
                ai_result = generate_audit_with_openai(
                    prompt,
                    settings,
                    model=model,
                    reasoning_effort=reasoning_effort,
                    max_output_tokens=max_output_tokens,
                    store=store_response,
                )
                report = ai_result.content
                openai_metadata_path = save_json(ai_result.to_dict(), output, normalized_url, "openai-response")

        report_path = save_report(report, output, normalized_url)
        console.print(f"[green]Done.[/green] Report saved to: [bold]{report_path}[/bold]")
        console.print(f"[green]Extraction JSON:[/green] {extraction_path}")
        console.print(f"[green]Deterministic audit JSON:[/green] {audit_json_path}")
        if not no_ai:
            console.print(f"[green]OpenAI response metadata:[/green] {openai_metadata_path}")

        if html_report:
            html_path = save_html_report(build_html_report(report, context), output, normalized_url)
            console.print(f"[green]HTML report:[/green] {html_path}")

    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command()
def inspect(
    url: str = typer.Argument(..., help="Public website URL to inspect without AI."),
    output: Path = typer.Option(Path("reports"), "--output", "-o", help="Output directory."),
    max_chars: int = typer.Option(12000, "--max-chars", help="Maximum extracted text characters."),
    crawl: bool = typer.Option(False, "--crawl", help="Sample internal links from the same domain."),
    max_pages: int = typer.Option(3, "--max-pages", help="Maximum pages to sample when --crawl is enabled."),
    html_report: bool = typer.Option(False, "--html", help="Also save a standalone HTML report."),
) -> None:
    """Extract metadata and deterministic checks without using the OpenAI API."""
    settings = get_settings()
    normalized_url = normalize_url(url)
    try:
        extraction = extract_site(normalized_url, settings, max_chars=max_chars, crawl=crawl, max_pages=max_pages if crawl else 1)
        deterministic = run_deterministic_audit(extraction)
        context = AuditContext(extraction=extraction, deterministic_audit=deterministic)
        _print_score_table(context)
        _print_quick_wins(context)
        save_extraction_json(extraction, output, normalized_url)
        report = build_local_report(context, "en")
        path = save_report(report, output, normalized_url)
        console.print(f"[green]Inspection saved:[/green] {path}")
        if html_report:
            html_path = save_html_report(build_html_report(report, context), output, normalized_url)
            console.print(f"[green]HTML report:[/green] {html_path}")
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command("show-config")
def show_config() -> None:
    """Print relevant runtime configuration without exposing secrets."""
    settings = get_settings()
    table = Table(title="Runtime Configuration")
    table.add_column("Key")
    table.add_column("Value")
    table.add_row("OpenAI model", settings.openai_model)
    table.add_row("OpenAI API", "Responses API / responses.create")
    table.add_row("OpenAI max output tokens", str(settings.openai_max_output_tokens))
    table.add_row("OpenAI reasoning effort", str(settings.openai_reasoning_effort))
    table.add_row("OpenAI store responses", "yes" if settings.openai_store_responses else "no")
    table.add_row("OpenAI service tier", str(settings.openai_service_tier))
    table.add_row("Request timeout", f"{settings.request_timeout_seconds}s")
    table.add_row("User agent", settings.user_agent)
    table.add_row("API key configured", "yes" if bool(settings.openai_api_key) else "no")
    console.print(table)


def _validate_url_and_language(url: str, language: str) -> str:
    try:
        normalized_url = normalize_url(url)
    except ValueError as exc:
        console.print(f"[red]Invalid URL:[/red] {exc}")
        raise typer.Exit(code=1)

    if language.lower() not in {"en", "de"}:
        console.print("[red]Invalid language.[/red] Use 'en' or 'de'.")
        raise typer.Exit(code=1)
    return normalized_url


def _print_score_table(context: AuditContext) -> None:
    score = context.deterministic_audit.score
    table = Table(title="Deterministic Audit Score")
    table.add_column("Area")
    table.add_column("Score", justify="right")
    table.add_row("Overall", f"{score.overall}/100")
    table.add_row("SEO", f"{score.seo}/100")
    table.add_row("Content", f"{score.content}/100")
    table.add_row("UX & Conversion", f"{score.ux}/100")
    table.add_row("Accessibility", f"{score.accessibility}/100")
    table.add_row("Trust", f"{score.trust}/100")
    table.add_row("Performance", f"{score.performance}/100")
    console.print(table)


def _print_quick_wins(context: AuditContext) -> None:
    wins = context.deterministic_audit.quick_wins[:5]
    if not wins:
        return
    table = Table(title="Top Quick Wins")
    table.add_column("#", justify="right")
    table.add_column("Recommendation")
    for index, win in enumerate(wins, start=1):
        table.add_row(str(index), win)
    console.print(table)


def _print_debug_details(context: AuditContext, extraction_path: Path, audit_json_path: Path) -> None:
    page = context.extraction.primary_page
    console.print(f"[dim]Extraction saved:[/dim] {extraction_path}")
    console.print(f"[dim]Deterministic audit saved:[/dim] {audit_json_path}")
    console.print(f"[dim]Title:[/dim] {page.title}")
    console.print(f"[dim]Readable characters:[/dim] {len(page.readable_text)}")
    console.print(f"[dim]Pages sampled:[/dim] {len(context.extraction.pages)}")
    console.print(f"[dim]Technology hints:[/dim] {', '.join(page.technology_hints) or 'none'}")
