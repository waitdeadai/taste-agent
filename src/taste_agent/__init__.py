"""taste-agent — adversarial design director for AI coding agents.

Write taste.md once. Enforce it adversarially on every output.
taste.memory learns what works across your project.

Usage:
    from taste_agent import TasteAgent, TasteConfig, VERDICT

    config = TasteConfig(
        taste_spec_path="taste.md",
        memory_path=".taste/taste.memory",
    )
    agent = TasteAgent(config)
    result = await agent.evaluate(
        task="Add hero section to landing page",
        output_files=["app/page.tsx"],
    )
    print(result.verdict)  # APPROVE | REVISE | REJECT
"""

from taste_agent.core.config import TasteConfig
from taste_agent.core.memory import TasteMemory
from taste_agent.core.taste_agent import TasteAgent
from taste_agent.core.verdict import VERDICT, Verdict
from taste_agent.models.evaluation import EvaluationResult, Issue
from taste_agent.models.persona import PersonaSpec
from taste_agent.models.severity import Severity, SeverityCounts
from taste_agent.models.taste_spec import TasteSpec, VisionSpec

__version__ = "0.2.0"

__all__ = [
    "VERDICT",
    "EvaluationResult",
    "Issue",
    "PersonaSpec",
    "Severity",
    "SeverityCounts",
    "TasteAgent",
    "TasteConfig",
    "TasteMemory",
    "TasteSpec",
    "Verdict",
    "VisionSpec",
]
