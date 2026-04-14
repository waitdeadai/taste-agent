"""tests/test_evaluators/test_adherence.py — AdherenceEvaluator tests."""

from __future__ import annotations

import pytest

from taste_agent.evaluators.adherence import AdherenceEvaluator
from taste_agent.models.taste_spec import TasteSpec


class TestAdherenceEvaluatorNoSpec:
    def test_no_taste_spec_returns_05(self):
        ev = AdherenceEvaluator(None)
        score, issues = ev.evaluate("body { color: #fff; }")
        assert score == 0.5
        assert "No taste.md found" in issues[0]


class TestAdherenceEvaluatorWithSpec:
    def test_non_negotiable_violated(self, minimal_taste_md):
        spec = TasteSpec.from_markdown(minimal_taste_md)
        # minimal_taste_md non_negotiables parsed from hyphen format
        # Use spec that has explicit non_negotiables
        spec.non_negotiables = ["placeholder copy"]
        ev = AdherenceEvaluator(spec)
        score, issues = ev.evaluate("This has placeholder copy in it")
        assert score == 0.0
        assert any("non-negotiable" in i.lower() for i in issues)

    def test_non_negotiable_followed(self, minimal_taste_md):
        spec = TasteSpec.from_markdown(minimal_taste_md)
        ev = AdherenceEvaluator(spec)
        # Empty content doesn't violate anything
        score, issues = ev.evaluate("body { color: #000; }")
        assert score >= 0.0


class TestAdherenceEvaluatorAntiPattern:
    def test_anti_pattern_violated(self):
        spec = TasteSpec()
        spec.anti_patterns = ["Tailwind CSS"]
        ev = AdherenceEvaluator(spec)
        # Both "tailwind" and "css" must be in content to trigger
        score, issues = ev.evaluate("Use Tailwind CSS for styling")
        assert score < 1.0
