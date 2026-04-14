"""tests/test_models/test_taste_spec.py — TasteSpec parsing and routing."""

from __future__ import annotations

import pytest

from taste_agent.models.taste_spec import ChangelogEntry, TasteSpec, VisionSpec


class TestTasteSpecFromMarkdown:
    def test_parses_aesthetic_direction(self, minimal_taste_md):
        spec = TasteSpec.from_markdown(minimal_taste_md)
        assert "dark institutional" in spec.aesthetic_direction.lower()

    def test_parses_non_negotiables(self):
        # Uses hyphen format which the parser expects
        content = """# Taste — Test Project

## 1. Visual Theme & Atmosphere
Dark institutional.

## 6. Copy Voice
Confident, direct, no hedging.

## 7. Non-Negotiables
- Placeholder copy
- Tailwind CSS
- Silent failures
"""
        spec = TasteSpec.from_markdown(content)
        assert len(spec.non_negotiables) >= 1

    def test_from_path_nonexistent_raises(self):
        with pytest.raises(FileNotFoundError):
            TasteSpec.from_path("/nonexistent/path/taste.md")


class TestVisionSpecFromMarkdown:
    def test_parses_anti_goals(self, full_taste_vision):
        spec = VisionSpec.from_markdown(full_taste_vision)
        assert len(spec.anti_goals) >= 1


class TestVisionSpecServesPurpose:
    def test_returns_true_when_anti_goal_not_in_output(self):
        spec = VisionSpec(anti_goals=["Tailwind CSS", "placeholder copy"])
        assert spec.serves_purpose("Here is some clean CSS code.") is True

    def test_returns_false_when_anti_goal_in_output(self):
        spec = VisionSpec(anti_goals=["Tailwind CSS", "placeholder copy"])
        assert spec.serves_purpose("We should use Tailwind CSS for this.") is False

    def test_empty_anti_goals_always_true(self):
        spec = VisionSpec(anti_goals=[])
        assert spec.serves_purpose("Anything goes here.") is True


class TestPersonaRouting:
    def test_markdown_with_persona_creates_persona(self, full_taste_md):
        # Add a persona block to minimal taste
        content = MINIMAL_TASTE_MD_WITH_PERSONA
        spec = TasteSpec.from_markdown(content)
        assert "marketing" in spec.personas

    def test_route_persona_webapp(self):
        spec = TasteSpec()
        spec._routing_table = {}
        from taste_agent.models.persona import DEFAULT_ROUTING

        for pattern, name in DEFAULT_ROUTING:
            spec._routing_table[pattern] = name

        result = spec.route_persona("webapp/page.tsx")
        assert result is not None

    def test_route_persona_api_routes(self):
        spec = TasteSpec()
        spec._routing_table = {}
        from taste_agent.models.persona import DEFAULT_ROUTING

        for pattern, name in DEFAULT_ROUTING:
            spec._routing_table[pattern] = name

        result = spec.route_persona("api/routes/users.py")
        assert result is not None

    def test_route_persona_default(self):
        spec = TasteSpec()
        spec._routing_table = {}
        from taste_agent.models.persona import DEFAULT_ROUTING

        for pattern, name in DEFAULT_ROUTING:
            spec._routing_table[pattern] = name

        result = spec.route_persona("src/main.py")
        assert result is spec  # base spec returned


class TestChangelog:
    def test_parses_changelog_entry(self):
        content = """# Taste — Test

## Changelog
- v2.1 (2026-06-01): Added API design section after discovering
  inconsistent response shapes across /users endpoints
- v2.0 (2026-04-01): Added architecture section
"""
        spec = TasteSpec.from_markdown(content)
        assert len(spec.changelog) >= 1
        versions = [e.version for e in spec.changelog]
        assert "2.1" in versions or "v2.1" in " ".join(versions)


class TestVisionSpecEmptyContent:
    def test_empty_content_returns_empty_spec(self):
        spec = VisionSpec.from_markdown("")
        assert spec.anti_goals == []

    def test_no_headers_content(self):
        spec = VisionSpec.from_markdown("Some text without headers")
        assert spec.anti_goals == []

    def test_p95_section_accumulates_lines(self):
        md = "## What P95 Looks Like\nFirst line\nSecond line"
        spec = VisionSpec.from_markdown(md)
        assert "First line" in spec.what_p95_looks_like
        assert "Second line" in spec.what_p95_looks_like

    def test_anti_goal_with_plain_text_line(self):
        md = "## Anti-Goals\nPlain text anti-goal"
        spec = VisionSpec.from_markdown(md)
        assert "Plain text anti-goal" in spec.anti_goals


class TestTasteSpecVersionAndChangelog:
    def test_title_without_version(self):
        md = "# Taste — My Project\n\n## 6. Copy Voice\nDirect."
        spec = TasteSpec.from_markdown(md)
        assert spec.version == ""

    def test_title_with_version(self):
        md = "# Taste — My Project (v2.1)\n\n## 6. Copy Voice\nDirect."
        spec = TasteSpec.from_markdown(md)
        assert spec.version == "v2.1"


