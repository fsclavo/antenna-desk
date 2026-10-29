# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Feed-point definitions."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.units import ensure_non_negative


@dataclass(frozen=True, slots=True)
class FeedPoint:
    """A feed point located along a wire, measured from its start."""

    wire_id: str
    offset_m: float

    def __post_init__(self) -> None:
        if not self.wire_id.strip():
            raise ValueError("feed wire_id must not be empty")
        ensure_non_negative(self.offset_m, name="feed offset_m")
