from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import List

from divaspmerger import (
    apply_resolution_plans,
    build_conflict_records,
    load_mod_config,
    plan_resolutions,
    print_conflict_details,
    export_report,
    detect_id_conflicts,
    detect_song_conflicts,
    discover_pvdb_files,
    parse_pvdb_file,
)
from divaspmerger.models import SongEntry
from divaspmerger.tooling import ExternalTool, ToolConfig

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan pv_db files inside mod folders, detect PV ID and song title conflicts, "
            "and export the results to Excel."
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
    return parser.parse_args()


def _build_tool_config(args: argparse.Namespace) -> ToolConfig | None:
    if not args.unpack_tool and not args.repack_tool:
        return None
    if not args.unpack_tool or not args.repack_tool:
        print("[warn] Both --unpack-tool and --repack-tool are required for automated resolution. Skipping tool steps.")
        return None

    unpack_tool = ExternalTool(
        executable=args.unpack_tool.expanduser(),
        args=tuple(str(arg) for arg in args.unpack_args),
    )
    repack_tool = ExternalTool(
        executable=args.repack_tool.expanduser(),
        args=tuple(str(arg) for arg in args.repack_args),
    )
    return ToolConfig(unpack_tool=unpack_tool, repack_tool=repack_tool, dry_run=args.dry_run)

    
def main() -> None:
    args = parse_args()
    game_root = args.game.expanduser().resolve()
    if not game_root.exists():
        raise SystemExit(f"Game path {game_root} does not exist.")

    mod_config_path = game_root.parent / "config.toml"
    priority_lookup, mods_root = load_mod_config(mod_config_path)
    
    tool_config = _build_tool_config(args)

    mod_entries: List[SongEntry] = []
    pvdb_files = discover_pvdb_files(mods_root)
    
    if not pvdb_files:
        print("[warn] No pv_db files found under the provided mods directory.")
    else:
        print(f"[info] Found {len(pvdb_files)} pv_db files in mods directory.")
    for mod_name, pvdb_path in pvdb_files:
        parsed = parse_pvdb_file(pvdb_path, mod_name)
        if not parsed:
            continue
        mod_entries.extend(parsed)

    all_entries = mod_entries
    if not mod_entries:
        print("[warn] No mod songs detected. Report will include base catalog only.")
        return

    mod_counter = Counter(entry.source_name for entry in mod_entries)
    if mod_counter:
        print("[info] Songs per mod:")
        for mod_name, count in mod_counter.most_common():
            print(f"  - {mod_name}: {count} songs")
    print(f"[info] Total songs indexed: {len(all_entries)}")

    id_conflicts = detect_id_conflicts(all_entries)
    song_conflicts = detect_song_conflicts(all_entries)
    
    if args.verbose_conflict:
        print_conflict_details(id_conflicts, song_conflicts)
        
    export_path = args.export_path
    if not export_path == Path(""):
        if export_path.suffix.lower() != ".xlsx":
            export_path = export_path / "conflict_export.xlsx"
        export_report(output_path=export_path, entries=all_entries,
                      id_conflicts=id_conflicts, song_conflicts=song_conflicts)
        print(f"[info] Report saved to {export_path}")

    conflict_records = build_conflict_records(id_conflicts=id_conflicts,
                                              song_conflicts=song_conflicts,
                                              priority_lookup=priority_lookup)
    plans = plan_resolutions(conflict_records)
    if plans:
        print(f"[info] Prepared {len(plans)} resolution plan(s). Starting execution...")
        apply_resolution_plans(plans, tool_config=tool_config)
    else:
        print("[info] No actionable conflicts detected. Nothing to resolve.")


if __name__ == "__main__":
    main()
