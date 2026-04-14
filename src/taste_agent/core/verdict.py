"""VERDICT enum for taste evaluation outcomes."""

from __future__ import annotations

from enum import Enum


class VERDICT(str, Enum):
    """Taste evaluation verdict.

    - APPROVE: Output meets taste.md standards. No revisions needed.
    - REVISE: Output has taste issues. Provide specific feedback to fix.
    - REJECT: Output fundamentally violates taste.md non-negotiables.
              Code must be rewritten, not incrementally fixed.
    """

    APPROVE = "approve"
    REVISE = "revise"
    REJECT = "reject"

    def __str__(self) -> str:
        return self.value


class Verdict:
    """Structured verdict with metadata."""

    __slots__ = ("value", "confidence", "reasoning", "issues", "suggestions")

    def __init__(
        self,
        value: VERDICT,
        confidence: float = 0.5,
        reasoning: str = "",
        issues: list[str] | None = None,
        suggestions: list[str] | None = None,
    ):
        self.value = value
        self.confidence = confidence
        self.reasoning = reasoning
        self.issues = issues or []
        self.suggestions = suggestions or []

    def to_dict(self) -> dict:
        return {
            "verdict": self.value.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "issues": self.issues,
            "suggestions": self.suggestions,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Verdict":
        return cls(
            value=VERDICT(data.get("verdict", "approve")),
            confidence=float(data.get("confidence", 0.5)),
            reasoning=data.get("reasoning", ""),
            issues=data.get("issues", []),
            suggestions=data.get("suggestions", []),
        )

    def __repr__(self) -> str:
        return f"Verdict({self.value.value}, confidence={self.confidence:.0%})"
