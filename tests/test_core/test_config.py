"""tests/test_core/test_config.py — TasteConfig weights validation and path resolution."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from taste_agent.core.config import TasteConfig, TasteWeights


class TestTasteConfigWeights:
    def test_default_weights_sum_to_one(self):
        config = TasteConfig()
        w = config.weights
        total = (
            w.aesthetic
            + w.ux
            + w.copy
            + w.adherence
            + w.architecture
            + w.naming
            + w.api_design
            + w.code_style
            + w.coherence
        )
        assert abs(total - 1.0) < 0.01

    def test_bad_weights_raise_valueerror(self):
        with pytest.raises(ValueError, match="must sum to 1.0"):
            TasteWeights(aesthetic=0.5, ux=0.5, copy=0.5)  # sum = 1.5


class TestResolveMemoryPath:
    def test_project_scope(self, tmp_path):
        config = TasteConfig(memory_scope="project")
        resolved = config.resolve_memory_path(tmp_path)
        assert resolved == tmp_path / config.memory_path

    def test_global_scope(self, tmp_path):
        config = TasteConfig(memory_scope="global")
        resolved = config.resolve_memory_path(tmp_path)
        assert "~" in str(resolved) or ".forgegod" in str(resolved)

    def test_both_falls_back_to_global(self, tmp_path):
        config = TasteConfig(memory_scope="both")
        # No project path exists, so should fall back to global
        resolved = config.resolve_memory_path(tmp_path)
        # Should resolve to global since project path doesn't exist
        assert resolved != tmp_path / config.memory_path or resolved.exists()


class TestResolveTasteSpecPath:
    def test_resolves_relative_to_project_root(self, tmp_path):
        config = TasteConfig(taste_spec_path="taste.md")
        resolved = config.resolve_taste_spec_path(tmp_path)
        assert resolved == tmp_path / "taste.md"
