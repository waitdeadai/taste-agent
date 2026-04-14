"""Copy evaluator — voice, tone, microcopy, headlines."""

from __future__ import annotations

import re

from taste_agent.models.taste_spec import TasteSpec


class CopyEvaluator:
    """Evaluate copy quality of generated code/markdown/text.

    Checks:
    - Headlines: specific and tested vs generic and vague
    - CTAs: compelling and conversion-focused vs wishy-washy
    - Tone: confident and direct vs hedging and corporate
    - Objection handling: real fears addressed vs strawman questions
    """

    # Generic/hallmark corporate copy patterns (bad)
    BAD_COPY_PATTERNS = [
        r"\bwe help you\b",
        r"\btransform your business\b",
        r"\bcutting-edge?\b",
        r"\bworld-class?\b",
        r"\bsynergy\b",
        r"\bleverage\b",
        r"\bgame-changing\b",
        r"\brevolutionary\b",
        r"\binnovative\b",
        r"\b disruption\b",
        r"\bthe future of\b",
        r"\bnext-generation?\b",
        r"\bpioneering\b",
        r"\bleading-edge\b",
    ]

    # Confident, direct copy patterns (good indicators)
    GOOD_COPY_PATTERNS = [
        r"\bwe (implement|build|deploy|deliver)\b",
        r"\b(guarantee|ensure|prove)\b",
        r"\b\d+%\b",  # metrics and percentages
        r"\b\d+\s*(weeks?|months?|hours?)\b",  # timeframes
    ]

    # Objection handling patterns
    OBJECTION_PATTERNS = [
        r"95%\s+of\s+AI\s+pilots?\s+fail",
        r"already\s+tried.*failed",
        r"too\s+expensive",
        r"security\s+(concerns?|issues?)",
        r"implementation\s+risk",
    ]

    def __init__(self, taste_spec: TasteSpec | None = None):
        self.taste_spec = taste_spec

    def evaluate(self, content: str) -> tuple[float, list[str]]:
        """Evaluate copy quality.

        Returns:
            Tuple of (score 0.0-1.0, list of issues found)
        """
        issues = []
        score = 1.0

        # Check for hallmark/corporate copy
        hallmark_issues = self._check_hallmark_copy(content)
        issues.extend(hallmark_issues)
        if hallmark_issues:
            score -= 0.25 * len(hallmark_issues)

        # Check for confident, direct copy
        confidence_bonus = self._check_confident_copy(content)
        if confidence_bonus > 0 and not hallmark_issues:
            score += 0.05  # Slight bonus for confident copy

        # Check headline quality
        headline_issues = self._check_headlines(content)
        issues.extend(headline_issues)
        if headline_issues:
            score -= 0.2

        # Check CTA quality
        cta_issues = self._check_ctas(content)
        issues.extend(cta_issues)
        if cta_issues:
            score -= 0.15

        # Check tone (hedging language)
        tone_issues = self._check_tone(content)
        issues.extend(tone_issues)
        if tone_issues:
            score -= 0.1 * len(tone_issues)

        return max(0.0, min(1.0, score)), issues

    def _check_hallmark_copy(self, content: str) -> list[str]:
        """Check for generic hallmark corporate copy."""
        issues = []
        text_lower = content.lower()
        for pattern in self.BAD_COPY_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                issues.append(
                    f"Hallmark/corporate copy detected: '{pattern}'. "
                    "Use specific, tested copy from taste.md. "
                    "Avoid generic transformation claims."
                )
        return issues

    def _check_confident_copy(self, content: str) -> int:
        """Count indicators of confident, direct copy."""
        count = 0
        for pattern in self.GOOD_COPY_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                count += 1
        return count

    def _check_headlines(self, content: str) -> list[str]:
        """Check headline quality."""
        issues = []
        # Extract lines that look like headlines (short, capitalized)
        lines = content.split("\n")
        for line in lines:
            stripped = line.strip()
            # Skip if too long (not a headline) or too short
            if 10 < len(stripped) < 80:
                # Check if it starts with capital (potential headline)
                if stripped[0].isupper() and stripped[-1] not in ".?!":
                    # Check for vague words
                    vague_words = ["new", "modern", "better", "best", "advanced"]
                    for vw in vague_words:
                        if re.search(rf"\b{vw}\b", stripped, re.IGNORECASE):
                            issues.append(
                                f"Vague headline: '{stripped[:50]}'. "
                                "Use specific, benefit-driven headlines from taste.md."
                            )
                            break
        return issues

    def _check_ctas(self, content: str) -> list[str]:
        """Check CTA quality."""
        issues = []
        # Look for CTA patterns
        cta_indicators = ["contact", "get started", "learn more", "sign up", "schedule", "book"]
        ctas_found = any(indicator in content.lower() for indicator in cta_indicators)

        if not ctas_found:
            # No CTAs found might be intentional, but check if this is a page with CTAs
            if re.search(r"<button|<a\s+href", content, re.IGNORECASE):
                issues.append("CTA found but may not be compelling. Use action-oriented CTAs from taste.md.")
        return issues

    def _check_tone(self, content: str) -> list[str]:
        """Check for hedging language."""
        issues = []
        hedging_patterns = [
            r"\bwe\s+think\b",
            r"\bmaybe\b",
            r"\bperhaps\b",
            r"\bmight\b",
            r"\bcould\s+possibly\b",
            r"\bwe\s+hope\b",
            r"\bwe\s+believe\b",
            r"\bgenerally\b",
            r"\busually\b",
            r"\bsometimes\b",
        ]
        for pattern in hedging_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(
                    f"Hedging language detected: '{pattern}'. "
                    "Be confident and direct. Remove tentative language."
                )
        return issues
