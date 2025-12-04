from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .file_utils import run_command


@dataclass(slots=True)
class ExternalTool:
	executable: Path
	args: Sequence[str] = ()

	def run(self, extra_args: Sequence[str] = (), *, cwd: Path | None = None, dry_run: bool = False) -> None:
		command = [str(self.executable), *self.args, *extra_args]
		run_command(command, cwd=cwd, dry_run=dry_run)


@dataclass(slots=True)
class ToolConfig:
	unpack_tool: ExternalTool
	repack_tool: ExternalTool
	dry_run: bool = False