# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Identifier helpers."""

from __future__ import annotations

from uuid import UUID, uuid4


def new_id() -> UUID:
    """Return a new random UUID."""

    return uuid4()


def parse_id(value: str) -> UUID:
    """Parse a UUID string, raising a clear ``ValueError`` on failure."""

    try:
        return UUID(value)
    except (AttributeError, ValueError) as exc:
        raise ValueError(f"invalid UUID: {value!r}") from exc
