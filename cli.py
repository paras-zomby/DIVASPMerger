from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict

from divaspmerger import (
    apply_resolution_plans,
    build_conflict_records,
    load_program_config,
    load_mod_config,
    plan_resolutions,
    print_conflict_details,
    export_report,
    detect_id_conflicts,
    detect_song_conflicts,
    discover_pvdb_files,
    collect_pack_and_songs,
)
from divaspmerger.file_utils import restore_backup
from divaspmerger.logging_utils import log_info, log_warn
from divaspmerger.models import PackInfo

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan pv_db files inside mod folders, detect PV ID and song title conflicts, "
            "and export the results to Excel."
            "Commence resolution of ID conflicts based on mod priority."
        )
    )
    parser.add_argument(
        "--game",
        required=True,
        type=Path,
        help="Path to the game executable (DivaMegaMix.exe).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print the actions that would be taken when resolving conflicts.",
    )
    parser.add_argument(
        "--verbose-conflict",
        action="store_true",
        default=False,
        help="Print detailed information about each conflict.",
    )
    parser.add_argument(
        "--export-path",
        type=Path,
        default=Path(""),
        help="Path to save the conflict report Excel file.",
    )
    parser.add_argument(
        "--config-path",
        type=Path,
        default=Path("config.toml"),
        help="Path to the program configuration TOML file.",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=Path("pvdb_backup"),
        help="Directory to store backup files before applying resolutions.",
    )
    parser.add_argument(
        "--restore-backup",
        action="store_true",
        default=False,
        help="Restore backup files before applying any resolutions.",
    )
    return parser.parse_args()

    
def main() -> None:
    args = parse_args()
    game_root = args.game.expanduser().resolve()
    if not game_root.exists():
        raise SystemExit(f"Game path {game_root} does not exist.")

    mod_config_path = game_root.parent / "config.toml"
    priority_lookup, mods_root = load_mod_config(mod_config_path)
    ignore_mods, exempt_mods = load_program_config(args.config_path.expanduser())
    
    pack_infos: Dict[str, PackInfo] = defaultdict()
    pvdb_files = discover_pvdb_files(mods_root)
    
    if not pvdb_files:
        log_warn("No pv_db files found under the provided mods directory.")
    else:
        log_info(f"Found {len(pvdb_files)} pv_db files in mods directory.")
        
    if args.restore_backup:
        log_info("Restoring backup files before proceeding...")
        for mod_name, pvdb_path in pvdb_files:
            restore_backup(args.backup_dir.expanduser(), pvdb_path, no_exist_ok=True)
    
    pack_infos, mod_entries = collect_pack_and_songs(
        mod_root=mods_root,
        pvdb_files=pvdb_files,
        priority_lookup=priority_lookup,
        ignore_mods=ignore_mods,
    )
    
    if not mod_entries:
        log_warn("No mod songs detected. Program exit.")
        return

    log_info("Songs per mod:")
    for mod_name, pack_info in pack_infos.items():
        log_info(f"{mod_name}: {pack_info.num_songs} songs", indent=2)
    log_info(f"Total songs indexed: {len(mod_entries)}")

    id_conflicts = detect_id_conflicts(mod_entries)
    song_conflicts = detect_song_conflicts(mod_entries)
    
    if args.verbose_conflict:
        print_conflict_details(id_conflicts, song_conflicts)

    conflict_records = build_conflict_records(id_conflicts=id_conflicts,
                                              song_conflicts=song_conflicts,
                                              pack_infos=pack_infos)
    plans = plan_resolutions(conflict_records)
    
    export_path = args.export_path
    if not export_path == Path(""):
        if export_path.suffix.lower() != ".xlsx":
            export_path = export_path / "conflict_report.xlsx"
        export_report(output_path=export_path, entries=mod_entries,
                      pack_infos=pack_infos, conflicts=conflict_records,
                      plans=plans)
        log_info(f"Report saved to {export_path}")
        
    if plans and not args.restore_backup:
        log_info(f"Prepared {len(plans)} resolution plan(s). Starting execution...")
        apply_resolution_plans(plans, backup_dir=args.backup_dir.expanduser(), 
                               dry_run=args.dry_run, exempt_mods=exempt_mods)


if __name__ == "__main__":
    main()
