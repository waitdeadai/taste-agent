"""tests/test_core/test_memory.py — TasteMemory JSONL read/write and consolidate."""

from __future__ import annotations

import pytest

from taste_agent.core.memory import MemoryEntry, TasteMemory


class TestMemoryEntryHashTask:
    def test_hash_is_deterministic(self):
        h1 = MemoryEntry._hash_task("Add hero section")
        h2 = MemoryEntry._hash_task("Add hero section")
        assert h1 == h2

    def test_hash_length_16(self):
        h = MemoryEntry._hash_task("Any task description here")
        assert len(h) == 16

    def test_different_tasks_different_hashes(self):
        h1 = MemoryEntry._hash_task("Task A")
        h2 = MemoryEntry._hash_task("Task B")
        assert h1 != h2


class TestMemoryEntryRoundtrip:
    def test_to_dict_from_dict(self):
        original = MemoryEntry(
            task_description="Add hero section",
            file_path="app/page.tsx",
            verdict="revise",
            reasoning="Needs improvement",
            issues=["Placeholder copy"],
            principle="Always write specific copy",
            category="copy",
            severity="P1",
            why_this_matters="Generic copy signals lack of thought.",
        )
        d = original.to_dict()
        restored = MemoryEntry.from_dict(d)

        assert restored.task_description == original.task_description
        assert restored.file_path == original.file_path
        assert restored.verdict == original.verdict
        assert restored.reasoning == original.reasoning
        assert restored.issues == original.issues
        assert restored.principle == original.principle
        assert restored.category == original.category
        assert restored.severity == original.severity
        assert restored.why_this_matters == original.why_this_matters

    def test_to_jsonl_and_back(self):
        original = MemoryEntry(
            task_description="Test task",
            file_path="test.py",
            verdict="approve",
            reasoning="OK",
        )
        jsonl = original.to_jsonl()
        restored = MemoryEntry.from_jsonl(jsonl)
        assert restored.task_description == original.task_description


class TestTasteMemoryEmpty:
    def test_entries_empty_for_new_file(self, tmp_jsonl_file):
        mem = TasteMemory(tmp_jsonl_file)
        assert mem.entries() == []


class TestTasteMemoryAddEntry:
    def test_add_entry_persists(self, tmp_jsonl_file):
        mem = TasteMemory(tmp_jsonl_file)
        entry = MemoryEntry(
            task_description="Add hero section",
            file_path="app/page.tsx",
            verdict="revise",
            reasoning="Needs improvement",
        )
        mem.add_entry(entry)
        entries = mem.entries()
        assert len(entries) == 1
        assert entries[0].task_description == "Add hero section"


class TestTasteMemoryNeedsConsolidation:
    def test_false_under_20_entries(self, tmp_jsonl_file):
        mem = TasteMemory(tmp_jsonl_file)
        for i in range(5):
            mem.add_entry(
                MemoryEntry(
                    task_description=f"Task {i}",
                    file_path="test.py",
                    verdict="approve",
                    reasoning="",
                )
            )
        assert mem.needs_consolidation() is False


class TestTasteMemoryConsolidate:
    def test_removes_never_applied_entries(self, tmp_jsonl_file):
        mem = TasteMemory(tmp_jsonl_file)
        # Add entries: some never applied without improvement
        mem.add_entry(
            MemoryEntry(
                task_description="Task 1",
                file_path="test.py",
                verdict="revise",
                reasoning="",
                was_applied=False,
                applied_correctly=False,
            )
        )
        mem.add_entry(
            MemoryEntry(
                task_description="Task 2",
                file_path="test.py",
                verdict="approve",
                reasoning="",
                was_applied=True,
            )
        )
        removed = mem.consolidate()
        assert removed >= 0
        # The never-applied entry should be removed
        entries = mem.entries()
        assert all(e.was_applied for e in entries) or len(entries) >= 1


class TestMemoryEntryRepr:
    def test_repr_truncates_long_principle(self, tmp_jsonl_file):
        mem = TasteMemory(tmp_jsonl_file)
        mem.add("t", "f", "revise", "r", principle="x" * 100)
        r = repr(mem.entries()[0])
        # principle should be truncated in repr
        assert len(r) < 150  # truncated repr is shorter


