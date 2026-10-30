# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Map parsed nec2c output to normalized domain results."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from ...domain.antennas.antenna import AntennaModel
from ...domain.common.validation import Diagnostic, Severity
from ...domain.simulation.result import (
    CurrentSample,
    FarFieldPoint,
    FrequencyResult,
    PowerBudget,
    SimulationResult,
    SimulationStatus,
)
from ...domain.simulation.solver import SolverMetadata
from ...domain.simulation.spec import SimulationSpec
from ..fingerprint import model_fingerprint
from ..normalization import calculate_swr
from .input_writer import Nec2Deck
from .parser import ParsedFarFieldPoint, ParsedNec2Output, ParsedPowerBudget


def _power_budget(value: ParsedPowerBudget | None) -> PowerBudget | None:
    if value is None:
        return None
    return PowerBudget(
        input_w=value.input_w,
        radiated_w=value.radiated_w,
        structure_loss_w=value.structure_loss_w,
        network_loss_w=value.network_loss_w,
        efficiency_percent=value.efficiency_percent,
    )


def _far_field_point(value: ParsedFarFieldPoint) -> FarFieldPoint:
    return FarFieldPoint(
        theta_deg=value.theta_deg,
        phi_deg=value.phi_deg,
        gain_vertical_db=value.gain_vertical_db,
        gain_horizontal_db=value.gain_horizontal_db,
        gain_total_db=value.gain_total_db,
        axial_ratio=value.axial_ratio,
        tilt_deg=value.tilt_deg,
        polarization=value.polarization,
        e_theta_magnitude_v_per_m=value.e_theta_magnitude_v_per_m,
        e_theta_phase_deg=value.e_theta_phase_deg,
        e_phi_magnitude_v_per_m=value.e_phi_magnitude_v_per_m,
        e_phi_phase_deg=value.e_phi_phase_deg,
    )


def normalize_nec2_result(
    *,
    model: AntennaModel,
    spec: SimulationSpec,
    deck: Nec2Deck,
    parsed: ParsedNec2Output,
    solver: SolverMetadata,
    diagnostics: Sequence[Diagnostic],
    raw_input: str,
    raw_output: str,
    stderr: str,
    started_at: datetime,
    finished_at: datetime,
) -> SimulationResult:
    problems: list[Diagnostic] = list(diagnostics)
    feed_line = spec.feed_line
    if feed_line is not None and feed_line.is_active:
        problems.append(
            Diagnostic(
                code="feed_line.applied",
                severity=Severity.INFO,
                message=(
                    "impedance and SWR are evaluated at the transmitter end of "
                    f"a {feed_line.length_m:g} m feed line"
                ),
                field="feed_line",
            )
        )
    frequency_results: list[FrequencyResult] = []

    for parsed_frequency in parsed.frequencies:
        input_parameters = next(
            (
                candidate
                for candidate in parsed_frequency.input_parameters
                if candidate.tag == deck.feed_tag and candidate.segment == deck.feed_segment
            ),
            None,
        )
        if input_parameters is None and parsed_frequency.input_parameters:
            input_parameters = parsed_frequency.input_parameters[0]
            problems.append(
                Diagnostic(
                    code="normalization.feed_segment_missing",
                    severity=Severity.WARNING,
                    message=(
                        "the requested feed segment was not found in the output; "
                        "using the first input parameter block"
                    ),
                    field="feed",
                )
            )

        if input_parameters is None:
            problems.append(
                Diagnostic(
                    code="normalization.impedance_missing",
                    severity=Severity.ERROR,
                    message=(f"no input impedance at {parsed_frequency.frequency_hz / 1e6:g} MHz"),
                    field="frequencies",
                )
            )
            continue

        currents = tuple(
            CurrentSample(
                segment=current.segment,
                tag=current.tag,
                x_m=current.x_m,
                y_m=current.y_m,
                z_m=current.z_m,
                length_m=current.length_m,
                current_a=current.current_a,
                magnitude_a=current.magnitude_a,
                phase_deg=current.phase_deg,
            )
            for current in parsed_frequency.currents
        )
        far_field = tuple(_far_field_point(point) for point in parsed_frequency.far_field)
        input_impedance = input_parameters.impedance_ohm
        if feed_line is not None:
            input_impedance = feed_line.input_impedance(
                input_impedance,
                parsed_frequency.frequency_hz,
            )

        frequency_results.append(
            FrequencyResult(
                frequency_hz=parsed_frequency.frequency_hz,
                feed_tag=deck.feed_tag,
                feed_segment=deck.feed_segment,
                impedance_ohm=input_impedance,
                swr=calculate_swr(
                    input_impedance,
                    spec.reference_impedance_ohm,
                ),
                input_power_w=input_parameters.power_w,
                currents=currents,
                far_field=far_field,
                power_budget=_power_budget(parsed_frequency.power_budget),
            )
        )

    if not frequency_results:
        status = SimulationStatus.ERROR
    elif len(frequency_results) < len(parsed.frequencies):
        status = SimulationStatus.PARTIAL
    else:
        status = SimulationStatus.COMPLETED

    return SimulationResult(
        status=status,
        spec=spec,
        model_fingerprint=model_fingerprint(model, spec),
        solver=solver,
        frequencies=tuple(frequency_results),
        diagnostics=tuple(problems),
        raw_input=raw_input,
        raw_output=raw_output,
        stderr=stderr,
        duration_s=(finished_at - started_at).total_seconds(),
        started_at=started_at,
        finished_at=finished_at,
    )
