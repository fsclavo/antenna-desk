# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Antenna solver port."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from ...domain.antennas.antenna import AntennaModel
from ...domain.common.validation import Diagnostic
from ...domain.simulation.result import SimulationResult
from ...domain.simulation.solver import SolverCapabilities, SolverMetadata
from ...domain.simulation.spec import SimulationSpec
from .cancellation import CancelToken

ProgressCallback = Callable[[float], None]


class AntennaSolver(Protocol):
    """A normalized electromagnetic solver adapter.

    ``run`` returns a normalized result, including the raw input and output
    text.  Expected solver failures (timeout, cancellation, non-zero exit
    code, parser failure) are represented in the result status and
    diagnostics rather than raised into the UI.
    """

    def capabilities(self) -> SolverCapabilities:
        """Return the solver capabilities."""

    def validate(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
    ) -> tuple[Diagnostic, ...]:
        """Return validation diagnostics for a model/spec pair."""

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: ProgressCallback | None = None,
        cancel_token: CancelToken | None = None,
    ) -> SimulationResult:
        """Run a simulation and return a normalized result."""

    def version(self) -> SolverMetadata:
        """Return the solver name, version, and executable."""
