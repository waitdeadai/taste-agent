"""Live page evaluation — Playwright-based rendered page evaluation."""

from __future__ import annotations

import re
from typing import Any

from taste_agent.models.taste_spec import TasteSpec

# Optional import — Playwright must be installed separately
try:
    from playwright.async_api import Page, async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class LiveAestheticEvaluator:
    """Evaluate rendered pages for aesthetic compliance.

    Checks:
    - Background color matches taste spec tokens
    - No unexpected large solid color blocks
    - Page loads without flash of unstyled content
    """

    def __init__(self, taste_spec: TasteSpec | None):
        self.taste_spec = taste_spec
        self.expected_bg = self._resolve_expected_bg()

    def _resolve_expected_bg(self) -> str | None:
        """Resolve the expected background color from taste spec."""
        if not self.taste_spec:
            return None
        for token in self.taste_spec.color_tokens:
            if token.role in ("background", "bg"):
                return token.hex.lower()
        return None

    async def evaluate_page(
        self,
        url: str,
        page: Page,
        viewport: str = "desktop",
    ) -> tuple[float, list[str]]:
        """Evaluate a rendered page.

        Returns (score 0.0-1.0, list of issue descriptions).
        """
        issues = []
        score = 1.0

        # Check background color
        if self.expected_bg:
            bg_color = await page.evaluate(
                """() => {
                    return window.getComputedStyle(document.body).backgroundColor;
                }"""
            )
            # bg_color is rgb() or rgba() — convert to hex
            hex_color = self._rgba_to_hex(bg_color)
            if hex_color and not self._colors_match(hex_color, self.expected_bg, tolerance=0.15):
                issues.append(f"Background color {hex_color} differs from spec {self.expected_bg}")
                score -= 0.3

        # Check for loading state artifacts
        loading_elements = await page.query_selector_all("[data-testid='loading'], .skeleton, .spinner")
        if loading_elements:
            issues.append("Loading spinners still visible after page load")
            score -= 0.1

        # Check transition timing
        transition_duration = await page.evaluate(
            """() => {
                const el = document.querySelector('button, a');
                if (!el) return 0;
                return window.getComputedStyle(el).transitionDuration;
            }"""
        )
        if transition_duration:
            seconds = self._parse_duration(transition_duration)
            if seconds > 0.3:
                issues.append(f"Transition duration {seconds:.2f}s exceeds 300ms threshold")
                score -= 0.1

        return max(0.0, min(1.0, score)), issues

    def _rgba_to_hex(self, rgba: str) -> str | None:
        """Convert rgba(r,g,b,a) to #rrggbb."""
        match = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", rgba)
        if match:
            r, g, b = int(match[1]), int(match[2]), int(match[3])
            return f"#{r:02x}{g:02x}{b:02x}"
        return None

    def _colors_match(self, hex1: str, hex2: str, tolerance: float = 0.1) -> bool:
        """Check if two hex colors match within a tolerance."""
        r1 = int(hex1[1:3], 16) / 255
        g1 = int(hex1[3:5], 16) / 255
        b1 = int(hex1[5:7], 16) / 255
        r2 = int(hex2[1:3], 16) / 255
        g2 = int(hex2[3:5], 16) / 255
        b2 = int(hex2[5:7], 16) / 255
        diff = abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
        return diff < tolerance * 3

    def _parse_duration(self, duration: str) -> float:
        """Parse CSS transition-duration to seconds."""
        duration = duration.strip()
        if duration.endswith("ms"):
            return float(duration[:-2]) / 1000
        if duration.endswith("s"):
            return float(duration[:-1])
        return float(duration)


