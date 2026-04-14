"""tests/test_evaluators/test_aesthetic.py — AestheticEvaluator tests."""

from __future__ import annotations

import pytest

from taste_agent.evaluators.aesthetic import AestheticEvaluator
from taste_agent.models.taste_spec import ColorToken, TasteSpec


class TestAestheticEvaluatorGoodCSS:
    def test_good_css_scores_1(self, good_css):
        ev = AestheticEvaluator(None)
        score, issues = ev.evaluate(good_css)
        assert score == 1.0
        assert issues == []


class TestAestheticEvaluatorBadCSS:
    def test_bad_css_scores_less_than_1(self, bad_css):
        ev = AestheticEvaluator(None)
        score, issues = ev.evaluate(bad_css)
        assert score < 1.0
        assert len(issues) > 0


class TestAestheticEvaluatorGradient:
    def test_detects_gradient_background(self):
        ev = AestheticEvaluator(None)
        score, issues = ev.evaluate(".hero { background: linear-gradient(135deg, #667eea, #764ba2); }")
        assert score < 1.0
        assert any("gradient" in i.lower() for i in issues)


class TestAestheticEvaluatorMagicShadow:
    def test_detects_colored_shadow(self):
        ev = AestheticEvaluator(None)
        score, issues = ev.evaluate(".magic { box-shadow: 0 4px 20px rgba(100,50,200,0.5); }")
        assert score < 1.0


class TestAestheticEvaluatorNoneSpec:
    def test_handles_none_taste_spec(self):
        ev = AestheticEvaluator(None)
        score, issues = ev.evaluate("body { color: #fff; }")
        # Should not raise, defaults to 0.5 or score
        assert isinstance(score, float)
        assert isinstance(issues, list)
