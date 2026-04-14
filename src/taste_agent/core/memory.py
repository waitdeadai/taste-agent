"""TasteMemory — read/write for taste.memory JSONL log."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class MemoryEntry:
    """A single entry in taste.memory.

    Written by Taste Agent on every REVISE/REJECT.
    Append-only log — never modify existing entries.
    """

    __slots__ = (
        "entry_id",
        "timestamp",
        "task_hash",
        "task_description",
        "file_path",
        "verdict",
        "reasoning",
        "issues",
        "principle",
        "category",
        "was_applied",
        "applied_correctly",
    )

    def __init__(
        self,
        task_description: str,
        file_path: str,
        verdict: str,
        reasoning: str,
        issues: list[str] | None = None,
        principle: str = "",
        category: str = "aesthetic",
        task_hash: str | None = None,
        was_applied: bool = False,
        applied_correctly: bool | None = None,
        entry_id: str | None = None,
        timestamp: str | None = None,
    ):
        self.entry_id = entry_id or f"tm-{uuid.uuid4().hex[:12]}"
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.task_hash = task_hash or self._hash_task(task_description)
        self.task_description = task_description
        self.file_path = file_path
        self.verdict = verdict
        self.reasoning = reasoning
        self.issues = issues or []
        self.principle = principle
        self.category = category  # aesthetic | ux | copy | adherence
        self.was_applied = was_applied
        self.applied_correctly = applied_correctly

    @staticmethod
    def _hash_task(task: str) -> str:
        """SHA256 hash of task for deduplication."""
        import hashlib

        return hashlib.sha256(task.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "task_hash": self.task_hash,
            "task_description": self.task_description,
            "file_path": self.file_path,
            "verdict": self.verdict,
            "reasoning": self.reasoning,
            "issues": self.issues,
            "principle": self.principle,
            "category": self.category,
            "was_applied": self.was_applied,
            "applied_correctly": self.applied_correctly,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        return cls(
            entry_id=data["entry_id"],
            timestamp=data["timestamp"],
            task_hash=data["task_hash"],
            task_description=data["task_description"],
            file_path=data["file_path"],
            verdict=data["verdict"],
            reasoning=data["reasoning"],
            issues=data.get("issues", []),
            principle=data.get("principle", ""),
            category=data.get("category", "aesthetic"),
            was_applied=data.get("was_applied", False),
            applied_correctly=data.get("applied_correctly"),
        )

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_jsonl(cls, line: str) -> "MemoryEntry":
        return cls.from_dict(json.loads(line))

    def __repr__(self) -> str:
        return f"MemoryEntry({self.verdict} | {self.category} | {self.principle[:50]})"


class TasteMemory:
    """Append-only taste.memory log.

    File format: JSONL (JSON Lines)
    One MemoryEntry per line, newest last.

    Memory consolidation happens when:
    - 20+ entries since last consolidation
    - 24+ hours since last consolidation

    Consolidation:
    - Merges similar principles (Jaccard similarity > 0.85)
    - Prunes entries with was_applied=false + applied_correctly=false
    """

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self._entries: list[MemoryEntry] | None = None

    @property
    def exists(self) -> bool:
        return self.path.exists()

    def _load(self) -> list[MemoryEntry]:
        """Load all entries from file."""
        if not self.exists:
            return []
        entries = []
        with self.path.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(MemoryEntry.from_jsonl(line))
                    except (json.JSONDecodeError, KeyError):
                        continue
        return entries

    def _ensure_loaded(self) -> list[MemoryEntry]:
        if self._entries is None:
            self._entries = self._load()
        return self._entries

    def entries(self) -> list[MemoryEntry]:
        """Get all memory entries."""
        return list(self._ensure_loaded())

    def entries_by_category(self, category: str) -> list[MemoryEntry]:
        """Get entries filtered by category."""
        return [e for e in self._ensure_loaded() if e.category == category]

    def entries_by_verdict(self, verdict: str) -> list[MemoryEntry]:
        """Get entries filtered by verdict."""
        return [e for e in self._ensure_loaded() if e.verdict == verdict]

    def add_entry(self, entry: MemoryEntry) -> None:
        """Append a new entry to taste.memory (append-only)."""
        self._ensure_loaded()
        self._entries.append(entry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(entry.to_jsonl() + "\n")

    def add(
        self,
        task_description: str,
        file_path: str,
        verdict: str,
        reasoning: str,
        issues: list[str] | None = None,
        principle: str = "",
        category: str = "aesthetic",
    ) -> MemoryEntry:
        """Convenience: create and add a memory entry."""
        entry = MemoryEntry(
            task_description=task_description,
            file_path=file_path,
            verdict=verdict,
            reasoning=reasoning,
            issues=issues,
            principle=principle,
            category=category,
        )
        self.add_entry(entry)
        return entry

    def principles(self) -> list[str]:
        """Get all non-empty principles learned."""
        return [e.principle for e in self._ensure_loaded() if e.principle]

    def stats(self) -> dict[str, int]:
        """Get memory statistics."""
        entries = self._ensure_loaded()
        return {
            "total": len(entries),
            "approve": sum(1 for e in entries if e.verdict == "approve"),
            "revise": sum(1 for e in entries if e.verdict == "revise"),
            "reject": sum(1 for e in entries if e.verdict == "reject"),
            "applied": sum(1 for e in entries if e.was_applied),
        }

    def needs_consolidation(self) -> bool:
        """Check if memory needs consolidation."""
        entries = self._ensure_loaded()
        if len(entries) < 20:
            return False
        # Check last consolidation timestamp
        meta_path = self.path.with_suffix(".meta")
        if not meta_path.exists():
            return True
        try:
            meta = json.loads(meta_path.read_text())
            last_ts = datetime.fromisoformat(meta["last_consolidation"])
            age_hours = (datetime.now(timezone.utc) - last_ts).total_seconds() / 3600
            return age_hours >= 24
        except (json.JSONDecodeError, KeyError, ValueError):
            return True

    def consolidate(self) -> int:
        """Consolidate memory — merge similar principles, prune bad entries.

        Returns number of entries removed.
        """
        entries = self._ensure_loaded()
        original_count = len(entries)

        # Remove entries that were never applied and didn't lead to improvement
        # (was_applied=False AND applied_correctly=False AND no principle extracted)
        pruned = [
            e
            for e in entries
            if not (not e.was_applied and e.applied_correctly is False and not e.principle)
        ]

        # TODO: Merge similar principles using Jaccard similarity > 0.85
        # For now, just deduplicate by principle text
        seen_principles: set[str] = set()
        deduplicated = []
        for e in pruned:
            if e.principle and e.principle in seen_principles:
                continue
            if e.principle:
                seen_principles.add(e.principle)
            deduplicated.append(e)

        removed = original_count - len(deduplicated)
        self._entries = deduplicated

        # Rewrite file
        with self.path.open("w", encoding="utf-8") as f:
            for e in deduplicated:
                f.write(e.to_jsonl() + "\n")

        # Update meta
        meta_path = self.path.with_suffix(".meta")
        meta_path.write_text(
            json.dumps(
                {
                    "last_consolidation": datetime.now(timezone.utc).isoformat(),
                    "entries_before": original_count,
                    "entries_after": len(deduplicated),
                    "removed": removed,
                }
            )
        )

        return removed
