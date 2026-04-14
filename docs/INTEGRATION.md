# Integration Guide

`taste-agent` is agent-agnostic. It can integrate with any AI coding agent that can:
1. Call a Python function (async)
2. Make an HTTP request

## ForgeGod (Recommended)

ForgeGod has first-class support for `taste-agent`.

### 1. Install

```bash
pip install "taste-agent[forgegod]"
```

### 2. Add to `.forgegod/config.toml`

```toml
[taste]
enabled = true
model = "zai:glm-5.1"
taste_spec_path = "taste.md"
memory_path = ".forgegod/taste.memory"
memory_scope = "both"       # project first, global fallback
auto_approve_threshold = 0.9
max_revision_cycles = 3

[taste.weights]
aesthetic = 0.3
ux = 0.3
copy = 0.2
adherence = 0.2
```

### 3. Place `taste.md` in Project Root

```bash
cp taste-agent/examples/full/taste.md ./taste.md
# Customize taste.md for your project
```

### 4. Role Chain

The `taste` role is inserted into the chain:

```
planner → coder → reviewer → taste → sentinel → escalation
```

Execution order:
1. `planner` — creates plan
2. `coder` — implements plan
3. `reviewer` — correctness + security gate
4. `taste` — aesthetic + copy + UX gate
5. `sentinel` — final safety gate
6. `escalation` — human escalation

### 5. Flow

```
CODER produces output
    ↓
REVIEWER evaluates (correctness + security)
    ↓ (if APPROVE)
TASTE evaluates (aesthetic + copy + UX)
    ↓
VERDICT:
  - APPROVE → sentinel → done
  - REVISE → coder gets feedback → taste re-evaluates
  - REJECT → full redesign required → sentinel notified
```

### 6. Memory Integration

`taste.memory` is stored at:
- Project: `{project}/.forgegod/taste.memory`
- Global: `~/.forgegod/taste.memory`

Both are automatically discovered. Use `memory_scope` to control priority.

---

## Other Agents

`taste-agent` works with any AI agent via its Python API.

### Cursor

```python
# In your Cursor custom script
from taste_agent import TasteAgent, TasteConfig

agent = TasteAgent(TasteConfig(enabled=True))

@cursor.on_file_save
async def taste_check(file_path):
    result = await agent.evaluate(
        task=f"File modified: {file_path}",
        output_files=[file_path],
        file_contents={file_path: open(file_path).read()},
    )
    if result.verdict != "approve":
        cursor.show_notification(
            f"Taste issues: {result.reasoning[:100]}"
        )
```

### Claude Code (claude.ai/code)

```bash
# In CLAUDE.md
## Taste Agent
pip install taste-agent
```

```python
# Use via subprocess wrapper
import subprocess

result = subprocess.run([
    "python", "-m", "taste_agent.cli",
    "eval", "--path", "app/page.tsx"
], capture_output=True)
```

### Custom Agent

```python
import asyncio
from taste_agent import TasteAgent, TasteConfig

async def agent_loop(task, coder_output):
    config = TasteConfig(
        enabled=True,
        taste_spec_path="taste.md",
    )
    taste = TasteAgent(config)

    result = await taste.evaluate(
        task=task,
        output_files=coder_output["files"],
        file_contents=coder_output["contents"],
        diff=coder_output.get("diff", ""),
    )

    if result.verdict == "reject":
        return "rewrite", result.revision_guidance
    elif result.verdict == "revise":
        return "revise", result.revision_guidance
    return "approve", ""
```

---

## HTTP API (Coming Soon)

For agent frameworks that don't support Python imports:

```bash
# Start the taste-agent server
taste-server --port 8765

# Evaluate via HTTP
curl -X POST http://localhost:8765/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Add hero section",
    "files": {"app/page.tsx": "..."},
    "taste_spec": "..."  # or use default
  }'
```

Response:
```json
{
  "verdict": "revise",
  "overall_score": 0.65,
  "reasoning": "...",
  "issues": [...],
  "revision_guidance": "..."
}
```

---

## Environment Variables

```bash
# API keys (if not using TasteConfig)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export ZAI_API_KEY="..."

# Or set in TasteConfig
config = TasteConfig(
    openai_api_key="sk-...",
    anthropic_api_key="sk-ant-...",
    zai_api_key="...",
)
```

---

## Troubleshooting

### taste.md not found

```
FileNotFoundError: taste.md not found at ... (require_taste_md=True)
```

Fix: Set `require_taste_md=False` or ensure `taste.md` exists at `taste_spec_path`.

### taste.memory grows too large

Enable automatic consolidation:
- `max_entries=20` triggers consolidation at 20+ entries
- Consolidation merges similar principles and prunes useless entries

### Model timeout

Increase timeout:
```python
config = TasteConfig(model="...", timeout=180.0)
```
