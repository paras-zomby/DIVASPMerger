from __future__ import annotations

import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Sequence


def ensure_directory(path: Path) -> None:
	path.mkdir(parents=True, exist_ok=True)


def backup_file(source: Path) -> Path:
	if not source.exists():
		raise FileNotFoundError(f"Cannot backup missing file: {source}")
	destination = source.parent / (source.name + ".bak")
	shutil.copy2(source, destination)
	return destination


def copy_tree(source: Path, destination: Path) -> None:
	if destination.exists():
		shutil.rmtree(destination)
	shutil.copytree(source, destination)


def run_command(command: Sequence[str], *, cwd: Path | None = None, dry_run: bool = False) -> subprocess.CompletedProcess[str]:
	if dry_run:
		print(f"[dry-run] Would execute: {' '.join(command)} (cwd={cwd})")
		return subprocess.CompletedProcess(command, 0, "", "")
	result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
	return result


@contextmanager
def temporary_directory(prefix: str = "divaspmerger_") -> Iterator[Path]:
	temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
	try:
		yield temp_dir
	finally:
		shutil.rmtree(temp_dir, ignore_errors=True)
