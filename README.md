# taste-agent

<p align="center">
  <img src="docs/mascot.png" alt="taste-agent mascot" width="256" />
</p>

**"Your AI coding agent is blind to taste — on the full stack. Fix that."**

`taste-agent` is an adversarial design director for AI coding agents that enforces *your* vision — not its generic default output — across the entire codebase: frontend *and* backend, architecture *and* copy, API contracts *and* naming conventions. Write `taste.md` once, `taste.vision` to capture intent, then let `taste-agent` adversarially evaluate every output with `APPROVE | REVISE | REJECT` verdicts. `taste.memory` learns what works across your project.

Unlike aesthetic-only tools, taste-agent evaluates **what your code says and does**, not just how it looks.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP Native](https://img.shields.io/badge/MCP-Native-blue.svg)](https://modelcontextprotocol.io)

---

## The Problem

AI coding agents are blind to taste — not just visual taste, but *all* taste:

- **Frontend**: They ship glassmorphism that looks amateur, copy that says nothing ("we help you transform"), CTAs that don't convert
- **Backend**: They create `foo_service.py` and `get_data()` functions that will confuse every developer who reads them in six months
- **Architecture**: They introduce circular dependencies, inconsistent layer boundaries, and API contracts that drift apart over time
- **Copy**: They write docstrings in a different voice than the project's established tone
- **API design**: They return different response shapes from the same endpoint across different sprints

The current solution — arguing with the AI on every file — doesn't scale. And it's not just frontend. A beautiful UI on top of a confusing API is still a bad product.

## The Solution

`taste-agent` adds an adversarial director to your AI coding workflow across **9 evaluation dimensions**:

1. **Aesthetic** — colors, typography, spacing, glassmorphism quality, motion
2. **UX** — layout hierarchy, interaction patterns, accessibility, mobile
3. **Copy** — voice, tone, headlines, CTAs, objection handling
4. **Adherence** — non-negotiable rules from taste.md
5. **Architecture** — folder structure, module boundaries, separation of concerns
6. **Naming** — variables, functions, files, routes, database tables
7. **API Design** — REST/RPC patterns, response shapes, error formats
8. **Code Style** — abstraction level, comment philosophy, function length
9. **Coherence** — cross-file consistency, drift detection over time

`taste-agent` evaluates **what the code says and does**, not just how it looks.

---

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
print(result.issues)   # Specific, actionable issues with severity
```

---

## Two Artifacts Per Project

### `taste.md` — Human-Written Design Spec

Written once by the human. Defines *what good looks like* across all 9 dimensions:

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

## 6. Copy Voice
- Tone: confident, direct, no hedging
- Results-oriented: metrics, timelines, guarantees

### Approved Headlines
- Hero H1: "The Execution Layer for Claude at Enterprise Scale"

### Rejected Patterns
- Placeholder/hallmark copy ("we help you achieve your goals")
- Corporate boilerplate ("synergy", "leverage")

## 7. Non-Negotiables (Hard Rules)
- NO Tailwind CSS — custom design system only
- NO emoji in UI
- NO gradient backgrounds on glass cards

## 8. Architecture Standards
- Layered architecture: routes → services → repositories
- Domain-driven module boundaries (not functional silos)
- No circular imports across layer boundaries
- All database access through repository pattern

## 9. Naming Conventions
- Files: `snake_case.py` for modules, `PascalCase.py` for classes
- Functions: `verb_object()` — `get_user()`, `create_order()`
- Variables: descriptive, no single letters except counters
- Database tables: `snake_case_plural` — `users`, `order_items`
- API routes: `kebab-case-plural` — `/user-profiles`, `/lead-tasks`

## 10. API Design Philosophy
- RESTful resource-based routing
- Response envelope: `{ "data": ..., "meta": {...} }`
- Error format: `{ "error": { "code": "...", "message": "...", "details": [...] } }`
- Always return appropriate status codes
- Pagination: cursor-based for collections

## 11. Code Style
- Function max length: 40 lines (extract helpers)
- Comment philosophy: explain *why*, not *what*
- Abstraction: allow one level of indirection for domain concepts
- No magic numbers — use named constants

## 12. Agent Prompt Guide
```
Color tokens: --bg: #0a0a0b, --accent: #ff6b35
Font: Sora (headings), Inter (body)
CTA: orange (#ff6b35), rounded-lg, scale on press
Glass: backdrop-filter: blur(20px) only
Layered architecture: routes → services → repositories
```
```

### `taste.vision` — Intent Document (Separate from taste.md)

`taste.vision` captures the *why* behind the rules, not just the rules themselves. Written once, read occasionally:

```markdown
# Vision — My Project

## Why This Project Exists
We build tools for enterprise infrastructure teams who are tired of AI demos
that look great in screenshots but fall apart in production. Every design
decision should make a skeptical CTO nod.

## What We Are Not
- Not a startup. We don't use "revolutionary" or "game-changing."
- Not a design agency. We don't lead with visuals — we lead with precision.
- Not trying to be liked. We're trying to be trusted.

## Anti-Goals (What We Explicitly Reject)
- Features that require a PhD to understand
- UIs that hide complexity instead of explaining it
- Documentation written for the team that built it, not the team inheriting it

## What P95 Looks Like for This Project
Linear-quality precision. Stripe Radar data density. Not prettier — clearer.
The person who inherits this codebase in 3 years should not need to ask "why
does this exist?"

## Where We Will Not Compromise
- Data integrity: never silently swallow errors
- Operational clarity: every action has a traceable log entry
- API contracts: once published, response shapes are versioned, never broken
```

### `taste.memory` — Learned Memory

Written by `taste-agent` on every REVISE/REJECT. Append-only log of what failed and why:

```jsonl
{"entry_id": "tm-a1b2c3d4", "timestamp": "2026-04-13T10:30:00Z",
 "task_description": "Add hero section", "file_path": "app/page.tsx",
 "verdict": "REVISE", "reasoning": "Primary color wrong",
 "severity": "P1", "principle": "Always use #ff6b35 as primary accent on dark backgrounds",
 "category": "aesthetic", "was_applied": false}
```

Memory is consolidated periodically:
- Merges similar principles (Jaccard similarity > 0.85)
- Prunes entries that never led to improvement

---

## Severity System

Every issue has a severity that determines the verdict:

| Severity | Meaning | Verdict Impact |
|----------|---------|----------------|
| **P0 (BLOCKER)** | Violates a hard non-negotiable from taste.md. Must fix before proceeding. | REJECT |
| **P1 (MAJOR)** | Significant deviation from aesthetic/architecture standard. Fix in current iteration. | REVISE (2+ P1s) |
| **P2 (MINOR)** | Drift that doesn't break vision but accumulates debt. Fix in next iteration. | REVISE (4+ P2s) |
| **P3 (SUGGESTION)** | Opportunity to exceed the spec, not just meet it. | APPROVE + note |

**REJECT only triggers on P0 violations. REVISE triggers on 2+ P1 issues.**

---

## Evaluation Dimensions

### Aesthetic (Frontend)
- Color harmony: intentional palette use vs arbitrary colors
- Typography: scale, hierarchy, pairing appropriateness
- Spacing: generous vs cramped
- Glassmorphism: refined (backdrop-filter only) vs amateur (gradient overlays)
- Motion: professional vs attention-seeking

### UX (Frontend)
- Layout: natural information hierarchy
- Interaction: purposeful micro-interactions
- Accessibility: WCAG 2.1 AA, 4.5:1 contrast
- Mobile: responsive, touch-friendly
- Flow: does the interaction feel natural?

### Copy (All outputs)
- Headlines: specific and tested vs generic and vague
- CTAs: compelling and conversion-focused vs wishy-washy
- Tone: confident and direct vs hedging and corporate
- Objection handling: real fears addressed vs strawman questions
- Docstring voice: consistent with taste.vision specified voice

### Adherence (All outputs)
- Non-negotiables: zero violations of hard rules
- Component standards: match specified inventory
- Architecture rules: layered structure, no circular deps
- Naming rules: consistent conventions across files

### Architecture (Backend)
- Folder structure: matches taste.md layer definitions
- Module boundaries: domain-driven separation, no god modules
- Separation of concerns: routes ≠ business logic ≠ data access
- Dependency direction: outward-in, no inward imports

### Naming (All code)
- Files: consistent casing (snake_case.py vs PascalCase.py)
- Functions: verb_object pattern, no generic names
- Variables: descriptive, no Hungarian notation
- Database tables: consistent pluralization

### API Design (Backend)
- REST/RPC consistency: routes follow consistent patterns
- Response shapes: same endpoint returns consistent structure
- Error formats: structured errors with codes, not raw messages
- Versioning: breaking changes are versioned, not silently introduced

### Code Style (All code)
- Function length: within taste.md tolerance
- Comment philosophy: explains *why*, not *what*
- Abstraction level: consistent across modules

### Coherence (Cross-file)
- Drift detection: flag when sprint 8 component contradicts sprint 1
- Cross-file consistency: same concept has same name everywhere
- Temporal coherence: output is consistent with project's established patterns

---

## CLI Commands

```bash
# Initialize taste.md in current directory (interactive wizard)
taste init

# Lint taste.md for contradictions and missing sections
taste lint

# Scan entire project and produce coherence report
taste scan

# Review taste.memory and suggest taste.md updates
taste evolve

# Explain why an element passes or fails
taste explain "app/page.tsx:23"

# Diff two taste.md versions
taste diff v1.2 v1.3

# CI gate — exit 1 if REJECT verdict count > threshold
taste gate --max-reject 0

# Manage taste.vision separately from taste.md
taste vision init
taste vision diff
```

### `taste init` — First-Run Wizard

Generates a first-draft `taste.md` by asking 10 opinionated questions:

1. Project type (web app, API, CLI tool, library, full-stack)
2. Industry vertical (B2B SaaS, consumer, developer tools, etc.)
3. Reference benchmarks (3 URLs you want to match quality of)
4. Aesthetic direction (dark institutional, light minimal, bold brutalist, etc.)
5. Copy voice (confident/direct, friendly/approachable, technical/precise)
6. Technical stack (frontend framework, backend framework, API style)
7. Architecture preferences (layered, domain-driven, microservices)
8. Naming conventions (current project style or strict rules)
9. Non-negotiables (3-5 hard rules that must never be broken)
10. Quality bar (Linear level, Stripe level, presentable, prototype)

### `taste lint` — Spec Validator

Validates `taste.md` for:
- Internal contradictions (e.g., "always use Sora" + "Sora is too expensive for our users")
- Missing sections that match the project type
- Non-negotiable rules that conflict with architecture rules
- Overly vague rules that provide no evaluation signal
- Outdated benchmarks (URLs that return 404)

### `taste scan` — Full Project Audit

Scans the entire project at once and produces a **coherence report**:
- Cross-file naming consistency score
- Architecture boundary violations
- Drift from taste.md over time (comparing sprint 1 vs sprint 8 output)
- Hotspots: files with most violations

### `taste gate` — CI/CD Integration

Blocks merges if taste standards are not met:

```yaml
# .github/workflows/taste-gate.yml
- name: Taste Gate
  run: taste gate --max-reject 0 --fail-on P0
```

---

## Evaluation Response Format

```json
{
  "verdict": "REVISE",
  "scores": {
    "aesthetic": 0.6,
    "ux": 0.7,
    "copy": 0.4,
    "adherence": 0.8,
    "architecture": 0.9,
    "naming": 0.5,
    "api_design": 0.9,
    "code_style": 0.7,
    "coherence": 0.8
  },
  "overall_score": 0.66,
  "reasoning": "Hero copy is generic placeholder — violates non-negotiable 'no hallmark copy'",
  "issues": [
    {
      "severity": "P0",
      "dimension": "copy",
      "location": "app/page.tsx:23",
      "problem": "Headline 'We help you transform your business' is hallmark/placeholder copy",
      "fix_required": "Replace with: 'The Execution Layer for Claude at Enterprise Scale'",
      "non_negotiable_violated": "No hallmark/placeholder copy"
    },
    {
      "severity": "P1",
      "dimension": "naming",
      "location": "services/user.py:45",
      "problem": "Function named 'get_data()' is too generic — violates verb_object naming",
      "fix_required": "Rename to: get_user_profile() or fetch_user_by_id()"
    }
  ],
  "principles_learned": [
    "Always use specific, tested headlines from taste.md. Never generic transformation copy."
  ],
  "revision_guidance": "Step 1: Replace line 23 headline with approved copy from taste.md section 6. Step 2: Rename get_data() to a descriptive function name."
}
```

---

## Mentor Mode — For Devs Who Don't Have Taste

`taste-agent` works for two audiences simultaneously:

**Devs with taste** — use `taste.md` as enforcement: "my vision, guarded"
**Devs without taste** — use `taste-agent` as a teacher: "why does this matter?"

On every REVISE/REJECT, Mentor Mode includes a **"Why This Matters"** section:

```json
{
  "revision_guidance": "Replace the generic 'We help you' copy.",
  "why_this_matters": "Generic copy signals that you haven't thought about who you're talking to. Enterprise buyers in particular are trained to distrust vague promises. Specific, tested copy ('The Execution Layer for Claude at Enterprise Scale') signals authority and specificity — the same traits you're trying to project as a company."
}
```

```bash
# Explain any UI element or code pattern
taste explain "app/page.tsx:23"  # Why this headline passes or fails
taste explain "services/foo.py"   # Why this module structure is or isn't correct

# Weekly digest — recurring taste.memory pattern summary
taste digest  # Emails a summary of this week's recurring violations
```

---

## Live Page Evaluation (Frontend)

For frontend projects, static file analysis is insufficient. taste-agent integrates with **Playwright MCP** for live evaluation:

```python
# In your evaluation pipeline
agent = TasteAgent(config)

result = await agent.evaluate_live(
    task="Add hero section",
    url="http://localhost:3000",
    viewport="mobile",  # Mobile is the real UI — desktop is bonus
    interactions=["hover:.cta", "click:.accordion"],
)
```

Live evaluation checks:
- **Rendered output** matches taste.md color tokens (not just source code)
- **Hover states** behave as specified
- **Transitions** are subtle and professional (not attention-seeking)
- **Mobile viewport** is usable and beautiful
- **Accessibility** via Playwright accessibility tree

---

## taste.md Versioning

`taste.md` evolves with the project. Track changes explicitly:

```markdown
# Taste — My Project (v2.1)

## Changelog
- v2.1 (2026-06-01): Added API design section after discovering
  inconsistent response shapes across /users endpoints
- v2.0 (2026-04-01): Added architecture section after sprint 8
  introduced circular dependencies
- v1.0 (2026-01-01): Initial spec
```

```bash
# See what changed between versions
taste diff v2.0 v2.1

# Evolve taste.md based on taste.memory patterns
taste evolve  # Reviews taste.memory, suggests spec updates
```

---

## Multi-Persona Support

One `taste.md` doesn't fit all contexts. Named personas within the spec:

```markdown
[persona.marketing]
## Copy Voice (Marketing Site)
Tone: bold, direct, objection-handling
CTAs: high-friction qualification forms

[persona.internal]
## Copy Voice (Internal Tools)
Tone: efficient, minimal, keyboard-first
No marketing copy — pure utility

[persona.api]
## API Design (Public API)
RESTful, versioned, comprehensive error codes
Response shapes stable for 12+ months
```

Evaluation uses the correct persona based on the file being evaluated:
- `webapp/pages/*` → `persona.marketing`
- `internal/tools/*` → `persona.internal`
- `api/routes/*` → `persona.api`

---

## Integration

### ForgeGod (First-Class)

```toml
# .forgegod/config.toml
[taste]
enabled = true
model = "zai:glm-5.1"
taste_spec_path = "taste.md"
taste_vision_path = "taste.vision"
memory_path = ".forgegod/taste.memory"
require_taste_md = true
auto_approve_threshold = 0.9
max_revision_cycles = 3

# CLI gate — blocks merge if P0 violations detected
[taste.gate]
max_reject = 0
fail_on = ["P0"]
notify_on_reject = ["slack", "github"]

# Mentor mode for devs who need teaching
[taste.mentor]
enabled = true
explain_why = true
weekly_digest = true
```

### Claude Code (MCP Native)

```bash
# Install MCP server
pip install "taste-agent[mcp]"

# Add to Claude Code's MCP settings
mcp__taste__evaluate  # Evaluate files after every ToolUse
```

### Other Agents

`taste-agent` is agent-agnostic. Works with any AI coding agent:

```python
# Cursor, Claude Code, or any agent
result = await taste_agent.evaluate(task=task, output_files=files)
```

### CI/CD Integration

```yaml
# GitHub Actions
- name: Taste Gate
  run: taste gate --max-reject 0 --fail-on P0
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

# GitLab CI
- taste gate --max-reject 0
```

---

## Architecture

```
taste-agent/
├── src/taste_agent/
│   ├── __init__.py
│   ├── version.py
│   ├── core/
│   │   ├── taste_agent.py       # Main TasteAgent class
│   │   ├── verdict.py           # VERDICT enum + severity
│   │   ├── memory.py            # TasteMemory read/write
│   │   └── config.py            # TasteConfig (pydantic)
│   ├── prompts/
│   │   ├── taste_system.py     # System prompt fragment
│   │   └── verdict_prompt.py   # Per-task evaluation prompt
│   ├── models/
│   │   ├── taste_spec.py       # Parsed taste.md + taste.vision
│   │   ├── evaluation.py        # EvaluationResult + Issue + Severity
│   │   └── coherence.py         # Cross-file coherence analysis
│   ├── evaluators/
│   │   ├── aesthetic.py        # Colors, typography, spacing
│   │   ├── ux.py               # Layout, interaction, accessibility
│   │   ├── copy.py             # Voice, tone, microcopy
│   │   ├── adherence.py        # Non-negotiable checks
│   │   ├── architecture.py     # Layer boundaries, module structure
│   │   ├── naming.py          # Variable, function, file naming
│   │   ├── api_design.py       # REST patterns, response shapes
│   │   ├── code_style.py       # Abstraction, comments, length
│   │   └── coherence.py        # Cross-file, temporal drift
│   ├── memory_store/
│   │   ├── file_store.py       # JSONL flat file store (default)
│   │   └── sqlite_store.py     # SQLite (high-volume)
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── init_cmd.py         # taste init wizard
│   │   ├── lint_cmd.py         # taste lint validator
│   │   ├── scan_cmd.py         # taste scan auditor
│   │   ├── evolve_cmd.py       # taste evolve suggester
│   │   ├── explain_cmd.py      # taste explain mentor
│   │   ├── diff_cmd.py         # taste diff versioner
│   │   └── gate_cmd.py         # taste gate CI/CD
│   ├── integration/
│   │   ├── forgegod_integration.py
│   │   ├── claude_code_mcp.py  # MCP server for Claude Code
│   │   └── playwright_live.py  # Live page evaluation
│   └── utils/
│       ├── markdown.py         # taste.md parsing
│       ├── diff.py             # Diff visualization
│       └── severity.py         # Severity classifier
├── tests/
├── examples/
│   ├── minimal/taste.md
│   ├── full/taste.md
│   └── full/taste.vision
└── docs/
    ├── mascot.png              # Official mascot (PNG)
    ├── mascot.svg              # CLI mascot (SVG, inverted triangle + tentacles)
    ├── GETTING_STARTED.md
    ├── TASTE_SPEC_FORMAT.md
    ├── TASTE_VISION_FORMAT.md
    ├── SEVERITY_SYSTEM.md
    └── INTEGRATION.md
```

---

## vs. Alternatives

| | taste-agent | Anthropic Harness Design | Google Stitch | VoltAgent awesome-design-md |
|--|--|--|--|--|
| **Spec** | Human-written taste.md | AI-generated criteria | Template-based | Community design presets |
| **Memory** | Learns across REJECTs | Static evaluation | Static | Static |
| **Frontend evaluation** | Yes | Yes (Playwright) | Yes | Yes |
| **Backend evaluation** | Yes (arch, naming, API, code style) | No | No | No |
| **Coherence** | Cross-file + temporal drift | No | No | No |
| **Severity system** | P0/P1/P2/P3 | Flat | Flat | Flat |
| **Mentor mode** | Yes | No | No | No |
| **CLI tools** | init/lint/scan/evolve/explain/diff/gate | No | No | No |
| **Agent-agnostic** | Yes | No | No | No |
| **MCP-native** | Yes | No | No | No |

**The key differentiator**: No one evaluates what your code *says and does*, not just how it *looks*. taste-agent is the only tool that covers the full stack — from CSS colors to database table naming to API response shapes.

---

## Dependencies

- `pydantic>=2.0` — Data validation and settings
- `httpx>=0.27` — HTTP client (for LLM API calls)

Optional:
- `playwright>=1.40` — Live page evaluation (`pip install taste-agent[live]`)
- `aiosqlite>=0.20` — SQLite memory store (`pip install taste-agent[sqlite]`)

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

---

`taste-agent` is part of the WAITDEAD system (Audit. Plan. Scale.) and complements [effort-agent](https://github.com/waitdeadai/effort-agent) — effort-agent answers "did you do the work?", taste-agent answers "did you do it *right*?"
