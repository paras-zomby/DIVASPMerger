from __future__ import annotations

from pathlib import Path
from typing import Iterable


def remove_songs_from_xml(xml_path: Path, pv_ids: Iterable[int], normalized_titles: Iterable[str]) -> None:
	"""Remove songs from the unpacked XML representation.

	The actual XML schema is currently unspecified. Implement the real removal logic
	once the structure is known. This placeholder only documents the expected inputs.
	"""

	raise NotImplementedError("XML editing logic is not implemented. Define schema-specific behavior here.")