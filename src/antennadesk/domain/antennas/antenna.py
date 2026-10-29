# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Canonical antenna model."""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

from ..common.units import ensure_positive
from ..common.validation import Diagnostic, Severity, raise_if_errors
from ..environment.environment import Environment
from .feed import FeedPoint
from .load import SeriesLoad
from .wire import Wire


@dataclass(frozen=True, slots=True)
class AntennaModel:
    """An immutable antenna model made of straight wires and one feed point."""

    name: str
    design_frequency_hz: float
    wires: tuple[Wire, ...]
    feed: FeedPoint
    environment: Environment = field(default_factory=Environment)
    loads: tuple[SeriesLoad, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "wires", tuple(self.wires))
        object.__setattr__(self, "loads", tuple(self.loads))
        raise_if_errors(self._invariants())

    def _invariants(self) -> tuple[Diagnostic, ...]:
        diagnostics: list[Diagnostic] = []

        if not self.name.strip():
            diagnostics.append(
                Diagnostic(
                    code="antenna.name.empty",
                    severity=Severity.ERROR,
                    message="antenna name must not be empty",
                    field="name",
                )
            )

        try:
            ensure_positive(self.design_frequency_hz, name="design_frequency_hz")
        except ValueError as exc:
            diagnostics.append(
                Diagnostic(
                    code="antenna.frequency.invalid",
                    severity=Severity.ERROR,
                    message=str(exc),
                    field="design_frequency_hz",
                )
            )

        if not self.wires:
            diagnostics.append(
                Diagnostic(
                    code="antenna.wires.empty",
                    severity=Severity.ERROR,
                    message="antenna must contain at least one wire",
                    field="wires",
                )
            )

        seen_ids: set[str] = set()
        for wire in self.wires:
            if wire.id in seen_ids:
                diagnostics.append(
                    Diagnostic(
                        code="antenna.wire.duplicate_id",
                        severity=Severity.ERROR,
                        message=f"duplicate wire id: {wire.id}",
                        field="wires",
                    )
                )
            seen_ids.add(wire.id)

        seen_load_ids: set[str] = set()
        for load in self.loads:
            if load.id in seen_load_ids:
                diagnostics.append(
                    Diagnostic(
                        code="antenna.load.duplicate_id",
                        severity=Severity.ERROR,
                        message=f"duplicate load id: {load.id}",
                        field="loads",
                    )
                )
            seen_load_ids.add(load.id)
            load_wire = next((wire for wire in self.wires if wire.id == load.wire_id), None)
            if load_wire is None:
                diagnostics.append(
                    Diagnostic(
                        code="antenna.load.unknown_wire",
                        severity=Severity.ERROR,
                        message=f"load references an unknown wire: {load.wire_id}",
                        field="loads",
                    )
                )
            elif load.offset_m > load_wire.length_m and not math.isclose(
                load.offset_m,
                load_wire.length_m,
                rel_tol=1e-9,
                abs_tol=1e-9,
            ):
                diagnostics.append(
                    Diagnostic(
                        code="antenna.load.out_of_range",
                        severity=Severity.ERROR,
                        message=(
                            f"load offset {load.offset_m} m is outside wire "
                            f"{load_wire.id} of length {load_wire.length_m} m"
                        ),
                        field="loads",
                    )
                )

        feed_wire = next(
            (wire for wire in self.wires if wire.id == self.feed.wire_id),
            None,
        )
        if feed_wire is None:
            diagnostics.append(
                Diagnostic(
                    code="antenna.feed.unknown_wire",
                    severity=Severity.ERROR,
                    message=f"feed references an unknown wire: {self.feed.wire_id}",
                    field="feed.wire_id",
                )
            )
        elif self.feed.offset_m > feed_wire.length_m and not math.isclose(
            self.feed.offset_m,
            feed_wire.length_m,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            diagnostics.append(
                Diagnostic(
                    code="antenna.feed.out_of_range",
                    severity=Severity.ERROR,
                    message=(
                        f"feed offset {self.feed.offset_m} m is outside wire "
                        f"{feed_wire.id} of length {feed_wire.length_m} m"
                    ),
                    field="feed.offset_m",
                )
            )

        return tuple(diagnostics)

    def _warnings(self) -> tuple[Diagnostic, ...]:
        feed_wire = next(
            (wire for wire in self.wires if wire.id == self.feed.wire_id),
            None,
        )
        if feed_wire is None:
            return ()
        at_start = self.feed.offset_m == 0.0
        at_end = math.isclose(
            self.feed.offset_m,
            feed_wire.length_m,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )
        if at_start or at_end:
            return (
                Diagnostic(
                    code="antenna.feed.at_wire_end",
                    severity=Severity.WARNING,
                    message="feed point is at the end of a wire",
                    field="feed.offset_m",
                ),
            )
        return ()

    def validate(self) -> tuple[Diagnostic, ...]:
        return self._invariants() + self._warnings()

    def wire_by_id(self, wire_id: str) -> Wire:
        for wire in self.wires:
            if wire.id == wire_id:
                return wire
        raise KeyError(f"unknown wire id: {wire_id}")

    @property
    def feed_wire(self) -> Wire:
        return self.wire_by_id(self.feed.wire_id)

    def with_loads(self, loads: tuple[SeriesLoad, ...]) -> AntennaModel:
        return replace(self, loads=loads)
