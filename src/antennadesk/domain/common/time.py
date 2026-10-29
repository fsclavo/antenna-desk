"""Timezone-aware time helpers."""

from __future__ import annotations

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""

    return datetime.now(UTC)


def ensure_utc(value: datetime, *, name: str) -> datetime:
    """Validate that *value* is timezone-aware and return it in UTC."""

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)
