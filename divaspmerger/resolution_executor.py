from __future__ import annotations

from pathlib import Path
from typing import Dict, Sequence, Set

from .file_utils import backup_file
from .models import ResolutionPlan
from .text_utils import PV_KEY_PATTERN
from .logging_utils import log_info, log_warn, log_error

def _extract_pv_id(line: str) -> int | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    key_part = stripped.split("=", 1)[0].strip()
    match = PV_KEY_PATTERN.match(key_part)
    if not match:
        return None
    return int(match.group(1))


def _comment_line(line: str) -> str:
    indent_len = len(line) - len(line.lstrip(" \t"))
    prefix = line[:indent_len]
    remainder = line[indent_len:]
    return f"{prefix}#@DIVASPMerger {remainder}"


def _comment_out_pv_entries(pvdb_file: Path, target_ids: Sequence[int]) -> tuple[int, Set[int]]:
    target_lookup = {int(pid) for pid in target_ids}
    if not target_lookup:
        return 0, set()

    with pvdb_file.open("r", encoding="utf-8", errors="ignore") as reader:
        lines = reader.readlines()

    changes = 0
    affected_ids: Set[int] = set()
    for idx, line in enumerate(lines):
        pv_id = _extract_pv_id(line)
        if pv_id is None or pv_id not in target_lookup:
            continue
        updated_line = _comment_line(line)
        lines[idx] = updated_line
        affected_ids.add(pv_id)
        changes += 1

    if changes:
        with pvdb_file.open("w", encoding="utf-8", newline="") as writer:
            writer.writelines(lines)

    return changes, affected_ids


def apply_resolution_plans(
    plans: Dict[str, ResolutionPlan],
    backup_dir: Path,
    dry_run: bool = False,
    exempt_mods: Sequence[str] | None = None,
) -> None:
    if not plans:
        log_info("No resolution actions required.")
        return

    exemptions = {mod_name.lower() for mod_name in (exempt_mods or [])}

    for mod_name, plan in plans.items():
        log_info(f"Resolving conflicts for mod '{mod_name}'")
        if mod_name.lower() in exemptions:
            log_info("Skipped: mod is exempt from automatic fixes via config.", indent=2)
            continue

        if not plan.pvdb_file.exists():
            log_warn(f"Skipped: pv_db file '{plan.pvdb_file}' not found.", indent=2)
            continue

        if not plan.pv_ids_to_remove:
            log_info("No conflicting PV IDs to remove.", indent=2)
            continue

        target_list = ", ".join(str(pid) for pid in sorted(plan.pv_ids_to_remove))
        log_info(f"Target PV IDs: {target_list}", indent=2)

        if dry_run:
            log_info("Dry run active. No file changes were made.", indent=2)
            continue
        
        backup_file(plan.pvdb_file, backup_dir)

        try:
            line_changes, affected_ids = _comment_out_pv_entries(plan.pvdb_file, plan.pv_ids_to_remove)
        except OSError as exc:
            log_error(f"Error while editing pv_db: {exc}", indent=2)
            continue

        if affected_ids:
            affected_msg = ", ".join(str(pid) for pid in sorted(affected_ids))
            log_info(f"Commented definitions for PV IDs: {affected_msg}", indent=2)
        else:
            log_warn("No matching PV definitions were found to comment out.", indent=2)

        missing_ids = sorted(set(plan.pv_ids_to_remove) - affected_ids)
        if missing_ids:
            missing_msg = ", ".join(str(pid) for pid in missing_ids)
            log_warn(f"Missing PV definitions for: {missing_msg}", indent=2)

        log_info(f"Total lines updated: {line_changes}", indent=2)



