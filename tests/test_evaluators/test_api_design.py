"""tests/test_evaluators/test_api_design.py — ApiDesignEvaluator tests."""

from __future__ import annotations

import pytest

from taste_agent.evaluators.api_design import ApiDesignEvaluator


class TestApiDesignEvaluator:
    def test_empty_content_scores_1(self):
        ev = ApiDesignEvaluator(None)
        score, issues = ev.evaluate("")
        assert score == 1.0
        assert issues == []

    def test_raw_string_error_detected(self, bad_api_error_response):
        ev = ApiDesignEvaluator(None)
        score, issues = ev.evaluate(f'return {{"error": "Something went wrong"}}')
        assert score < 1.0
        assert any("error format" in i.lower() for i in issues)

    def test_structured_error_ok(self, good_api_error):
        ev = ApiDesignEvaluator(None)
        score, issues = ev.evaluate(good_api_error)
        assert score == 1.0

    def test_wrong_status_code_200_for_create(self):
        ev = ApiDesignEvaluator(None)
        # The evaluator checks: status_code=200 AND 'return' AND ('create' or 'post')
        content = 'return HTTPException(status_code=200, detail="User created")'
        score, issues = ev.evaluate(content)
        assert score < 1.0
        assert any("status code" in i.lower() for i in issues)

    def test_snake_case_route(self):
        ev = ApiDesignEvaluator(None)
        content = '@app.get("/user_profile")'
        score, issues = ev.evaluate(content)
        assert score < 1.0
        assert any("kebab-case" in i.lower() or "snake_case" in i.lower() for i in issues)

    def test_none_taste_spec_handled(self):
        ev = ApiDesignEvaluator(None)
        score, issues = ev.evaluate('{"data": {"id": 1}}')
        assert isinstance(score, float)
        assert isinstance(issues, list)
