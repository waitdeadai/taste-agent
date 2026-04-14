"""taste init — bootstrap a new taste.md for a project."""
from __future__ import annotations

import click
import questionary

TEMPLATE = """# Taste — {project_name}

## Changelog
- v1.0 ({date}): Initial taste specification

## 1. Visual Theme & Atmosphere

**Aesthetic direction:** {aesthetic}
**Mood:** {mood_words}

## 2. Reference Benchmarks

{benchmarks}

## 3. Color Palette

| Name | Hex | Role |
|------|-----|------|
| Primary | #0a0a0a | Background |
| Accent | #00ff88 | CTA, highlights |
| Text | #ffffff | Primary text |
| Muted | #888888 | Secondary text |

## 4. Typography

- Headings: **Inter** (geometric, clean)
- Body: **Inter** (optical sizing enabled)
- Mono: **JetBrains Mono** (numbers, code)

## 5. Component Standards

### Button
Primary action element. States: default, hover, active, disabled, loading.
- Primary: accent background, black text
- Secondary: transparent, accent border

### Card
Content container with subtle glass effect.
- Background: rgba(255,255,255,0.03)
- Border: 1px solid rgba(255,255,255,0.08)
- Radius: 12px

## 6. Copy Voice

**Tone:** {copy_voice}

Guidelines:
- Confident and direct — no hedging
- Specific over generic — no placeholder copy
- Technical precision when needed — approachable when not

## 7. Non-Negotiables

1. No placeholder or Lorem Ipsum copy
2. All interactive elements must have accessible labels
3. Error states must be visible and actionable
4. No silent failures — always surface errors to the user

## 8. Layout & Spacing

base_unit: 4px
spacing_scale: 4, 8, 12, 16, 24, 32, 48, 64, 96
max_content_width: 1200px
gutter: 24px

## 9. Agent Prompt Guide

When evaluating output:
- Aesthetic: does it match the visual theme?
- UX: are interactions clear and responsive?
- Copy: is the voice consistent and specific?
- Adherence: does it follow these specifications exactly?

## 10. Architecture Standards (v2)

layer_1: Interface (UI, API endpoints)
layer_2: Application (business logic, use cases)
layer_3: Domain (entities, value objects)
layer_4: Infrastructure (database, external services)

## 11. Naming Conventions (v2)

files: snake_case.py
classes: PascalCase
functions: snake_case
constants: UPPER_SNAKE_CASE
database_tables: snake_case_plural

## 12. API Design (v2)

restful: true
versioned: true
pagination: cursor-based
error_format: {{"error": {{"code": "...", "message": "..."}}}}
response_envelope: {{"data": ..., "meta": {{}}}}
"""

AESTHETIC_MAP = {
    "B2B SaaS": "Dark institutional — Linear meets Stripe",
    "consumer": "Light and playful — Figma meets Airbnb",
    "developer tools": "Technical precision — Vercel meets Raycast",
    "consulting": "Editorial and confident — McKinsey meets Linear",
    "other": "Dark and premium — Apple meets Linear",
}


@click.command()
@click.option("--defaults", is_flag=True, help="Skip questions, use defaults.")
@click.option("--output", type=str, default="taste.md", help="Output path.")
@click.option("--industry", type=str, default=None, help="Industry preset (used with --defaults).")
@click.pass_context
def init(ctx: click.Context, defaults: bool, output: str, industry: str | None) -> None:
    """Bootstrap a new taste.md for this project."""
    project_root = ctx.obj["project_root"]
    output_path = project_root / output

    if output_path.exists():
        click.echo(f"Error: {output_path} already exists. Delete it first or use --force.", err=True)
        raise click.Abort()

    if defaults:
        date = "2026-04-14"
        project_name = project_root.name
        aesthetic_str = (
            AESTHETIC_MAP.get(industry, "Dark, premium, institutional — Apple meets Linear")
            if industry
            else "Dark, premium, institutional — Apple meets Linear"
        )
        taste_md = TEMPLATE.format(
            project_name=project_name,
            date=date,
            aesthetic=aesthetic_str,
            mood_words="dark, bold, precise, premium",
            benchmarks="",
            copy_voice="Confident, direct, specific — enterprise-grade authority",
        )
        output_path.write_text(taste_md, encoding="utf-8")
        click.echo(f"Created {output_path} with defaults.")
        return

    # Interactive wizard
    click.echo("Taste Agent — taste.md wizard")
    click.echo("Answer 10 questions to define your project's design standards.\n")

    project_name = questionary.text("Project name:", default=project_root.name).ask()
    questionary.select(
        "Project type:",
        choices=["webapp", "api", "cli", "library", "full-stack"],
    ).ask()
    industry = questionary.select(
        "Industry:",
        choices=["B2B SaaS", "consumer", "developer tools", "consulting", "other"],
    ).ask()
    benchmarks_raw = questionary.text(
        "Reference URLs (comma-separated, e.g. linear.app, stripe.com):",
        default="linear.app, stripe.com",
    ).ask()
    benchmarks = "\n".join(f"- https://{b.strip()}" for b in benchmarks_raw.split(",") if b.strip())
    aesthetic = questionary.text(
        "Aesthetic direction (e.g. 'Dark, premium, institutional — Apple meets Linear'):",
        default="Dark, premium, institutional",
    ).ask()
    mood_words = questionary.text(
        "Mood words (comma-separated, e.g. dark, bold, precise):",
        default="dark, bold, precise",
    ).ask()
    copy_voice = questionary.select(
        "Copy voice:",
        choices=[
            "Confident and direct — enterprise authority",
            "Friendly and approachable — warm professionalism",
            "Technical and precise — developer-first",
        ],
    ).ask()
    questionary.text(
        "Tech stack (e.g. Next.js, FastAPI, PostgreSQL):",
        default="Next.js, FastAPI, PostgreSQL",
    ).ask()
    questionary.select(
        "Quality bar:",
        choices=["Linear / Stripe quality", "GitHub / Vercel quality", "Presentable / prototype"],
    ).ask()
    questionary.text(
        "Non-negotiables (comma-separated hard rules):",
        default="no placeholder copy, no silent failures, accessible UI",
    ).ask()

    date = "2026-04-14"
    taste_md = TEMPLATE.format(
        project_name=project_name or project_root.name,
        date=date,
        aesthetic=aesthetic or AESTHETIC_MAP.get(industry, "Dark, premium"),
        mood_words=mood_words or "dark, bold, precise",
        benchmarks=benchmarks or "- https://linear.app",
        copy_voice=copy_voice or "Confident and direct",
    )

    output_path.write_text(taste_md, encoding="utf-8")
    click.echo(f"\nCreated {output_path}")
    click.echo("Edit it to refine your taste standards, then run 'taste lint' to validate.")
