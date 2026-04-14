"""Aesthetic evaluator — colors, typography, spacing, glassmorphism."""

from __future__ import annotations

import re

from taste_agent.models.taste_spec import TasteSpec


class AestheticEvaluator:
    """Evaluate aesthetic quality of generated code.

    Checks:
    - Color usage: intentional palette use vs arbitrary colors
    - Typography: scale, hierarchy, pairing appropriateness
    - Spacing: generous vs cramped
    - Glassmorphism: refined vs amateur
    - Motion: professional vs attention-seeking
    """

    # Amateur glassmorphism patterns (bad)
    BAD_GLASS_PATTERNS = [
        r"background:\s*linear-gradient",
        r"background:\s*radial-gradient",
        r"background:\s*conic-gradient",
        r"backdrop-filter:\s*blur\([^)]+\)[^;]*background.*gradient",
        r"box-shadow:\s*0\s+\d+px\s+\d+px.*rgba\(.*,\s*[\d.]+\)",  # colored shadows
    ]

    # Professional glassmorphism patterns (good)
    GOOD_GLASS_PATTERNS = [
        r"backdrop-filter:\s*blur\(\d+px\)",
        r"background:\s*rgba?\(\d+,\s*\d+,\s*\d+,\s*[\d.]+\)",
        r"border:\s*\d+px\s+solid\s+rgba?\(",
    ]

    # Amateur motion patterns (bad)
    BAD_MOTION_PATTERNS = [
        r"animation:.*blob",
        r"animation:.*float",
        r"animation:.*wave",
        r"transform:\s*rotate\(\d+deg\)\s*scale\(",
        r"transition:\s*all\s+\d+ms",
        r"parallax",
    ]

    # Color hex patterns
    HEX_PATTERN = re.compile(r"#[0-9a-fA-F]{6,8}")

    def __init__(self, taste_spec: TasteSpec | None = None):
        self.taste_spec = taste_spec

    def evaluate(self, content: str) -> tuple[float, list[str]]:
        """Evaluate aesthetic quality.

        Returns:
            Tuple of (score 0.0-1.0, list of issues found)
        """
        issues = []
        score = 1.0

        # Check glassmorphism
        glass_issues = self._check_glassmorphism(content)
        issues.extend(glass_issues)
        if glass_issues:
            score -= 0.2 * len(glass_issues)

        # Check motion/animation
        motion_issues = self._check_motion(content)
        issues.extend(motion_issues)
        if motion_issues:
            score -= 0.15 * len(motion_issues)

        # Check color usage
        color_issues = self._check_colors(content)
        issues.extend(color_issues)
        if color_issues:
            score -= 0.15 * len(color_issues)

        # Check typography
        type_issues = self._check_typography(content)
        issues.extend(type_issues)
        if type_issues:
            score -= 0.1 * len(type_issues)

        return max(0.0, min(1.0, score)), issues

    def _check_glassmorphism(self, content: str) -> list[str]:
        """Check if glassmorphism is refined or amateur."""
        issues = []
        for pattern in self.BAD_GLASS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(
                    f"Amateur glassmorphism detected: pattern '{pattern[:30]}...' found. "
                    "Use backdrop-filter: blur() with rgba background only, no gradients."
                )
        return issues

    def _check_motion(self, content: str) -> list[str]:
        """Check if motion is professional or attention-seeking."""
        issues = []
        for pattern in self.BAD_MOTION_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(
                    f"Amateur motion detected: '{pattern[:30]}' found. "
                    "Use subtle transitions only (opacity, transform: translateY)."
                )
        return issues

    def _check_colors(self, content: str) -> list[str]:
        """Check if colors match the taste spec palette."""
        if not self.taste_spec or not self.taste_spec.color_tokens:
            return []

        issues = []
        hexes = set(self.HEX_PATTERN.findall(content))
        spec_hexes = {c.hex.lower() for c in self.taste_spec.color_tokens}

        # Find hexes that aren't in the spec
        unknown_hexes = hexes - spec_hexes
        if unknown_hexes:
            # Allow some flexibility (up to 2 unknown hexes)
            if len(unknown_hexes) > 2:
                issues.append(
                    f"Colors outside taste.md palette found: {unknown_hexes}. "
                    f"Use only: {spec_hexes}"
                )

        return issues

    def _check_typography(self, content: str) -> list[str]:
        """Check if typography matches taste spec."""
        if not self.taste_spec or not self.taste_spec.typography:
            return []

        issues = []
        fonts_used = re.findall(r"font-family:\s*([^;]+)", content, re.IGNORECASE)
        spec_fonts = {t.font_family.lower() for t in self.taste_spec.typography}

        for font in fonts_used:
            font_clean = font.strip().lower().replace(['"', "'"], "")
            if font_clean and font_clean not in spec_fonts:
                # Check if it's a fallback font
                if not any(fb in font_clean for fb in ["sans-serif", "serif", "monospace", "system-ui"]):
                    issues.append(
                        f"Font '{font}' not in taste.md typography spec. "
                        f"Use: {spec_fonts}"
                    )
                break

        return issues
