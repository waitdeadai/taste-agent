# Getting Started with taste-agent

## Installation

```bash
pip install taste-agent
```

For ForgeGod integration:
```bash
pip install "taste-agent[forgegod]"
```

## Quick Start

### 1. Create `taste.md` in Your Project Root

```bash
cp node_modules/taste-agent/examples/minimal/taste.md .
# OR copy manually from examples/full/taste.md for a full-featured example
```

Edit `taste.md` to match your project's design system.

### 2. Initialize the Taste Agent

```python
from taste_agent import TasteAgent, TasteConfig

config = TasteConfig(
    taste_spec_path="taste.md",
    memory_path=".taste/taste.memory",
    enabled=True,
)
agent = TasteAgent(config, project_root=".")
```

### 3. Evaluate Output

```python
result = await agent.evaluate(
    task="Add hero section to the landing page",
    output_files=["app/landing/page.tsx"],
    file_contents={
        "app/landing/page.tsx": open("app/landing/page.tsx").read()
    },
)

print(result.verdict)       # "approve" | "revise" | "reject"
print(result.reasoning)     # Why this verdict
print(result.issues)        # Specific issues with fix_required
print(result.scores)        # Per-dimension scores
```

### 4. Handle the Verdict

```python
if result.verdict == "reject":
    # Fundamental failure — rewrite, not revise
    await coder.rewrite(result.revision_guidance)
elif result.verdict == "revise":
    # Fix the specific issues
    await coder.revise(result.revision_guidance)
# approve — proceed
```

---

## taste.md Discovery

`taste.md` is discovered by searching **upward** from the project root:

```
~/dev/project/.git/           ← project root
~/dev/.forgegod/config.toml  ← workspace root
~/dev/taste.md               ← FOUND (org-level taste.md)
~/dev/                       ← stop at filesystem root
```

This allows a single `taste.md` at the org level to apply to all projects,
while individual projects can override with their own `taste.md`.

---

## taste.memory Location

`memory_path` is resolved relative to project root by default:

| `memory_scope` | Path |
|----------------|------|
| `"project"` | `{project}/.forgegod/taste.memory` |
| `"global"` | `~/.forgegod/taste.memory` |
| `"both"` | project first, global fallback |

---

## Configuration Options

```python
from taste_agent import TasteConfig

config = TasteConfig(
    # Enable taste gate (default: False)
    enabled=True,

    # Model for taste evaluation
    # Supports: openai:gpt-4o, anthropic:claude-3-5, zai:glm-5.1, etc.
    model="zai:glm-5.1",

    # Paths (relative to project_root)
    taste_spec_path="taste.md",
    memory_path=".forgegod/taste.memory",

    # Memory discovery
    memory_scope="both",  # "project" | "global" | "both"

    # Behavior
    require_taste_md=False,  # Fail if taste.md not found
    auto_approve_threshold=0.9,  # Score above this = auto-approve
    max_revision_cycles=3,

    # Weights for overall score
    weights=TasteWeights(
        aesthetic=0.3,
        ux=0.3,
        copy=0.2,
        adherence=0.2,
    ),
)
```

---

## Programmatic Usage

### Single Evaluation

```python
result = await agent.evaluate(
    task="Add contact form",
    output_files=["app/contact/form.tsx"],
    file_contents={"app/contact/form.tsx": code},
)
```

### With Git Diff

```python
result = await agent.evaluate(
    task="Update hero section",
    output_files=["app/page.tsx"],
    file_contents={"app/page.tsx": new_code},
    diff=old_code,  # Optional diff for context
)
```

### Without taste.md (Default Standards)

```python
config = TasteConfig(enabled=True)
# Uses built-in defaults (Linear/Vercel/Claude.ai benchmarks)
agent = TasteAgent(config)
```

---

## Memory Management

### View Memory Stats

```python
stats = agent.memory.stats()
print(stats)
# {'total': 23, 'approve': 5, 'revise': 15, 'reject': 3, 'applied': 18}
```

### Get Learned Principles

```python
principles = agent.memory.principles()
for p in principles[-10:]:
    print(f"- {p}")
```

### Force Consolidation

```python
if agent.memory.needs_consolidation():
    removed = agent.memory.consolidate()
    print(f"Consolidated: {removed} entries removed")
```

---

## CLI Usage

```bash
# Evaluate a file
taste eval app/page.tsx

# Evaluate with taste.md
taste eval --taste-path=taste.md app/

# Run on changed files
taste eval $(git diff --name-only)

# Check memory
taste memory --stats
```

---

## Next Steps

- [TASTE_SPEC_FORMAT.md](TASTE_SPEC_FORMAT.md) — Full taste.md format reference
- [INTEGRATION.md](INTEGRATION.md) — ForgeGod and other agent integrations
