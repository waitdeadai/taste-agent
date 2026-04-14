"""tests/test_core/test_verdict.py — Verdict class full coverage."""

from __future__ import annotations

import pytest

from taste_agent.core.verdict import VERDICT, Verdict


class TestVerdictStr:
    def test_approve_str(self):
        assert str(VERDICT.APPROVE) == "approve"

    def test_reject_str(self):
        assert str(VERDICT.REJECT) == "reject"

    def test_revise_str(self):
        assert str(VERDICT.REVISE) == "revise"


class TestVerdictToDict:
    def test_full_verdict_to_dict(self):
        v = Verdict(VERDICT.REVISE, confidence=0.8, reasoning="test",
                    issues=["issue1"], suggestions=["fix1"])
        d = v.to_dict()
        assert d["verdict"] == "revise"
        assert d["confidence"] == 0.8
        assert d["reasoning"] == "test"
        assert d["issues"] == ["issue1"]
        assert d["suggestions"] == ["fix1"]

    def test_minimal_verdict_to_dict(self):
        v = Verdict(VERDICT.APPROVE, confidence=0.5)
        d = v.to_dict()
        assert d["verdict"] == "approve"
        assert d["confidence"] == 0.5
        assert d["issues"] == []
        assert d["suggestions"] == []


class TestVerdictFromDict:
    def test_valid_reject_from_dict(self):
        d = {"verdict": "reject", "confidence": 0.3, "reasoning": "bad",
             "issues": ["p0"], "suggestions": ["rewrite"]}
        v = Verdict.from_dict(d)
        assert v.value == VERDICT.REJECT
        assert v.confidence == 0.3
        assert v.issues == ["p0"]

    def test_valid_revise_from_dict(self):
        d = {"verdict": "revise"}
        v = Verdict.from_dict(d)
        assert v.value == VERDICT.REVISE

    def test_invalid_verdict_raises(self):
        d = {"verdict": "invalid", "confidence": 0.5}
        with pytest.raises(ValueError):
            Verdict.from_dict(d)

    def test_missing_keys_use_defaults(self):
        v = Verdict.from_dict({})
        assert v.value == VERDICT.APPROVE
        assert v.confidence == 0.5
        assert v.issues == []

    def test_only_verdict_key(self):
        v = Verdict.from_dict({"verdict": "revise"})
        assert v.value == VERDICT.REVISE


class TestVerdictRepr:
    def test_repr_shows_confidence_percent(self):
        v = Verdict(VERDICT.APPROVE, confidence=0.75)
        r = repr(v)
        assert "approve" in r
        assert "75%" in r
