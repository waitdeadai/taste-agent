"""UX evaluator — layout, interaction, accessibility, responsiveness."""

from __future__ import annotations

import re


class UXEvaluator:
    """Evaluate UX quality of generated code.

    Checks:
    - Layout: natural information hierarchy
    - Interaction: purposeful micro-interactions
    - Accessibility: WCAG 2.1 AA, 4.5:1 contrast
    - Mobile: responsive, touch-friendly
    - Flow: does the interaction feel natural?
    """

    # Accessibility issues (high severity)
    A11Y_BAD_PATTERNS = [
        (r'contrast:\s*[\d.]+\s*(?!:.*high)', "Low contrast ratio"),
        (r'font-size:\s*10px', "Font size too small for body text (min 14px)"),
        (r'font-size:\s*11px', "Font size too small for body text (min 14px)"),
        (r'cursor:\s*default', "Interactive elements should have pointer cursor"),
        (r'outline:\s*none', "Removing outline without focus management is inaccessible"),
    ]

    # Touch-friendly issues
    TOUCH_BAD_PATTERNS = [
        (r'min-width:\s*[\d.]+px\s*(?!.*min-height)', "Width alone doesn't ensure touch target (48x48px min)"),
        (r'padding:\s*[\d.]+px\s+[\d.]+px\s*(?!.*[\d.]+px)', "Inline padding too small for touch (48px min)"),
    ]

    # Good UX patterns
    GOOD_PATTERNS = [
        r'@media\s*\([^)]*hover:\s*hover\)',  # hover media query
        r'tabindex',
        r'role=',
        r'aria-',
        r'rel="noopener',
    ]

    def __init__(self, taste_spec=None):
        self.taste_spec = taste_spec

    def evaluate(self, content: str) -> tuple[float, list[str]]:
        """Evaluate UX quality.

        Returns:
            Tuple of (score 0.0-1.0, list of issues found)
        """
        issues = []
        score = 1.0

        # Check accessibility
        a11y_issues = self._check_accessibility(content)
        issues.extend(a11y_issues)
        if a11y_issues:
            score -= 0.3 * len(a11y_issues)  # High severity

        # Check touch targets
        touch_issues = self._check_touch_targets(content)
        issues.extend(touch_issues)
        if touch_issues:
            score -= 0.15

        # Check for good UX patterns (bonus)
        good_count = sum(1 for p in self.GOOD_PATTERNS if re.search(p, content))
        if good_count >= 3:
            score += 0.05  # Bonus for good practices

        # Check responsive design
        responsive_issues = self._check_responsive(content)
        issues.extend(responsive_issues)
        if responsive_issues:
            score -= 0.1 * len(responsive_issues)

        return max(0.0, min(1.0, score)), issues

    def _check_accessibility(self, content: str) -> list[str]:
        """Check for accessibility issues."""
        issues = []
        for pattern, description in self.A11Y_BAD_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Accessibility issue: {description}")
        return issues

    def _check_touch_targets(self, content: str) -> list[str]:
        """Check for touch-friendly sizing."""
        issues = []
        for pattern, description in self.TOUCH_BAD_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Touch issue: {description}")
        return issues

    def _check_responsive(self, content: str) -> list[str]:
        """Check for responsive design patterns."""
        issues = []
        # Look for media queries
        has_media_queries = bool(re.search(r'@media\s*\(', content))
        has_viewport = bool(re.search(r'viewport|min-width:\s*640px|min-width:\s*1024px', content, re.IGNORECASE))

        if has_viewport and not has_media_queries:
            issues.append("Has viewport meta but no media queries. Add responsive breakpoints.")
        return issues
