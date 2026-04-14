# Taste Spec Format (`taste.md`)

`taste.md` is a human-written design specification that the Taste Agent uses as the source of truth for evaluation. It is inspired by Google Stitch's DESIGN.md format, extended with taste-specific sections.

## File Structure

`taste.md` is a single markdown file with 9 sections. Not all sections are required — only sections 1 and 7 (Visual Theme and Non-Negotiables) are essential.

---

## Section 1: Visual Theme & Atmosphere

**Purpose**: Describe the emotional feel of the product in one paragraph.

```markdown
## 1. Visual Theme & Atmosphere
Dark institutional elegance meets technical precision. Not AI-startup hype.
Corporate, serious, trustworthy. The visitor should think "these people have
done this 100 times at enterprise scale."
```

**Mood words** (optional list):
- dark / light / bold / subtle
- corporate / playful / technical / warm / cold
- premium / mature / youthful

---

## Section 2: Reference Benchmarks

**Purpose**: List 3-5 real URLs the Taste Agent must match the quality level of.

```markdown
## 2. Reference Benchmarks
- https://linear.app — dark glass, precision typography, zero fluff
- https://stripe.com/radar — data density without clutter
- https://claude.ai — warm AI authority, conversational but precise
```

These are used as SOTA reference points. Any generated output should be comparable in quality.

---

## Section 3: Color Palette & Roles

**Purpose**: Define the exact colors used in the design system.

```markdown
## 3. Color Palette & Roles
| Name | Hex | Role |
|------|-----|------|
| Background | #0a0a0b | Page background |
| Surface | #111114 | Cards, elevated |
| Border | #1e1e24 | Subtle glass edges |
| Text Primary | #f0f0f5 | Headings, body |
| Text Secondary | #8b8b99 | Muted text |
| Accent Primary | #ff6b35 | CTAs, highlights |
| Accent Secondary | #3b82f6 | Secondary actions |
```

Alternative bullet format:
```markdown
## 3. Color Palette
- Background: #0a0a0b (page background)
- Accent Primary: #ff6b35 (CTAs, highlights)
```

---

## Section 4: Typography

**Purpose**: Define font families and scale.

```markdown
## 4. Typography
- Headings: **Sora** (geometric with personality)
- Body: **Inter** (optical sizing, variable)
- Mono: **JetBrains Mono** (code blocks)
- Scale: 12/14/16/18/24/32/48/64/80px
```

---

## Section 5: Component Standards

**Purpose**: Define how specific components should look and behave.

```markdown
## 5. Component Standards

### CTA Button
- Primary: bg #ff6b35, white text, rounded-lg
- Hover: brightness-110 + shadow-lg
- Active: scale 0.98
- Disabled: opacity 0.5

### Glass Card
- Background: rgba(17,17,20,0.8) + backdrop-filter: blur(20px)
- Border: 1px solid rgba(255,255,255,0.08)
- Border-radius: 16px
- Hover: border-color → rgba(255,107,53,0.3)
```

---

## Section 6: Copy Voice

**Purpose**: Define the tone and voice for all copy.

```markdown
## 6. Copy Voice
- Tone: confident, direct, no hedging
- Technical authority without being cold
- Results-oriented: metrics, timelines, guarantees
- Objection handling: address enterprise fears head-on

### Approved Headlines
- Hero H1: "The Execution Layer for Claude at Enterprise Scale"
- Objection: "95% of AI pilots fail. We engineer for the other 5%."

### Rejected Patterns
- Placeholder/hallmark copy ("we help you achieve your goals")
- Corporate boilerplate ("synergy", "leverage")
```

---

## Section 7: Non-Negotiables (Hard Rules)

**Purpose**: List absolute rules that must never be violated.

```markdown
## 7. Non-Negotiables
- NO Tailwind CSS — custom design system only
- NO generic stock photos
- NO gradient backgrounds on glass cards
- NO emoji in UI
- NO motion that draws attention to itself
- NO placeholder/hallmark copy
```

**These are binary — any violation = REJECT verdict.**

---

## Section 8: Layout & Spacing

**Purpose**: Define spatial system.

```markdown
## 8. Layout & Spacing
- Section padding: 120px vertical (desktop), 64px (mobile)
- Card padding: 32px
- Grid: 12 columns, 24px gutter
- Max content width: 1280px
- Base unit: 4px
```

---

## Section 9: Agent Prompt Guide

**Purpose**: Quick reference snippets for AI agents.

```markdown
## 9. Agent Prompt Guide
```
Colors: --bg: #0a0a0b, --surface: #111114, --accent: #ff6b35
Font: Sora (headings), Inter (body)
CTA: #ff6b35, rounded-lg, scale on press
Glass: backdrop-filter: blur(20px) only
```
```

---

## Minimal Example

Only sections 1 and 7 are required. Everything else is optional:

```markdown
# Taste — My Project

## 1. Visual Theme
Clean, modern, professional.

## 7. Non-Negotiables
- NO Tailwind CSS
- NO emoji
```

---

## Full Example

See `examples/full/taste.md` for a complete reference.
