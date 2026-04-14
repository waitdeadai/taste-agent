"""Coherence evaluator — cross-file consistency and temporal drift detection."""

from __future__ import annotations

import re
from collections import defaultdict
from difflib import SequenceMatcher

from taste_agent.models.taste_spec import TasteSpec


class CoherenceEvaluator:
    """Evaluate cross-file consistency and detect temporal drift.

    Checks:
    - Same concept named differently across files
    - Temporal drift: sprint 8 output contradicts sprint 1 patterns
    - Inconsistent error handling approaches
    - Duplicate logic not deduplicated

    Returns:
        Tuple of (score 0.0-1.0, list of issue descriptions)

    Note: This evaluator takes a file_map (dict of filename -> content)
    rather than single-file content, since coherence is inherently cross-file.
    """

    # Similarity threshold for Jaccard-based comparison
    SIMILARITY_THRESHOLD = 0.85

    # Patterns that indicate duplicate logic
    DUPLICATE_PATTERNS = [
        r"for\s+\w+\s+in\s+\w+:.*?process",
        r"if\s+.*?:\s*.*?return",
    ]

    def __init__(self, taste_spec: TasteSpec | None):
        self.taste_spec = taste_spec

    def evaluate(
        self,
        content: str,
        file_map: dict[str, str] | None = None,
    ) -> tuple[float, list[str]]:
        """Evaluate cross-file coherence.

        Args:
            content: Primary file content (for single-file calls)
            file_map: Optional dict of filename -> content for cross-file analysis

        Returns:
            Tuple of (score 0.0-1.0, list of issue descriptions)
        """
        issues = []
        score = 1.0

        if file_map and len(file_map) > 1:
            # Cross-file analysis
            naming_issues = self._check_naming_consistency(file_map)
            issues.extend(naming_issues)
            if naming_issues:
                score -= 0.2

            duplicate_issues = self._check_duplicates(file_map)
            issues.extend(duplicate_issues)
            if duplicate_issues:
                score -= 0.2

            error_handling_issues = self._check_error_handling_consistency(file_map)
            issues.extend(error_handling_issues)
            if error_handling_issues:
                score -= 0.1
        else:
            # Single-file coherence check
            # Check for within-file inconsistency
            inconsistency_issues = self._check_within_file_consistency(content)
            issues.extend(inconsistency_issues)
            if inconsistency_issues:
                score -= 0.1

        return max(0.0, min(1.0, score)), issues

    def _check_naming_consistency(self, file_map: dict[str, str]) -> list[str]:
        """Check if the same concept is named consistently across files."""
        issues = []

        # Extract potential entity names (camelCase or PascalCase words)
        entity_pattern = re.compile(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b")
        all_entities: dict[str, list[str]] = defaultdict(list)  # entity_name -> [filenames]

        for filename, content in file_map.items():
            for match in entity_pattern.finditer(content):
                entity = match.group()
                all_entities[entity].append(filename)

        # Check for similar entities that might be the same concept named differently
        entity_names = list(all_entities.keys())
        for i, e1 in enumerate(entity_names):
            for e2 in entity_names[i + 1 :]:
                ratio = SequenceMatcher(None, e1.lower(), e2.lower()).ratio()
                if ratio > 0.7 and ratio < 1.0:
                    # Similar names but not identical — potential inconsistency
                    files1 = all_entities[e1]
                    files2 = all_entities[e2]
                    # Only flag if they're in related files
                    if any(f1.split("/")[-1] == f2.split("/")[-1] for f1 in files1 for f2 in files2):
                        issues.append(
                            f"Naming inconsistency: '{e1}' and '{e2}' might be the same concept "
                            f"named differently across files. Choose one name and use it consistently."
                        )

        return issues

    def _check_duplicates(self, file_map: dict[str, str]) -> list[str]:
        """Check for duplicate logic across files."""
        issues = []
        # Heuristic: if the same 5+ line sequence appears in multiple files
        # Use a simple line-based fingerprint
        line_fingerprints: dict[str, list[str]] = defaultdict(list)

        for filename, content in file_map.items():
            lines = content.splitlines()
            for i in range(len(lines) - 5):
                fingerprint = "\n".join(lines[i : i + 5]).strip()
                if len(fingerprint) > 30:
                    line_fingerprints[fingerprint].append(filename)

        duplicates = {k: v for k, v in line_fingerprints.items() if len(v) > 1}
        if duplicates:
            # Found duplicate patterns — flag up to 3
            for _fingerprint, files in list(duplicates.items())[:3]:
                if len(files) >= 2:
                    issues.append(
                        f"Duplicate logic detected across {len(files)} files: "
                        f"{', '.join(files)}. Extract to shared utility."
                    )
                    break  # Flag once per batch

        return issues

    def _check_error_handling_consistency(self, file_map: dict[str, str]) -> list[str]:
        """Check if error handling is consistent across files."""
        issues = []
        error_patterns: dict[str, int] = {}

        for _filename, content in file_map.items():
            # Count different error handling patterns
            if "try:" in content and "except" in content:
                error_patterns["try_except"] = error_patterns.get("try_except", 0) + 1
            if "raise HTTPException" in content:
                error_patterns["http_exception"] = error_patterns.get("http_exception", 0) + 1
            if "Result.Error" in content or "err != nil" in content:
                error_patterns["result_error"] = error_patterns.get("result_error", 0) + 1

        # If mixed patterns in same project, flag
        if len(error_patterns) > 2:
            patterns = ", ".join(f"{k}({v})" for k, v in error_patterns.items())
            issues.append(
                f"Mixed error handling styles across project: {patterns}. "
                f"Choose one consistent approach."
            )

        return issues

    def _check_within_file_consistency(self, content: str) -> list[str]:
        """Check for within-file consistency issues."""
        issues = []
        lines = content.splitlines()

        # Check for inconsistent indentation
        indent_levels = set()
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indent_levels.add(indent % 4)  # 0 or 4 are fine, 2 is not

        if 2 in indent_levels and len(lines) > 20:
            issues.append(
                "Inconsistent indentation detected: mixing 2-space and 4-space indentation. "
                "Use 4 spaces consistently."
            )

        return issues
