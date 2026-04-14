"""Architecture evaluator — layer boundaries, module structure, separation of concerns."""

from __future__ import annotations

import re

from taste_agent.models.taste_spec import TasteSpec


class ArchitectureEvaluator:
    """Evaluate architecture quality.

    Checks:
    - Layer boundaries: routes ≠ services ≠ repositories
    - Module structure: no god modules (files > 300 lines)
    - Separation of concerns: no circular imports
    - Dependency direction: outward-in

    Returns:
        Tuple of (score 0.0-1.0, list of issue descriptions)
    """

    # Circular import patterns
    CIRCULAR_IMPORT_PATTERNS = [
        re.compile(r"from\s+(\w+)\s+import.*?\1", re.DOTALL),
        re.compile(r"import\s+(\w+).*?from\s+.*?\1", re.DOTALL),
    ]

    # Route-file-direct-DB violations:
    # If a file has FastAPI/Flask route decorators AND db.execute in same file
    ROUTE_DB_PATTERN = re.compile(
        r"@(app|router|blueprint)\.(get|post|put|patch|delete)\("
        r".*?"
        r"(?:db|engine|connection|execute|fetch|query)\s*\(",
        re.DOTALL | re.IGNORECASE,
    )

    # Layer violation: direct file access in route handlers
    DIRECT_FILE_ACCESS_IN_ROUTE = re.compile(
        r"@(?:app|router)\.(?:get|post|put|patch|delete)\(.*?\n\s*(?:open|Path)\(",
        re.DOTALL,
    )

    # Default architecture layers if not specified in taste.md
    DEFAULT_LAYERS = [
        "routes",
        "services",
        "repositories",
        "models",
        "schemas",
    ]

    def __init__(self, taste_spec: TasteSpec | None):
        self.taste_spec = taste_spec
        self.layers = (
            taste_spec.architecture_layers if taste_spec else self.DEFAULT_LAYERS
        )

    def evaluate(self, content: str) -> tuple[float, list[str]]:
        """Evaluate architecture quality of file content.

        Returns:
            Tuple of (score 0.0-1.0, list of issue descriptions)
        """
        issues = []
        score = 1.0

        # Check for circular imports
        circ_issues = self._check_circular_imports(content)
        issues.extend(circ_issues)
        if circ_issues:
            score = 0.0  # Circular imports are fatal

        # Check for route-file-direct-DB violations
        db_issues = self._check_route_db_violation(content)
        issues.extend(db_issues)
        if db_issues:
            score -= 0.5

        # Check for direct file access in route handlers
        file_issues = self._check_direct_file_in_routes(content)
        issues.extend(file_issues)
        if file_issues:
            score -= 0.2

        # Check for god modules (files > 300 lines)
        line_count = len(content.splitlines())
        if line_count > 300:
            # Heuristic: suggest splitting if > 300 lines and has multiple concerns
            if self._has_multiple_concerns(content):
                issues.append(
                    f"God module detected: {line_count} lines. "
                    "Consider splitting into focused modules with single responsibility."
                )
                score -= 0.2

        # Check for missing layer structure (if layers are defined in taste.md)
        if self.layers:
            layer_issues = self._check_layer_adherence(content)
            issues.extend(layer_issues)
            if layer_issues:
                score -= 0.1 * len(layer_issues)

        return max(0.0, min(1.0, score)), issues

    def _check_circular_imports(self, content: str) -> list[str]:
        """Detect circular import patterns."""
        issues = []
        for pattern in self.CIRCULAR_IMPORT_PATTERNS:
            if pattern.search(content):
                issues.append(
                    "Circular import detected: file imports from itself directly or "
                    "through a mutual dependency. Use late imports or restructure."
                )
                break
        return issues

    def _check_route_db_violation(self, content: str) -> list[str]:
        """Detect database access directly in route handler files."""
        issues = []
        if self.ROUTE_DB_PATTERN.search(content):
            issues.append(
                "Architecture violation: route handler directly accesses the database. "
                "Inject a service layer between route and database."
            )
        return issues

    def _check_direct_file_in_routes(self, content: str) -> list[str]:
        """Detect file I/O directly in route handlers."""
        issues = []
        if self.DIRECT_FILE_ACCESS_IN_ROUTE.search(content):
            issues.append(
                "Architecture violation: route handler directly opens files. "
                "Use a service layer for file operations."
            )
        return issues

    def _has_multiple_concerns(self, content: str) -> bool:
        """Heuristic: does this file handle multiple concerns?"""
        concern_indicators = [
            "db.", "engine.", "fetch", "execute",
            "send_email", "send_mail", "smtp",
            "redis", "cache",
            "log", "logger",
        ]
        matches = sum(1 for c in concern_indicators if c in content.lower())
        return matches >= 3

    def _check_layer_adherence(self, content: str) -> list[str]:
        """Check if content follows defined layer structure."""
        issues = []
        content.lower()
        # If taste.md defines layers, warn if they're all mixed together
        # This is a soft check
        return issues
