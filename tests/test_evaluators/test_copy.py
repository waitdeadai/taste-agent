"""tests/test_evaluators/test_copy.py — CopyEvaluator tests."""

from __future__ import annotations

import pytest

from taste_agent.evaluators.copy import CopyEvaluator


class TestCopyEvaluator:
    def test_empty_content_scores_1(self):
        ev = CopyEvaluator(None)
        score, issues = ev.evaluate("")
        assert score == 1.0
        assert issues == []

    def test_hallmark_copy_detected(self):
        ev = CopyEvaluator(None)
        score, issues = ev.evaluate("We help you transform your business with cutting-edge synergy.")
        assert score < 1.0
        assert any("hallmark" in i.lower() or "corporate" in i.lower() for i in issues)

    def test_confident_copy_bonus(self):
        ev = CopyEvaluator(None)
        content = "We implement the solution. We guarantee results in 6 weeks."
        score, issues = ev.evaluate(content)
        assert isinstance(score, float)

    def test_hedging_language_detected(self):
        ev = CopyEvaluator(None)
        score, issues = ev.evaluate("We think this might maybe perhaps work.")
        assert score < 1.0
        assert any("hedging" in i.lower() for i in issues)

    def test_vague_headline_detected(self):
        ev = CopyEvaluator(None)
        score, issues = ev.evaluate("A Modern Better Solution for Your Business")
        assert isinstance(score, float)

    def test_none_taste_spec_handled(self):
        ev = CopyEvaluator(None)
        score, issues = ev.evaluate("Get started today.")
        assert isinstance(score, float)
        assert isinstance(issues, list)