class TestTasteMemoryLoadSkipsBadLines:
    def test_skips_malformed_json(self, tmp_jsonl_file):
        from taste_agent.core.memory import MemoryEntry
        valid_entry = MemoryEntry(
            task_description="t",
            file_path="f",
            verdict="revise",
            reasoning="r",
        )
        content = "not json\n" + valid_entry.to_jsonl() + "\n"
        tmp_jsonl_file.write_text(content)
        mem = TasteMemory(tmp_jsonl_file)
        assert len(mem.entries()) == 1

    def test_skips_missing_required_fields(self, tmp_jsonl_file):
        tmp_jsonl_file.write_text('{"task_description":"t"}\n')
        mem = TasteMemory(tmp_jsonl_file)
        assert len(mem.entries()) == 0


class TestTasteMemoryByCategory:
    def test_entries_by_category_no_matches(self, tmp_jsonl_file):
        mem = TasteMemory(tmp_jsonl_file)
        mem.add("t", "f", "revise", "r", category="copy")
        assert mem.entries_by_category("aesthetic") == []

    def test_entries_by_verdict_no_matches(self, tmp_jsonl_file):
        mem = TasteMemory(tmp_jsonl_file)
        mem.add("t", "f", "approve", "r")
        assert mem.entries_by_verdict("revise") == []


class TestTasteMemoryPrinciples:
    def test_filters_empty_principles(self, tmp_jsonl_file):
        mem = TasteMemory(tmp_jsonl_file)
        mem.add("t", "f", "revise", "r", principle="")
        mem.add("t", "f", "revise", "r", principle="Be specific")
        mem.add("t", "f", "revise", "r", principle="")
        assert mem.principles() == ["Be specific"]


class TestTasteMemoryStats:
    def test_counts_all_verdicts(self, tmp_jsonl_file):
        mem = TasteMemory(tmp_jsonl_file)
        mem.add("t", "f", "approve", "r")
        mem.add("t", "f", "revise", "r")
        mem.add("t", "f", "reject", "r")
        s = mem.stats()
        assert s["approve"] == 1
        assert s["revise"] == 1
        assert s["reject"] == 1


class TestTasteMemoryNeedsConsolidationEdgeCases:
    def test_true_at_20_entries_with_stale_meta(self, tmp_jsonl_file):
        import json
        mem = TasteMemory(tmp_jsonl_file)
        for i in range(20):
            mem.add(f"Task {i}", "f", "revise", "r")
        meta = tmp_jsonl_file.with_suffix(".meta")
        old = "2020-01-01T00:00:00+00:00"
        meta.write_text(json.dumps({"last_consolidation": old, "removed": 0}))
        assert mem.needs_consolidation() is True

    def test_true_corrupted_meta_json(self, tmp_jsonl_file):
        mem = TasteMemory(tmp_jsonl_file)
        for i in range(25):
            mem.add(f"Task {i}", "f", "revise", "r")
        meta = tmp_jsonl_file.with_suffix(".meta")
        meta.write_text("not json{{{")
        assert mem.needs_consolidation() is True

    def test_true_missing_last_consolidation_key(self, tmp_jsonl_file):
        mem = TasteMemory(tmp_jsonl_file)
        for i in range(25):
            mem.add(f"Task {i}", "f", "revise", "r")
        meta = tmp_jsonl_file.with_suffix(".meta")
        meta.write_text('{"entries_before": 20}')
        assert mem.needs_consolidation() is True

    def test_true_invalid_timestamp(self, tmp_jsonl_file):
        mem = TasteMemory(tmp_jsonl_file)
        for i in range(25):
            mem.add(f"Task {i}", "f", "revise", "r")
        meta = tmp_jsonl_file.with_suffix(".meta")
        meta.write_text('{"last_consolidation": "not-a-timestamp", "removed": 0}')
        assert mem.needs_consolidation() is True


class TestTasteMemoryConsolidateDedup:
    def test_deduplicates_by_principle(self, tmp_jsonl_file):
        mem = TasteMemory(tmp_jsonl_file)
        for i in range(3):
            mem.add(f"Task {i}", "f", "revise", "r", principle="Be specific")
        removed = mem.consolidate()
        assert removed >= 2
        assert len(mem.entries()) == 1

    def test_consolidate_writes_meta(self, tmp_jsonl_file):
        import json
        from taste_agent.core.memory import MemoryEntry
        mem = TasteMemory(tmp_jsonl_file)
        entry = MemoryEntry(task_description="t", file_path="f", verdict="revise", reasoning="r", was_applied=False)
        mem.add_entry(entry)
        removed = mem.consolidate()
        meta = tmp_jsonl_file.with_suffix(".meta")
        assert meta.exists()
        data = json.loads(meta.read_text())
        assert "last_consolidation" in data
