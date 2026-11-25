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

import math
from dataclasses import dataclass

from ..common.units import ensure_positive

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
    size = len(left)
    result = _zero_matrix(size)
    for row in range(size):
        for column in range(size):
            result[row][column] = sum(
                left[row][index] * right[index][column] for index in range(size)
            )
    return result


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

    def __post_init__(self) -> None:
        if self.node_a < 0 or self.node_b < 0 or self.node_a == self.node_b:
            raise ValueError("a transmission line needs two distinct non-negative nodes")
        ensure_positive(self.characteristic_impedance_ohm, name="characteristic_impedance_ohm")
        ensure_positive(self.length_m, name="length_m")
        ensure_positive(self.velocity_factor, name="velocity_factor")
        if self.velocity_factor > 1.0:
            raise ValueError("velocity_factor must not exceed 1")

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
        if abs(sin_theta) < 1e-9:
            # A half-wave line is a through connection with a phase reversal.
            # A tiny series impedance keeps the nodal matrix finite.
            series = 1.0 / complex(1e-6, 0.0)
            return (series, -series, -series, series)
        y0 = 1.0 / self.characteristic_impedance_ohm
        y11 = complex(0.0, -y0 / math.tan(theta))
        y12 = complex(0.0, y0 / sin_theta)
        return (y11, y12, y12, y11)


NetworkBranch = SeriesBranch | ShuntBranch | TransmissionLineBranch
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
            if isinstance(branch, TransmissionLineBranch):
                y11, y12, y21, y22 = branch.y_parameters(frequency_hz)
                a, b = branch.node_a, branch.node_b
                admittance[a][a] += y11
                admittance[a][b] += y12
                admittance[b][a] += y21
                admittance[b][b] += y22
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
) -> FeedNetworkSolution:
    """Connect an antenna admittance matrix to a feed network.

    The feed network's ``input_port_index`` is driven by an ideal current
    source; the remaining ports are connected to the antenna. ``antenna_admittance``
    has one row and column per antenna port and must match the other ports in
    order.
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

    port_order = [index for index in range(port_count) if index != input_port_index]
    admittance = network.y_matrix(frequency_hz)
    combined = [row[:] for row in admittance]
    for antenna_row, network_row in enumerate(port_order):
        for antenna_column, network_column in enumerate(port_order):
            combined[network_row][network_column] += antenna_admittance[antenna_row][antenna_column]

    current = [0.0 + 0.0j for _ in range(port_count)]
    current[input_port_index] = complex(source_current_a, 0.0)
    voltage = _solve(combined, current)
    input_voltage = voltage[input_port_index]
    input_current = current[input_port_index]
    input_power = 0.5 * (input_voltage * input_current.conjugate()).real
    antenna_voltages = [voltage[index] for index in port_order]
    antenna_currents = _matvec(antenna_admittance, antenna_voltages)
    antenna_powers = tuple(
        0.5 * (voltage_value * current_value.conjugate()).real
        for voltage_value, current_value in zip(antenna_voltages, antenna_currents, strict=True)
    )
    return FeedNetworkSolution(
        input_impedance_ohm=input_voltage / input_current,
        port_voltages_v=tuple(voltage),
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
