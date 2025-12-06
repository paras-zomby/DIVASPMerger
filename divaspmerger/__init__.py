"""Core package for DIVASP Merger tooling."""

from .conflict_detector import (
    detect_id_conflicts,
    detect_song_conflicts,
    discover_pvdb_files,
    parse_pvdb_file,
    collect_pack_and_songs,
)
from .load_config import load_mod_config, load_program_config
from .models import ConflictRecord, PackInfo, ResolutionPlan, SongEntry
from .resolution_executor import apply_resolution_plans
from .resolution_planner import build_conflict_records, plan_resolutions
from .report import print_conflict_details, export_report
from .file_utils import backup_file, ensure_directory

__all__ = [
    "ConflictRecord",
    "PackInfo",
    "ResolutionPlan",
    "SongEntry",
    "load_program_config",
    "load_mod_config",
    "discover_pvdb_files",
    "parse_pvdb_file",
    "detect_id_conflicts",
    "detect_song_conflicts",
    "collect_pack_and_songs",
    "build_conflict_records",
    "plan_resolutions",
    "apply_resolution_plans",
    "print_conflict_details",
    "export_report",
    "backup_file",
    "ensure_directory",
]