"""tests/conftest.py — shared fixtures for taste-agent test suite."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

# Set PYTHONPATH so imports work
os.environ.setdefault("PYTHONPATH", str(Path(__file__).parent.parent / "src"))

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

# =============================================================================
# Sample code snippets
# =============================================================================

GOOD_CSS = """.hero { background: rgba(10,10,10,0.95); }
.backdrop { backdrop-filter: blur(20px); }
.btn-primary {
    background: rgba(0,255,136,0.15);
    border: 1px solid rgba(0,255,136,0.3);
    color: #00ff88;
    transition: opacity 200ms ease;
}
"""

BAD_CSS = """.hero { background: linear-gradient(135deg, #667eea, #764ba2); }
.blob { animation: blob 3s infinite; }
.magic { box-shadow: 0 4px 20px rgba(100,50,200,0.5); transition: all 300ms; }
.font { font-family: Arial, sans-serif; color: #XYZCOLOR; }
"""

GOOD_PY = """
def get_user(user_id: str) -> dict:
    return {"id": user_id}

def create_order(order_id: str) -> None:
    pass

class UserService:
    pass
"""

BAD_PY_CIRCULAR = """
from app.models import User
from app import database
"""

BAD_PY_GOD = (
    "# God module: "
    + "\n".join([f"x = {i}" for i in range(310)])
    + "\ndef do_email(): pass\ndef do_auth(): pass\ndef do_redis(): pass"
)

GOOD_API_JSON = '{"data": {"id": "1"}, "meta": {}}'
BAD_API_JSON_ERROR = '{"error": "Something went wrong"}'
GOOD_API_ERROR = '{"error": {"code": "NOT_FOUND", "message": "Not found"}}'

# =============================================================================
# Taste spec fixtures
# =============================================================================

MINIMAL_TASTE_MD = """# Taste — Test Project

## 1. Visual Theme & Atmosphere
Dark institutional. Inspired by Linear.

## 6. Copy Voice
Confident, direct, no hedging.

## 7. Non-Negotiables
1. No placeholder copy
2. No Tailwind CSS
3. No silent failures
"""

FULL_TASTE_MD = (Path(__file__).parent.parent / "examples" / "full" / "taste.md").read_text()
FULL_TASTE_VISION = (Path(__file__).parent.parent / "examples" / "full" / "taste.vision").read_text()


# =============================================================================
# Pytest fixtures
# =============================================================================


@pytest.fixture
def minimal_taste_md():
    return MINIMAL_TASTE_MD


@pytest.fixture
def full_taste_md():
    return FULL_TASTE_MD


@pytest.fixture
def full_taste_vision():
    return FULL_TASTE_VISION


@pytest.fixture
def good_css():
    return GOOD_CSS.strip()


@pytest.fixture
def bad_css():
    return BAD_CSS.strip()


@pytest.fixture
def good_py():
    return GOOD_PY.strip()


@pytest.fixture
def bad_py_circular():
    return BAD_PY_CIRCULAR.strip()


@pytest.fixture
def bad_py_god():
    return BAD_PY_GOD.strip()


@pytest.fixture
def good_api_response():
    return GOOD_API_JSON


@pytest.fixture
def bad_api_error_response():
    return BAD_API_JSON_ERROR


@pytest.fixture
def good_api_error():
    return GOOD_API_ERROR


@pytest.fixture
def tmp_jsonl_file():
    """Temporary JSONL file that persists for a test."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        path = f.name

    yield Path(path)

    Path(path).unlink(missing_ok=True)


@pytest.fixture
def mock_llm_response_approve():
    return {
        "verdict": "approve",
        "overall_score": 0.92,
        "reasoning": "Output meets taste standards.",
        "scores": {d: 0.9 for d in ALL_DIMENSIONS},
        "issues": [],
        "principles_learned": [],
        "revision_guidance": "",
    }


@pytest.fixture
def mock_llm_response_revise():
    return {
        "verdict": "revise",
        "overall_score": 0.55,
        "reasoning": "Several issues found.",
        "scores": {d: 0.55 for d in ALL_DIMENSIONS},
        "issues": [
            {
                "severity": "P1",
                "dimension": "copy",
                "location": "app/page.tsx",
                "problem": "Generic placeholder copy",
                "fix_required": "Replace with specific copy",
                "non_negotiable_violated": "",
                "why_this_matters": "Generic copy signals you haven't thought about who you're talking to.",
            }
        ],
        "principles_learned": [],
        "revision_guidance": "Replace generic copy with specific, authoritative language.",
    }
