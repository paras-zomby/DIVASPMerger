from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Sequence

from .text_utils import normalize_title

class ConflictType(str, Enum):
    ID = "id_conflict"
    SONG = "song_conflict"


@dataclass(slots=True)
class ModInfo:
    name: str
    priority: int
    location: Path | None = None


@dataclass(slots=True)
class SongEntry:
    pv_id: int
    title: str
    title_en: str | None
    source_name: str
    source_type: str
    pvdb_path: Path

    @property
    def normalized_title(self) -> str:
        reference = self.title_en or ""
        return normalize_title(reference)

    @property
    def source_label(self) -> str:
        return f"{self.source_type}:{self.source_name}"


@dataclass(slots=True)
class ConflictRecord:
    conflict_type: ConflictType
    key: str | int
    entries: List[SongEntry]
    winner: SongEntry
    losers: List[SongEntry] = field(default_factory=list)

    def involved_mods(self) -> Sequence[str]:
        return sorted({entry.source_name for entry in self.entries})

    def losers_by_mod(self) -> dict[str, List[SongEntry]]:
        grouping: dict[str, List[SongEntry]] = {}
        for entry in self.losers:
            grouping.setdefault(entry.source_name, []).append(entry)
        return grouping


@dataclass(slots=True)
class ResolutionPlan:
    mod_name: str
    pvdb_file: Path
    pv_ids_to_remove: List[int] = field(default_factory=list)

    def merge(self, other: "ResolutionPlan") -> None:
        assert self.mod_name == other.mod_name, "Can only merge plans for the same mod"
        assert self.pvdb_file == other.pvdb_file, "Can only merge plans with the same pvdb_file"
        self.pv_ids_to_remove.extend(pid for pid in other.pv_ids_to_remove if pid not in self.pv_ids_to_remove)
