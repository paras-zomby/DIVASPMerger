from __future__ import annotations

from typing import Dict, Iterable, List

from .models import ConflictRecord, ConflictType, ModInfo, ResolutionPlan, SongEntry

DEFAULT_LOW_PRIORITY = 9999


def _entry_priority(entry: SongEntry, priority_lookup: Dict[str, ModInfo]) -> int:
    mod_info = priority_lookup.get(entry.source_name)
    if mod_info:
        return mod_info.priority
    return DEFAULT_LOW_PRIORITY


def _select_winner(entries: Iterable[SongEntry], priority_lookup: Dict[str, ModInfo]) -> tuple[SongEntry, List[SongEntry]]:
    sorted_entries = sorted(entries, key=lambda e: (_entry_priority(e, priority_lookup), e.source_name))
    winner = sorted_entries[0]
    losers = sorted_entries[1:]
    return winner, losers


def build_conflict_records(
    id_conflicts: Dict[int, List[SongEntry]],
    song_conflicts: Dict[str, List[SongEntry]],
    priority_lookup: Dict[str, ModInfo],
) -> List[ConflictRecord]:
    records: List[ConflictRecord] = []
    for pv_id, group in id_conflicts.items():
        winner, losers = _select_winner(group, priority_lookup)
        records.append(
            ConflictRecord(
                conflict_type=ConflictType.ID,
                key=pv_id,
                entries=list(group),
                winner=winner,
                losers=list(losers),
            )
        )

    for normalized_title, group in song_conflicts.items():
        winner, losers = _select_winner(group, priority_lookup)
        records.append(
            ConflictRecord(
                conflict_type=ConflictType.SONG,
                key=normalized_title,
                entries=list(group),
                winner=winner,
                losers=list(losers),
            )
        )
    return records


def plan_resolutions(conflicts: Iterable[ConflictRecord]) -> Dict[str, ResolutionPlan]:
    plans: Dict[str, ResolutionPlan] = {}
    for conflict in conflicts:
        for loser in conflict.losers:
            plan = plans.setdefault(
                loser.source_name,
                ResolutionPlan(mod_name=loser.source_name, pvdb_file=loser.pvdb_path),
            )
            if loser.pv_id not in plan.pv_ids_to_remove:
                plan.pv_ids_to_remove.append(loser.pv_id)
    return plans