class TestTasteSpecBenchmarkParsing:
    def test_benchmark_em_dash_separator(self):
        md = """## Reference Benchmarks\n- https://linear.app — Fast, minimal UI\n"""
        spec = TasteSpec.from_markdown(md)
        assert "https://linear.app" in spec.benchmarks

    def test_benchmark_asterisk_bullet(self):
        md = "## Reference Benchmarks\n* https://example.com"
        spec = TasteSpec.from_markdown(md)
        assert "https://example.com" in spec.benchmarks


class TestTasteSpecColorParsing:
    def test_color_table_row(self):
        md = "## Color Palette\n| Name | Hex | Role |\n|---|---|---|\n| primary | #ff6b35 | accent |"
        spec = TasteSpec.from_markdown(md)
        assert len(spec.color_tokens) >= 1

    def test_color_8_digit_hex(self):
        md = "## Color Palette\n- primary: #ff6b35ff (CTAs)"
        spec = TasteSpec.from_markdown(md)
        assert any(t.hex == "#ff6b35ff" for t in spec.color_tokens)


class TestTasteSpecNonNegotiables:
    def test_negotiable_no_prefix(self):
        md = "## Non-Negotiables\n- Placeholder copy"
        spec = TasteSpec.from_markdown(md)
        assert "Placeholder copy" in spec.non_negotiables

    def test_negotiable_with_no_prefix(self):
        md = "## Non-Negotiables\n- NO placeholder copy"
        spec = TasteSpec.from_markdown(md)
        assert len(spec.non_negotiables) >= 1

    def test_negotiable_deduplicated(self):
        md = "## Non-Negotiables\n- A\n- A"
        spec = TasteSpec.from_markdown(md)
        assert len(spec.non_negotiables) == 1


class TestTasteSpecLayoutSpacing:
    def test_layout_key_value(self):
        md = "## Layout & Spacing\ncolumn_gap: 24px"
        spec = TasteSpec.from_markdown(md)
        assert spec.layout_spacing.get("column_gap") == "24px"

    def test_layout_header_skipped(self):
        md = "## Layout & Spacing\n### Headers"
        spec = TasteSpec.from_markdown(md)
        assert spec.layout_spacing == {}


class TestTasteSpecArchitecture:
    def test_architecture_bullet(self):
        md = "## Architecture Standards\n- Data layer"
        spec = TasteSpec.from_markdown(md)
        assert "Data layer" in spec.architecture_layers


class TestTasteSpecNaming:
    def test_naming_colon_format(self):
        md = "## Naming Conventions\nfiles: snake_case.py"
        spec = TasteSpec.from_markdown(md)
        assert spec.naming_conventions.get("files") == "snake_case.py"


class TestTasteSpecApiDesign:
    def test_api_design_key_value(self):
        md = "## API Design\nrestfulness: avoid nesting"
        spec = TasteSpec.from_markdown(md)
        assert spec.api_design.get("restfulness") == "avoid nesting"


class TestTasteSpecMethods:
    def test_non_negotiables_text_empty(self):
        md = "# Taste — Test\n\n## 6. Copy Voice\nDirect."
        spec = TasteSpec.from_markdown(md)
        assert "None" in spec.non_negotiables_text()

    def test_color_tokens_text_empty(self):
        md = "# Taste — Test\n\n## 6. Copy Voice\nDirect."
        spec = TasteSpec.from_markdown(md)
        assert "None" in spec.color_tokens_text()

    def test_color_tokens_text_with_tokens(self):
        md = "## Color Palette\n| Name | Hex | Role |\n|---|---|---|\n| primary | #ff6b35 | accent |"
        spec = TasteSpec.from_markdown(md)
        txt = spec.color_tokens_text()
        assert "primary" in txt
        assert "#ff6b35" in txt


class TestPersonaRoutingBuildTable:
    def test_empty_personas_dict(self):
        from taste_agent.models.persona import build_persona_routing_table
        table = build_persona_routing_table({})
        assert table == {}

    def test_persona_uses_default_when_no_rules(self):
        from taste_agent.models.persona import PersonaSpec, build_persona_routing_table
        p = PersonaSpec(name="mkt", routing_rules=[])
        table = build_persona_routing_table({"mkt": p})
        assert "mkt" in table.values()


MINIMAL_TASTE_MD_WITH_PERSONA = """# Taste — Test Project

## 1. Visual Theme & Atmosphere
Dark institutional. Inspired by Linear.

## 6. Copy Voice
Confident, direct, no hedging.

## 7. Non-Negotiables
1. No placeholder copy
2. No Tailwind CSS

[persona.marketing]
## 6. Copy Voice
Bold, objection-handling, high-friction CTAs.
"""
