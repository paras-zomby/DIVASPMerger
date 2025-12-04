from __future__ import annotations

from pathlib import Path
from typing import Dict

from .file_utils import backup_file, temporary_directory
from .models import ResolutionPlan
from .tooling import ToolConfig
from .xml_editor import remove_songs_from_xml


def apply_resolution_plans(
    plans: Dict[str, ResolutionPlan],
    *,
    tool_config: ToolConfig | None = None,
) -> None:
    if not plans:
        print("[info] No resolution actions required.")
        return

    for mod_name, plan in plans.items():
        print(f"[info] Resolving conflicts for mod '{mod_name}'")
        backup_path = backup_file(plan.pvdb_file)
        print(f"  - Backup created at {backup_path}")

        with temporary_directory(prefix=f"divasp_{mod_name}_") as temp_dir:
            unpack_args = [str(pvdb_file), str(temp_dir)]
            tool_config.unpack_tool.run(unpack_args, dry_run=tool_config.dry_run)

            xml_path = temp_dir / "pv_db.xml"
            try:
                remove_songs_from_xml(xml_path, plan.pv_ids_to_remove)
            except NotImplementedError as exc:
                print(f"  - XML editing not implemented: {exc}")
                continue

            repack_args = [str(xml_path), str(pvdb_file)]
            tool_config.repack_tool.run(repack_args, dry_run=tool_config.dry_run)
