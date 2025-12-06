from __future__ import annotations

import re

WHITESPACE_PATTERN = re.compile(r"\s+")
PV_KEY_PATTERN = re.compile(r"^pv_(\d+)\.(.+)$", re.IGNORECASE)
COMMENT_PATTERN = re.compile(r"^#\s*(\d+)\s*-\s*(.+)$")


def normalize_title(raw: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", raw).strip().lower()
