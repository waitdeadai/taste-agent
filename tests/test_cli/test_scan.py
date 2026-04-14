"""tests/test_cli/test_scan.py — taste scan tests."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from taste_agent.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestScan:
    def test_scan_reports_dimensions(self, runner, tmp_path):
        # Create a minimal Python file
        (tmp_path / "test.py").write_text("def helper():\n    pass\n")

        result = runner.invoke(
            cli,
            ["--project-root", str(tmp_path), "scan"],
        )
        assert result.exit_code == 0
        # Should report scores for dimensions
        assert "aesthetic" in result.output.lower() or "score" in result.output.lower()

    def test_scan_with_output_file(self, runner, tmp_path):
        (tmp_path / "test.py").write_text("def helper():\n    pass\n")
        output_file = tmp_path / "report.md"

        result = runner.invoke(
            cli,
            [
                "--project-root", str(tmp_path), "scan",
                "--output", str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()

    def test_scan_no_code_files(self, runner, tmp_path):
        result = runner.invoke(
            cli,
            ["--project-root", str(tmp_path), "scan"],
        )
        # Should handle gracefully
        assert result.exit_code == 0 or "no code" in result.output.lower()
