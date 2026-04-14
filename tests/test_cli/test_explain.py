"""tests/test_cli/test_explain.py — taste explain tests."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from taste_agent.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestExplain:
    def test_no_args_prints_general_guidance(self, runner, tmp_path):
        result = runner.invoke(
            cli,
            ["--project-root", str(tmp_path), "explain"],
        )
        assert result.exit_code == 0
        assert "guidance" in result.output.lower() or "mentor" in result.output.lower()

    def test_placeholder_copy_explains(self, runner, tmp_path):
        result = runner.invoke(
            cli,
            ["--project-root", str(tmp_path), "explain", "placeholder copy"],
        )
        assert result.exit_code == 0
        # Should print mentor guidance
        assert len(result.output) > 50

    def test_circular_import_architecture(self, runner, tmp_path):
        result = runner.invoke(
            cli,
            ["--project-root", str(tmp_path), "explain", "circular import"],
        )
        assert result.exit_code == 0
        assert len(result.output) > 20

    def test_unknown_issue_falls_back(self, runner, tmp_path):
        result = runner.invoke(
            cli,
            ["--project-root", str(tmp_path), "explain", "xyzzy unknown issue"],
        )
        assert result.exit_code == 0
        assert len(result.output) > 0
