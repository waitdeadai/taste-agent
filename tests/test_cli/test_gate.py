"""tests/test_cli/test_gate.py — taste gate tests."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from taste_agent.cli.main import cli


MINIMAL_TASTE_MD = """# Taste — Test

## 6. Copy Voice
Direct.

## 7. Non-Negotiables
1. No placeholder copy
"""


@pytest.fixture
def runner():
    return CliRunner()


class TestGate:
    def test_no_files_passes(self, runner, tmp_path):
        (tmp_path / "taste.md").write_text(MINIMAL_TASTE_MD)
        result = runner.invoke(
            cli,
            ["--project-root", str(tmp_path), "gate"],
        )
        # No files to evaluate = pass
        assert "pass" in result.output.lower() or result.exit_code == 0

    def test_nonexistent_file_warns(self, runner, tmp_path):
        (tmp_path / "taste.md").write_text(MINIMAL_TASTE_MD)
        result = runner.invoke(
            cli,
            [
                "--project-root", str(tmp_path), "gate",
                "--files", "nonexistent.tsx",
            ],
        )
        assert "warning" in result.output.lower() or "not found" in result.output.lower()


class TestGateThresholds:
    def test_p0_above_max_triggers_fail(self, runner, tmp_path, monkeypatch):
        from taste_agent.models.evaluation import EvaluationResult, Issue
        from taste_agent.models.severity import Severity

        (tmp_path / "taste.md").write_text(MINIMAL_TASTE_MD)
        (tmp_path / "a.tsx").write_text("// code")

        mock_result = EvaluationResult(
            verdict="revise",
            overall_score=0.6,
            reasoning="",
            issues=[
                Issue(
                    severity=Severity.P0,
                    dimension="copy",
                    problem="p0",
                    fix_required="fix",
                )
            ],
        )

        # Create a mock agent class
        class MockAgent:
            def __init__(self, *args, **kwargs):
                pass

            async def evaluate(self, **kwargs):
                return mock_result

        monkeypatch.setattr("taste_agent.cli.gate_cmd.TasteAgent", MockAgent)
        result = runner.invoke(
            cli,
            [
                "--project-root", str(tmp_path),
                "gate",
                "--files", "a.tsx",
                "--max-p0", "0",
            ],
        )
        assert result.exit_code == 1

    def test_score_below_min_triggers_fail(self, runner, tmp_path, monkeypatch):
        from taste_agent.models.evaluation import EvaluationResult

        (tmp_path / "taste.md").write_text(MINIMAL_TASTE_MD)
        (tmp_path / "a.tsx").write_text("// code")

        mock_result = EvaluationResult(
            verdict="revise",
            overall_score=0.5,
            reasoning="",
            issues=[],
        )

        class MockAgent:
            def __init__(self, *args, **kwargs):
                pass

            async def evaluate(self, **kwargs):
                return mock_result

        monkeypatch.setattr("taste_agent.cli.gate_cmd.TasteAgent", MockAgent)
        result = runner.invoke(
            cli,
            [
                "--project-root", str(tmp_path),
                "gate",
                "--files", "a.tsx",
                "--min-score", "0.7",
            ],
        )
        assert result.exit_code == 1

    def test_reject_verdict_triggers_fail(self, runner, tmp_path, monkeypatch):
        from taste_agent.models.evaluation import EvaluationResult

        (tmp_path / "taste.md").write_text(MINIMAL_TASTE_MD)
        (tmp_path / "a.tsx").write_text("// code")

        mock_result = EvaluationResult(
            verdict="reject",
            overall_score=0.3,
            reasoning="",
            issues=[],
        )

        class MockAgent:
            def __init__(self, *args, **kwargs):
                pass

            async def evaluate(self, **kwargs):
                return mock_result

        monkeypatch.setattr("taste_agent.cli.gate_cmd.TasteAgent", MockAgent)
        result = runner.invoke(
            cli,
            [
                "--project-root", str(tmp_path),
                "gate",
                "--files", "a.tsx",
            ],
        )
        assert result.exit_code == 1

    def test_all_thresholds_pass(self, runner, tmp_path, monkeypatch):
        from taste_agent.models.evaluation import EvaluationResult

        (tmp_path / "taste.md").write_text(MINIMAL_TASTE_MD)
        (tmp_path / "a.tsx").write_text("// code")

        mock_result = EvaluationResult(
            verdict="approve",
            overall_score=0.9,
            reasoning="",
            issues=[],
        )

        class MockAgent:
            def __init__(self, *args, **kwargs):
                pass

            async def evaluate(self, **kwargs):
                return mock_result

        monkeypatch.setattr("taste_agent.cli.gate_cmd.TasteAgent", MockAgent)
        result = runner.invoke(
            cli,
            [
                "--project-root", str(tmp_path),
                "gate",
                "--files", "a.tsx",
                "--min-score", "0.7",
                "--max-p0", "0",
            ],
        )
        assert result.exit_code == 0
