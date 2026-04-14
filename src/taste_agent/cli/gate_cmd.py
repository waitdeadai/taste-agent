"""taste gate — CI/CD threshold check."""
from __future__ import annotations

import asyncio

import click

from taste_agent import TasteAgent, TasteConfig
from taste_agent.models.severity import Severity


@click.command()
@click.option("--min-score", type=float, default=0.7, help="Minimum overall score to pass.")
@click.option("--max-p0", type=int, default=0, help="Max P0 issues before fail.")
@click.option("--max-reject", type=int, default=0, help="Max REJECT verdicts before fail.")
@click.option("--files", type=str, default=None, help="Comma-separated list of files to evaluate.")
@click.option("--task", type=str, default="CI gate check", help="Task description for the gate.")
@click.pass_context
def gate(
    ctx: click.Context,
    min_score: float,
    max_p0: int,
    max_reject: int,
    files: str | None,
    task: str,
) -> None:
    """CI/CD gate: run taste evaluation and exit non-zero if thresholds exceeded.

    Use in CI pipelines:
        taste gate --files "app/page.tsx,app/layout.tsx" || exit 1
    """
    project_root = ctx.obj["project_root"]
    config = TasteConfig(enabled=True, require_taste_md=False)
    agent = TasteAgent(config, project_root=project_root)

    file_list: list[str] = []
    file_contents: dict[str, str] = {}

    if files:
        for rel_path in files.split(","):
            rel_path = rel_path.strip()
            full_path = project_root / rel_path
            if not full_path.exists():
                click.echo(f"Warning: {rel_path} not found, skipping.", err=True)
                continue
            content = full_path.read_text(encoding="utf-8", errors="replace")
            file_list.append(rel_path)
            file_contents[rel_path] = content

    if not file_list:
        click.echo("No files to evaluate. Gate passes by default.")
        return

    click.echo(f"Evaluating {len(file_list)} file(s)...")

    result = asyncio.run(agent.evaluate(
        task=task,
        output_files=file_list,
        file_contents=file_contents,
    ))

    # Count severities
    p0_count = sum(1 for i in result.issues if i.severity == Severity.P0)
    p1_count = sum(1 for i in result.issues if i.severity == Severity.P1)
    p2_count = sum(1 for i in result.issues if i.severity == Severity.P2)

    click.echo(f"\n{'='*50}")
    click.echo(f"VERDICT: {result.verdict.upper()}")
    click.echo(f"SCORE: {result.overall_score:.3f} (threshold: {min_score})")
    click.echo(f"P0: {p0_count}/{max_p0}  P1: {p1_count}  P2: {p2_count}")
    click.echo(f"{'='*50}")

    if result.issues:
        click.echo(f"\n{len(result.issues)} issue(s):")
        for issue in result.issues[:10]:
            click.echo(f"  [{issue.severity.value}] {issue.dimension}: {issue.problem[:80]}")

    failed = False

    if p0_count > max_p0:
        click.echo(f"\nFAIL: {p0_count} P0 issues exceed threshold of {max_p0}", err=True)
        failed = True

    if result.overall_score < min_score:
        click.echo(f"\nFAIL: score {result.overall_score:.3f} below threshold {min_score}", err=True)
        failed = True

    if result.verdict == "reject":
        click.echo("\nFAIL: verdict is REJECT", err=True)
        failed = True

    if failed:
        raise SystemExit(1)
    else:
        click.echo("\nPASS: All gate checks cleared.")
