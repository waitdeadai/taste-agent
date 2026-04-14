"""taste.md schema — human-written design specification."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ColorToken:
    """A color in the design palette."""

    name: str
    hex: str
    role: str  # primary | secondary | accent | semantic | background | text


@dataclass
class TypographyRule:
    """A typography rule for an element."""

    element: str  # h1 | h2 | h3 | body | caption | mono
    font_family: str
    size: str
    weight: str = ""
    line_height: str = ""


@dataclass
class ComponentStandard:
    """A component standard (button, card, input, etc.)."""

    name: str
    description: str
    states: list[str] | None = None


@dataclass
class CopyExample:
    """A copy example (approved or rejected)."""

    category: str  # "approved" | "rejected"
    text: str
    context: str = ""  # where this copy appears


@dataclass
class RevisionNote:
    """A note about a revision made to the taste spec."""

    date: str
    change: str
    reason: str = ""


@dataclass
class TasteSpec:
    """Parsed taste.md — human-written design specification.

    This is written BY THE HUMAN and describes what "good" looks like
    for a project. The Taste Agent uses this as the source of truth.

    Sections mirror Google Stitch's DESIGN.md format.
    """

    project_name: str = ""
    aesthetic_direction: str = ""
    mood_words: list[str] = field(default_factory=list)
    benchmarks: list[str] = field(default_factory=list)
    color_tokens: list[ColorToken] = field(default_factory=list)
    typography: list[TypographyRule] = field(default_factory=list)
    component_standards: list[ComponentStandard] = field(default_factory=list)
    copy_voice: str = ""
    copy_examples: list[CopyExample] = field(default_factory=list)
    non_negotiables: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)
    layout_spacing: dict[str, str] = field(default_factory=dict)
    revision_history: list[RevisionNote] = field(default_factory=list)
    agent_prompt_guide: str = ""

    @classmethod
    def from_markdown(cls, content: str) -> "TasteSpec":
        """Parse a taste.md markdown file into a TasteSpec."""
        spec = cls()
        lines = content.split("\n")
        current_section = ""
        current_component_name = ""
        current_component_desc: list[str] = []

        for line in lines:
            stripped = line.strip()

            # Section headers (## 1. through ## 9.)
            section_match = re.match(r"##\s+(\d+)\.\s+(.+)", stripped)
            if section_match:
                current_section = section_match.group(2).strip().lower()
                continue

            # H2-level sections without numbers
            if stripped.startswith("## "):
                current_section = stripped[3:].strip().lower()
                continue

            if not current_section:
                # Check for title (# Taste — ...)
                title_match = re.match(r"#\s+Taste\s+[-—]\s+(.+)", stripped)
                if title_match:
                    spec.project_name = title_match.group(1).strip()
                continue

            # Section 1: Visual Theme & Atmosphere
            if "visual theme" in current_section or "aesthetic direction" in current_section:
                if stripped and not stripped.startswith("#"):
                    spec.aesthetic_direction += " " + stripped
                    spec.aesthetic_direction = spec.aesthetic_direction.strip()
                    # Extract mood words
                    mood_words = re.findall(r"\b(dark|light|bold|subtle|corporate|playful|technical|warm|cold|premium|mature|youthful)\b", stripped, re.IGNORECASE)
                    for w in mood_words:
                        if w.lower() not in spec.mood_words:
                            spec.mood_words.append(w.lower())

            # Section 2: Reference Benchmarks
            elif "reference" in current_section or "benchmark" in current_section:
                if stripped.startswith("- ") or stripped.startswith("* "):
                    url = stripped[2:].strip().split("—")[0].strip()
                    if url.startswith("http"):
                        spec.benchmarks.append(url)

            # Section 3: Color Palette
            elif "color" in current_section:
                # Parse markdown tables
                if "|" in stripped and stripped.startswith("|"):
                    parts = [p.strip() for p in stripped.split("|")[1:-1]]
                    if len(parts) >= 3 and not any(x in parts[0].lower() for x in ["name", "hex", "role"]):
                        # Name | Hex | Role format
                        spec.color_tokens.append(
                            ColorToken(name=parts[0], hex=parts[1], role=parts[2])
                        )
                elif stripped.startswith("- ") or stripped.startswith("* "):
                    # - Primary: #ff6b35 (CTAs, highlights)
                    color_match = re.match(r"-?\s*(.+?):\s*(#[0-9a-fA-F]{6,8})\s*\((.+)\)", stripped)
                    if color_match:
                        spec.color_tokens.append(
                            ColorToken(
                                name=color_match.group(1).strip().lower(),
                                hex=color_match.group(2),
                                role=color_match.group(3),
                            )
                        )

            # Section 4: Typography
            elif "typograph" in current_section:
                if stripped.startswith("- ") or stripped.startswith("* "):
                    # - Headings: **Sora** (geometric)
                    font_match = re.match(r"-?\s*(.+?):\s*\*\*(.+?)\*\*", stripped)
                    if font_match:
                        element = font_match.group(1).strip().lower()
                        family = font_match.group(2)
                        # Check for size/weight hints
                        size_match = re.search(r"\b(\d+px|\d+rem)\b", stripped)
                        weight_match = re.search(r"\b(\d{3})\b", stripped)
                        rule = TypographyRule(
                            element=element,
                            font_family=family,
                            size=size_match.group(1) if size_match else "",
                            weight=weight_match.group(1) if weight_match else "",
                        )
                        spec.typography.append(rule)

            # Section 5: Component Standards
            elif "component" in current_section:
                if stripped.startswith("### "):
                    if current_component_name and current_component_desc:
                        spec.component_standards.append(
                            ComponentStandard(
                                name=current_component_name,
                                description=" ".join(current_component_desc),
                            )
                        )
                    current_component_name = stripped[4:].strip()
                    current_component_desc = []
                elif stripped and not stripped.startswith("#"):
                    current_component_desc.append(stripped)
                elif not stripped and current_component_name:
                    spec.component_standards.append(
                        ComponentStandard(
                            name=current_component_name,
                            description=" ".join(current_component_desc),
                        )
                    )
                    current_component_name = ""
                    current_component_desc = []

            # Section 6: Copy Voice
            elif "copy voice" in current_section or "tone" in current_section:
                if stripped.startswith("- ") or stripped.startswith("* "):
                    spec.copy_voice += " " + stripped[2:]
                    spec.copy_voice = spec.copy_voice.strip()

            # Section 7: Non-Negotiables
            elif "non-negotiable" in current_section or "hard rules" in current_section:
                if stripped.startswith("- NO ") or stripped.startswith("* NO "):
                    rule = re.sub(r"^-?\s*NO\s+", "", stripped).strip()
                    rule = re.sub(r"^.+?\s+[-–—]\s+", "", rule).strip()
                    if rule not in spec.non_negotiables:
                        spec.non_negotiables.append(rule)
                elif stripped.startswith("- ") or stripped.startswith("* "):
                    rule = stripped[2:].strip().lstrip("NO ").strip()
                    if rule and rule not in spec.non_negotiables:
                        spec.non_negotiables.append(rule)

            # Section 8: Layout & Spacing
            elif "layout" in current_section or "spacing" in current_section:
                if ":" in stripped and not stripped.startswith("#"):
                    key, val = stripped.split(":", 1)
                    key = key.strip().lower().replace(" ", "_")
                    val = val.strip()
                    if key and val:
                        spec.layout_spacing[key] = val

            # Section 9: Agent Prompt Guide
            elif "agent prompt" in current_section or "quick reference" in current_section:
                if stripped.startswith("```") or stripped.endswith("```"):
                    continue
                if stripped:
                    spec.agent_prompt_guide += " " + stripped
                    spec.agent_prompt_guide = spec.agent_prompt_guide.strip()

        # Flush last component
        if current_component_name and current_component_desc:
            spec.component_standards.append(
                ComponentStandard(name=current_component_name, description=" ".join(current_component_desc))
            )

        return spec

    @classmethod
    def from_path(cls, path: Path | str) -> "TasteSpec":
        """Load TasteSpec from a taste.md file path."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"taste.md not found at {path}")
        return cls.from_markdown(p.read_text(encoding="utf-8", errors="replace"))

    def non_negotiables_text(self) -> str:
        """Render non-negotiables as a numbered list for prompt injection."""
        if not self.non_negotiables:
            return "None specified."
        return "\n".join(f"{i+1}. {n}" for i, n in enumerate(self.non_negotiables))

    def color_tokens_text(self) -> str:
        """Render color tokens as a readable block for prompt injection."""
        if not self.color_tokens:
            return "None specified."
        lines = []
        for c in self.color_tokens:
            lines.append(f"- {c.name}: {c.hex} ({c.role})")
        return "\n".join(lines)

    def agent_prompt_block(self) -> str:
        """Render the agent prompt guide section."""
        if self.agent_prompt_guide:
            return self.agent_prompt_guide
        # Generate from other sections
        parts = []
        if self.color_tokens:
            colors = ", ".join(f"{c.name}:{c.hex}" for c in self.color_tokens)
            parts.append(f"Colors: {colors}")
        if self.typography:
            fonts = ", ".join(f"{t.element}:{t.font_family}" for t in self.typography)
            parts.append(f"Fonts: {fonts}")
        return "\n".join(parts)
