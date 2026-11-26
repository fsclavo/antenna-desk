# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Wilkinson feed-network solver wrapper.

The base NEC solver extracts the antenna short-circuit admittance matrix at
the level ports. The bounded N-port solver then solves the Wilkinson divider
and feed lines. Finally, the base solver runs a reconstruction with ideal
sources at the solved antenna port voltages, so the combined pattern and
currents remain available. Feed-network efficiency, splitter excess loss, and
line loss are applied to the reconstructed realized gain.
"""

from __future__ import annotations

import math
import time
from dataclasses import replace
from datetime import UTC, datetime

from ..domain.antennas.antenna import AntennaModel
from ..domain.antennas.feed import FeedPoint, Source
from ..domain.antennas.feed_network import (
    FeedNetworkSolution,
    n_way_wilkinson,
    solve_feed_network,
)
from ..domain.antennas.transmission_line import mismatched_line_loss_db
from ..domain.common.reflection import calculate_reflection_coefficient, calculate_swr
from ..domain.common.validation import Diagnostic, Severity
from ..domain.simulation.frequency import FrequencyPlan
from ..domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
    SourceResult,
)
from ..domain.simulation.solver import SolverCapabilities, SolverMetadata
from ..domain.simulation.spec import FeedNetworkKind, FeedNetworkSpec, SimulationSpec
from .feed_network_y import AntennaYMatrix, extract_antenna_y_matrices
from .fingerprint import model_fingerprint
from .ports.antenna_solver import AntennaSolver, ProgressCallback
from .ports.cancellation import CancelToken


class WilkinsonFeedSolver:
    """Wrap a base solver and dispatch specs with a Wilkinson feed network."""

    def __init__(self, base: AntennaSolver) -> None:
        self._base = base
        self._raw_inputs: list[str] = []
        self._raw_outputs: list[str] = []
        self._reconstruction_diagnostics: list[Diagnostic] = []

    def capabilities(self) -> SolverCapabilities:
        return self._base.capabilities()

    def version(self) -> SolverMetadata:
        return self._base.version()

    def validate(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
    ) -> tuple[Diagnostic, ...]:
        diagnostics = list(self._base.validate(model, spec))
        feed_network = spec.feed_network
        if feed_network is not None:
            port_count = len(model.effective_sources)
            if port_count != feed_network.port_count:
                diagnostics.append(
                    Diagnostic(
                        code="wilkinson.port_count_mismatch",
                        severity=Severity.ERROR,
                        message=("the feed network port count does not match the antenna ports"),
                        field="feed_network.port_count",
                    )
                )
        return tuple(diagnostics)

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: ProgressCallback | None = None,
        cancel_token: CancelToken | None = None,
    ) -> SimulationResult:
        feed_network = spec.feed_network
        if feed_network is None or feed_network.kind is not FeedNetworkKind.WILKINSON:
            return self._base.run(
                model,
                spec,
                progress_callback=progress_callback,
                cancel_token=cancel_token,
            )
        started_at = datetime.now(UTC)
        started = time.perf_counter()
        self._raw_inputs.clear()
        self._raw_outputs.clear()
        self._reconstruction_diagnostics.clear()
        try:
            y_matrices = extract_antenna_y_matrices(
                self._base,
                model,
                spec,
                progress_callback=progress_callback,
                cancel_token=cancel_token,
            )
            frequencies = tuple(
                self._solve_frequency(
                    model,
                    spec,
                    y_matrix,
                    progress_callback=progress_callback,
                    cancel_token=cancel_token,
                )
                for y_matrix in y_matrices
            )
        except Exception as exc:
            status = (
                SimulationStatus.CANCELLED
                if cancel_token is not None and cancel_token.is_cancelled()
                else SimulationStatus.ERROR
            )
            return SimulationResult(
                status=status,
                spec=spec,
                model_fingerprint=model_fingerprint(model, spec),
                solver=self._base.version(),
                frequencies=(),
                diagnostics=(
                    Diagnostic(
                        code="wilkinson.solve_failed",
                        severity=Severity.ERROR,
                        message=str(exc),
                    ),
                ),
                duration_s=time.perf_counter() - started,
                started_at=started_at,
                finished_at=datetime.now(UTC),
            )
        diagnostics = (
            *tuple(_unique_diagnostics(self._reconstruction_diagnostics)),
            Diagnostic(
                code="wilkinson.pattern_reconstruction",
                severity=Severity.INFO,
                message=(
                    "pattern reconstructed from the N-port splitter port voltages; "
                    "splitter efficiency, excess loss, and line loss are applied to "
                    "realized gain"
                ),
            ),
            Diagnostic(
                code="wilkinson.ideal_components",
                severity=Severity.WARNING,
                message=(
                    "Wilkinson branches, isolation resistors, and feed lines are ideal; "
                    "component tolerance, loss, and broadband behavior are not modeled"
                ),
            ),
            Diagnostic(
                code="wilkinson.power_budget_unavailable",
                severity=Severity.INFO,
                message=(
                    "the reconstructed multi-source power budget is not used; "
                    "realized gain is adjusted from the N-port feed solution"
                ),
            ),
        )
        raw_input = "\n\n".join(self._raw_inputs)
        raw_output = "\n\n".join(self._raw_outputs)
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint=model_fingerprint(model, spec),
            solver=self._base.version(),
            frequencies=frequencies,
            diagnostics=diagnostics,
            raw_input=raw_input,
            raw_output=raw_output,
            duration_s=time.perf_counter() - started,
            started_at=started_at,
            finished_at=datetime.now(UTC),
        )

    def _solve_frequency(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        y_matrix: AntennaYMatrix,
        *,
        progress_callback: ProgressCallback | None,
        cancel_token: CancelToken | None,
    ) -> FrequencyResult:
        feed = spec.feed_network
        if feed is None:
            raise ValueError("the Wilkinson wrapper requires a feed network spec")
        network = n_way_wilkinson(
            frequency_hz=feed.design_frequency_hz,
            port_count=feed.port_count,
            feed_line_lengths_m=feed.feed_line_lengths_m,
            system_impedance_ohm=feed.feed_line_impedance_ohm,
            velocity_factor=feed.velocity_factor,
            level_matching_networks=feed.level_matching_networks,
            branch_loss_db_per_100m=feed.branch_loss_db_per_100m,
            isolation_resistor_inductance_h=feed.isolation_resistor_inductance_h,
        )
        solution = solve_feed_network(
            network,
            y_matrix.matrix,
            frequency_hz=y_matrix.frequency_hz,
            source_current_a=1.0,
            level_transformer_ratios=feed.level_transformer_ratios,
        )
        port_voltages = solution.antenna_port_voltages_v
        if not port_voltages or max(abs(value) for value in port_voltages) <= 1e-15:
            raise ValueError("the Wilkinson solution has no driven antenna port")
        reference_index = max(
            range(len(port_voltages)),
            key=lambda index: abs(port_voltages[index]),
        )
        reference_voltage = port_voltages[reference_index]
        ports = y_matrix.ports
        sources = tuple(
            Source(
                wire_id=wire_id,
                offset_m=offset_m,
                amplitude=abs(port_voltages[index] / reference_voltage),
                phase_deg=math.degrees(
                    math.atan2(
                        (port_voltages[index] / reference_voltage).imag,
                        (port_voltages[index] / reference_voltage).real,
                    )
                ),
            )
            for index, (wire_id, offset_m) in enumerate(ports)
            if index != reference_index and abs(port_voltages[index] / reference_voltage) > 1e-12
        )
        reconstruction_model = replace(
            model,
            feed=FeedPoint(
                wire_id=ports[reference_index][0],
                offset_m=ports[reference_index][1],
            ),
            sources=sources,
            transmission_lines=(),
        )
        reconstruction_spec = replace(
            spec,
            frequency_plan=FrequencyPlan.single(y_matrix.frequency_hz),
            feed_network=None,
            co_simulate_feed_network=False,
            feed_network_loss_db=0.0,
            feed_network_line_loss_db_per_100m=0.0,
        )
        reconstruction = self._base.run(
            reconstruction_model,
            reconstruction_spec,
            progress_callback=progress_callback,
            cancel_token=cancel_token,
        )
        self._raw_inputs.append(reconstruction.raw_input)
        self._raw_outputs.append(reconstruction.raw_output)
        self._reconstruction_diagnostics.extend(reconstruction.diagnostics)
        if (
            reconstruction.status is not SimulationStatus.COMPLETED
            or not reconstruction.frequencies
        ):
            detail = "; ".join(item.message for item in reconstruction.diagnostics)
            raise ValueError(
                f"Wilkinson pattern reconstruction failed: {detail or reconstruction.status.value}"
            )
        point = reconstruction.frequencies[0]
        return self._adjusted_result(
            point,
            solution,
            feed,
            spec,
            y_matrix.ports,
            reference_index,
        )

    @staticmethod
    def _adjusted_result(
        point: FrequencyResult,
        solution: FeedNetworkSolution,
        feed: FeedNetworkSpec,
        spec: SimulationSpec,
        ports: tuple[tuple[str, float], ...],
        reference_index: int,
    ) -> FrequencyResult:
        antenna_powers = solution.antenna_port_powers_w
        antenna_currents = solution.antenna_port_currents_a
        antenna_voltages = solution.antenna_port_voltages_v
        antenna_impedances = solution.antenna_port_impedances_ohm
        input_power = solution.input_power_w
        delivered_power = sum(antenna_powers)
        reconstruction_power = sum(source.power_w for source in point.source_results)
        if (
            delivered_power > 1e-15
            and math.isfinite(reconstruction_power)
            and reconstruction_power > 0.0
        ):
            scale = reconstruction_power / delivered_power
        else:
            scale = 1.0
        input_power_actual = input_power * scale
        efficiency = min(1.0, max(0.0, delivered_power / input_power)) if input_power > 0.0 else 0.0
        efficiency_db = 10.0 * math.log10(max(efficiency, 1e-12))
        line_loss_db = _weighted_line_loss(solution, feed, point.frequency_hz)
        splitter_loss_db = feed.splitter_excess_loss_db
        try:
            gamma = calculate_reflection_coefficient(
                solution.input_impedance_ohm,
                spec.reference_impedance_ohm,
            )
            mismatch_loss_db = (
                -10.0 * math.log10(1.0 - abs(gamma) ** 2) if abs(gamma) < 1.0 else None
            )
        except ValueError:
            mismatch_loss_db = None
        realized_gain_db = point.realized_gain_db
        if realized_gain_db is not None:
            # The reconstruction's gain includes the mismatch at its reference
            # level port, but the real source is the splitter input. Replace
            # that mismatch with the splitter-input mismatch.
            realized_gain_db = (
                realized_gain_db
                + (point.mismatch_loss_db or 0.0)
                + efficiency_db
                - splitter_loss_db
                - line_loss_db
                - (mismatch_loss_db or 0.0)
            )
        source_results = _solver_source_results(
            point.source_results,
            ports,
            reference_index,
            antenna_voltages,
            antenna_currents,
            antenna_impedances,
            antenna_powers,
            scale,
        )
        return replace(
            point,
            impedance_ohm=solution.input_impedance_ohm,
            swr=calculate_swr(
                solution.input_impedance_ohm,
                spec.reference_impedance_ohm,
            ),
            input_power_w=input_power_actual,
            source_results=source_results,
            power_budget=None,
            realized_gain_db=realized_gain_db,
            mismatch_loss_db=mismatch_loss_db,
            feed_line_loss_db=line_loss_db,
            network_loss_db=max(0.0, -efficiency_db) + splitter_loss_db,
        )


def _weighted_line_loss(
    solution: FeedNetworkSolution,
    feed: FeedNetworkSpec,
    frequency_hz: float,
) -> float:
    lengths = feed.feed_line_lengths_m
    total_power = 0.0
    input_power = 0.0
    for index, (power, impedance) in enumerate(
        zip(
            solution.antenna_port_powers_w,
            solution.antenna_port_impedances_ohm,
            strict=True,
        )
    ):
        if power <= 0.0 or not math.isfinite(impedance.real):
            continue
        feed_side_impedance = impedance / feed.level_transformer_ratio_for_level(index)
        level_matching = feed.level_matching_network_for_level(index)
        load_impedance = (
            level_matching.abcd(frequency_hz).input_impedance(feed_side_impedance)
            if level_matching is not None
            else feed_side_impedance
        )
        loss_db = mismatched_line_loss_db(
            length_m=lengths[index],
            loss_db_per_100m=feed.line_loss_db_per_100m,
            characteristic_impedance_ohm=feed.feed_line_impedance_ohm,
            load_impedance_ohm=load_impedance,
        )
        total_power += power
        input_power += power * 10.0 ** (loss_db / 10.0)
    if total_power <= 0.0 or input_power <= 0.0:
        return 0.0
    return 10.0 * math.log10(input_power / total_power)


def _solver_source_results(
    reconstruction_results: tuple[SourceResult, ...],
    ports: tuple[tuple[str, float], ...],
    reference_index: int,
    voltages: tuple[complex, ...],
    currents: tuple[complex, ...],
    impedances: tuple[complex, ...],
    powers: tuple[float, ...],
    scale: float,
) -> tuple[SourceResult, ...]:
    by_port = {
        (source.wire_id, round(source.offset_m, 9)): source for source in reconstruction_results
    }
    order = [reference_index, *(index for index in range(len(ports)) if index != reference_index)]
    voltage_scale = math.sqrt(max(scale, 0.0))
    results: list[SourceResult] = []
    for index in order:
        wire_id, offset_m = ports[index]
        original = by_port.get((wire_id, round(offset_m, 9)))
        voltage = voltages[index] * voltage_scale
        results.append(
            SourceResult(
                wire_id=wire_id,
                offset_m=offset_m,
                tag=original.tag if original is not None else 0,
                segment=original.segment if original is not None else 0,
                amplitude=max(abs(voltage), 1e-30),
                phase_deg=math.degrees(math.atan2(voltage.imag, voltage.real)) % 360.0,
                voltage_v=voltage,
                current_a=currents[index] * voltage_scale,
                impedance_ohm=impedances[index],
                power_w=powers[index] * scale,
            )
        )
    return tuple(results)


def _unique_diagnostics(diagnostics: list[Diagnostic]) -> tuple[Diagnostic, ...]:
    seen: set[tuple[str, str]] = set()
    unique: list[Diagnostic] = []
    for diagnostic in diagnostics:
        key = (diagnostic.code, diagnostic.message)
        if key in seen:
            continue
        seen.add(key)
        unique.append(diagnostic)
    return tuple(unique)
