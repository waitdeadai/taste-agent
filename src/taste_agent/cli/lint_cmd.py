"""taste lint — validate taste.md for contradictions and missing sections."""
from __future__ import annotations

import click

from taste_agent.models.taste_spec import TasteSpec


@click.command()
@click.option("--strict", is_flag=True, help="Fail on any warning.")
@click.pass_context
def lint(ctx: click.Context, strict: bool) -> None:
    """Validate taste.md for contradictions and missing sections."""
    project_root = ctx.obj["project_root"]
    spec_path = project_root / "taste.md"

    if not spec_path.exists():
        click.echo("Error: taste.md not found. Run 'taste init' first.", err=True)
        raise click.Abort()

    try:
        content = spec_path.read_text(encoding="utf-8", errors="replace")
        spec = TasteSpec.from_markdown(content)
    except Exception as e:
        click.echo(f"Error parsing taste.md: {e}", err=True)
        raise click.Abort() from None

    issues: list[str] = []

    # Check required sections exist
    string_attrs = ["aesthetic_direction", "copy_voice"]
    for attr in string_attrs:
        if not getattr(spec, attr, "").strip():
            issues.append(f"Section '{attr}' is empty or missing")

    # Check non-negotiables list is not empty
    if not spec.non_negotiables:
        issues.append("Section 'non_negotiables' is empty or missing")

    # Check color tokens have valid hex
    import re
    for token in spec.color_tokens:
        if not re.match(r"^#[0-9a-fA-F]{6,8}$", token.hex):
            issues.append(f"Invalid hex color: {token.name}={token.hex}")

    # Check non-negotiables aren't empty
    for i, n in enumerate(spec.non_negotiables, 1):
        if len(n) < 5:
            issues.append(f"Non-negotiable #{i} is too short: '{n}'")

    # Check benchmarks are valid URLs
    for bm in spec.benchmarks:
        if not bm.startswith("http"):
            issues.append(f"Invalid benchmark URL: {bm}")

    if issues:
        click.echo(f"Found {len(issues)} issue(s):")
        for issue in issues:
            click.echo(f"  [X] {issue}")
        if strict:
            raise click.Abort()
    else:
        click.echo("taste.md is valid. No issues found.")
