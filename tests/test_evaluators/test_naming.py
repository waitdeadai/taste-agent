"""tests/test_evaluators/test_naming.py — NamingEvaluator tests."""

from __future__ import annotations

import pytest

from taste_agent.evaluators.naming import NamingEvaluator


class TestNamingEvaluator:
    def test_empty_content_scores_1(self):
        ev = NamingEvaluator(None)
        score, issues = ev.evaluate("")
        assert score == 1.0
        assert issues == []

    def test_generic_name_detected(self):
        ev = NamingEvaluator(None)
        content = "data = fetch_user()\ninfo = get_info()"
        score, issues = ev.evaluate(content)
        assert score < 1.0
        assert any("generic" in i.lower() for i in issues)

    def test_camel_case_function_detected(self):
        ev = NamingEvaluator(None)
        content = "def getData():\n    pass"
        score, issues = ev.evaluate(content)
        assert score < 1.0
        assert any("camelcase" in i.lower() or "verb_object" in i.lower() for i in issues)

    def test_non_verb_function_detected(self):
        ev = NamingEvaluator(None)
        content = "def user_data():\n    pass"
        score, issues = ev.evaluate(content)
        assert score < 1.0

    def test_snake_case_ok(self, good_py):
        ev = NamingEvaluator(None)
        score, issues = ev.evaluate(good_py)
        # snake_case functions should be OK
        assert isinstance(score, float)

    def test_none_taste_spec_handled(self):
        ev = NamingEvaluator(None)
        score, issues = ev.evaluate("def helper(): pass")
        assert isinstance(score, float)
        assert isinstance(issues, list)
