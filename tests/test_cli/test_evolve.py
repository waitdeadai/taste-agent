"""tests/test_cli/test_evolve.py — taste evolve tests."""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from taste_agent.cli.main import cli
from taste_agent.core.memory import MemoryEntry


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def forgegod_dir(tmp_path):
    d = tmp_path / ".forgegod"
    d.mkdir()
    return d


class TestEvolve:
    def test_no_memory_file_prints_message(self, runner, tmp_path):
        result = runner.invoke(cli, ["--project-root", str(tmp_path), "evolve"])
        assert result.exit_code == 0
        assert "no taste.memory" in result.output.lower()

    def test_empty_memory_prints_message(self, runner, forgegod_dir):
        (forgegod_dir / "taste.memory").write_text("")
        result = runner.invoke(cli, ["--project-root", str(forgegod_dir.parent), "evolve"])
        assert result.exit_code == 0
        assert "empty" in result.output.lower()

    def test_dry_run_shows_suggestions(self, runner, forgegod_dir):
        entry = MemoryEntry(
            task_description="Write marketing copy",
            file_path="pages/index.tsx",
            verdict="revise",
            reasoning="Too generic",
            category="copy",
            principle="Be specific and concrete",
        )
        (forgegod_dir / "taste.memory").write_text(entry.to_jsonl() + "\n")
        result = runner.invoke(cli, ["--project-root", str(forgegod_dir.parent), "evolve", "--dry-run"])
        assert result.exit_code == 0
        assert "Patterns by Category" in result.output or "COPY" in result.output

    def test_memory_with_entries(self, runner, forgegod_dir):
        entries = [
            MemoryEntry(
                task_description="t1", file_path="f1", verdict="revise",
                reasoning="r1", category="copy", principle="Be specific",
            ),
            MemoryEntry(
                task_description="t2", file_path="f2", verdict="revise",
                reasoning="r2", category="copy", principle="Be bold",
            ),
            MemoryEntry(
                task_description="t3", file_path="f3", verdict="revise",
                reasoning="r3", category="aesthetic", principle="Use dark theme",
            ),
        ]
        (forgegod_dir / "taste.memory").write_text("\n".join(e.to_jsonl() for e in entries) + "\n")
        result = runner.invoke(cli, ["--project-root", str(forgegod_dir.parent), "evolve", "--dry-run"])
        assert result.exit_code == 0
        assert "COPY" in result.output or "AESTHETIC" in result.output
