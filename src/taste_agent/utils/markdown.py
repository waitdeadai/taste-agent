"""Markdown parsing utilities for taste.md."""

from __future__ import annotations

import re


def extract_code_blocks(markdown: str) -> list[tuple[str, str]]:
    """Extract (language, code) tuples from a markdown string.

    Returns:
        List of (language, code) tuples, newest first.
    """
    pattern = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
    matches = pattern.findall(markdown)
    return list(reversed(matches))


def extract_color_tokens(markdown: str) -> list[dict[str, str]]:
    """Extract color tokens from taste.md.

    Looks for patterns like:
    - | Name | Hex | Role |
    - - Primary: #ff6b35 (CTAs)

    Returns:
        List of {"name", "hex", "role"} dicts.
    """
    tokens = []

    # Markdown table format
    table_pattern = re.compile(r"\|(.+?)\|(.+?)\|(.+?)\|", re.MULTILINE)
    for row in table_pattern.finditer(markdown):
        name = row.group(1).strip().lower()
        hex_val = row.group(2).strip()
        role = row.group(3).strip().lower()
        if hex_val.startswith("#") and len(hex_val) in (7, 9):
            tokens.append({"name": name, "hex": hex_val, "role": role})

    # Bullet point format
    bullet_pattern = re.compile(r"-?\s*(.+?):\s*(#[0-9a-fA-F]{6,8})\s*\((.+)\)", re.MULTILINE)
    for match in bullet_pattern.finditer(markdown):
        tokens.append({
            "name": match.group(1).strip().lower(),
            "hex": match.group(2),
            "role": match.group(3),
        })

    return tokens


def extract_non_negotiables(markdown: str) -> list[str]:
    """Extract non-negotiable rules from taste.md.

    Looks for patterns like:
    - NO Tailwind CSS
    - ## Non-Negotiables
      - NO emoji in UI
    """
    rules = []

    # "NO X" pattern
    no_pattern = re.compile(r"NO\s+(.+?)(?:\n|$)", re.IGNORECASE)
    for match in no_pattern.finditer(markdown):
        rule = match.group(1).strip()
        if rule and len(rule) > 2:
            rules.append(rule)

    return rules
