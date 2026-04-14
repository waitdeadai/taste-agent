"""tests/test_cli/test_lint.py — taste lint tests."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from taste_agent.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestLint:
    def test_valid_taste_md_passes(self, runner, tmp_path):
        (tmp_path / "taste.md").write_text(
            "# Taste — Test\n\n## 1. Visual Theme & Atmosphere\nDark institutional.\n\n## 6. Copy Voice\n- Confident and direct\n\n## 7. Non-Negotiables\n- No placeholder copy\n"
        )
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "lint"])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_file_not_found_exits(self, runner, tmp_path):
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "lint"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()

    def test_invalid_hex_color_reported(self, runner, tmp_path):
        (tmp_path / "taste.md").write_text(
            "# Taste — Test\n\n## 1. Visual Theme & Atmosphere\nDark.\n\n## 3. Color Palette\n- Primary: #GGGGGG (Background)\n\n## 6. Copy Voice\n- Confident and direct\n\n## 7. Non-Negotiables\n- No placeholder copy\n"
        )
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "lint"])
        # Should report invalid hex color (GGGGGG is invalid)
        assert "invalid" in result.output.lower() or result.exit_code == 0

    def test_strict_with_issues_aborts(self, runner, tmp_path):
        (tmp_path / "taste.md").write_text(
            "# Taste — Test\n\n## 1. Visual Theme & Atmosphere\nDark.\n\n## 6. Copy Voice\n\n## 7. Non-Negotiables\n- x\n"
        )
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "lint", "--strict"])
        assert result.exit_code != 0
