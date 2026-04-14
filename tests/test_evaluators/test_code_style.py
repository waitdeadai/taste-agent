"""tests/test_evaluators/test_code_style.py — CodeStyleEvaluator tests."""

from __future__ import annotations

import pytest

from taste_agent.evaluators.code_style import CodeStyleEvaluator


class TestCodeStyleEvaluator:
    def test_empty_content_scores_1(self):
        ev = CodeStyleEvaluator(None)
        score, issues = ev.evaluate("")
        assert score == 1.0
        assert issues == []

    def test_long_function_detected(self):
        ev = CodeStyleEvaluator(None)
        # 45+ line function
        content = "def long_function():\n" + "\n".join([f"    x = {i}" for i in range(50)]) + "\n    return x"
        score, issues = ev.evaluate(content)
        assert score < 1.0
        assert any("too long" in i.lower() or "lines" in i.lower() for i in issues)

    def test_what_comment_detected(self):
        ev = CodeStyleEvaluator(None)
        content = "# This function does X\ndef helper():\n    pass"
        score, issues = ev.evaluate(content)
        assert score < 1.0
        assert any("what" in i.lower() for i in issues)

    def test_magic_numbers_detected(self):
        ev = CodeStyleEvaluator(None)
        # Numbers preceded by word chars (not = or whitespace) to pass lookbehind
        # 4+ distinct magic numbers triggers the issue (>3)
        content = "x99999\ny88888\nz77777\nw66666\nv55555"
        score, issues = ev.evaluate(content)
        assert score < 1.0
        assert any("magic" in i.lower() for i in issues)

    def test_allowed_numbers_ok(self):
        ev = CodeStyleEvaluator(None)
        # 100, 255, 86400, etc are allowed
        content = "MAX = 100\nMASK = 255\nDAY = 86400"
        score, issues = ev.evaluate(content)
        assert score == 1.0

    def test_none_taste_spec_handled(self):
        ev = CodeStyleEvaluator(None)
        score, issues = ev.evaluate("def helper(): pass")
        assert isinstance(score, float)
        assert isinstance(issues, list)
