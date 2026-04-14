"""tests/test_models/test_evaluation.py — Issue and EvaluationResult."""

from __future__ import annotations

import pytest

from taste_agent.models.evaluation import EvaluationResult, Issue
from taste_agent.models.severity import Severity


class TestIssueToDict:
    def test_roundtrip(self):
        issue = Issue(
            severity=Severity.P1,
            dimension="copy",
            location="app/page.tsx",
            problem="Generic placeholder copy",
            fix_required="Replace with specific copy",
            non_negotiable_violated="No placeholder copy",
            why_this_matters="Generic copy signals lack of thought.",
        )
        d = issue.to_dict()
        restored = Issue.from_dict(d)

        assert restored.severity == Severity.P1
        assert restored.dimension == "copy"
        assert restored.location == "app/page.tsx"
        assert restored.problem == "Generic placeholder copy"
        assert restored.fix_required == "Replace with specific copy"
        assert restored.non_negotiable_violated == "No placeholder copy"
        assert restored.why_this_matters == "Generic copy signals lack of thought."

    def test_from_dict_unknown_severity_falls_back_to_p2(self):
        d = {"severity": "P5", "dimension": "copy", "problem": "test"}
        issue = Issue.from_dict(d)
        assert issue.severity == Severity.P2


class TestEvaluationResultSkip:
    def test_skip_returns_approve(self):
        result = EvaluationResult.skip()
        assert result.verdict == "approve"
        assert result.overall_score == 1.0


class TestEvaluationResultSuggestedVerdict:
    def test_p0_returns_reject(self):
        result = EvaluationResult(
            verdict="approve",
            overall_score=0.5,
            reasoning="",
            issues=[Issue(severity=Severity.P0, problem="test")],
        )
        assert result.suggested_verdict() == "reject"

    def test_two_p1_returns_revise(self):
        result = EvaluationResult(
            verdict="approve",
            overall_score=0.5,
            reasoning="",
            issues=[
                Issue(severity=Severity.P1, problem="a"),
                Issue(severity=Severity.P1, problem="b"),
            ],
        )
        assert result.suggested_verdict() == "revise"

    def test_four_p2_returns_revise(self):
        result = EvaluationResult(
            verdict="approve",
            overall_score=0.5,
            reasoning="",
            issues=[
                Issue(severity=Severity.P2, problem=f"p2-{i}") for i in range(4)
            ],
        )
        assert result.suggested_verdict() == "revise"

    def test_clean_returns_approve(self):
        result = EvaluationResult(
            verdict="approve",
            overall_score=1.0,
            reasoning="",
            issues=[],
        )
        assert result.suggested_verdict() == "approve"


class TestSeverityCounts:
    def test_severity_counts(self):
        result = EvaluationResult(
            verdict="revise",
            overall_score=0.5,
            reasoning="",
            issues=[
                Issue(severity=Severity.P0, problem="a"),
                Issue(severity=Severity.P1, problem="b"),
                Issue(severity=Severity.P2, problem="c"),
                Issue(severity=Severity.P3, problem="d"),
            ],
        )
        counts = result.severity_counts()
        assert counts.p0 == 1
        assert counts.p1 == 1
        assert counts.p2 == 1
        assert counts.p3 == 1


class TestP0P1P2P3Filters:
    def test_p0_issues(self):
        result = EvaluationResult(
            verdict="revise",
            overall_score=0.5,
            reasoning="",
            issues=[
                Issue(severity=Severity.P0, problem="p0"),
                Issue(severity=Severity.P1, problem="p1"),
            ],
        )
        p0s = result.p0_issues()
        assert len(p0s) == 1
        assert p0s[0].severity == Severity.P0

    def test_p1_issues(self):
        result = EvaluationResult(
            verdict="revise",
            overall_score=0.5,
            reasoning="",
            issues=[
                Issue(severity=Severity.P0, problem="p0"),
                Issue(severity=Severity.P1, problem="p1"),
            ],
        )
        p1s = result.p1_issues()
        assert len(p1s) == 1
        assert p1s[0].severity == Severity.P1

    def test_p2_issues(self):
        result = EvaluationResult(
            verdict="revise",
            overall_score=0.5,
            reasoning="",
            issues=[
                Issue(severity=Severity.P2, problem="p2"),
                Issue(severity=Severity.P3, problem="p3"),
            ],
        )
        p2s = result.p2_issues()
        assert len(p2s) == 1
        assert p2s[0].severity == Severity.P2

    def test_p3_issues(self):
        result = EvaluationResult(
            verdict="revise",
            overall_score=0.5,
            reasoning="",
            issues=[
                Issue(severity=Severity.P2, problem="p2"),
                Issue(severity=Severity.P3, problem="p3"),
            ],
        )
        p3s = result.p3_issues()
        assert len(p3s) == 1
        assert p3s[0].severity == Severity.P3
