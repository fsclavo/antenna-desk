# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Constructive feed-connection metadata.

These values describe how the antenna is wired for construction. They are not
solver inputs: the canonical model still has one feed point and the NEC deck
still applies an ideal source there.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FeedBalance(StrEnum):
    """Whether the physical antenna load is balanced, unbalanced, or unknown."""

    BALANCED = "balanced"
    UNBALANCED = "unbalanced"
    UNKNOWN = "unknown"


class FeedTopology(StrEnum):
    """Physical feed arrangement used by the construction detail."""

    CENTER_FED_DIPOLE = "center_fed_dipole"
    OFF_CENTER_FED_DIPOLE = "off_center_fed_dipole"
    FOLDED_DIPOLE = "folded_dipole"
    BETA_HAIRPIN = "beta_hairpin"
    LOOP_GAP = "loop_gap"
    BASE_FED_VERTICAL = "base_fed_vertical"
    TOP_JUNCTION_FEED = "top_junction_feed"
    END_FED = "end_fed"
    END_FED_STUB = "end_fed_stub"
    APEX_GAP = "apex_gap"
    MULTI_PORT = "multi_port"
    UNKNOWN = "unknown"


class FeedInterface(StrEnum):
    """What sits between the antenna terminals and the transmitter coax."""

    DIRECT_COAX = "direct_coax"
    CURRENT_BALUN = "current_balun"
    TRANSFORMER = "transformer"
    BALANCED_LINE = "balanced_line"
    MULTI_PORT = "multi_port"
    UNKNOWN = "unknown"


class BalunRequirement(StrEnum):
    """Construction requirement derived from the family and topology."""

    REQUIRED = "required"
    RECOMMENDED = "recommended"
    NOT_REQUIRED = "not_required"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class FeedTerminal:
    """One physical terminal of the feed.

    ``side`` describes where the terminal sits on the referenced wire:
    ``start``, ``end``, ``before``/``after`` around the feed offset, or a named
    return such as ``ground`` or ``counterpoise``.
    """

    role: str
    wire_id: str | None
    offset_m: float | None
    side: str


@dataclass(frozen=True, slots=True)
class FeedConnection:
    """One row of the physical connection table."""

    source: str
    target: str
    note: str | None = None


@dataclass(frozen=True, slots=True)
class FeedConnectionDetail:
    """Read-only construction detail for one design and project feed state."""

    topology: FeedTopology
    interface: FeedInterface
    balance: FeedBalance
    balun_requirement: BalunRequirement
    terminals: tuple[FeedTerminal, FeedTerminal]
    connections: tuple[FeedConnection, ...]
    summary: str
    transformer_ratio: float | None = None
    match_hardware: str | None = None
    gap_m: float | None = None
    modeled: tuple[str, ...] = ()
    recorded: tuple[str, ...] = ()
    recommended: tuple[str, ...] = ()
    not_modeled: tuple[str, ...] = ()
    steps: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    def terminal(self, role: str) -> FeedTerminal:
        for terminal in self.terminals:
            if terminal.role == role:
                return terminal
        raise KeyError(role)
