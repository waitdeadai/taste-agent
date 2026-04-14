# taste-agent

**"Your AI coding agent is blind to taste. Fix that."**

`taste-agent` is an adversarial design director for AI coding agents. It evaluates every output against a human-written `taste.md` spec and an accumulated `taste.memory`, issuing `APPROVE | REVISE | REJECT` verdicts that force quality up to SOTA.

---

## The Problem

AI coding agents are excellent at implementation — but blind to taste:

- They ship "technically correct but tasteless" code
- Glassmorphism borders that look amateur
- Copy that says nothing ("we help you transform your business")
- CTAs that don't convert
- No aesthetic consistency across a project

The current solution is to argue with the AI on every single file. That's not scalable.

## The Solution

`taste-agent` adds an adversarial design director to your AI coding workflow:

1. **Write `taste.md` once** — like a design brief (aesthetic direction, benchmarks, non-negotiables, copy examples)
2. **taste-agent enforces it** — adversarially, on every output
3. **`taste.memory` learns** — every REVISE/REJECT teaches future iterations

## Quick Start

```bash
pip install taste-agent
```

```python
from taste_agent import TasteAgent, TasteConfig

config = TasteConfig(
    taste_spec_path="taste.md",
    memory_path=".taste/taste.memory",
    enabled=True,
)
agent = TasteAgent(config, project_root=".")

result = await agent.evaluate(
    task="Add hero section to landing page",
    output_files=["app/page.tsx"],
    file_contents={"app/page.tsx": open("app/page.tsx").read()},
)

print(result.verdict)  # APPROVE | REVISE | REJECT
print(result.reasoning)
print(result.issues)   # Specific, actionable issues
```

---

## Two Artifacts Per Project

### `taste.md` — Human-Written Design Spec

Written once by the human. Never modified by the AI. Example:

```markdown
# Taste — My Project

## 1. Visual Theme & Atmosphere
Dark institutional elegance meets technical precision. Not AI-startup hype.
Corporate, serious, trustworthy.

## 2. Reference Benchmarks
- https://linear.app — dark glass, precision typography
- https://stripe.com/radar — data density without clutter

## 3. Color Palette
| Name    | Hex     | Role          |
|---------|---------|---------------|
| Background | #0a0a0b | Page background |
| Accent  | #ff6b35 | CTAs, highlights |

## 4. Typography
- Headings: **Sora** (geometric with personality)
- Body: **Inter** (optical sizing)

## 5. Component Standards
### CTA Button
- Primary: bg #ff6b35, white text, rounded-lg
- Hover: brightness-110 + shadow

### Glass Card
- Background: rgba(17,17,20,0.8) + backdrop-filter: blur(20px)
- Border: 1px solid rgba(255,255,255,0.08)
- Border-radius: 16px

## 6. Copy Voice
- Tone: confident, direct, no hedging
- Technical authority without being cold
- Results-oriented: metrics, timelines, guarantees

### Approved Headlines
- Hero H1: "The Execution Layer for Claude at Enterprise Scale"

### Rejected Patterns
- Placeholder/hallmark copy ("we help you achieve your goals")
- Corporate boilerplate ("synergy", "leverage")

## 7. Non-Negotiables (Hard Rules)
- NO Tailwind CSS — custom design system only
- NO gradient backgrounds on glass cards
- NO emoji in UI
- NO motion that draws attention to itself
```

### `taste.memory` — Learned Memory

Written by `taste-agent` on every REVISE/REJECT. Append-only log of what failed and why:

```jsonl
{"entry_id": "tm-a1b2c3d4", "timestamp": "2026-04-13T10:30:00Z", "task_description": "Add hero section", "file_path": "app/page.tsx", "verdict": "REVISE", "reasoning": "Primary color wrong", "principle": "Always use #ff6b35 as primary accent on dark backgrounds", "category": "aesthetic"}
```

Memory is consolidated periodically (similar to ForgeGod's AutoDream):
- Merges similar principles (Jaccard similarity > 0.85)
- Prunes entries that never led to improvement

---

## Evaluation Dimensions

`taste-agent` evaluates across 4 dimensions:

| Dimension | Checks |
|-----------|--------|
| **Aesthetic** | Colors, typography, spacing, glassmorphism, motion |
| **UX** | Layout, interaction, accessibility, mobile, responsiveness |
| **Copy** | Voice, tone, headlines, CTAs, objection handling |
| **Adherence** | Non-negotiables, component standards, anti-patterns |

---

## Verdict

| Verdict | Meaning |
|---------|---------|
| **APPROVE** | Output meets taste.md standards. Proceed. |
| **REVISE** | Taste issues found. Fix with specific feedback. |
| **REJECT** | Fundamental violation of non-negotiables. Rewrite. |

---

## Integration

### ForgeGod

```toml
# .forgegod/config.toml
[taste]
enabled = true
model = "zai:glm-5.1"
taste_spec_path = "taste.md"
memory_path = ".forgegod/taste.memory"
auto_approve_threshold = 0.9
max_revision_cycles = 3
```

See [INTEGRATION.md](docs/INTEGRATION.md) for full ForgeGod integration guide.

### Other Agents

`taste-agent` is agent-agnostic. Works with any AI coding agent that can call a Python function or make an HTTP request:

```python
# Cursor, Claude Code, or any agent
result = await taste_agent.evaluate(task=task, output_files=files)
```

---

## Memory Consolidation

`taste.memory` undergoes periodic consolidation:

- **Trigger A**: 20+ entries since last consolidation
- **Trigger B**: 24+ hours since last consolidation

Consolidation:
- Merges similar principles (Jaccard similarity > 0.85)
- Prunes entries with `was_applied=false` + `applied_correctly=false`
- Writes updated meta file

---

## Architecture

```
taste-agent/
├── core/
│   ├── taste_agent.py   # Main class
│   ├── verdict.py       # VERDICT enum
│   ├── memory.py        # TasteMemory (JSONL store)
│   └── config.py       # TasteConfig
├── models/
│   ├── taste_spec.py    # Parsed taste.md
│   └── evaluation.py    # EvaluationResult
├── prompts/
│   ├── taste_system.py   # System prompt fragment
│   └── verdict_prompt.py # Per-task prompt
├── evaluators/
│   ├── aesthetic.py     # Color/typography/spacing
│   ├── ux.py            # Layout/interaction
│   ├── copy.py          # Voice/tone/copy
│   └── adherence.py     # Non-negotiable checks
└── memory_store/
    ├── file_store.py    # JSONL (default)
    └── sqlite_store.py  # SQLite (high-volume)
```

---

## License

Apache 2.0 — use freely, modify freely, contribute back.

---

## The Compelling Pitch

**"Write taste.md once. Enforce it on every output. Learn what works."**

`taste-agent` is inspired by VoltAgent/awesome-design-md (48k stars) but adds adversarial evaluation + memory that learns.

Where awesome-design-md is a **static collection** of design presets, `taste-agent` is an **active enforcement mechanism** that learns from every REVISE/REJECT and gets smarter over time.
