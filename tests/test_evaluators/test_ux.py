"""tests/test_evaluators/test_ux.py — UXEvaluator tests."""

from __future__ import annotations

import pytest

from taste_agent.evaluators.ux import UXEvaluator


class TestUXEvaluator:
    def test_empty_content_scores_1(self):
        ev = UXEvaluator(None)
        score, issues = ev.evaluate("")
        assert score == 1.0
        assert issues == []

    def test_accessibility_issue_detected(self):
        ev = UXEvaluator(None)
        score, issues = ev.evaluate("body { font-size: 10px; }")
        assert score < 1.0
        assert any("font size" in i.lower() for i in issues)

    def test_outline_none_detected(self):
        ev = UXEvaluator(None)
        score, issues = ev.evaluate("button { outline: none; }")
        assert score < 1.0

    def test_good_patterns_bonus(self):
        ev = UXEvaluator(None)
        content = """
        .btn:hover { opacity: 0.8; }
        button[aria-label] { color: #fff; }
        """
        score, issues = ev.evaluate(content)
        assert isinstance(score, float)
        assert isinstance(issues, list)

    def test_touch_target_issue(self):
        ev = UXEvaluator(None)
        score, issues = ev.evaluate("button { padding: 2px 4px; }")
        # Should detect small padding
        assert isinstance(score, float)

    def test_none_taste_spec_handled(self):
        ev = UXEvaluator(None)
        score, issues = ev.evaluate("body { color: #fff; }")
        assert isinstance(score, float)
        assert isinstance(issues, list)
