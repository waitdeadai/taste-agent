"""TasteConfig — configuration for the Taste Agent."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class TasteWeights(BaseModel):
    """Weights for evaluation dimensions."""

    aesthetic: float = 0.2
    ux: float = 0.15
    copy: float = 0.15
    adherence: float = 0.1
    architecture: float = 0.1
    naming: float = 0.1
    api_design: float = 0.1
    code_style: float = 0.05
    coherence: float = 0.05

    def __init__(self, **data):
        super().__init__(**data)
        total = (
            self.aesthetic
            + self.ux
            + self.copy
            + self.adherence
            + self.architecture
            + self.naming
            + self.api_design
            + self.code_style
            + self.coherence
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Taste weights must sum to 1.0, got {total}")


class TasteConfig(BaseModel):
    """Configuration for the Taste Agent.

    Attributes:
        enabled: Whether the taste gate is active. Default False (opt-in).
        model: Model to use for taste evaluation. Defaults to zai:glm-5.1.
        taste_spec_path: Path to taste.md (relative to project root).
        memory_path: Path to taste.memory directory.
        memory_scope: Where to look for taste.memory.
            - "project": project_root/.forgegod/taste.memory
            - "global": ~/.forgegod/taste.memory
            - "both": project first, global fallback
        require_taste_md: If True, fail when taste.md is not found.
        auto_approve_threshold: Score above this threshold auto-approves
            without writing to taste.memory. Default 0.9.
        max_revision_cycles: Max REVISE cycles before escalating to REJECT.
        weights: Dimension weights for overall score.
        openai_api_key: OpenAI API key for GPT-4o/gpt-5 evaluation.
        anthropic_api_key: Anthropic API key for Claude evaluation.
        zai_api_key: Z.AI API key for GLM evaluation.
    """

    enabled: bool = False
    model: str = "zai:glm-5.1"
    taste_spec_path: str = "taste.md"
    memory_path: str = ".forgegod/taste.memory"
    memory_scope: Literal["project", "global", "both"] = "both"
    require_taste_md: bool = False
    auto_approve_threshold: float = 0.9
    max_revision_cycles: int = 3
    weights: TasteWeights = Field(default_factory=TasteWeights)

    # API keys (optional — uses env vars if not set)
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    zai_api_key: str | None = None

    def model_post_init(self, _) -> None:
        """Validate weights sum to 1.0."""
        total = (
            self.weights.aesthetic
            + self.weights.ux
            + self.weights.copy
            + self.weights.adherence
            + self.weights.architecture
            + self.weights.naming
            + self.weights.api_design
            + self.weights.code_style
            + self.weights.coherence
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Taste weights must sum to 1.0, got {total}")

    @property
    def memory_scope_global(self) -> Path:
        """Global taste.memory path (~/.forgegod/taste.memory)."""
        import os

        home = Path(os.path.expanduser("~"))
        return home / ".forgegod" / "taste.memory"

    def resolve_memory_path(self, project_root: Path) -> Path:
        """Resolve the effective memory path for a project."""
        if self.memory_scope == "global":
            return self.memory_scope_global
        project_path = project_root / self.memory_path
        if self.memory_scope == "both" and not project_path.exists():
            return self.memory_scope_global
        return project_path

    def resolve_taste_spec_path(self, project_root: Path) -> Path:
        """Resolve the taste.md path (relative to project root)."""
        return project_root / self.taste_spec_path
