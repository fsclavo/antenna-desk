# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Normalized simulation results."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from ..common.validation import Diagnostic
from .solver import SolverMetadata
from .spec import SimulationSpec


class SimulationStatus(StrEnum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class PowerBudget:
    input_w: float
    radiated_w: float
    structure_loss_w: float
    network_loss_w: float
    efficiency_percent: float


@dataclass(frozen=True, slots=True)
class CurrentSample:
    segment: int
    tag: int
    x_m: float
    y_m: float
    z_m: float
    length_m: float
    current_a: complex
    magnitude_a: float
    phase_deg: float


@dataclass(frozen=True, slots=True)
class FarFieldPoint:
    theta_deg: float
    phi_deg: float
    gain_vertical_db: float | None
    gain_horizontal_db: float | None
    gain_total_db: float | None
    axial_ratio: float
    tilt_deg: float
    polarization: str | None
    e_theta_magnitude_v_per_m: float | None
    e_theta_phase_deg: float | None
    e_phi_magnitude_v_per_m: float | None
    e_phi_phase_deg: float | None


@dataclass(frozen=True, slots=True)
class FrequencyResult:
    frequency_hz: float
    feed_tag: int
    feed_segment: int
    impedance_ohm: complex
    swr: float
    input_power_w: float
    currents: tuple[CurrentSample, ...] = ()
    far_field: tuple[FarFieldPoint, ...] = ()
    power_budget: PowerBudget | None = None


@dataclass(frozen=True, slots=True)
class SimulationResult:
    status: SimulationStatus
    spec: SimulationSpec
    model_fingerprint: str
    solver: SolverMetadata
    frequencies: tuple[FrequencyResult, ...]
    diagnostics: tuple[Diagnostic, ...] = ()
    raw_input: str = ""
    raw_output: str = ""
    stderr: str = ""
    duration_s: float = 0.0
    started_at: datetime | None = None
    finished_at: datetime | None = None

    @property
    def cache_key(self) -> str:
        return f"{self.model_fingerprint}:{self.solver.name}:{self.solver.version}"

    @property
    def max_total_gain_db(self) -> float | None:
        gains = [
            point.gain_total_db
            for frequency in self.frequencies
            for point in frequency.far_field
            if point.gain_total_db is not None
        ]
        return max(gains) if gains else None
