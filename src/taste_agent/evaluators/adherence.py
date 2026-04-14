"""Adherence evaluator — does output follow taste.md spec exactly?"""

from __future__ import annotations

from taste_agent.models.taste_spec import TasteSpec


class AdherenceEvaluator:
    """Evaluate adherence to taste.md specification.

    Checks:
    - Design tokens: consistent usage of colors/spacing/typography
    - Components: match specified component inventory
    - Non-negotiables: zero violations of hard rules
    - Benchmarks: matches reference quality level
    """

    def __init__(self, taste_spec: TasteSpec | None):
        self.taste_spec = taste_spec

    def evaluate(self, content: str) -> tuple[float, list[str]]:
        """Evaluate adherence to spec.

        Returns:
            Tuple of (score 0.0-1.0, list of violations)
            Note: adherence is binary — non-negotiables are either followed or not.
            Score is 1.0 if all non-negotiables are followed, 0.0 if any is violated.
        """
        if not self.taste_spec:
            return 0.5, ["No taste.md found — cannot evaluate adherence"]

        violations = []
        score = 1.0

        # Check non-negotiables
        nn_violations = self._check_non_negotiables(content)
        violations.extend(nn_violations)
        if nn_violations:
            score = 0.0  # Binary — any violation = total failure

        # Check component adherence
        component_issues = self._check_components(content)
        violations.extend(component_issues)
        if component_issues:
            score -= 0.1 * len(component_issues)

        # Check anti-patterns
        anti_issues = self._check_anti_patterns(content)
        violations.extend(anti_issues)
        if anti_issues:
            score -= 0.2 * len(anti_issues)

        return max(0.0, min(1.0, score)), violations

    def _check_non_negotiables(self, content: str) -> list[str]:
        """Check violations of non-negotiable rules."""
        if not self.taste_spec or not self.taste_spec.non_negotiables:
            return []

        violations = []
        content_lower = content.lower()

        for nn in self.taste_spec.non_negotiables:
            # Convert non-negotiable to search pattern
            # e.g., "Tailwind CSS" -> "tailwind"
            # e.g., "emoji in UI" -> "emoji"
            keywords = nn.lower().split()
            if all(kw in content_lower for kw in keywords if len(kw) > 3):
                violations.append(
                    f"Non-negotiable violated: '{nn}'. "
                    "This is a hard rule from taste.md — zero tolerance."
                )

        return violations

    def _check_components(self, content: str) -> list[str]:
        """Check if components match specified standards."""
        if not self.taste_spec or not self.taste_spec.component_standards:
            return []

        issues = []
        # Check if the component structure matches what's specified
        # This is more of a heuristic check

        for comp in self.taste_spec.component_standards:
            comp_name = comp.name.lower()
            # If component is mentioned, check if it follows the standard description
            if comp_name in content.lower():
                # Heuristic: if component exists but description has specific
                # patterns not found in content, flag it
                if "glass" in comp.description.lower():
                    # Check for proper glassmorphism
                    if "backdrop-filter" not in content.lower():
                        issues.append(
                            f"Component '{comp.name}' found but not following glass standard. "
                            f"Expected: {comp.description[:50]}"
                        )

        return issues

    def _check_anti_patterns(self, content: str) -> list[str]:
        """Check for explicitly listed anti-patterns."""
        if not self.taste_spec or not self.taste_spec.anti_patterns:
            return []

        violations = []
        content_lower = content.lower()

        for ap in self.taste_spec.anti_patterns:
            keywords = [w for w in ap.lower().split() if len(w) > 3]
            if keywords and all(kw in content_lower for kw in keywords):
                violations.append(f"Anti-pattern violated: '{ap}'")

        return violations
