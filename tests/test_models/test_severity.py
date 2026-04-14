"""tests/test_models/test_severity.py — Severity enum and SeverityCounts."""

from __future__ import annotations

import pytest

from taste_agent.models.severity import ALL_DIMENSIONS, Severity, SeverityCounts


class TestSeverity:
    def test_p0_equals_string(self):
        assert Severity.P0 == "P0"

    def test_str_p0(self):
        assert str(Severity.P0) == "P0"

    def test_all_severity_values(self):
        assert Severity.P0 == "P0"
        assert Severity.P1 == "P1"
        assert Severity.P2 == "P2"
        assert Severity.P3 == "P3"


class TestSeverityCounts:
    def test_from_issues_p0_p1(self):
        from taste_agent.models.evaluation import Issue

        issues = [
            Issue(severity=Severity.P0, problem="a"),
            Issue(severity=Severity.P1, problem="b"),
            Issue(severity=Severity.P0, problem="c"),
        ]
        counts = SeverityCounts.from_issues(issues)
        assert counts.p0 == 2
        assert counts.p1 == 1
        assert counts.p2 == 0
        assert counts.p3 == 0

    def test_from_issues_empty(self):
        counts = SeverityCounts.from_issues([])
        assert counts.p0 == 0
        assert counts.p1 == 0
        assert counts.p2 == 0
        assert counts.p3 == 0

    def test_total(self):
        from taste_agent.models.evaluation import Issue

        issues = [
            Issue(severity=Severity.P0, problem="a"),
            Issue(severity=Severity.P1, problem="b"),
            Issue(severity=Severity.P2, problem="c"),
            Issue(severity=Severity.P3, problem="d"),
        ]
        counts = SeverityCounts.from_issues(issues)
        assert counts.total() == 4


class TestAllDimensions:
    def test_has_nine_items(self):
        assert len(ALL_DIMENSIONS) == 9

    def test_all_expected_dimensions(self):
        expected = {
            "aesthetic",
            "ux",
            "copy",
            "adherence",
            "architecture",
            "naming",
            "api_design",
            "code_style",
            "coherence",
        }
        assert set(ALL_DIMENSIONS) == expected
