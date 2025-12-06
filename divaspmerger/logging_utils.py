from __future__ import annotations

LEVEL_DEFAULT = "info"


def _normalize_level(level: str | None) -> str:
    if not level:
        return LEVEL_DEFAULT
    return level.strip().lower() or LEVEL_DEFAULT


def log(message: str, level: str = LEVEL_DEFAULT, indent: int = 0) -> None:
    prefix = " " * max(indent, 0)
    normalized = _normalize_level(level)
    print(f"{prefix}[{normalized}] {message}")


def log_info(message: str, indent: int = 0) -> None:
    log(message, "info", indent)


def log_warn(message: str, indent: int = 0) -> None:
    log(message, "warn", indent)


def log_error(message: str, indent: int = 0) -> None:
    log(message, "error", indent)


def log_conflict(message: str, indent: int = 0) -> None:
    log(message, "conflict", indent)


def log_ok(message: str, indent: int = 0) -> None:
    log(message, "ok", indent)
