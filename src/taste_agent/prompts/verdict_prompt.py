"""Per-task evaluation prompt template.

Builds the full prompt injected with taste.md content,
taste.memory principles, and the output to evaluate.
"""

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from taste_agent.models.taste_spec import TasteSpec
    from taste_agent.core.memory import TasteMemory


def build_verdict_prompt(
    task: str,
    taste_spec: "TasteSpec | None",
    taste_memory: "TasteMemory | None",
    output_files: list[str],
    file_contents: dict[str, str],
    diff: str = "",
) -> str:
    """Build the full verdict prompt for a taste evaluation.

    Args:
        task: The original task description.
        taste_spec: Parsed taste.md (or None if not found).
        taste_memory: TasteMemory instance (or None).
        output_files: List of files that were modified.
        file_contents: Dict of filename -> content for files to evaluate.
        diff: Optional git diff string.

    Returns:
        The full prompt string to send to the LLM.
    """
    from taste_agent.prompts.taste_system import TASTE_SYSTEM_PROMPT, DEFAULT_TASTE_PROMPT

    # Build taste.md block
    if taste_spec:
        taste_md_block = _build_taste_spec_block(taste_spec)
    else:
        taste_md_block = DEFAULT_TASTE_PROMPT

    # Build taste.memory block
    memory_block = _build_memory_block(taste_memory) if taste_memory else ""

    # Build output files block
    files_block = _build_files_block(output_files, file_contents)

    # Build diff block
    diff_block = f"\n## Diff Against Previous\n```diff\n{diff}\n```\n" if diff else ""

    return f"""## Task
{task}

{TASTE_SYSTEM_PROMPT}

{taste_md_block}
{memory_block}
{files_block}
{diff_block}

## Your Evaluation
Return ONLY valid JSON as specified in the system prompt."""


def _build_taste_spec_block(spec: "TasteSpec") -> str:
    """Build the taste.md content block for the prompt."""
    parts = ["## taste.md (Human's Design Specification)"]

    if spec.project_name:
        parts.append(f"\nProject: {spec.project_name}\n")

    if spec.aesthetic_direction:
        parts.append(f"\n### Visual Theme & Atmosphere\n{spec.aesthetic_direction}")

    if spec.mood_words:
        parts.append(f"\nMood: {', '.join(spec.mood_words)}")

    if spec.benchmarks:
        parts.append(f"\n### Reference Benchmarks\n")
        for b in spec.benchmarks:
            parts.append(f"- {b}")

    if spec.color_tokens:
        parts.append(f"\n### Color Palette\n{spec.color_tokens_text()}")

    if spec.typography:
        parts.append("\n### Typography")
        for t in spec.typography:
            parts.append(f"- {t.element}: {t.font_family} {t.size} {t.weight}".strip())

    if spec.component_standards:
        parts.append("\n### Component Standards")
        for c in spec.component_standards:
            parts.append(f"\n#### {c.name}")
            parts.append(c.description)

    if spec.copy_voice:
        parts.append(f"\n### Copy Voice\n{spec.copy_voice}")

    if spec.non_negotiables:
        parts.append(f"\n### Non-Negotiables (Hard Rules)\n{spec.non_negotiables_text()}")

    if spec.agent_prompt_guide:
        parts.append(f"\n### Agent Prompt Guide\n{spec.agent_prompt_guide}")

    return "\n".join(parts)


def _build_memory_block(memory: "TasteMemory") -> str:
    """Build the taste.memory content block for the prompt."""
    entries = memory.entries()
    if not entries:
        return ""

    principles = memory.principles()
    if not principles:
        return ""

    parts = ["\n## taste.memory (What We've Learned)"]
    parts.append("\nThese principles were extracted from past REVISE/REJECT verdicts:")
    for p in principles[-10:]:  # Last 10 principles
        parts.append(f"- {p}")

    stats = memory.stats()
    parts.append(f"\nMemory stats: {stats['total']} total, {stats['revise']} revise, {stats['reject']} reject")

    return "\n".join(parts)


def _build_files_block(
    output_files: list[str],
    file_contents: dict[str, str],
) -> str:
    """Build the output files content block."""
    if not output_files:
        return ""

    parts = ["\n## Output to Evaluate\n"]
    for filename in output_files:
        content = file_contents.get(filename, f"[File not provided: {filename}]")
        # Truncate very long files
        if len(content) > 8000:
            content = content[:8000] + "\n\n[...truncated...]"
        parts.append(f"\n### {filename}\n```\n{content}\n```")

    return "\n".join(parts)