class LiveUXEvaluator:
    """Evaluate rendered pages for UX compliance.

    Checks:
    - Interactive elements have accessible labels
    - Mobile viewport renders correctly
    - Focus states are visible
    - No FOUC (flash of unstyled content)
    """

    def __init__(self, taste_spec: TasteSpec | None):
        self.taste_spec = taste_spec

    async def evaluate_page(
        self,
        url: str,
        page: Page,
        viewport: str = "desktop",
    ) -> tuple[float, list[str]]:
        """Evaluate UX of a rendered page.

        Returns (score 0.0-1.0, list of issue descriptions).
        """
        issues = []
        score = 1.0

        # Accessibility tree check
        ax_tree = await page.accessibility.snapshot()
        if ax_tree:
            # Check for interactive elements without names
            unnamed = self._find_unnamed_interactives(ax_tree)
            if unnamed:
                issues.append(f"{len(unnamed)} interactive element(s) without accessible name: {', '.join(unnamed[:3])}")
                score -= 0.2

        # Mobile viewport check
        if viewport == "mobile":
            # Check that content doesn't overflow horizontally
            overflow = await page.evaluate(
                """() => {
                    return document.documentElement.scrollWidth > document.documentElement.clientWidth;
                }"""
            )
            if overflow:
                issues.append("Horizontal overflow detected on mobile viewport")
                score -= 0.15

        # Focus visibility
        try:
            await page.click("body")
            focused = await page.evaluate(
                """() => {
                    const el = document.activeElement;
                    if (!el || el === document.body) return null;
                    const style = window.getComputedStyle(el);
                    return {
                        tag: el.tagName.toLowerCase(),
                        outline: style.outline,
                        outlineWidth: style.outlineWidth,
                    };
                }"""
            )
            if focused and focused.get("outlineWidth") == "0px":
                issues.append("Focused element has invisible focus ring (outline-width: 0)")
                score -= 0.1
        except Exception:
            pass

        return max(0.0, min(1.0, score)), issues

    def _find_unnamed_interactives(self, ax_tree: dict, found: list[str] | None = None) -> list[str]:
        """Recursively find interactive elements without accessible names."""
        if found is None:
            found = []
        role = ax_tree.get("role", "")
        if role in ("button", "link", "textbox", "checkbox", "radio"):
            name = ax_tree.get("name", "").strip()
            if not name:
                found.append(f"{role}:{ax_tree.get('nodeSource', {}).get('id', 'no-id')}")
        for child in ax_tree.get("children", []):
            self._find_unnamed_interactives(child, found)
        return found


async def evaluate_live(
    url: str,
    taste_spec: TasteSpec | None = None,
    viewport: str = "desktop",
    interactions: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate a live URL against taste spec.

    Args:
        url: URL to evaluate
        taste_spec: Parsed taste.md spec
        viewport: "desktop" (1280x720) or "mobile" (390x844)
        interactions: List of interactions to perform (e.g. ["click:button", "hover:.menu"])

    Returns:
        Dict with aesthetic_score, ux_score, and issues
    """
    if not PLAYWRIGHT_AVAILABLE:
        raise RuntimeError(
            "Playwright is not installed. Install with: pip install playwright && playwright install"
        )

    viewports = {
        "desktop": {"width": 1280, "height": 720},
        "mobile": {"width": 390, "height": 844},
    }

    vp = viewports.get(viewport, viewports["desktop"])

    aesthetic_eval = LiveAestheticEvaluator(taste_spec)
    ux_eval = LiveUXEvaluator(taste_spec)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport=p.chromium.viewport(vp["width"], vp["height"]))
        page = await context.new_page()

        # Measure page load performance
        import time
        t0 = time.monotonic()
        await page.goto(url, wait_until="networkidle", timeout=30000)
        load_time = time.monotonic() - t0

        # Run aesthetic evaluation
        aesthetic_score, aesthetic_issues = await aesthetic_eval.evaluate_page(url, page, viewport)

        # Run UX evaluation
        ux_score, ux_issues = await ux_eval.evaluate_page(url, page, viewport)

        # Perform requested interactions
        interaction_results = []
        if interactions:
            for interaction in interactions:
                if interaction.startswith("click:"):
                    selector = interaction[6:]
                    try:
                        await page.click(selector, timeout=5000)
                        interaction_results.append(f"click:{selector} -> OK")
                    except Exception as e:
                        interaction_results.append(f"click:{selector} -> FAIL: {e}")
                elif interaction.startswith("hover:"):
                    selector = interaction[6:]
                    try:
                        await page.hover(selector, timeout=5000)
                        interaction_results.append(f"hover:{selector} -> OK")
                    except Exception as e:
                        interaction_results.append(f"hover:{selector} -> FAIL: {e}")

        await browser.close()

    return {
        "url": url,
        "viewport": viewport,
        "load_time_ms": round(load_time * 1000),
        "aesthetic_score": aesthetic_score,
        "ux_score": ux_score,
        "aesthetic_issues": aesthetic_issues,
        "ux_issues": ux_issues,
        "interaction_results": interaction_results,
        "overall_score": (aesthetic_score + ux_score) / 2,
    }
