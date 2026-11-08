# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Map parsed nec2c output to normalized domain results."""

from __future__ import annotations

import math
from collections.abc import Sequence
from datetime import datetime

from ...domain.antennas.antenna import AntennaModel
from ...domain.common.validation import Diagnostic, Severity
from ...domain.simulation.link import link_budget
from ...domain.simulation.result import (
    CurrentSample,
    FarFieldPoint,
    FrequencyResult,
    PowerBudget,
    SimulationResult,
    SimulationStatus,
    SourceResult,
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
    matching_network = spec.matching_network
    if matching_network is not None and matching_network.is_active:
        problems.append(
            Diagnostic(
                code="matching_network.applied",
                severity=Severity.INFO,
                message=("impedance, SWR, and realized gain include the matching network"),
                field="matching_network",
            )
        )
    if not math.isclose(spec.feed_transformer_ratio, 1.0):
        problems.append(
            Diagnostic(
                code="transformer.applied",
                severity=Severity.INFO,
                message=(
                    "impedance, SWR, and realized gain include an ideal "
                    f"{spec.feed_transformer_ratio:g}:1 feed transformer"
                ),
                field="feed_transformer_ratio",
            )
        )
    if spec.balun_loss is not None and spec.balun_loss.is_active:
        problems.append(
            Diagnostic(
                code="balun_loss.applied",
                severity=Severity.INFO,
                message=(
                    "impedance and SWR exclude the matched balun/unun loss; "
                    "realized gain includes it"
                ),
                field="balun_loss",
            )
        )
    if feed_line is not None and feed_line.is_active:
        problems.append(
            Diagnostic(
                code="feed_line.applied",
                severity=Severity.INFO,
                message=(
                    "impedance, SWR, and realized gain include a "
                    f"{feed_line.length_m:g} m feed line"
                ),
                field="feed_line",
            )
        )
    frequency_results: list[FrequencyResult] = []
    negative_resistance_hz: list[float] = []
    absorbing_source_hz: list[float] = []
    main_count = spec.frequency_plan.count
    parsed_main = parsed.frequencies[:main_count]
    parsed_patterns = parsed.frequencies[main_count:] if spec.pattern_frequencies_hz else ()
    pattern_by_main_index: dict[int, tuple[ParsedFarFieldPoint, ...]] = {}
    if parsed_patterns:
        tolerance_hz = (
            spec.frequency_plan.step_hz / 2.0 + 1.0 if spec.frequency_plan.count > 1 else 1.0
        )
        for pattern in parsed_patterns:
            if not pattern.far_field:
                continue
            main_index = min(
                range(len(parsed_main)),
                key=lambda index: abs(parsed_main[index].frequency_hz - pattern.frequency_hz),
            )
            if abs(parsed_main[main_index].frequency_hz - pattern.frequency_hz) <= tolerance_hz:
                pattern_by_main_index[main_index] = tuple(pattern.far_field)

    for parsed_index, parsed_frequency in enumerate(parsed_main):
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

        if input_parameters.impedance_ohm.real <= 0.0:
            negative_resistance_hz.append(parsed_frequency.frequency_hz)

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
        source_results: list[SourceResult] = []
        for feed in deck.layout.feeds:
            parsed_source = next(
                (
                    candidate
                    for candidate in parsed_frequency.input_parameters
                    if candidate.tag == feed.tag and candidate.segment == feed.segment
                ),
                None,
            )
            if parsed_source is None:
                continue
            source_results.append(
                SourceResult(
                    wire_id=feed.wire_id,
                    offset_m=feed.offset_m,
                    tag=feed.tag,
                    segment=feed.segment,
                    amplitude=feed.amplitude,
                    phase_deg=feed.phase_deg,
                    voltage_v=parsed_source.voltage_v,
                    current_a=parsed_source.current_a,
                    impedance_ohm=parsed_source.impedance_ohm,
                    power_w=parsed_source.power_w,
                )
            )
        if any(source.power_w < 0.0 for source in source_results):
            absorbing_source_hz.append(parsed_frequency.frequency_hz)
        if pattern_by_main_index:
            pattern_points = pattern_by_main_index.get(parsed_index, ())
        else:
            pattern_points = tuple(parsed_frequency.far_field)
        far_field = tuple(_far_field_point(point) for point in pattern_points)
        link = link_budget(
            antenna_impedance_ohm=input_parameters.impedance_ohm,
            frequency_hz=parsed_frequency.frequency_hz,
            spec=spec,
        )
        input_impedance = link.input_impedance_ohm
        gains = [
            point.gain_total_db
            for point in far_field
            if point.gain_total_db is not None and math.isfinite(point.gain_total_db)
        ]
        max_gain_db = max(gains) if gains else None
        power_budget = _power_budget(parsed_frequency.power_budget)
        efficiency_percent = power_budget.efficiency_percent if power_budget is not None else None
        directivity_db = (
            max_gain_db - 10.0 * math.log10(efficiency_percent / 100.0)
            if max_gain_db is not None
            and efficiency_percent is not None
            and efficiency_percent > 0.0
            else None
        )
        realized_gain_db = (
            max_gain_db + link.transducer_gain_db
            if max_gain_db is not None and math.isfinite(link.transducer_gain_db)
            else None
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
                source_results=tuple(source_results),
                power_budget=power_budget,
                directivity_db=directivity_db,
                realized_gain_db=realized_gain_db,
                mismatch_loss_db=(
                    link.mismatch_loss_db if math.isfinite(link.mismatch_loss_db) else None
                ),
                feed_line_loss_db=(
                    link.feed_line_loss_db if math.isfinite(link.feed_line_loss_db) else None
                ),
                network_loss_db=(
                    link.network_loss_db if math.isfinite(link.network_loss_db) else None
                ),
                balun_loss_db=(link.balun_loss_db if math.isfinite(link.balun_loss_db) else None),
            )
        )

    if absorbing_source_hz:
        first = absorbing_source_hz[0] / 1e6
        last = absorbing_source_hz[-1] / 1e6
        range_text = (
            f"{first:g} MHz" if len(absorbing_source_hz) == 1 else f"{first:g}-{last:g} MHz"
        )
        problems.append(
            Diagnostic(
                code="normalization.source_absorbs_power",
                severity=Severity.WARNING,
                message=(
                    f"one or more ideal sources absorb power at {range_text} "
                    f"({len(absorbing_source_hz)} frequency/frequencies); the "
                    "excitation is an ideal source model, not a physical feed "
                    "network. Check the source amplitudes and phases."
                ),
                field="sources",
            )
        )

    if negative_resistance_hz:
        all_negative = len(negative_resistance_hz) == len(frequency_results)
        first = negative_resistance_hz[0] / 1e6
        last = negative_resistance_hz[-1] / 1e6
        range_text = (
            f"{first:g} MHz" if len(negative_resistance_hz) == 1 else f"{first:g}-{last:g} MHz"
        )
        problems.append(
            Diagnostic(
                code="normalization.negative_resistance",
                severity=(Severity.ERROR if all_negative else Severity.WARNING),
                message=(
                    f"negative input resistance at {range_text} ({len(negative_resistance_hz)} "
                    "frequency/frequencies); the passive antenna model is invalid. "
                    "Check the geometry, very short gaps or matching wires, "
                    "segmentation, radial height, and ground model; far-field "
                    "gains are unavailable."
                ),
                field="impedance",
            )
        )

    if spec.pattern_frequencies_hz:
        expected_patterns = len(spec.pattern_frequencies_hz)
        if len(pattern_by_main_index) < expected_patterns and len(frequency_results) >= main_count:
            problems.append(
                Diagnostic(
                    code="normalization.pattern_missing",
                    severity=Severity.WARNING,
                    message=(
                        f"{expected_patterns - len(pattern_by_main_index)} of "
                        f"{expected_patterns} far-field snapshots were missing "
                        "from the solver output"
                    ),
                    field="far_field",
                )
            )

    if not frequency_results:
        status = SimulationStatus.ERROR
    elif len(frequency_results) < main_count:
        status = SimulationStatus.PARTIAL
    elif negative_resistance_hz and len(negative_resistance_hz) == len(frequency_results):
        status = SimulationStatus.ERROR
    elif negative_resistance_hz:
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
