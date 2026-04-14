"""Diff visualization utilities for taste feedback."""

from __future__ import annotations


def format_diff_issue(diff: str, issue_location: str) -> str:
    """Format a diff with issue location highlighted.

    Args:
        diff: The git diff string.
        issue_location: The location of the issue (e.g., "app/page.tsx:23").

    Returns:
        A formatted diff string with the relevant lines highlighted.
    """
    if not diff or not issue_location:
        return diff

    # Parse location
    file_part = issue_location
    line_part = ""
    if ":" in issue_location:
        file_part, line_part = issue_location.rsplit(":", 1)
        try:
            int(line_part)
        except ValueError:
            line_part = ""

    lines = diff.split("\n")
    highlighted_lines = []

    for _i, line in enumerate(lines):
        # Highlight lines from the relevant file
        if file_part in line and line_part:
            highlighted_lines.append(f">>> {line} <<<")
        else:
            highlighted_lines.append(line)

    return "\n".join(highlighted_lines)
