"""tests/test_models/test_persona.py — PersonaSpec and DEFAULT_ROUTING."""

from __future__ import annotations

import pytest

from taste_agent.models.persona import DEFAULT_ROUTING, PersonaSpec


class TestDefaultRouting:
    def test_has_three_entries(self):
        assert len(DEFAULT_ROUTING) == 3

    def test_marketing_pattern(self):
        pattern, name = DEFAULT_ROUTING[0]
        assert name == "marketing"
        assert "webapp" in pattern or "pages" in pattern or "site" in pattern

    def test_internal_pattern(self):
        pattern, name = DEFAULT_ROUTING[1]
        assert name == "internal"
        assert "internal" in pattern or "admin" in pattern

    def test_api_pattern(self):
        pattern, name = DEFAULT_ROUTING[2]
        assert name == "api"


class TestPersonaSpecRouteFile:
    def test_route_file_marketing_true(self):
        persona = PersonaSpec(name="marketing")
        assert persona.route_file("webapp/index.tsx") is True

    def test_route_file_marketing_false_for_api(self):
        persona = PersonaSpec(name="marketing")
        assert persona.route_file("api/routes/users.py") is False

    def test_route_file_api_true(self):
        persona = PersonaSpec(name="api")
        assert persona.route_file("api/routes/users.py") is True

    def test_route_file_unknown_path(self):
        persona = PersonaSpec(name="marketing")
        # Should not raise, just return False
        result = persona.route_file("src/main.py")
        assert result is False
