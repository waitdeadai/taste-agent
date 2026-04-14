"""taste diff — show changes between two taste.md versions."""
from __future__ import annotations

import difflib
from pathlib import Path

import click

from taste_agent.models.taste_spec import TasteSpec


@click.command()
@click.argument("old_path", type=str)
@click.argument("new_path", type=str)
@click.option("--color/--no-color", default=True)
@click.pass_context
def diff(ctx: click.Context, old_path: str, new_path: str, color: bool) -> None:
    """Diff two taste.md versions (files or directories with --before/--after tags).

    Shows sections that changed, added, or removed.
    """
    old_file = ctx.obj["project_root"] / old_path
    new_file = ctx.obj["project_root"] / new_path

    if not old_file.exists():
        click.echo(f"Error: {old_file} not found.", err=True)
        raise click.Abort()
    if not new_file.exists():
        click.echo(f"Error: {new_file} not found.", err=True)
        raise click.Abort()

    old_content = old_file.read_text(encoding="utf-8", errors="replace")
    new_content = new_file.read_text(encoding="utf-8", errors="replace")

    # Parse into specs
    old_spec = TasteSpec.from_markdown(old_content)
    new_spec = TasteSpec.from_markdown(new_content)

    # Build unified diff
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    diff_lines = list(difflib.unified_diff(
        old_lines, new_lines,
        fromfile=str(old_path),
        tofile=str(new_path),
        lineterm="",
    ))

    if not diff_lines:
        click.echo("No differences found.")
        return

    # Group by section
    section_changes: dict[str, list[str]] = {}
    current_section = "header"
    section_changes[current_section] = []

    section_keywords = ["Visual Theme", "Reference", "Color", "Typography",
                        "Component", "Copy Voice", "Non-Negotiable", "Layout",
                        "Agent Prompt", "Architecture", "Naming", "API Design",
                        "Changelog"]

    for line in diff_lines:
        is_section_header = any(kw in line for kw in section_keywords)
        if is_section_header and (line.startswith("##") or line.startswith("+++") or line.startswith("---")):
            current_section = line.strip().lstrip("+-").strip()
            if current_section not in section_changes:
                section_changes[current_section] = []
        elif line.startswith(("+", "-", "^", "\\")):
            continue
        else:
            if line.strip():
                section_changes[current_section].append(line)

    # Print summary
    click.echo(f"# Taste Diff: {old_path} -> {new_path}\n")

    added_sections = []
    removed_sections = []

    for section, lines in section_changes.items():
        if section == "header":
            continue
        if any("---" in ln for ln in lines if len(ln) > 0):
            added_sections.append(section)
        elif any("+++" in ln for ln in lines if len(ln) > 0):
            removed_sections.append(section)

    if added_sections:
        click.echo("## New Sections\n")
        for s in added_sections:
            click.echo(f"  + {s}")

    if removed_sections:
        click.echo("\n## Removed Sections\n")
        for s in removed_sections:
            click.echo(f"  - {s}")

    click.echo("\n## Full Diff\n")
    for line in diff_lines:
        if color:
            if line.startswith("+"):
                click.echo(f"\033[32m{line}\033[0m", nl=False)
            elif line.startswith("-"):
                click.echo(f"\033[31m{line}\033[0m", nl=False)
            elif line.startswith("^"):
                pass
            else:
                click.echo(line, nl=False)
        else:
            click.echo(line, nl=False)

    # Show changelog
    if new_spec.changelog and old_spec.changelog:
        old_versions = {e.version for e in old_spec.changelog}
        new_entries = [e for e in new_spec.changelog if e.version not in old_versions]
        if new_entries:
            click.echo("\n## Version History\n")
            for entry in new_entries:
                click.echo(f"  v{entry.version} ({entry.date}): {entry.change}")
