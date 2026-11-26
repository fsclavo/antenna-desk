# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small N-port circuit solver for feed networks.

The solver works with nodal admittance matrices at one frequency. It is
intended for bounded feed networks such as a two-way Wilkinson divider or a
set of transmission lines and resistors. It is not a general circuit simulator
and does not model distributed losses or frequency-dependent components beyond
the ideal transmission-line phase.

The module is pure Python: networks are small (a few ports and internal
nodes), so a dense Gaussian elimination is sufficient and no new runtime
dependency is needed. ``scikit-rf`` remains a development-only cross-check.
"""

from __future__ import annotations

import cmath
import math
from collections.abc import Sequence
from dataclasses import dataclass

from ..common.units import ensure_positive
from .matching_network import LNetwork, MatchingNetwork, PiNetwork, TNetwork

Matrix = list[list[complex]]
Vector = list[complex]


def _zero_matrix(size: int) -> Matrix:
    return [[0.0 + 0.0j for _ in range(size)] for _ in range(size)]


def _identity(size: int) -> Matrix:
    return [
        [1.0 + 0.0j if row == column else 0.0 + 0.0j for column in range(size)]
        for row in range(size)
    ]


def _add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] + right[row][column] for column in range(len(left))]
        for row in range(len(left))
    ]


def _subtract(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][column] - right[row][column] for column in range(len(left))]
        for row in range(len(left))
    ]


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    rows = len(left)
    inner = len(right)
    columns = len(right[0]) if right else 0
    return [
        [
            sum(left[row][index] * right[index][column] for index in range(inner))
            for column in range(columns)
        ]
        for row in range(rows)
    ]


def _matvec(matrix: Matrix, vector: Vector) -> Vector:
    return [
        sum(matrix[row][column] * vector[column] for column in range(len(vector)))
        for row in range(len(matrix))
    ]


def _solve(matrix: Matrix, vector: Vector) -> Vector:
    """Solve a dense complex linear system with partial pivoting."""

    size = len(matrix)
    if size == 0:
        return []
    augmented = [[*list(matrix[row]), vector[row]] for row in range(size)]
    for column in range(size):
        pivot_row = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        pivot = augmented[pivot_row][column]
        if abs(pivot) < 1e-18:
            raise ValueError("feed-network matrix is singular")
        if pivot_row != column:
            augmented[column], augmented[pivot_row] = augmented[pivot_row], augmented[column]
        pivot = augmented[column][column]
        for index in range(column, size + 1):
            augmented[column][index] /= pivot
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if abs(factor) < 1e-30:
                continue
            for index in range(column, size + 1):
                augmented[row][index] -= factor * augmented[column][index]
    return [augmented[row][size] for row in range(size)]


def _inverse(matrix: Matrix) -> Matrix:
    size = len(matrix)
    inverse = _zero_matrix(size)
    for column in range(size):
        unit = [1.0 + 0.0j if row == column else 0.0 + 0.0j for row in range(size)]
        solution = _solve(matrix, unit)
        for row in range(size):
            inverse[row][column] = solution[row]
    return inverse


@dataclass(frozen=True, slots=True)
class SeriesBranch:
    """A series impedance between two nodes."""

    node_a: int
    node_b: int
    impedance_ohm: complex

    def __post_init__(self) -> None:
        if self.node_a < 0 or self.node_b < 0 or self.node_a == self.node_b:
            raise ValueError("a series branch needs two distinct non-negative nodes")
        if abs(self.impedance_ohm) <= 0.0:
            raise ValueError("a series branch needs a non-zero impedance")


@dataclass(frozen=True, slots=True)
class SeriesRlBranch:
    """A series resistor-inductor branch between two nodes."""

    node_a: int
    node_b: int
    resistance_ohm: float
    inductance_h: float = 0.0

    def __post_init__(self) -> None:
        if self.node_a < 0 or self.node_b < 0 or self.node_a == self.node_b:
            raise ValueError("a series RL branch needs two distinct non-negative nodes")
        ensure_positive(self.resistance_ohm, name="resistance_ohm")
        if not math.isfinite(self.inductance_h) or self.inductance_h < 0.0:
            raise ValueError("inductance_h must be finite and non-negative")

    def impedance_ohm_at(self, frequency_hz: float) -> complex:
        ensure_positive(frequency_hz, name="frequency_hz")
        return complex(
            self.resistance_ohm,
            math.tau * frequency_hz * self.inductance_h,
        )


@dataclass(frozen=True, slots=True)
class IsolationResistorBranch:
    """A series R-L resistor with a parallel parasitic capacitance."""

    node_a: int
    node_b: int
    resistance_ohm: float
    inductance_h: float = 0.0
    capacitance_f: float = 0.0

    def __post_init__(self) -> None:
        if self.node_a < 0 or self.node_b < 0 or self.node_a == self.node_b:
            raise ValueError("an isolation resistor branch needs two distinct nodes")
        ensure_positive(self.resistance_ohm, name="resistance_ohm")
        for name, value in (
            ("inductance_h", self.inductance_h),
            ("capacitance_f", self.capacitance_f),
        ):
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and non-negative")

    def admittance_s_at(self, frequency_hz: float) -> complex:
        ensure_positive(frequency_hz, name="frequency_hz")
        series = complex(
            self.resistance_ohm,
            math.tau * frequency_hz * self.inductance_h,
        )
        admittance = 1.0 / series
        if self.capacitance_f > 0.0:
            admittance += complex(0.0, math.tau * frequency_hz * self.capacitance_f)
        return admittance


@dataclass(frozen=True, slots=True)
class ShuntBranch:
    """A shunt impedance from a node to the common reference."""

    node: int
    impedance_ohm: complex

    def __post_init__(self) -> None:
        if self.node < 0:
            raise ValueError("a shunt branch needs a non-negative node")
        if abs(self.impedance_ohm) <= 0.0:
            raise ValueError("a shunt branch needs a non-zero impedance")


@dataclass(frozen=True, slots=True)
class TransmissionLineBranch:
    """An ideal lossless transmission line between two nodes."""

    node_a: int
    node_b: int
    characteristic_impedance_ohm: float
    length_m: float
    velocity_factor: float = 1.0
    matched_loss_db_per_100m: float = 0.0

    def __post_init__(self) -> None:
        if self.node_a < 0 or self.node_b < 0 or self.node_a == self.node_b:
            raise ValueError("a transmission line needs two distinct non-negative nodes")
        ensure_positive(self.characteristic_impedance_ohm, name="characteristic_impedance_ohm")
        ensure_positive(self.length_m, name="length_m")
        ensure_positive(self.velocity_factor, name="velocity_factor")
        if self.velocity_factor > 1.0:
            raise ValueError("velocity_factor must not exceed 1")
        if not math.isfinite(self.matched_loss_db_per_100m) or self.matched_loss_db_per_100m < 0.0:
            raise ValueError("matched_loss_db_per_100m must be finite and non-negative")

    def y_parameters(self, frequency_hz: float) -> tuple[complex, complex, complex, complex]:
        """Return the two-port admittance parameters at ``frequency_hz``."""

        ensure_positive(frequency_hz, name="frequency_hz")
        theta = (
            math.tau
            * frequency_hz
            * self.length_m
            / (_SPEED_OF_LIGHT_M_PER_S * self.velocity_factor)
        )
        sin_theta = math.sin(theta)
        attenuation_np_per_m = self.matched_loss_db_per_100m / 100.0 * math.log(10.0) / 20.0
        if attenuation_np_per_m > 0.0:
            propagation = complex(attenuation_np_per_m * self.length_m, theta)
            y0 = 1.0 / self.characteristic_impedance_ohm
            y11 = y0 / cmath.tanh(propagation)
            y12 = -y0 / cmath.sinh(propagation)
            return (y11, y12, y12, y11)
        if abs(sin_theta) < 1e-9:
            # A half-wave line is a through connection with a phase reversal.
            # A tiny series impedance keeps the nodal matrix finite.
            series = 1.0 / complex(1e-6, 0.0)
            return (series, -series, -series, series)
        y0 = 1.0 / self.characteristic_impedance_ohm
        y11 = complex(0.0, -y0 / math.tan(theta))
        y12 = complex(0.0, y0 / sin_theta)
        return (y11, y12, y12, y11)


@dataclass(frozen=True, slots=True)
class TwoPortBranch:
    """A two-port ABCD network between two nodes.

    The matching network's input is ``node_a`` and its output is ``node_b``.
    The network must have a non-zero series element so its ABCD matrix has a
    finite B term; a pure shunt one-port is not a valid feed-network branch.
    """

    node_a: int
    node_b: int
    network: MatchingNetwork

    def __post_init__(self) -> None:
        if self.node_a < 0 or self.node_b < 0 or self.node_a == self.node_b:
            raise ValueError("a two-port branch needs two distinct non-negative nodes")
        if not self.network.is_active:
            raise ValueError("a two-port matching branch needs an active network")

    def y_parameters(self, frequency_hz: float) -> tuple[complex, complex, complex, complex]:
        abcd = self.network.abcd(frequency_hz)
        if abs(abcd.b) <= 1e-15:
            raise ValueError("a two-port matching branch needs a non-zero series element")
        return (
            abcd.d / abcd.b,
            (abcd.b * abcd.c - abcd.a * abcd.d) / abcd.b,
            -1.0 / abcd.b,
            abcd.a / abcd.b,
        )


NetworkBranch = (
    SeriesBranch
    | SeriesRlBranch
    | IsolationResistorBranch
    | ShuntBranch
    | TransmissionLineBranch
    | TwoPortBranch
)
_SPEED_OF_LIGHT_M_PER_S = 299_792_458.0


@dataclass(frozen=True, slots=True)
class NPortNetwork:
    """A feed network with named external ports and internal nodes.

    External ports are nodes ``0 .. len(port_names) - 1``. Internal nodes are
    numbered after them. The common reference (ground) is implicit.
    """

    port_names: tuple[str, ...]
    branches: tuple[NetworkBranch, ...]
    internal_node_count: int = 0

    def __post_init__(self) -> None:
        if len(self.port_names) < 1:
            raise ValueError("a feed network needs at least one port")
        if len(set(self.port_names)) != len(self.port_names):
            raise ValueError("feed-network port names must be unique")
        if self.internal_node_count < 0:
            raise ValueError("internal_node_count must not be negative")
        node_count = len(self.port_names) + self.internal_node_count
        for branch in self.branches:
            for node in self._branch_nodes(branch):
                if node >= node_count:
                    raise ValueError("a branch references an unknown node")

    @staticmethod
    def _branch_nodes(branch: NetworkBranch) -> tuple[int, ...]:
        if isinstance(branch, ShuntBranch):
            return (branch.node,)
        return (branch.node_a, branch.node_b)

    @property
    def node_count(self) -> int:
        return len(self.port_names) + self.internal_node_count

    def y_matrix(self, frequency_hz: float) -> Matrix:
        """Return the port admittance matrix with internal nodes eliminated."""

        size = self.node_count
        admittance = _zero_matrix(size)
        for branch in self.branches:
            if isinstance(branch, (TransmissionLineBranch, TwoPortBranch)):
                y11, y12, y21, y22 = branch.y_parameters(frequency_hz)
                a, b = branch.node_a, branch.node_b
                admittance[a][a] += y11
                admittance[a][b] += y12
                admittance[b][a] += y21
                admittance[b][b] += y22
                continue
            if isinstance(branch, SeriesRlBranch):
                series = 1.0 / branch.impedance_ohm_at(frequency_hz)
                a, b = branch.node_a, branch.node_b
                admittance[a][a] += series
                admittance[b][b] += series
                admittance[a][b] -= series
                admittance[b][a] -= series
                continue
            if isinstance(branch, IsolationResistorBranch):
                shunt = branch.admittance_s_at(frequency_hz)
                a, b = branch.node_a, branch.node_b
                admittance[a][a] += shunt
                admittance[b][b] += shunt
                admittance[a][b] -= shunt
                admittance[b][a] -= shunt
                continue
            series = 1.0 / branch.impedance_ohm
            if isinstance(branch, ShuntBranch):
                admittance[branch.node][branch.node] += series
                continue
            a, b = branch.node_a, branch.node_b
            admittance[a][a] += series
            admittance[b][b] += series
            admittance[a][b] -= series
            admittance[b][a] -= series

        port_count = len(self.port_names)
        if self.internal_node_count == 0:
            return admittance

        port_admittance = [row[:port_count] for row in admittance[:port_count]]
        port_to_internal = [row[port_count:] for row in admittance[:port_count]]
        internal_to_port = [row[:port_count] for row in admittance[port_count:]]
        internal_admittance = [row[port_count:] for row in admittance[port_count:]]
        inverse_internal = _inverse(internal_admittance)
        return _subtract(
            port_admittance,
            _multiply(_multiply(port_to_internal, inverse_internal), internal_to_port),
        )

    def s_matrix(self, frequency_hz: float, reference_impedance_ohm: float = 50.0) -> Matrix:
        """Return the port S-matrix for equal real reference impedances."""

        ensure_positive(reference_impedance_ohm, name="reference_impedance_ohm")
        admittance = self.y_matrix(frequency_hz)
        port_count = len(self.port_names)
        reference = _identity(port_count)
        for row in range(port_count):
            reference[row][row] = complex(reference_impedance_ohm, 0.0)
        return _multiply(
            _subtract(_identity(port_count), _multiply(reference, admittance)),
            _inverse(_add(_identity(port_count), _multiply(reference, admittance))),
        )


@dataclass(frozen=True, slots=True)
class FeedNetworkSolution:
    """The solved input impedance and port powers for one feed network."""

    input_impedance_ohm: complex
    port_voltages_v: tuple[complex, ...]
    antenna_port_voltages_v: tuple[complex, ...]
    antenna_port_currents_a: tuple[complex, ...]
    antenna_port_impedances_ohm: tuple[complex, ...]
    antenna_port_powers_w: tuple[float, ...]
    input_power_w: float
    network_loss_w: float


def solve_feed_network(
    network: NPortNetwork,
    antenna_admittance: Matrix,
    *,
    frequency_hz: float,
    source_current_a: float = 1.0,
    input_port_index: int = 0,
    level_transformer_ratios: Sequence[float] | None = None,
) -> FeedNetworkSolution:
    """Connect an antenna admittance matrix to a feed network.

    The feed network's ``input_port_index`` is driven by an ideal current
    source; the remaining ports are connected to the antenna. ``antenna_admittance``
    has one row and column per antenna port and must match the other ports in
    order. ``level_transformer_ratios`` places an ideal impedance transformer
    at each antenna port; a ratio ``r`` means the feed sees ``Z_ant / r``.
    Empty or omitted means 1:1 everywhere.
    """

    ensure_positive(source_current_a, name="source_current_a")
    port_count = len(network.port_names)
    antenna_ports = port_count - 1
    if len(antenna_admittance) != antenna_ports or any(
        len(row) != antenna_ports for row in antenna_admittance
    ):
        raise ValueError("antenna_admittance size does not match the feed-network ports")
    if not 0 <= input_port_index < port_count:
        raise ValueError("input_port_index is outside the feed-network ports")
    ratios = (
        (1.0,) * antenna_ports
        if level_transformer_ratios is None or not level_transformer_ratios
        else tuple(level_transformer_ratios)
    )
    if len(ratios) != antenna_ports:
        raise ValueError("level_transformer_ratios size does not match the antenna ports")
    for ratio in ratios:
        if not math.isfinite(ratio) or ratio <= 0.0:
            raise ValueError("level_transformer_ratios must be positive and finite")
    scales = tuple(math.sqrt(ratio) for ratio in ratios)
    transformed_admittance = [
        [
            antenna_admittance[row][column] * scales[row] * scales[column]
            for column in range(antenna_ports)
        ]
        for row in range(antenna_ports)
    ]

    port_order = [index for index in range(port_count) if index != input_port_index]
    admittance = network.y_matrix(frequency_hz)
    combined = [row[:] for row in admittance]
    for antenna_row, network_row in enumerate(port_order):
        for antenna_column, network_column in enumerate(port_order):
            combined[network_row][network_column] += transformed_admittance[antenna_row][
                antenna_column
            ]

    current = [0.0 + 0.0j for _ in range(port_count)]
    current[input_port_index] = complex(source_current_a, 0.0)
    voltage = _solve(combined, current)
    input_voltage = voltage[input_port_index]
    input_current = current[input_port_index]
    input_power = 0.5 * (input_voltage * input_current.conjugate()).real
    feed_side_voltages = [voltage[index] for index in port_order]
    antenna_voltages = [
        voltage_value * scale
        for voltage_value, scale in zip(feed_side_voltages, scales, strict=True)
    ]
    antenna_currents = _matvec(antenna_admittance, antenna_voltages)
    antenna_impedances = tuple(
        voltage_value / current_value if abs(current_value) > 1e-30 else complex(float("inf"), 0.0)
        for voltage_value, current_value in zip(
            antenna_voltages,
            antenna_currents,
            strict=True,
        )
    )
    antenna_powers = tuple(
        0.5 * (voltage_value * current_value.conjugate()).real
        for voltage_value, current_value in zip(antenna_voltages, antenna_currents, strict=True)
    )
    return FeedNetworkSolution(
        input_impedance_ohm=input_voltage / input_current,
        port_voltages_v=tuple(voltage),
        antenna_port_voltages_v=tuple(antenna_voltages),
        antenna_port_currents_a=tuple(antenna_currents),
        antenna_port_impedances_ohm=antenna_impedances,
        antenna_port_powers_w=antenna_powers,
        input_power_w=input_power,
        network_loss_w=input_power - sum(antenna_powers),
    )


def two_way_wilkinson(
    *,
    frequency_hz: float,
    system_impedance_ohm: float = 50.0,
    velocity_factor: float = 1.0,
    length_m: float | None = None,
) -> NPortNetwork:
    """Return an ideal two-way Wilkinson divider at ``frequency_hz``."""

    ensure_positive(frequency_hz, name="frequency_hz")
    ensure_positive(system_impedance_ohm, name="system_impedance_ohm")
    ensure_positive(velocity_factor, name="velocity_factor")
    if velocity_factor > 1.0:
        raise ValueError("velocity_factor must not exceed 1")
    quarter_wave_m = _SPEED_OF_LIGHT_M_PER_S / frequency_hz / 4.0 * velocity_factor
    line_length = quarter_wave_m if length_m is None else length_m
    ensure_positive(line_length, name="length_m")
    return NPortNetwork(
        port_names=("input", "output-1", "output-2"),
        branches=(
            TransmissionLineBranch(
                node_a=0,
                node_b=1,
                characteristic_impedance_ohm=system_impedance_ohm * math.sqrt(2.0),
                length_m=line_length,
                velocity_factor=velocity_factor,
            ),
            TransmissionLineBranch(
                node_a=0,
                node_b=2,
                characteristic_impedance_ohm=system_impedance_ohm * math.sqrt(2.0),
                length_m=line_length,
                velocity_factor=velocity_factor,
            ),
            SeriesBranch(
                node_a=1,
                node_b=2,
                impedance_ohm=complex(2.0 * system_impedance_ohm, 0.0),
            ),
        ),
    )


def n_way_wilkinson(
    *,
    frequency_hz: float,
    port_count: int,
    feed_line_lengths_m: Sequence[float],
    system_impedance_ohm: float = 50.0,
    velocity_factor: float = 1.0,
    branch_velocity_factor: float = 1.0,
    level_matching_network: MatchingNetwork | None = None,
    level_matching_networks: Sequence[MatchingNetwork | None] | None = None,
    branch_impedance_scales: Sequence[float] | None = None,
    isolation_resistor_scales: Sequence[float] | None = None,
    branch_loss_db_per_100m: float = 0.0,
    isolation_resistor_inductance_h: float = 0.0,
    isolation_resistor_capacitance_f: float = 0.0,
) -> NPortNetwork:
    """Return an equal N-way Wilkinson with feed lines to each output.

    The external ports are the input (node 0) and the N level ports (nodes
    1..N). The splitter branches are quarter-wave at ``frequency_hz`` with
    impedance ``system_impedance_ohm * sqrt(N)``. The isolation network is a
    star of N resistors of ``system_impedance_ohm`` around a floating center.
    Each splitter output then runs through a feed line of the given length and
    the system impedance to its level port. ``level_matching_network`` applies
    the same two-port network to every output; ``level_matching_networks``
    supplies one entry per output, where ``None`` leaves that level unmatched.
    Provide at most one of the two. ``branch_impedance_scales`` and
    ``isolation_resistor_scales`` apply a per-output multiplier to the nominal
    branch impedance and star resistor for tolerance analysis; omitted means
    1.0 everywhere. ``branch_loss_db_per_100m`` adds a matched attenuation to
    each quarter-wave branch. ``isolation_resistor_inductance_h`` and
    ``isolation_resistor_capacitance_f`` add series inductance and parallel
    capacitance to every star resistor, making isolation and input match
    frequency-dependent. The floating star center is regularized by a very high
    numerical shunt; it is not a physical component.
    """

    ensure_positive(frequency_hz, name="frequency_hz")
    if port_count < 2:
        raise ValueError("an N-way Wilkinson needs at least two outputs")
    if len(feed_line_lengths_m) != port_count:
        raise ValueError("feed_line_lengths_m must have one length per output")
    ensure_positive(system_impedance_ohm, name="system_impedance_ohm")
    ensure_positive(velocity_factor, name="velocity_factor")
    ensure_positive(branch_velocity_factor, name="branch_velocity_factor")
    if not math.isfinite(branch_loss_db_per_100m) or branch_loss_db_per_100m < 0.0:
        raise ValueError("branch_loss_db_per_100m must be finite and non-negative")
    if not math.isfinite(isolation_resistor_inductance_h) or isolation_resistor_inductance_h < 0.0:
        raise ValueError("isolation_resistor_inductance_h must be finite and non-negative")
    if velocity_factor > 1.0:
        raise ValueError("velocity_factor must not exceed 1")
    if branch_velocity_factor > 1.0:
        raise ValueError("branch_velocity_factor must not exceed 1")
    for length_m in feed_line_lengths_m:
        ensure_positive(length_m, name="feed_line_lengths_m")
    if level_matching_network is not None and level_matching_networks is not None:
        raise ValueError(
            "provide either level_matching_network or level_matching_networks, not both"
        )
    if level_matching_networks is None:
        networks: tuple[MatchingNetwork | None, ...] = (level_matching_network,) * port_count
    else:
        networks = tuple(level_matching_networks)
        if not networks:
            networks = (None,) * port_count
        elif len(networks) != port_count:
            raise ValueError("level_matching_networks must have one entry per output")
    for network in networks:
        if network is not None and not isinstance(network, (LNetwork, PiNetwork, TNetwork)):
            raise ValueError("per-level matching supports L, Pi, or T networks only")
    branch_scales = (
        (1.0,) * port_count
        if branch_impedance_scales is None or not branch_impedance_scales
        else tuple(branch_impedance_scales)
    )
    resistor_scales = (
        (1.0,) * port_count
        if isolation_resistor_scales is None or not isolation_resistor_scales
        else tuple(isolation_resistor_scales)
    )
    if len(branch_scales) != port_count or len(resistor_scales) != port_count:
        raise ValueError("Wilkinson component scales must have one entry per output")
    for scale in (*branch_scales, *resistor_scales):
        if not math.isfinite(scale) or scale <= 0.0:
            raise ValueError("Wilkinson component scales must be positive and finite")

    branch_length_m = _SPEED_OF_LIGHT_M_PER_S / frequency_hz / 4.0 * branch_velocity_factor
    nominal_branch_impedance_ohm = system_impedance_ohm * math.sqrt(port_count)
    first_splitter_node = port_count + 1
    star_center = first_splitter_node + port_count
    matching_node_start = star_center + 1
    matching_nodes = {
        output_index: matching_node_start + slot
        for slot, output_index in enumerate(
            index for index, network in enumerate(networks) if network is not None
        )
    }
    branches: list[NetworkBranch] = []
    for output_index in range(port_count):
        splitter_node = first_splitter_node + output_index
        branches.append(
            TransmissionLineBranch(
                node_a=0,
                node_b=splitter_node,
                characteristic_impedance_ohm=(
                    nominal_branch_impedance_ohm * branch_scales[output_index]
                ),
                length_m=branch_length_m,
                velocity_factor=branch_velocity_factor,
                matched_loss_db_per_100m=branch_loss_db_per_100m,
            )
        )
        branches.append(
            IsolationResistorBranch(
                node_a=splitter_node,
                node_b=star_center,
                resistance_ohm=system_impedance_ohm * resistor_scales[output_index],
                inductance_h=isolation_resistor_inductance_h,
                capacitance_f=isolation_resistor_capacitance_f,
            )
        )
        matching_node = matching_nodes.get(output_index)
        network = networks[output_index]
        feed_line_end = matching_node if matching_node is not None else output_index + 1
        branches.append(
            TransmissionLineBranch(
                node_a=splitter_node,
                node_b=feed_line_end,
                characteristic_impedance_ohm=system_impedance_ohm,
                length_m=feed_line_lengths_m[output_index],
                velocity_factor=velocity_factor,
            )
        )
        if matching_node is not None and network is not None:
            branches.append(
                TwoPortBranch(
                    node_a=matching_node,
                    node_b=output_index + 1,
                    network=network,
                )
            )
    # The star center has no connection to the reference, so its common mode
    # is arbitrary and the internal nodal matrix would be singular at the
    # equal-split frequency. A very high shunt regularizes that common mode
    # without changing the differential split.
    branches.append(
        ShuntBranch(
            node=star_center,
            impedance_ohm=complex(1e7, 0.0),
        )
    )
    return NPortNetwork(
        port_names=("input", *(f"output-{index + 1}" for index in range(port_count))),
        branches=tuple(branches),
        internal_node_count=port_count + 1 + len(matching_nodes),
    )
