"""tests/test_cli/test_init.py — taste init tests."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from taste_agent.cli.main import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestInit:
    def test_defaults_creates_taste_md(self, runner, tmp_path):
        result = runner.invoke(
            cli,
            ["--project-root", str(tmp_path), "init", "--defaults"],
        )
        assert result.exit_code == 0
        assert (tmp_path / "taste.md").exists()
        content = (tmp_path / "taste.md").read_text()
        assert "Taste" in content
        assert "Visual Theme" in content

    def test_defaults_fails_if_file_exists(self, runner, tmp_path):
        (tmp_path / "taste.md").write_text("existing content")
        result = runner.invoke(
            cli,
            ["--project-root", str(tmp_path), "init", "--defaults"],
        )
        assert result.exit_code != 0
        assert "already exists" in result.output.lower()


class TestInitIndustryMapping:
    @pytest.mark.parametrize("industry,expected_aesthetic", [
        ("B2B SaaS", "Dark institutional"),
        ("consumer", "Light and playful"),
        ("developer tools", "Technical precision"),
        ("consulting", "Editorial and confident"),
        ("other", "Dark and premium"),
    ])
    def test_industry_aesthetic_mapping(self, runner, tmp_path, industry, expected_aesthetic):
        from taste_agent.cli.init_cmd import AESTHETIC_MAP
        assert expected_aesthetic in AESTHETIC_MAP[industry]

    @pytest.mark.parametrize("industry,expected_aesthetic", [
        ("B2B SaaS", "Dark institutional"),
        ("consumer", "Light and playful"),
        ("developer tools", "Technical precision"),
        ("consulting", "Editorial and confident"),
        ("other", "Dark and premium"),
    ])
    def test_industry_defaults_flag(self, runner, tmp_path, industry, expected_aesthetic):
        # Test --industry flag with --defaults
        result = runner.invoke(
            cli,
            ["--project-root", str(tmp_path), "init", "--defaults", "--industry", industry],
        )
        assert result.exit_code == 0, result.output
        content = (tmp_path / "taste.md").read_text()
        assert expected_aesthetic in content
