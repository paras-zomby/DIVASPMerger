from __future__ import annotations

import shutil
from pathlib import Path

from .logging_utils import log_info

def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def backup_file(source: Path, backup_dir: Path) -> Path:
    if not source.exists():
        raise FileNotFoundError(f"Cannot backup missing file: {source}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    mod_name = source.parent.parent.name
    destination = backup_dir / (mod_name + "_" + source.name + ".bak")
    if not destination.exists():
        shutil.copy2(source, destination)
        log_info(f"Created backup: {destination}")
    else:
        log_info(f"Backup already exists: {destination}")
    return destination


def restore_backup(
    backup_dir: Path, target_path: Path, no_exist_ok: bool = False
) -> None:
    mod_name = target_path.parent.parent.name
    backup_path = backup_dir / (mod_name + "_" + target_path.name + ".bak")
    if not backup_path.exists():
        if no_exist_ok:
            return
        raise FileNotFoundError(f"Cannot restore missing backup: {backup_path}")
    shutil.copy2(backup_path, target_path)
    log_info(f"Restored backup from {backup_path} to {target_path}")


def copy_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
