"""Naming evaluator — consistent naming conventions across files."""

from __future__ import annotations

import re

from taste_agent.models.taste_spec import TasteSpec


class NamingEvaluator:
    """Evaluate naming consistency.

    Checks:
    - Files: snake_case.py for modules, PascalCase.py for classes
    - Functions: verb_object pattern (get_user, create_order)
    - Variables: descriptive, no single letters except counters
    - Database tables: snake_case_plural

    Returns:
        Tuple of (score 0.0-1.0, list of issue descriptions)
    """

    # Generic/bad names
    GENERIC_NAMES = [
        "data", "info", "stuff", "thing", "item", "temp", "tmp",
        "result", "output", "input", "value", "val",
        "handle", "process", "do_stuff",
    ]

    # Verb-object function pattern (good)
    VERB_OBJECT_PATTERN = re.compile(r"^[a-z][a-z0-9_]*_[a-z][a-z0-9_]*$")

    # Bad function names (camelCase, PascalCase, Hungarian)
    BAD_FUNCTION_PATTERNS = [
        re.compile(r"^[a-z]+[A-Z]"),  # camelCase: getData
        re.compile(r"^[A-Z][a-z]+[A-Z]"),  # PascalCase function: GetData
        re.compile(r"^[a-z]+_[a-z]+_[a-z]+_[a-z]+"),  # too_many_underscores
    ]

    # snake_case file check
    SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*\.py$")

    # PascalCase class check
    PASCAL_CASE_PATTERN = re.compile(r"^(?:class|Enum)\s+([A-Z][a-zA-Z0-9]*)")

    # Database table plural check
    TABLE_NAME_PATTERN = re.compile(r"(?:from|import|Table)\s+['\"]([^'\"]+)['\"]")

    def __init__(self, taste_spec: TasteSpec | None):
        self.taste_spec = taste_spec
        self.conventions = (
            taste_spec.naming_conventions if taste_spec else {}
        )

    def evaluate(self, content: str) -> tuple[float, list[str]]:
        """Evaluate naming consistency.

        Returns:
            Tuple of (score 0.0-1.0, list of issue descriptions)
        """
        issues = []
        score = 1.0

        # Check for generic/bad variable names
        generic_issues = self._check_generic_names(content)
        issues.extend(generic_issues)
        if generic_issues:
            score -= min(0.3, 0.05 * len(generic_issues))

        # Check for bad function names
        fn_issues = self._check_function_names(content)
        issues.extend(fn_issues)
        if fn_issues:
            score -= 0.1 * len(fn_issues)

        # Check for non-verb_object function names
        non_verb_issues = self._check_non_verb_object(content)
        issues.extend(non_verb_issues)
        if non_verb_issues:
            score -= 0.1 * len(non_verb_issues)

        # Check class names (if PascalCase expected)
        class_issues = self._check_class_names(content)
        issues.extend(class_issues)
        if class_issues:
            score -= 0.1 * len(class_issues)

        return max(0.0, min(1.0, score)), issues

    def evaluate_file(self, filename: str, content: str) -> tuple[float, list[str]]:
        """Evaluate naming for a specific file.

        Args:
            filename: Name of the file (e.g., "user_service.py")
            content: File content

        Returns:
            Tuple of (score 0.0-1.0, list of issue descriptions)
        """
        issues = []
        score = 1.0

        # Check filename casing
        if filename.endswith(".py"):
            base = filename[:-3]
            if not self.SNAKE_CASE_PATTERN.match(base):
                # Allow PascalCase for files that define a single class (e.g., UserModel.py)
                if not self.PASCAL_CASE_PATTERN.search(content):
                    issues.append(
                        f"File '{filename}' should be snake_case.py. "
                        f"Modules containing only utility functions should use snake_case."
                    )
                    score -= 0.2

        # Run standard evaluation
        content_score, content_issues = self.evaluate(content)
        issues.extend(content_issues)
        score = score * content_score

        return max(0.0, min(1.0, score)), issues

    def _check_generic_names(self, content: str) -> list[str]:
        """Check for generic/bad variable names."""
        issues = []
        for name in self.GENERIC_NAMES:
            # Match: data, info, stuff, etc. as variable assignments
            pattern = re.compile(rf"^\s*(?:const\s+)?(?:{name})\s*=", re.MULTILINE)
            if pattern.search(content):
                issues.append(
                    f"Generic name '{name}': use descriptive names. "
                    f"'{name}' tells nothing about what the variable holds."
                )
        return issues

    def _check_function_names(self, content: str) -> list[str]:
        """Check for non-verb_object function names."""
        issues = []
        # Find all def statements
        for match in re.finditer(r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", content, re.MULTILINE):
            fn_name = match.group(1)
            for bad_pattern in self.BAD_FUNCTION_PATTERNS:
                if bad_pattern.match(fn_name):
                    issues.append(
                        f"Function '{fn_name}': use verb_object naming (e.g., get_user, create_order). "
                        f"Avoid camelCase, PascalCase, or excessive underscores."
                    )
                    break
        return issues

    def _check_non_verb_object(self, content: str) -> list[str]:
        """Check functions don't follow verb_object pattern."""
        issues = []
        verbs = {"get", "create", "update", "delete", "remove", "add", "set", "fetch", "load", "save", "send", "build", "make", "generate", "parse", "validate", "check", "is", "has", "can"}
        for match in re.finditer(r"^def\s+([a-z_][a-z0-9_]*)\s*\(", content, re.MULTILINE):
            fn_name = match.group(1)
            word = fn_name.split("_")[0] if "_" in fn_name else fn_name
            if word.lower() not in verbs:
                # Not a strict verb — could be noun (bad) or allowed (e.g., main, run)
                if fn_name.lower() not in ("main", "run", "start", "stop", "init", "setup", "teardown"):
                    issues.append(
                        f"Function '{fn_name}': should start with a verb (get, create, update, delete). "
                        f"Non-verb function names make it unclear what the function does."
                    )
        return issues

    def _check_class_names(self, content: str) -> list[str]:
        """Check class names follow PascalCase."""
        issues = []
        for match in self.PASCAL_CASE_PATTERN.finditer(content):
            class_name = match.group(1)
            if not class_name[0].isupper():
                issues.append(
                    f"Class '{class_name}': should be PascalCase. "
                    f"e.g., UserProfile, OrderItem."
                )
        return issues
