"""File-based taste.memory store (JSONL — default)."""

from __future__ import annotations

from pathlib import Path

from taste_agent.core.memory import TasteMemory


class FileStore(TasteMemory):
    """JSONL-based taste.memory store.

    Default store. Append-only JSONL file at the configured path.

    This is just an alias for the base TasteMemory class since
    the base class already implements JSONL file storage.
    """

    def __init__(self, path: Path | str = ".taste/taste.memory"):
        super().__init__(path)
