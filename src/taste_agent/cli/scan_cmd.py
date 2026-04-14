"""taste scan — audit an entire project with all 9 evaluators."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import click

from taste_agent import TasteAgent, TasteConfig
from taste_agent.models.severity import ALL_DIMENSIONS


@click.command()
@click.option("--path", type=click.Path(Path), default=".", help="Path to scan.")
@click.option("--output", type=click.Path(Path), default=None, help="Output report path (default: stdout).")
@click.pass_context
def scan(ctx: click.Context, path: str, output: str | None) -> None:
    """Scan a project with all 9 evaluators and produce a coherence report."""
    project_root = (ctx.obj["project_root"] / path).resolve()
    config = TasteConfig(enabled=True, require_taste_md=False)
    agent = TasteAgent(config, project_root=project_root)

    if not agent.has_taste_spec:
        click.echo("Warning: no taste.md found. Running with defaults.", err=True)

    # Collect files by extension
    file_map: dict[str, str] = {}
    for ext in ("*.py", "*.ts", "*.tsx", "*.js", "*.jsx"):
        for f in project_root.rglob(ext):
            if "node_modules" in f.parts or ".venv" in f.parts:
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                rel = f.relative_to(project_root).as_posix()
                file_map[rel] = content
            except Exception:
                pass

    if not file_map:
        click.echo("No code files found.", err=True)
        return

    click.echo(f"Scanning {len(file_map)} files...")

    # Run coherence evaluator on full file_map
    from taste_agent.evaluators.coherence import CoherenceEvaluator
    coherence_eval = CoherenceEvaluator(agent.taste_spec)
    coherence_score, coherence_issues = coherence_eval.evaluate("", file_map=file_map)

    # Run per-file evaluators
    dimension_scores: dict[str, list[float]] = defaultdict(list)
    all_issues_by_dim: dict[str, list[str]] = defaultdict(list)

    from taste_agent.evaluators import (
        AdherenceEvaluator,
        AestheticEvaluator,
        ApiDesignEvaluator,
        ArchitectureEvaluator,
        CodeStyleEvaluator,
        CopyEvaluator,
        NamingEvaluator,
        UXEvaluator,
    )
    evaluators = {
        "aesthetic": AestheticEvaluator(agent.taste_spec),
        "ux": UXEvaluator(agent.taste_spec),
        "copy": CopyEvaluator(agent.taste_spec),
        "adherence": AdherenceEvaluator(agent.taste_spec),
        "architecture": ArchitectureEvaluator(agent.taste_spec),
        "naming": NamingEvaluator(agent.taste_spec),
        "api_design": ApiDesignEvaluator(agent.taste_spec),
        "code_style": CodeStyleEvaluator(agent.taste_spec),
    }

    for rel_path, content in file_map.items():
        for dim_name, evaluator in evaluators.items():
            try:
                score, issues = evaluator.evaluate(content)
                dimension_scores[dim_name].append(score)
                for issue in issues:
                    all_issues_by_dim[dim_name].append(f"{rel_path}: {issue}")
            except Exception:
                pass

    # Build report
    lines = [f"# Taste Scan Report — {project_root.name}"]
    lines.append(f"\nFiles scanned: {len(file_map)}")
    lines.append("\n## Dimension Scores")

    avg_scores = {}
    for dim in ALL_DIMENSIONS:
        if dim == "coherence":
            score = coherence_score
        else:
            scores = dimension_scores.get(dim, [])
            score = sum(scores) / len(scores) if scores else 0.5
        avg_scores[dim] = score
        bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
        status = "PASS" if score >= 0.7 else "WARN" if score >= 0.4 else "FAIL"
        lines.append(f"  {dim:<15} {bar} {score:.2f}  [{status}]")

    lines.append("\n## Critical Issues")

    # Collect top issues per dimension
    issue_count = 0
    for dim in ALL_DIMENSIONS:
        issues = all_issues_by_dim.get(dim, [])
        if dim == "coherence":
            issues = coherence_issues
        for issue in issues[:3]:
            lines.append(f"  [{dim.upper()}] {issue}")
            issue_count += 1
            if issue_count >= 20:
                break
        if issue_count >= 20:
            break

    if issue_count == 0:
        lines.append("  No critical issues found.")

    report = "\n".join(lines)
    if output:
        Path(output).write_text(report, encoding="utf-8")
        click.echo(f"Report written to {output}")
    else:
        click.echo(report)
