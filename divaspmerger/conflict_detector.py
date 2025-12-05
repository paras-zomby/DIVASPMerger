from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List

from .models import PackInfo, SongEntry

PV_KEY_PATTERN = re.compile(r"^pv_(\d+)\.(.+)$", re.IGNORECASE)
COMMENT_PATTERN = re.compile(r"^#\s*(\d+)\s*-\s*(.+)$")
DEFAULT_PRIORITY = 9999


def discover_pvdb_files(mods_root: Path) -> List[tuple[str, Path]]:
	"""Return every mod pv_db file found under the provided mods directory."""

	files: List[tuple[str, Path]] = []
	for mod_dir in mods_root.iterdir():
		if not mod_dir.is_dir():
			continue
		mod_name = mod_dir.name
		for path in mod_dir.rglob("*.txt"):
			if not path.is_file():
				continue
			if path.parent.name != "rom":
				continue
			if path.name.lower() != "mod_pv_db.txt":
				continue
			files.append((mod_name, path))
	return files


def parse_pvdb_file(
	pvdb_path: Path,
	mod_name: str,
) -> List[SongEntry]:
	"""Parse a mod's pv_db text file into song entries and pack metadata."""

	song_data: Dict[int, Dict[str, str]] = defaultdict(dict)
	with pvdb_path.open("r", encoding="utf-8", errors="ignore") as handle:
		for raw_line in handle:
			line = raw_line.strip()
			if not line:
				continue
			match = COMMENT_PATTERN.match(line)
			if match:
				pv_id = int(match.group(1))
				song_data[pv_id]["comment_title"] = match.group(2).strip()
				continue
			if line.startswith("#"):
				continue
			if "=" not in line:
				continue
			key, value = line.split("=", 1)
			key = key.strip()
			value = value.strip()
			key_match = PV_KEY_PATTERN.match(key)
			if not key_match:
				continue
			pv_id = int(key_match.group(1))
			attr = key_match.group(2).lower()
			if attr == "song_name":
				song_data[pv_id]["song_name"] = value
			elif attr == "song_name_en":
				song_data[pv_id]["song_name_en"] = value

	song_entries = []
	for pv_id, data in song_data.items():
		primary = data.get("song_name") or data.get("comment_title")
		secondary = data.get("song_name_en")
		title = primary or secondary
		if not title:
			continue
		song_entries.append(
			SongEntry(
				pv_id=pv_id,
				title=title,
				title_en=secondary,
				source_name=mod_name,
				source_type="mod",
				pvdb_path=pvdb_path,
			)
		)
	return song_entries


def collect_pack_and_songs(
    mod_root: Path,
    pvdb_files: List[tuple[str, Path]],
    priority_lookup: Dict[str, int] | None = None,
) -> tuple[Dict[str, PackInfo], List[SongEntry]]:
	"""Construct PackInfo objects for each mod based on their pv_db files."""
    
	packs: Dict[str, PackInfo] = defaultdict()
	all_songs: List[SongEntry] = []
	for mod_name, pvdb_path in pvdb_files:
		parsed_songs = parse_pvdb_file(pvdb_path, mod_name)
		priority = priority_lookup.get(mod_name, DEFAULT_PRIORITY) if priority_lookup else DEFAULT_PRIORITY
		pack = PackInfo(
			name=mod_name,
			priority=priority,
			location=mod_root / mod_name,
			pvdb_path=pvdb_path,
			songs=parsed_songs,
		)
		all_songs.extend(parsed_songs)
		if mod_name in packs:
			raise SystemExit(f"Duplicate mod name detected: {mod_name}. Please check two 'pvdb' files." \
                            f"One: {packs[mod_name].pvdb_path}, Other: {pack.pvdb_path}." \
                            f"It may because of pvdb file discover rule not Complete and find a wrong pvdb file." \
                            f"Please remove one of them as a temporary workaround.")
		else:
			packs[mod_name] = pack
	return packs, all_songs


def detect_id_conflicts(entries: Iterable[SongEntry]) -> Dict[int, List[SongEntry]]:
	"""Group entries that share the same PV ID across different sources."""

	grouped: Dict[int, List[SongEntry]] = defaultdict(list)
	for entry in entries:
		grouped[entry.pv_id].append(entry)

	conflicts: Dict[int, List[SongEntry]] = {}
	for pv_id, group in grouped.items():
		sources = {(item.source_type, item.source_name) for item in group}
		if len(sources) > 1:
			conflicts[pv_id] = group
	return conflicts


def detect_song_conflicts(entries: Iterable[SongEntry]) -> Dict[str, List[SongEntry]]:
	"""Group entries that resolve to the same normalized title across sources."""

	grouped: Dict[str, List[SongEntry]] = defaultdict(list)
	for entry in entries:
		key = entry.normalized_title
		if not key:
			continue
		grouped[key].append(entry)

	conflicts: Dict[str, List[SongEntry]] = {}
	for normalized_title, group in grouped.items():
		sources = {(item.source_type, item.source_name) for item in group}
		if len(sources) > 1:
			conflicts[normalized_title] = group
	return conflicts


__all__ = [
	"discover_pvdb_files",
	"parse_pvdb_file",
	"detect_id_conflicts",
	"detect_song_conflicts",
	"collect_pack_and_songs",
]
