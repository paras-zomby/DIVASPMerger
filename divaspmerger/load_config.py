from __future__ import annotations

import toml
from pathlib import Path
from typing import Dict

from .models import ModInfo


def load_mod_config(mod_config_path: Path) -> tuple[Dict[str, ModInfo], Path]:
    """Load mod priority information from a JSON file.

    The exact schema of the JSON file is currently undefined. This function attempts
    to read a list of objects with at least `name` and `priority` fields, but you can
    adjust the parsing logic once the final format is confirmed.
    """

    priorities: Dict[str, ModInfo] = {}
    
    if not mod_config_path.exists():
        print(f"[warn] Load-order file {mod_config_path} not found. Proceeding without priorities.")
        return priorities, mod_config_path.parent / 'mods'

    raw_text = mod_config_path.read_text(encoding="utf-8")
    try:
        config = toml.loads(raw_text)
    except toml.TomlDecodeError as exc:
        raise ValueError(f"Invalid TOML in load-order file: {mod_config_path}") from exc

    mods_root_dir = mod_config_path.parent / config['mods']
    
    mod_priorities_list = config['priority']
    
    for pri, name in enumerate(mod_priorities_list):
        priorities[name] = ModInfo(
            name=name,
            priority=pri,
            location=mods_root_dir / name,
        )

    return priorities, mods_root_dir
