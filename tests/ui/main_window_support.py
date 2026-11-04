# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Helpers shared by the main-window test modules."""

from __future__ import annotations

from antennadesk.application.ports.antenna_solver import ProgressCallback
from antennadesk.application.ports.cancellation import CancelToken
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.main_window import MainWindow


class FakeSolver:
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="fake",
            supports_frequency_sweep=True,
            supports_currents=True,
            supports_far_field=True,
            supports_perfect_ground=True,
            supports_finite_ground=True,
            supports_extended_thin_wire_kernel=True,
        )

    def validate(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
    ) -> tuple[Diagnostic, ...]:
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="fake", version="1.0")

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: ProgressCallback | None = None,
        cancel_token: CancelToken | None = None,
    ) -> SimulationResult:
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=7_100_000.0,
                    feed_tag=1,
                    feed_segment=11,
                    impedance_ohm=complex(50.0, 0.0),
                    swr=1.0,
                    input_power_w=0.001,
                ),
            ),
            duration_s=0.01,
        )


def use_parameters(window: MainWindow, parameters) -> None:
    assert window._project is not None
    assert window._design_id is not None
    current = window._project.design_by_id(window._design_id)
    window._project = window._project.with_design(
        current.with_parameters(parameters),
        updated_at=window._project.updated_at,
    )
    window._select_design(current.id)
