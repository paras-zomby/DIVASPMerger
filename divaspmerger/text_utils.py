from __future__ import annotations

import re

WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_title(raw: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", raw).strip().lower()
