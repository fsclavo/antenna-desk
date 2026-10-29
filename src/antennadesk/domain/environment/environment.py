# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Environmental conditions for an antenna model."""

from __future__ import annotations

from dataclasses import dataclass, replace

from .ground import FREE_SPACE, GroundModel


@dataclass(frozen=True, slots=True)
class Environment:
    """Environmental conditions that affect the antenna model."""

    ground: GroundModel = FREE_SPACE

    def with_ground(self, ground: GroundModel) -> Environment:
        return replace(self, ground=ground)
