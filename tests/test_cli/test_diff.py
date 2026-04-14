"""tests/test_cli/test_diff.py — taste diff tests."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from taste_agent.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestDiff:
    def test_identical_files_no_diff(self, runner, tmp_path):
        content = "# Taste — Test\n\n## 1. Visual Theme\nDark.\n\n## 6. Copy Voice\nDirect.\n\n## 7. Non-Negotiables\n1. No placeholder copy\n"
        (tmp_path / "a.md").write_text(content)
        (tmp_path / "b.md").write_text(content)

        result = runner.invoke(
            cli,
            ["--project-root", str(tmp_path), "diff", "a.md", "b.md"],
        )
        assert result.exit_code == 0
        assert "no differences" in result.output.lower()

    def test_changed_files_shows_diff(self, runner, tmp_path):
        (tmp_path / "a.md").write_text("# Taste — Test\n\n## 1. Visual Theme\nDark.\n")
        (tmp_path / "b.md").write_text("# Taste — Test\n\n## 1. Visual Theme\nLight.\n")

        result = runner.invoke(
            cli,
            ["--project-root", str(tmp_path), "diff", "a.md", "b.md"],
        )
        assert result.exit_code == 0
        assert "diff" in result.output.lower() or "taste diff" in result.output.lower()

    def test_nonexistent_old_file_errors(self, runner, tmp_path):
        result = runner.invoke(
            cli,
            ["--project-root", str(tmp_path), "diff", "nonexistent.md", "b.md"],
        )
        assert result.exit_code != 0
        assert "not found" in result.output.lower()
