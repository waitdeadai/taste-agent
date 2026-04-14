"""PersonaSpec — named personas for different project contexts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# Default routing rules: file path prefix → persona name
DEFAULT_ROUTING: list[tuple[str, str]] = [
    (r"^(?:webapp|pages|site|marketing|app)/", "marketing"),
    (r"^(?:internal|tools|admin|dashboard)/", "internal"),
    (r"^(?:api|routes|endpoints|v\d+)/", "api"),
]


@dataclass
class PersonaSpec:
    """A named persona with its own subset of taste rules.

    Personas allow different evaluation standards for different parts
    of the codebase. E.g., marketing copy gets different rules than
    internal tool code or public API contracts.
    """

    name: str  # e.g. "marketing", "internal", "api"
    description: str = ""
    # Subset of the parent TasteSpec relevant to this persona
    non_negotiables: list[str] = field(default_factory=list)
    copy_voice: str = ""
    copy_examples: list[str] = field(default_factory=list)
    aesthetic_direction: str = ""
    benchmarks: list[str] = field(default_factory=list)
    # Routing rules specific to this persona (overrides DEFAULT_ROUTING)
    routing_rules: list[tuple[str, str]] = field(default_factory=list)

    def route_file(self, file_path: str) -> bool:
        """Check if a file matches this persona's routing rules."""
        rules = self.routing_rules or DEFAULT_ROUTING
        persona_prefix = self.name.lower()
        for pattern, persona in rules:
            if re.match(pattern, file_path):
                return persona == persona_prefix
        return False


def build_persona_routing_table(personas: dict[str, PersonaSpec]) -> dict[str, str]:
    """Build a lookup table: file path pattern → persona name.

    Returns a dict mapping persona name to the regex pattern that routes to it.
    This is used by TasteSpec.route_persona() for fast O(1) lookups.
    """
    table: dict[str, str] = {}
    for name, persona in personas.items():
        for pattern, _ in persona.routing_rules or DEFAULT_ROUTING:
            if table.get(pattern) == name:
                continue
            table[pattern] = name
    return table
