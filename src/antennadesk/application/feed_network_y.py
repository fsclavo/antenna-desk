# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Antenna N-port admittance extraction for feed-network co-simulation.

The antenna ports are driven one at a time with a 1 V source while the other
ports are held at a near-zero voltage (1 µV). The normalized source currents
then form the short-circuit admittance matrix ``Y`` at the port segments. The
near-zero rather than exact zero voltage is a nec2c workaround: a zero EX
voltage is treated as the default 1 V excitation by that engine.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from ..domain.antennas.antenna import AntennaModel
from ..domain.antennas.feed import FeedPoint, Source
from ..domain.antennas.feed_network import Matrix
from ..domain.simulation.result import SimulationStatus
from ..domain.simulation.spec import SimulationSpec
from .ports.antenna_solver import AntennaSolver

_NEAR_SHORT_VOLTAGE = 1e-6


@dataclass(frozen=True, slots=True)
class AntennaYMatrix:
    """The antenna short-circuit admittance matrix at named ports."""

    ports: tuple[tuple[str, float], ...]
    matrix: Matrix
    frequency_hz: float


def extract_antenna_y_matrix(
    solver: AntennaSolver,
    model: AntennaModel,
    spec: SimulationSpec,
    *,
    port_locations: tuple[tuple[str, float], ...] | None = None,
    frequency_index: int = 0,
) -> AntennaYMatrix:
    """Extract the antenna Y-matrix by shorting every port but one.

    ``port_locations`` defaults to the model's effective sources (the primary
    feed plus additional sources). The model's own transmission lines are
    removed: the feed network is added later by the N-port solver.
    """

    ports = port_locations or tuple(
        (source.wire_id, source.offset_m) for source in model.effective_sources
    )
    if not ports:
        raise ValueError("an antenna Y-matrix needs at least one port")
    if len(set(ports)) != len(ports):
        raise ValueError("antenna port locations must be unique")
    if frequency_index < 0:
        raise ValueError("frequency_index must not be negative")

    antenna_model = replace(model, transmission_lines=())
    driven_spec = replace(spec, co_simulate_feed_network=False)
    matrix: Matrix = [[0.0 + 0.0j for _ in ports] for _ in ports]
    solved_frequency_hz: float | None = None

    for driven_index, (wire_id, offset_m) in enumerate(ports):
        sources = tuple(
            Source(source_wire_id, source_offset_m, amplitude=_NEAR_SHORT_VOLTAGE)
            for index, (source_wire_id, source_offset_m) in enumerate(ports)
            if index != driven_index
        )
        driven_model = replace(
            antenna_model,
            feed=FeedPoint(wire_id=wire_id, offset_m=offset_m),
            sources=sources,
        )
        result = solver.run(driven_model, driven_spec)
        if result.status is not SimulationStatus.COMPLETED or not result.frequencies:
            detail = "; ".join(diagnostic.message for diagnostic in result.diagnostics)
            raise ValueError(f"antenna Y-matrix run failed: {detail or result.status.value}")
        if frequency_index >= len(result.frequencies):
            raise ValueError("frequency_index is outside the solver result")
        point = result.frequencies[frequency_index]
        solved_frequency_hz = point.frequency_hz
        by_port = {
            (source.wire_id, round(source.offset_m, 9)): source for source in point.source_results
        }
        for port_index, (port_wire_id, port_offset_m) in enumerate(ports):
            source = by_port.get((port_wire_id, round(port_offset_m, 9)))
            if source is None:
                raise ValueError(
                    f"the solver did not report port {port_wire_id} at {port_offset_m:g} m"
                )
            matrix[port_index][driven_index] = source.current_a

    if solved_frequency_hz is None:
        raise ValueError("no antenna Y-matrix frequency was solved")
    return AntennaYMatrix(
        ports=ports,
        matrix=matrix,
        frequency_hz=solved_frequency_hz,
    )
