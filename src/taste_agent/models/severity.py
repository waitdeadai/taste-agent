"""Severity enum and aggregation helpers for issue prioritization."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    """Issue severity levels.

    P0 (BLOCKER): Violates a hard non-negotiable. REJECT immediately.
    P1 (MAJOR): Significant deviation. Fix in current iteration. 2+ P1s → REJECT.
    P2 (MINOR): Drift that accumulates debt. Fix in next iteration. 4+ P2s → REJECT.
    P3 (SUGGESTION): Opportunity to exceed spec. APPROVE with note.
    """

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

    def __str__(self) -> str:
        return self.value


# All dimensions across all evaluators (v1: 4, v2: 9)
ALL_DIMENSIONS = [
    "aesthetic",
    "ux",
    "copy",
    "adherence",
    "architecture",
    "naming",
    "api_design",
    "code_style",
    "coherence",
]


@dataclass
class SeverityCounts:
    """Count of issues per severity level."""

    p0: int = 0
    p1: int = 0
    p2: int = 0
    p3: int = 0

    @classmethod
    def from_issues(cls, issues: list) -> SeverityCounts:
        counts = cls()
        for issue in issues:
            sev = getattr(issue, "severity", None)
            if sev == Severity.P0:
                counts.p0 += 1
            elif sev == Severity.P1:
                counts.p1 += 1
            elif sev == Severity.P2:
                counts.p2 += 1
            elif sev == Severity.P3:
                counts.p3 += 1
        return counts

    def total(self) -> int:
        return self.p0 + self.p1 + self.p2 + self.p3

