"""tests/test_evaluators/test_architecture.py — ArchitectureEvaluator tests."""

from __future__ import annotations

import pytest

from taste_agent.evaluators.architecture import ArchitectureEvaluator


class TestArchitectureEvaluator:
    def test_empty_content_scores_1(self):
        ev = ArchitectureEvaluator(None)
        score, issues = ev.evaluate("")
        assert score == 1.0
        assert issues == []

    def test_circular_import_detected(self):
        # from app import app — direct circular import
        ev = ArchitectureEvaluator(None)
        score, issues = ev.evaluate("from app import app")
        assert score == 0.0
        assert any("circular" in i.lower() for i in issues)

    def test_god_module_detected(self):
        # 310 lines with multiple concerns (3+ concern indicators required)
        lines = ["# God module:"]
        for i in range(305):
            lines.append(f"x_{i} = {i}")
        # These match the actual concern indicators in the evaluator
        lines.extend([
            "def process_data():",
            "    db.execute('SELECT * FROM data')",
            "    redis.set('key', 'value')",
            "    send_email('hello@example.com', 'Subject')",
            "    return result",
        ])
        content = "\n".join(lines)
        ev = ArchitectureEvaluator(None)
        score, issues = ev.evaluate(content)
        assert score < 1.0

    def test_route_db_violation(self):
        ev = ArchitectureEvaluator(None)
        content = """
@app.get('/users')
def get_users():
    db.execute('SELECT * FROM users')
    return users
"""
        score, issues = ev.evaluate(content)
        assert score < 1.0

    def test_none_taste_spec_handled(self):
        ev = ArchitectureEvaluator(None)
        score, issues = ev.evaluate("def helper(): pass")
        assert isinstance(score, float)
        assert isinstance(issues, list)
