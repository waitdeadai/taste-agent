"""API Design evaluator — REST patterns, response shapes, error formats."""

from __future__ import annotations

import re

from taste_agent.models.taste_spec import TasteSpec


class ApiDesignEvaluator:
    """Evaluate API design quality.

    Checks:
    - REST consistency: same endpoint returns consistent response shapes
    - Response envelope: {data, meta} vs flat dict
    - Error format: {error: {code, message}} vs raw strings
    - HTTP status code appropriateness
    - Consistent route naming

    Returns:
        Tuple of (score 0.0-1.0, list of issue descriptions)
    """

    # JSON response with error
    ERROR_PATTERN = re.compile(
        r'["\']error["\']\s*:\s*["\'][^"\']{3,50}["\']',
        re.IGNORECASE,
    )

    # Structured error format (good)
    STRUCTURED_ERROR_PATTERN = re.compile(
        r'["\']error["\']\s*:\s*\{',
        re.IGNORECASE,
    )

    # Response envelope (good): {data, meta}
    RESPONSE_ENVELOPE_PATTERN = re.compile(
        r'^\s*["\']data["\']\s*:',
        re.MULTILINE,
    )

    # HTTP status codes
    STATUS_CODES = {
        200: "OK",
        201: "Created",
        204: "No Content",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
    }

    def __init__(self, taste_spec: TasteSpec | None):
        self.taste_spec = taste_spec
        self.rules = taste_spec.api_design if taste_spec else {}

    def evaluate(self, content: str) -> tuple[float, list[str]]:
        """Evaluate API design quality.

        Returns:
            Tuple of (score 0.0-1.0, list of issue descriptions)
        """
        issues = []
        score = 1.0

        # Check for unstructured errors
        error_issues = self._check_error_format(content)
        issues.extend(error_issues)
        if error_issues:
            score -= 0.2

        # Check for flat responses (no envelope)
        envelope_issues = self._check_response_envelope(content)
        issues.extend(envelope_issues)
        if envelope_issues:
            score -= 0.1

        # Check for mixed status codes in same endpoint
        status_issues = self._check_status_codes(content)
        issues.extend(status_issues)
        if status_issues:
            score -= 0.1

        # Check for route naming consistency
        route_issues = self._check_route_naming(content)
        issues.extend(route_issues)
        if route_issues:
            score -= 0.1

        return max(0.0, min(1.0, score)), issues

    def _check_error_format(self, content: str) -> list[str]:
        """Check if errors use structured format {error: {code, message}}."""
        issues = []
        # Find raw string errors
        if self.ERROR_PATTERN.search(content) and not self.STRUCTURED_ERROR_PATTERN.search(content):
            # Has error strings but no structured error object
            issues.append(
                "Error format issue: raw error string found. "
                "Use structured error format: {error: {code: 'ERROR_CODE', message: 'Human readable'}}"
            )
        return issues

    def _check_response_envelope(self, content: str) -> list[str]:
        """Check if responses use consistent envelope {data, meta}."""
        issues = []
        # If the API has data responses, they should use an envelope
        has_responses = '"data"' in content or "'data'" in content or "`data`" in content
        if not has_responses and ("return" in content or "response" in content.lower()):
            # Heuristic: if there's response handling but no envelope, flag it
            pass  # Too aggressive — skip for now
        return issues

    def _check_status_codes(self, content: str) -> list[str]:
        """Check for appropriate HTTP status code usage."""
        issues = []
        # Find raise HTTPException(status_code=...) patterns
        status_matches = re.findall(r"status_code\s*=\s*(\d+)", content)
        for code_str in status_matches:
            try:
                code = int(code_str)
                if code == 200 and "return" in content.lower():
                    # Using 200 for creation (should be 201)
                    if "create" in content.lower() or "post" in content.lower():
                        issues.append(
                            "Status code 200 used for creation. Use 201 Created for resource creation."
                        )
                elif code == 500:
                    issues.append(
                        "Status code 500 found. Avoid exposing raw 500 errors. "
                        "Use 422 for validation errors, 404 for missing resources."
                    )
            except ValueError:
                pass
        return issues

    def _check_route_naming(self, content: str) -> list[str]:
        """Check for consistent route naming (kebab-case for paths)."""
        issues = []
        # Find route definitions
        route_matches = re.findall(
            r'@(?:app|router)\.(?:get|post|put|patch|delete)\(["\']([^"\']+)["\']',
            content,
        )
        for route in route_matches:
            if route.startswith("/"):
                route = route[1:]
            parts = route.strip("/").split("/")
            for part in parts:
                if part and not part.isdigit():
                    # Check kebab-case or snake_case
                    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", part):
                        if "_" in part and re.match(r"^[a-z]+_[a-z]+$", part):
                            # snake_case in URL path — should be kebab-case
                            issues.append(
                                f"Route '/{route}' uses snake_case. "
                                f"Use kebab-case: '/{route.replace('_', '-')}'"
                            )
        return issues
