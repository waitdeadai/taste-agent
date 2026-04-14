"""EvaluationResult — output of a taste evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Issue:
    """A single taste issue found during evaluation."""

    dimension: str  # aesthetic | ux | copy | adherence
    location: str  # file:line or component name
    problem: str  # what is wrong
    fix_required: str  # what must be done
    non_negotiable_violated: str = ""  # which non-negotiable is violated


@dataclass
class EvaluationResult:
    """Result of a taste evaluation.

    Produced by TasteAgent.evaluate(). Contains the verdict,
    dimension scores, issues found, and guidance for revision.
    """

    verdict: str  # "approve" | "revise" | "reject"
    overall_score: float  # 0.0 - 1.0
    reasoning: str

    scores: dict[str, float] = field(
        default_factory=lambda: {
            "aesthetic": 0.5,
            "ux": 0.5,
            "copy": 0.5,
            "adherence": 0.5,
        }
    )

    issues: list[Issue] = field(default_factory=list)
    principles_learned: list[str] = field(default_factory=list)
    revision_guidance: str = ""

    # Metadata
    model_used: str = ""
    cost_usd: float = 0.0
    latency_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "overall_score": self.overall_score,
            "reasoning": self.reasoning,
            "scores": self.scores,
            "issues": [
                {
                    "dimension": i.dimension,
                    "location": i.location,
                    "problem": i.problem,
                    "fix_required": i.fix_required,
                    "non_negotiable_violated": i.non_negotiable_violated,
                }
                for i in self.issues
            ],
            "principles_learned": self.principles_learned,
            "revision_guidance": self.revision_guidance,
            "model_used": self.model_used,
            "cost_usd": self.cost_usd,
            "latency_ms": self.latency_ms,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EvaluationResult":
        issues = []
        for i in data.get("issues", []):
            issues.append(
                Issue(
                    dimension=i.get("dimension", "aesthetic"),
                    location=i.get("location", ""),
                    problem=i.get("problem", ""),
                    fix_required=i.get("fix_required", ""),
                    non_negotiable_violated=i.get("non_negotiable_violated", ""),
                )
            )
        return cls(
            verdict=data.get("verdict", "approve"),
            overall_score=float(data.get("overall_score", 0.5)),
            reasoning=data.get("reasoning", ""),
            scores=data.get("scores", {}),
            issues=issues,
            principles_learned=data.get("principles_learned", []),
            revision_guidance=data.get("revision_guidance", ""),
            model_used=data.get("model_used", ""),
            cost_usd=float(data.get("cost_usd", 0.0)),
            latency_ms=int(data.get("latency_ms", 0)),
        )

    @classmethod
    def skip(cls) -> "EvaluationResult":
        """Return a skipped evaluation result (taste disabled)."""
        return cls(
            verdict="approve",
            overall_score=1.0,
            reasoning="Taste agent disabled — skipped.",
        )

    def __repr__(self) -> str:
        return f"EvaluationResult({self.verdict}, score={self.overall_score:.0%}, issues={len(self.issues)})"
