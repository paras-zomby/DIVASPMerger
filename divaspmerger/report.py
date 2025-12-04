from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, DefaultDict, Dict, List, Sequence

from openpyxl import Workbook

from .models import SongEntry


def _format_song_names(group: Sequence[SongEntry]) -> str:
    names = [entry.title_en or entry.title for entry in group if entry.title_en or entry.title]
    if not names:
        return ""
    return ", ".join(sorted(set(names)))


def _format_sources(group: Sequence[SongEntry]) -> str:
    return ", ".join(sorted({entry.source_label for entry in group}))


def _build_conflict_rows(
    id_conflicts: Dict[int, List[SongEntry]],
    song_conflicts: Dict[str, List[SongEntry]],
) -> List[List[str]]:
    rows: List[List[str]] = []
    for pv_id, group in sorted(id_conflicts.items()):
        rows.append(
            [
                "id_conflict",
                _format_song_names(group),
                str(pv_id),
                _format_sources(group),
            ]
        )

    for normalized_title, group in sorted(song_conflicts.items()):
        pv_ids = ", ".join(str(pid) for pid in sorted({entry.pv_id for entry in group}))
        display_name = _format_song_names(group) or normalized_title
        rows.append(
            [
                "song_conflict",
                display_name,
                pv_ids,
                _format_sources(group),
            ]
        )
    return rows


def _build_pack_conflict_rows(
    entries: Sequence[SongEntry],
    id_conflicts: Dict[int, List[SongEntry]],
    song_conflicts: Dict[str, List[SongEntry]],
) -> List[List[Any]]:
    songs_by_sp: Dict[str, List[SongEntry]] = defaultdict(list)
    for entry in entries:
        songs_by_sp[entry.source_name].append(entry)

    def _stat_record():
        return {
            "total": 0,
            "conflict_keys": set(),
            "partners": defaultdict(set),
        }

    stats: DefaultDict[str, Dict[str, Any]] = defaultdict(_stat_record)
    for sp_name, songs in songs_by_sp.items():
        stats[sp_name]["total"] = len(songs)

    def register_conflict(group: Sequence[SongEntry], key: tuple[str, object]) -> None:
        source_map: Dict[str, List[SongEntry]] = defaultdict(list)
        for item in group:
            source_map[item.source_name].append(item)
        if len(source_map) < 2:
            return
        labels = sorted(source_map.keys())
        for label in labels:
            stats[label]["conflict_keys"].add(key)
        for left, right in combinations(labels, 2):
            stats[left]["partners"][right].add(key)
            stats[right]["partners"][left].add(key)

    for pv_id, group in id_conflicts.items():
        register_conflict(group, ("id", pv_id))

    for normalized_title, group in song_conflicts.items():
        register_conflict(group, ("song", normalized_title))

    rows: List[List[Any]] = []
    for pack_name in sorted(songs_by_sp.keys()):
        record = stats[pack_name]
        total = record["total"]
        conflict_total = len(record["conflict_keys"])
        rows.append([pack_name, conflict_total, "", total])
        partner_map = record["partners"]
        for partner_name, partner_conflict_keys in sorted(partner_map.items()):
            rows.append([pack_name, len(partner_conflict_keys), partner_name, len(songs_by_sp[partner_name])])
    return rows


def print_conflict_details(id_conflicts: Dict[int, List[SongEntry]], song_conflicts: Dict[str, List[SongEntry]]) -> None:
    if id_conflicts:
        print("[conflict] PV ID clashes detected:")
        for pv_id, group in sorted(id_conflicts.items()):
            details = "; ".join(f"{entry.title} ({entry.source_label})" for entry in group)
            print(f"  - {pv_id}: {details}")
    else:
        print("[ok] No PV ID conflicts found.")
    if song_conflicts:
        print("[conflict] Song title clashes detected:")
        for normalized_title, group in sorted(song_conflicts.items()):
            human_title = group[0].title
            details = "; ".join(f"id {entry.pv_id} ({entry.source_label})" for entry in group)
            print(f"  - {human_title}: {details}")
    else:
        print("[ok] No song title conflicts found.")


def export_report(
    output_path: Path,
    entries: List[SongEntry],
    id_conflicts: Dict[int, List[SongEntry]],
    song_conflicts: Dict[str, List[SongEntry]],
) -> None:
    """Write an Excel report summarizing detected conflicts."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    workbook = Workbook()
    songs_sheet = workbook.active
    songs_sheet.title = "songs"
    songs_sheet.append([
        "pv_id",
        "title",
        "title_en",
        "source_type",
        "source_name",
        "pvdb_path",
    ])
    for entry in sorted(entries, key=lambda item: (item.source_type, item.source_name, item.pv_id)):
        songs_sheet.append(
            [
                entry.pv_id,
                entry.title,
                entry.title_en or "",
                entry.source_type,
                entry.source_name,
                str(entry.pvdb_path) if entry.pvdb_path else "",
            ]
        )

    conflicts_sheet = workbook.create_sheet("conflicts")
    conflicts_sheet.append(["conflict_type", "song_name", "pv_ids", "sources"])
    for row in _build_conflict_rows(id_conflicts, song_conflicts):
        conflicts_sheet.append(row)

    pack_sheet = workbook.create_sheet("pack_conflicts")
    pack_sheet.append(["pack_name", "conflict_count", "conflict_partner", "total_songs"])
    for row in _build_pack_conflict_rows(entries, id_conflicts, song_conflicts):
        pack_sheet.append(row)

    workbook.save(output_path)
    workbook.close()


__all__ = ["print_conflict_details", "export_report"]
