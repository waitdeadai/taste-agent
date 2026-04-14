"""taste evolve — suggest taste.md updates from taste.memory patterns."""
from __future__ import annotations

import click

from taste_agent import TasteConfig
from taste_agent.core.memory import TasteMemory


@click.command()
@click.option("--dry-run", is_flag=True, help="Show suggestions without writing changes.")
@click.pass_context
def evolve(ctx: click.Context, dry_run: bool) -> None:
    """Analyze taste.memory and suggest taste.md updates.

    Patterns detected from memory entries inform potential spec additions.
    """
    project_root = ctx.obj["project_root"]
    config = TasteConfig(enabled=True, memory_scope="project")
    memory_path = config.resolve_memory_path(project_root)

    if not memory_path.exists():
        click.echo("No taste.memory found. Nothing to evolve.", err=True)
        return

    memory = TasteMemory(memory_path)
    all_entries = memory.entries()
    entries = all_entries[-50:] if len(all_entries) > 50 else all_entries

    if not entries:
        click.echo("taste.memory is empty.")
        return

    # Analyze patterns
    category_issues: dict[str, list[str]] = {}
    principle_counts: dict[str, int] = {}

    for entry in entries:
        cat = getattr(entry, "category", "adherence") or "adherence"
        if cat not in category_issues:
            category_issues[cat] = []
        issues_text = getattr(entry, "issues", [])
        issues_str = ", ".join(issues_text) if issues_text else ""
        category_issues[cat].append(issues_str)
        principle = getattr(entry, "principle", "") or ""
        if principle:
            principle_counts[principle] = principle_counts.get(principle, 0) + 1

    lines = ["# Taste Evolve — Suggested Spec Updates\n"]
    lines.append(f"\nAnalyzed {len(entries)} recent memory entries.\n")

    lines.append("## Patterns by Category\n")
    for cat, issues in sorted(category_issues.items()):
        lines.append(f"\n### {cat.upper()}")
        seen = set()
        for issue in issues[:5]:
            if issue and issue not in seen:
                lines.append(f"- {issue}")
                seen.add(issue)

    lines.append("\n## Suggested Non-Negotiables\n")
    top_principles = sorted(principle_counts.items(), key=lambda x: -x[1])[:5]
    for principle, count in top_principles:
        if count >= 2:
            lines.append(f"- [{count}x] {principle[:100]}")

    if dry_run:
        click.echo("\n".join(lines))
        click.echo("\n(Dry-run complete. Run without --dry-run to append suggestions to taste.md)")
    else:
        click.echo("\n".join(lines))
