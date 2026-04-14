"""taste-agent evaluators."""

from taste_agent.evaluators.adherence import AdherenceEvaluator
from taste_agent.evaluators.aesthetic import AestheticEvaluator
from taste_agent.evaluators.api_design import ApiDesignEvaluator
from taste_agent.evaluators.architecture import ArchitectureEvaluator
from taste_agent.evaluators.code_style import CodeStyleEvaluator
from taste_agent.evaluators.coherence import CoherenceEvaluator
from taste_agent.evaluators.copy import CopyEvaluator
from taste_agent.evaluators.naming import NamingEvaluator
from taste_agent.evaluators.ux import UXEvaluator

__all__ = [
    "AdherenceEvaluator",
    "AestheticEvaluator",
    "ApiDesignEvaluator",
    "ArchitectureEvaluator",
    "CodeStyleEvaluator",
    "CoherenceEvaluator",
    "CopyEvaluator",
    "NamingEvaluator",
    "UXEvaluator",
]
