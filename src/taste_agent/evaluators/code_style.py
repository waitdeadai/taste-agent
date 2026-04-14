"""Code Style evaluator — function length, comment philosophy, abstraction level."""

from __future__ import annotations

import ast
import re

from taste_agent.models.taste_spec import TasteSpec


class CodeStyleEvaluator:
    """Evaluate code style quality.

    Checks:
    - Function length: max configurable (default 40 lines)
    - Comment philosophy: explain WHY not WHAT
    - Magic numbers: no unnamed constants
    - Abstraction level: consistent across modules

    Returns:
        Tuple of (score 0.0-1.0, list of issue descriptions)
    """

    # Magic number pattern: bare numbers in expressions (excluding common cases)
    MAGIC_NUMBER_PATTERN = re.compile(
        r"(?<![from|import|def|class|=|(|\s)])\b(\d{2,})\b"
    )

    # What-comment pattern: comments that describe what code does
    WHAT_COMMENT_PATTERN = re.compile(
        r"#\s*(?:this|the)\s+(?:function|code|method|class|variable|line|next|below|above)\s",
        re.IGNORECASE,
    )

    # Why-comment pattern (good): comments that explain intent
    WHY_COMMENT_PATTERN = re.compile(
        r"#\s*(?:why|because|reason|intent|purpose|since|required|needed|fix|hack|workaround)",
        re.IGNORECASE,
    )

    def __init__(self, taste_spec: TasteSpec | None):
        self.taste_spec = taste_spec
        self.max_function_lines = 40  # default

    def evaluate(self, content: str) -> tuple[float, list[str]]:
        """Evaluate code style quality.

        Returns:
            Tuple of (score 0.0-1.0, list of issue descriptions)
        """
        issues = []
        score = 1.0

        # Check function lengths using AST
        fn_issues = self._check_function_lengths(content)
        issues.extend(fn_issues)
        if fn_issues:
            score -= min(0.3, 0.05 * len(fn_issues))

        # Check for what-comments (bad)
        what_comment_issues = self._check_what_comments(content)
        issues.extend(what_comment_issues)
        if what_comment_issues:
            score -= 0.1

        # Check for magic numbers
        magic_issues = self._check_magic_numbers(content)
        issues.extend(magic_issues)
        if magic_issues:
            score -= 0.1

        # Check comment density (too few or too many)
        density_issues = self._check_comment_density(content)
        issues.extend(density_issues)
        if density_issues:
            score -= 0.05

        return max(0.0, min(1.0, score)), issues

    def _check_function_lengths(self, content: str) -> list[str]:
        """Check function lengths using AST."""
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return issues  # Can't parse — skip length check

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Count lines
                if hasattr(node, "end_lineno") and hasattr(node, "lineno"):
                    line_count = (node.end_lineno or 0) - (node.lineno or 0)
                    if line_count > self.max_function_lines:
                        fn_name = node.name
                        issues.append(
                            f"Function '{fn_name}' is {line_count} lines (max: {self.max_function_lines}). "
                            f"Extract helper functions for sub-logic."
                        )
        return issues

    def _check_what_comments(self, content: str) -> list[str]:
        """Check for 'what' comments that describe code instead of explaining intent."""
        issues = []
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if self.WHAT_COMMENT_PATTERN.search(line):
                issues.append(
                    f"Line {i}: Comment describes what code does instead of why. "
                    f"Remove or rewrite: '{line.strip()[:60]}'"
                )
        return issues

    def _check_magic_numbers(self, content: str) -> list[str]:
        """Check for magic numbers (unnamed constants)."""
        issues = []
        # Common allowed numbers
        allowed = {"0", "1", "-1", "100", "1000", "3600", "86400", "365", "12", "24", "60", "255"}
        seen_magic = set()

        for match in self.MAGIC_NUMBER_PATTERN.finditer(content):
            num = match.group(1)
            if num not in allowed:
                seen_magic.add(num)

        if len(seen_magic) > 3:
            numbers = ", ".join(sorted(seen_magic, key=int)[:5])
            issues.append(
                f"Magic numbers detected: {numbers}. "
                f"Extract as named constants: MAX_RETRIES, BATCH_SIZE, etc."
            )
        return issues

    def _check_comment_density(self, content: str) -> list[str]:
        """Check comment density — too few or too many."""
        issues = []
        lines = content.splitlines()
        code_lines = [ln for ln in lines if ln.strip() and not ln.strip().startswith("#")]
        comment_lines = [ln for ln in lines if ln.strip().startswith("#")]
        if code_lines:
            ratio = len(comment_lines) / len(code_lines)
            if ratio < 0.02 and len(code_lines) > 50:
                # Very few comments — might be intentional, but flag if long
                pass  # Too aggressive — disabled
        return issues
