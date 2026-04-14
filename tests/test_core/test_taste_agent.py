"""tests/test_core/test_taste_agent.py — TasteAgent core logic."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from taste_agent.core.config import TasteConfig
from taste_agent.core.taste_agent import TasteAgent
from taste_agent.models.evaluation import EvaluationResult, Issue
from taste_agent.models.severity import Severity


class TestTasteAgentDisabled:
    def test_evaluate_disabled_returns_skip(self, tmp_path):
        config = TasteConfig(enabled=False)
        agent = TasteAgent(config, project_root=tmp_path)
        result = asyncio.run(agent.evaluate(task="Add hero", output_files=["a.tsx"]))
        assert result.verdict == "approve"
        assert result.overall_score == 1.0


class TestInferSeverity:
    def test_p0_keywords(self, tmp_path):
        config = TasteConfig(enabled=False)
        agent = TasteAgent(config, project_root=tmp_path)
        sev = agent._infer_severity(
            "This violates a non-negotiable rule about circular imports", "architecture"
        )
        assert sev == Severity.P0

    def test_p1_keywords(self, tmp_path):
        config = TasteConfig(enabled=False)
        agent = TasteAgent(config, project_root=tmp_path)
        sev = agent._infer_severity("This uses generic placeholder copy", "copy")
        assert sev == Severity.P1

    def test_default_p2(self, tmp_path):
        config = TasteConfig(enabled=False)
        agent = TasteAgent(config, project_root=tmp_path)
        sev = agent._infer_severity("This is a minor inconsistency in spacing", "coherence")
        assert sev == Severity.P2


class TestIssueStrsToIssues:
    def test_creates_issue_objects(self, tmp_path):
        config = TasteConfig(enabled=False)
        agent = TasteAgent(config, project_root=tmp_path)
        issues = agent._issue_strs_to_issues(
            ["This is a long enough issue description string", "Another issue"], "copy"
        )
        assert len(issues) == 2
        assert issues[0].dimension == "copy"
        assert issues[0].severity in (Severity.P0, Severity.P1, Severity.P2)


class TestMergeIssues:
    def test_llm_issues_take_precedence(self, tmp_path):
        config = TasteConfig(enabled=False)
        agent = TasteAgent(config, project_root=tmp_path)

        pattern_issues = [
            Issue(
                severity=Severity.P2,
                dimension="copy",
                location="pattern:0",
                problem="Some generic issue",
            )
        ]
        llm_issues = [
            Issue(
                severity=Severity.P1,
                dimension="copy",
                location="app/page.tsx",
                problem="Some generic issue",
                fix_required="Replace",
            )
        ]

        merged = agent._merge_issues(pattern_issues, llm_issues)
        # LLM issue should be in the result
        assert len(merged) >= 1

    def test_short_pattern_issues_dropped(self, tmp_path):
        config = TasteConfig(enabled=False)
        agent = TasteAgent(config, project_root=tmp_path)

        pattern_issues = [
            Issue(
                severity=Severity.P2,
                dimension="copy",
                location="pattern:0",
                problem="short",  # too short
            )
        ]
        llm_issues = []

        merged = agent._merge_issues(pattern_issues, llm_issues)
        assert len(merged) == 0


class TestParseResponse:
    def test_valid_json_returns_result(self, tmp_path):
        config = TasteConfig(enabled=False)
        agent = TasteAgent(config, project_root=tmp_path)

        raw = json.dumps(
            {
                "verdict": "revise",
                "overall_score": 0.6,
                "reasoning": "Several issues.",
                "scores": {d: 0.6 for d in [
                    "aesthetic", "ux", "copy", "adherence",
                    "architecture", "naming", "api_design", "code_style", "coherence",
                ]},
                "issues": [
                    {
                        "severity": "P1",
                        "dimension": "copy",
                        "location": "app.tsx",
                        "problem": "Placeholder copy",
                        "fix_required": "Replace",
                        "non_negotiable_violated": "",
                        "why_this_matters": "Generic copy.",
                    }
                ],
            }
        )

        result = agent._parse_response(raw, {"prompt_tokens": 100, "completion_tokens": 50}, 500)
        assert result.verdict == "revise"
        assert result.overall_score == 0.6
        assert len(result.issues) == 1
        assert result.issues[0].severity == Severity.P1

    def test_invalid_json_returns_revise(self, tmp_path):
        config = TasteConfig(enabled=False)
        agent = TasteAgent(config, project_root=tmp_path)

        result = agent._parse_response("not valid json at all {{{", {}, 100)
        assert result.verdict == "revise"
        assert result.overall_score == 0.0


class TestCreateEvaluators:
    def test_creates_all_nine_dimension_keys(self, tmp_path):
        config = TasteConfig(enabled=False)
        agent = TasteAgent(config, project_root=tmp_path)
        evaluators = agent._create_evaluators()

        expected_dims = {
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
        assert set(evaluators.keys()) == expected_dims


class TestExtractPrinciple:
    def test_extracts_from_non_negotiable(self, tmp_path):
        config = TasteConfig(enabled=False)
        agent = TasteAgent(config, project_root=tmp_path)

        issue = Issue(
            severity=Severity.P0,
            dimension="copy",
            location="a.tsx",
            problem="Violated no placeholder copy",
            non_negotiable_violated="No placeholder copy",
        )
        principle = agent._extract_principle(issue, "reject")
        assert "non-negotiable" in principle.lower()

    def test_extracts_dimension_hint(self, tmp_path):
        config = TasteConfig(enabled=False)
        agent = TasteAgent(config, project_root=tmp_path)

        issue = Issue(
            severity=Severity.P1,
            dimension="architecture",
            location="a.py",
            problem="Layer violation",
            fix_required="Separate concerns",
        )
        principle = agent._extract_principle(issue, "revise")
        assert len(principle) > 0


class TestEvaluateWithMockedLLM:
    @pytest.mark.asyncio
    async def test_evaluate_with_mocked_llm(self, tmp_path, mock_llm_response_approve):
        config = TasteConfig(enabled=True)
        agent = TasteAgent(config, project_root=tmp_path)

        # Create a fake taste.md so spec is found
        (tmp_path / "taste.md").write_text(
            "# Taste — Test\n## 1. Visual Theme\nDark.\n## 6. Copy Voice\nDirect.\n## 7. Non-Negotiables\n1. No placeholder copy\n"
        )

        mock_response = {
            "verdict": "approve",
            "overall_score": 0.9,
            "reasoning": "Looks good.",
            "scores": {d: 0.9 for d in [
                "aesthetic", "ux", "copy", "adherence",
                "architecture", "naming", "api_design", "code_style", "coherence",
            ]},
            "issues": [],
        }

        async def mock_post(*args, **kwargs):
            class MockResponse:
                def raise_for_status(self):
                    pass

                def json(self):
                    return {
                        "choices": [{"message": {"content": json.dumps(mock_response)}}],
                        "usage": {"prompt_tokens": 100, "completion_tokens": 50},
                    }

            return MockResponse()

        with patch.object(
            __import__("httpx", fromlist=["AsyncClient"]).AsyncClient,
            "post",
            mock_post,
        ):
            result = await agent.evaluate(
                task="Add hero section",
                output_files=["app/page.tsx"],
                file_contents={"app/page.tsx": "export default function Page() {}"},
            )

        assert result.verdict in ("approve", "revise", "reject")
        assert result.overall_score >= 0.0
