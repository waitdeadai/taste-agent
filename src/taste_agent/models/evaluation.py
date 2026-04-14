"""EvaluationResult — output of a taste evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from taste_agent.models.severity import ALL_DIMENSIONS, Severity, SeverityCounts


@dataclass
class Issue:
    """A single taste issue found during evaluation."""

    severity: Severity = Severity.P2
    dimension: str = ""  # aesthetic | ux | copy | adherence | architecture | naming | api_design | code_style | coherence
    location: str = ""  # file:line or component name
    problem: str = ""  # what is wrong
    fix_required: str = ""  # what must be done
    non_negotiable_violated: str = ""  # which non-negotiable is violated
    why_this_matters: str = ""  # mentor mode: explains the design principle violated

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity.value,
            "dimension": self.dimension,
            "location": self.location,
            "problem": self.problem,
            "fix_required": self.fix_required,
            "non_negotiable_violated": self.non_negotiable_violated,
            "why_this_matters": self.why_this_matters,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Issue:
        return cls(
            severity=Severity(data.get("severity", "P2")),
            dimension=data.get("dimension", ""),
            location=data.get("location", ""),
            problem=data.get("problem", ""),
            fix_required=data.get("fix_required", ""),
            non_negotiable_violated=data.get("non_negotiable_violated", ""),
            why_this_matters=data.get("why_this_matters", ""),
        )


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
        default_factory=lambda: dict.fromkeys(ALL_DIMENSIONS, 0.5)
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
            "issues": [i.to_dict() for i in self.issues],
            "principles_learned": self.principles_learned,
            "revision_guidance": self.revision_guidance,
            "model_used": self.model_used,
            "cost_usd": self.cost_usd,
            "latency_ms": self.latency_ms,
        }

    @classmethod
    def from_dict(cls, data: dict) -> EvaluationResult:
        raw_issues = data.get("issues", [])
        issues = [Issue.from_dict(i) for i in raw_issues]
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
    def skip(cls) -> EvaluationResult:
        """Return a skipped evaluation result (taste disabled)."""
        return cls(
            verdict="approve",
            overall_score=1.0,
            reasoning="Taste agent disabled — skipped.",
        )

    def __repr__(self) -> str:
        return f"EvaluationResult({self.verdict}, score={self.overall_score:.0%}, issues={len(self.issues)})"

    def severity_counts(self) -> SeverityCounts:
        """Return count of issues per severity level."""
        from taste_agent.models.severity import SeverityCounts

        return SeverityCounts.from_issues(self.issues)

    def suggested_verdict(self) -> str:
        """Python-side verdict determination from severity counts.

        REJECT if any P0 (non-negotiable violated).
        REVISE if 2+ P1 or 4+ P2.
        APPROVE otherwise (with P3 suggestions noted).
        """

        counts = self.severity_counts()
        if counts.p0 > 0:
            return "reject"
        if counts.p1 >= 2:
            return "revise"
        if counts.p2 >= 4:
            return "revise"
        return "approve"

    def p0_issues(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.P0]

    def p1_issues(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.P1]

    def p2_issues(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.P2]

    def p3_issues(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.P3]

