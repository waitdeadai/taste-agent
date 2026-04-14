"""Taste CLI — taste-agent command-line interface."""
from __future__ import annotations

from pathlib import Path

import click

from taste_agent.cli import (
    diff_cmd,
    evolve_cmd,
    explain_cmd,
    gate_cmd,
    init_cmd,
    lint_cmd,
    scan_cmd,
)


@click.group()
@click.option("--project-root", type=click.Path(Path), default=".", help="Project root directory.")
@click.option("--config", type=click.Path(Path), default=None, help="Path to config file.")
@click.pass_context
def cli(ctx: click.Context, project_root: str, config: str | None) -> None:
    ctx.ensure_object(dict)
    ctx.obj["project_root"] = Path(project_root).resolve()
    ctx.obj["config_path"] = Path(config) if config else None


# Register subcommands
cli.add_command(init_cmd.init)
cli.add_command(lint_cmd.lint)
cli.add_command(scan_cmd.scan)
cli.add_command(evolve_cmd.evolve)
cli.add_command(explain_cmd.explain)
cli.add_command(diff_cmd.diff)
cli.add_command(gate_cmd.gate)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
