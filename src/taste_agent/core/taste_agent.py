"""TasteAgent — adversarial design director for AI coding agents.

The Taste Agent evaluates output against a human-written taste.md spec
and the accumulated taste.memory. It issues APPROVE / REVISE / REJECT
verdicts with specific feedback.

Usage:
    from taste_agent import TasteAgent, TasteConfig

    config = TasteConfig(
        taste_spec_path="taste.md",
        memory_path=".taste/taste.memory",
        enabled=True,
    )
    agent = TasteAgent(config)

    result = await agent.evaluate(
        task="Add hero section to landing page",
        output_files=["app/page.tsx"],
        file_contents={"app/page.tsx": open("app/page.tsx").read()},
    )
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import httpx

from taste_agent.core.config import TasteConfig
from taste_agent.core.memory import TasteMemory, MemoryEntry
from taste_agent.core.verdict import VERDICT, Verdict
from taste_agent.models.evaluation import EvaluationResult, Issue
from taste_agent.models.taste_spec import TasteSpec
from taste_agent.prompts.taste_system import TASTE_SYSTEM_PROMPT
from taste_agent.prompts.verdict_prompt import build_verdict_prompt

logger = logging.getLogger("taste_agent")


class TasteAgent:
    """Adversarial design director for AI coding agents.

    Reads:
    - taste.md: the human's written design spec
    - taste.memory: what the Taste Agent has learned across projects

    Produces:
    - VERDICT: APPROVE | REVISE | REJECT
    - Specific, actionable feedback
    - Memory updates on REVISE/REJECT
    """

    def __init__(
        self,
        config: TasteConfig | None = None,
        *,
        project_root: Path | str | None = None,
    ):
        self.config = config or TasteConfig()
        self.project_root = Path(project_root or Path.cwd()).resolve()

        # Discover taste.md
        self._taste_spec: TasteSpec | None = None
        self._taste_md_content: str | None = None
        self._discover_taste_spec()

        # Discover taste.memory
        self._memory: TasteMemory | None = None
        if self.config.enabled:
            self._discover_memory()

    def _discover_taste_spec(self) -> None:
        """Search upward from project root for taste.md."""
        spec_path = self.config.resolve_taste_spec_path(self.project_root)
        if spec_path.exists():
            try:
                self._taste_md_content = spec_path.read_text(encoding="utf-8", errors="replace")
                self._taste_spec = TasteSpec.from_markdown(self._taste_md_content)
                logger.debug(f"Loaded taste.md from {spec_path}")
            except Exception as e:
                logger.warning(f"Failed to parse taste.md from {spec_path}: {e}")

        if self._taste_spec is None and self.config.require_taste_md:
            raise FileNotFoundError(
                f"taste.md not found at {spec_path} (require_taste_md=True)"
            )

    def _discover_memory(self) -> None:
        """Discover and initialize taste.memory."""
        memory_path = self.config.resolve_memory_path(self.project_root)
        self._memory = TasteMemory(memory_path)
        logger.debug(f"Using taste.memory at {memory_path} (exists={memory_path.exists()})")

    @property
    def taste_spec(self) -> TasteSpec | None:
        return self._taste_spec

    @property
    def has_taste_spec(self) -> bool:
        return self._taste_spec is not None

    @property
    def memory(self) -> TasteMemory | None:
        return self._memory

    @property
    def has_memory(self) -> bool:
        return self._memory is not None and self._memory.exists

    async def evaluate(
        self,
        task: str,
        output_files: list[str] | None = None,
        file_contents: dict[str, str] | None = None,
        diff: str = "",
        **kwargs: Any,
    ) -> EvaluationResult:
        """Judge output against taste standards.

        Args:
            task: The original task description.
            output_files: List of files modified.
            file_contents: Dict of filename -> content for files to evaluate.
            diff: Optional git diff string.
            **kwargs: Additional context passed to the prompt builder.

        Returns:
            EvaluationResult with verdict, scores, issues, and guidance.
        """
        if not self.config.enabled:
            return EvaluationResult.skip()

        output_files = output_files or []
        file_contents = file_contents or {}

        prompt = build_verdict_prompt(
            task=task,
            taste_spec=self._taste_spec,
            taste_memory=self._memory,
            output_files=output_files,
            file_contents=file_contents,
            diff=diff,
        )

        start = time.monotonic()
        raw_response, usage = await self._call_llm(prompt)
        latency_ms = int((time.monotonic() - start) * 1000)

        result = self._parse_response(raw_response, usage, latency_ms)

        # Write to memory on REVISE/REJECT
        if result.verdict in ("revise", "reject") and self._memory:
            for issue in result.issues:
                principle = self._extract_principle(issue, result.verdict)
                if principle:
                    self._memory.add(
                        task_description=task,
                        file_path=issue.location or ", ".join(output_files),
                        verdict=result.verdict,
                        reasoning=result.reasoning,
                        issues=[issue.problem],
                        principle=principle,
                        category=issue.dimension,
                    )

        # Consolidate if needed
        if self._memory and self._memory.needs_consolidation():
            removed = self._memory.consolidate()
            logger.info(f"Memory consolidated: {removed} entries removed")

        return result

    async def _call_llm(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> tuple[str, Any]:
        """Call the configured LLM for taste evaluation.

        Supports OpenAI, Anthropic, Z.AI, or any OpenAI-compatible endpoint.
        API key is read from TasteConfig or environment variables.
        """
        model = model or self.config.model
        timeout = 120.0

        # Determine provider and call appropriate endpoint
        if "gpt" in model.lower() or "openai" in model.lower():
            return await self._call_openai(prompt, model, temperature, max_tokens, timeout)
        elif "claude" in model.lower() or "anthropic" in model.lower():
            return await self._call_anthropic(prompt, model, temperature, max_tokens, timeout)
        elif "glm" in model.lower() or "z.ai" in model.lower():
            return await self._call_zai(prompt, model, temperature, max_tokens, timeout)
        else:
            # Default: assume OpenAI-compatible
            return await self._call_openai_compatible(prompt, model, temperature, max_tokens, timeout)

    async def _call_openai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: float,
    ) -> tuple[str, Any]:
        """Call OpenAI GPT-4o or compatible."""
        api_key = self.config.openai_api_key or os.environ.get("OPENAI_API_KEY", "")
        base_url = "https://api.openai.com/v1"

        messages = [
            {"role": "system", "content": TASTE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model.replace("openai:", ""),
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        cost = (
            (usage.get("prompt_tokens", 0) * 2.25 + usage.get("completion_tokens", 0) * 9.0)
            / 1_000_000
        )
        return content, usage

    async def _call_anthropic(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: float,
    ) -> tuple[str, Any]:
        """Call Anthropic Claude."""
        api_key = self.config.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        base_url = "https://api.anthropic.com/v1"

        system_prompt = TASTE_SYSTEM_PROMPT + "\n\nOutput must be valid JSON only, no markdown."

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model.replace("anthropic:", "").replace("claude-", "claude-"),
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()

        content = data["content"][0]["text"]
        usage = data.get("usage", {})
        cost = (
            (usage.get("input_tokens", 0) * 1.5 + usage.get("output_tokens", 0) * 7.5)
            / 1_000_000
        )
        return content, usage

    async def _call_zai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: float,
    ) -> tuple[str, Any]:
        """Call Z.AI GLM (zai:glm-5.1) via OpenAI-compatible endpoint."""
        api_key = self.config.zai_api_key or os.environ.get("ZAI_API_KEY", "")
        base_url = "https://api.z.ai/api/paas/v4"

        messages = [
            {"role": "system", "content": TASTE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model.replace("zai:", ""),
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        cost = 0.0  # Z.AI pricing not known
        return content, {"model": model, "cost": cost, **usage}

    async def _call_openai_compatible(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: float,
    ) -> tuple[str, Any]:
        """Call any OpenAI-compatible endpoint (Ollama, LM Studio, etc.)."""
        # Extract base URL from model name if it contains one
        if "://" in model:
            parts = model.split("://", 1)
            base_url = parts[0] + "://" + parts[1].split("/")[0]
            model = "/".join(parts[1].split("/")[1:]) if "/" in parts[1] else parts[1]
        else:
            base_url = "http://localhost:11434/v1"

        api_key = os.environ.get("OLLAMA_API_KEY", "ollama")

        messages = [
            {"role": "system", "content": TASTE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return content, usage

    def _parse_response(
        self,
        raw: str,
        usage: dict,
        latency_ms: int,
    ) -> EvaluationResult:
        """Parse LLM JSON response into EvaluationResult."""
        # Strip markdown code blocks if present
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse taste response JSON: {e}")
            return EvaluationResult(
                verdict="revise",
                overall_score=0.0,
                reasoning=f"Failed to parse model output as JSON: {e}",
                latency_ms=latency_ms,
            )

        # Extract issues
        issues = []
        for i in data.get("issues", []):
            issues.append(
                Issue(
                    dimension=i.get("dimension", "aesthetic"),
                    location=i.get("location", ""),
                    problem=i.get("problem", ""),
                    fix_required=i.get("fix_required", ""),
                    non_negotiable_violated=i.get("non_negotiable_violated", ""),
                )
            )

        # Compute cost
        cost = 0.0
        if "cost" in usage:
            cost = float(usage["cost"])
        elif "prompt_tokens" in usage:
            # Approximate OpenAI pricing
            cost = (
                usage.get("prompt_tokens", 0) * 2.25 + usage.get("completion_tokens", 0) * 9.0
            ) / 1_000_000

        return EvaluationResult(
            verdict=data.get("verdict", "revise"),
            overall_score=float(data.get("overall_score", 0.5)),
            reasoning=data.get("reasoning", ""),
            scores=data.get("scores", {}),
            issues=issues,
            principles_learned=data.get("principles_learned", []),
            revision_guidance=data.get("revision_guidance", ""),
            model_used=usage.get("model", self.config.model),
            cost_usd=cost,
            latency_ms=latency_ms,
        )

    def _extract_principle(self, issue: Issue, verdict: str) -> str:
        """Extract a learnable principle from an issue.

        This is stored in taste.memory so future evaluations
        can use it as additional context.
        """
        if issue.non_negotiable_violated:
            return f"Always respect non-negotiable: {issue.non_negotiable_violated}. Problem: {issue.problem}"

        dimension_hints = {
            "aesthetic": "Use colors/typography from taste.md. ",
            "ux": "Ensure UX patterns match taste.md. ",
            "copy": "Use voice and copy from taste.md. ",
            "adherence": "Follow taste.md specifications exactly. ",
        }

        hint = dimension_hints.get(issue.dimension, "")
        if issue.fix_required:
            return f"{hint}{issue.fix_required}"
        return f"{hint}Issue: {issue.problem}"
