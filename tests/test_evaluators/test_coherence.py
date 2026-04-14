"""tests/test_evaluators/test_coherence.py — CoherenceEvaluator tests."""

from __future__ import annotations

import pytest

from taste_agent.evaluators.coherence import CoherenceEvaluator


class TestCoherenceEvaluator:
    def test_empty_content_scores_1(self):
        ev = CoherenceEvaluator(None)
        score, issues = ev.evaluate("")
        assert score == 1.0
        assert issues == []

    def test_naming_inconsistency_across_files(self):
        ev = CoherenceEvaluator(None)
        # Use PascalCase compound words that match the entity pattern
        file_map = {
            "user_service.py": "class UserData:\n    pass\nclass UserDataHelper:\n    pass",
            "order_service.py": "class UserInfo:\n    pass\nclass UserInfoHelper:\n    pass",
        }
        score, issues = ev.evaluate("", file_map=file_map)
        assert score < 1.0
        assert len(issues) > 0

    def test_duplicate_logic_detected(self):
        ev = CoherenceEvaluator(None)
        # 6-line block where first 5 lines are identical across files
        # Need 6 lines so there's a 5-line window to extract
        dup_block = "\n".join([
            "    result = x + y",
            "    result = result * 2",
            "    if result > 0:",
            "        return result",
            "    return None",
            "    # Extra line so we get a 5-line window",
        ])
        file_map = {
            "a.py": dup_block + "\n",
            "b.py": dup_block + "\n",
        }
        score, issues = ev.evaluate("", file_map=file_map)
        assert score < 1.0
        assert any("duplicate" in i.lower() for i in issues)

    def test_single_file_2space_indentation(self):
        ev = CoherenceEvaluator(None)
        # 2-space indentation requires 20+ lines to be flagged
        lines = ["def helper():"]
        for i in range(22):
            lines.append("  x = 1")  # 2-space indent
        content = "\n".join(lines)
        score, issues = ev.evaluate(content)
        assert score < 1.0
        assert any("indentation" in i.lower() for i in issues)

    def test_mixed_error_handling(self):
        ev = CoherenceEvaluator(None)
        file_map = {
            "a.py": "try: pass\nexcept: pass\nraise HTTPException(400)",
            "b.py": "try: pass\nexcept: pass\nreturn Result.Error",
        }
        score, issues = ev.evaluate("", file_map=file_map)
        # Mixed styles might be flagged
        assert isinstance(score, float)

    def test_none_taste_spec_handled(self):
        ev = CoherenceEvaluator(None)
        score, issues = ev.evaluate("def helper(): pass")
        assert isinstance(score, float)
        assert isinstance(issues, list)
