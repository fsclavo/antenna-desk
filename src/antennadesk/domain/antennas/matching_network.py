# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Ideal L, Pi, and T matching networks evaluated at the antenna feedpoint."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from ..common.units import ensure_non_negative, ensure_positive
from .two_port import Abcd


class MatchingNetworkPosition(StrEnum):
    """Where the project matching network sits in the feed chain.

    ``SHACK`` places the tuner before the feed line, so the line sees the
    antenna impedance. ``FEEDPOINT`` places it after the line, which is the
    legacy behavior. ``NONE`` disables an otherwise defined network.
    """

    NONE = "none"
    FEEDPOINT = "feedpoint"
    SHACK = "shack"


class MatchingNetworkOrigin(StrEnum):
    """Which owner supplied the effective matching network.

    This is runtime context for diagnostics.  It is not persisted and does not
    participate in the model fingerprint.
    """

    NONE = "none"
    INTERNAL_ENDFED = "internal_endfed"
    DESIGN_ENDFED = "design_endfed"
    PROJECT = "project"


def _branch_impedance(
    inductance_h: float,
    capacitance_f: float,
    omega: float,
    q_factor: float | None,
) -> complex:
    impedance = complex(0.0, 0.0)
    if inductance_h:
        impedance += complex(0.0, omega * inductance_h)
        if q_factor is not None:
            impedance += omega * inductance_h / q_factor
    if capacitance_f:
        impedance += complex(0.0, -1.0 / (omega * capacitance_f))
        if q_factor is not None:
            impedance += 1.0 / (omega * capacitance_f * q_factor)
    return impedance


def _branch_admittance(
    inductance_h: float,
    capacitance_f: float,
    omega: float,
    q_factor: float | None,
) -> complex:
    if not _active(inductance_h, capacitance_f):
        return complex(0.0, 0.0)
    if q_factor is not None:
        return 1.0 / _branch_impedance(inductance_h, capacitance_f, omega, q_factor)
    admittance = complex(0.0, 0.0)
    if inductance_h:
        admittance += complex(0.0, -1.0 / (omega * inductance_h))
    if capacitance_f:
        admittance += complex(0.0, omega * capacitance_f)
    return admittance


def _validate_q(q_factor: float | None) -> None:
    if q_factor is not None:
        ensure_positive(q_factor, name="q_factor")


def _validate_branch(name: str, inductance_h: float, capacitance_f: float) -> None:
    ensure_non_negative(inductance_h, name=f"{name}_inductance_h")
    ensure_non_negative(capacitance_f, name=f"{name}_capacitance_f")
    if inductance_h > 0.0 and capacitance_f > 0.0:
        raise ValueError(f"{name} branch must use either L or C, not both")


def _active(inductance_h: float, capacitance_f: float) -> bool:
    return inductance_h > 0.0 or capacitance_f > 0.0


@dataclass(frozen=True, slots=True)
class LNetwork:
    """An L matching network with optional component loss.

    The series branch is between the antenna and the shunt branch.  When
    ``shunt_at_input`` is true the shunt branch is on the transmitter side;
    otherwise it is on the antenna side.
    """

    series_inductance_h: float = 0.0
    series_capacitance_f: float = 0.0
    shunt_inductance_h: float = 0.0
    shunt_capacitance_f: float = 0.0
    shunt_at_input: bool = False
    q_factor: float | None = None

    def __post_init__(self) -> None:
        _validate_q(self.q_factor)
        _validate_branch("series", self.series_inductance_h, self.series_capacitance_f)
        _validate_branch("shunt", self.shunt_inductance_h, self.shunt_capacitance_f)
        series = _active(self.series_inductance_h, self.series_capacitance_f)
        shunt = _active(self.shunt_inductance_h, self.shunt_capacitance_f)
        if series != shunt:
            raise ValueError("an L-network needs both a series and a shunt element")

    @property
    def is_active(self) -> bool:
        return _active(self.series_inductance_h, self.series_capacitance_f) or _active(
            self.shunt_inductance_h, self.shunt_capacitance_f
        )

    def input_impedance(self, load_impedance_ohm: complex, frequency_hz: float) -> complex:
        ensure_positive(frequency_hz, name="frequency_hz")
        if not self.is_active:
            return load_impedance_ohm
        omega = 2.0 * math.pi * frequency_hz
        series = _branch_impedance(
            self.series_inductance_h, self.series_capacitance_f, omega, self.q_factor
        )
        shunt = _branch_admittance(
            self.shunt_inductance_h, self.shunt_capacitance_f, omega, self.q_factor
        )
        if self.shunt_at_input:
            return 1.0 / (shunt + 1.0 / (series + load_impedance_ohm))
        return series + 1.0 / (shunt + 1.0 / load_impedance_ohm)

    def abcd(self, frequency_hz: float) -> Abcd:
        ensure_positive(frequency_hz, name="frequency_hz")
        omega = 2.0 * math.pi * frequency_hz
        series = Abcd.series(
            _branch_impedance(
                self.series_inductance_h,
                self.series_capacitance_f,
                omega,
                self.q_factor,
            )
        )
        shunt = Abcd.shunt(
            _branch_admittance(
                self.shunt_inductance_h,
                self.shunt_capacitance_f,
                omega,
                self.q_factor,
            )
        )
        return shunt @ series if self.shunt_at_input else series @ shunt


@dataclass(frozen=True, slots=True)
class PiNetwork:
    """A Pi network with optional component loss: input shunt, series, output shunt."""

    input_shunt_inductance_h: float = 0.0
    input_shunt_capacitance_f: float = 0.0
    series_inductance_h: float = 0.0
    series_capacitance_f: float = 0.0
    output_shunt_inductance_h: float = 0.0
    output_shunt_capacitance_f: float = 0.0
    q_factor: float | None = None

    def __post_init__(self) -> None:
        _validate_q(self.q_factor)
        _validate_branch(
            "input_shunt", self.input_shunt_inductance_h, self.input_shunt_capacitance_f
        )
        _validate_branch("series", self.series_inductance_h, self.series_capacitance_f)
        _validate_branch(
            "output_shunt", self.output_shunt_inductance_h, self.output_shunt_capacitance_f
        )
        if not any(
            _active(*pair)
            for pair in (
                (self.input_shunt_inductance_h, self.input_shunt_capacitance_f),
                (self.series_inductance_h, self.series_capacitance_f),
                (self.output_shunt_inductance_h, self.output_shunt_capacitance_f),
            )
        ):
            raise ValueError("a Pi network needs at least one non-zero element")

    @property
    def is_active(self) -> bool:
        return any(
            _active(*pair)
            for pair in (
                (self.input_shunt_inductance_h, self.input_shunt_capacitance_f),
                (self.series_inductance_h, self.series_capacitance_f),
                (self.output_shunt_inductance_h, self.output_shunt_capacitance_f),
            )
        )

    def input_impedance(self, load_impedance_ohm: complex, frequency_hz: float) -> complex:
        ensure_positive(frequency_hz, name="frequency_hz")
        if not self.is_active:
            return load_impedance_ohm
        omega = 2.0 * math.pi * frequency_hz
        output_shunt = _branch_admittance(
            self.output_shunt_inductance_h,
            self.output_shunt_capacitance_f,
            omega,
            self.q_factor,
        )
        series = _branch_impedance(
            self.series_inductance_h, self.series_capacitance_f, omega, self.q_factor
        )
        input_shunt = _branch_admittance(
            self.input_shunt_inductance_h,
            self.input_shunt_capacitance_f,
            omega,
            self.q_factor,
        )
        output_impedance = 1.0 / (output_shunt + 1.0 / load_impedance_ohm)
        return 1.0 / (input_shunt + 1.0 / (series + output_impedance))

    def abcd(self, frequency_hz: float) -> Abcd:
        ensure_positive(frequency_hz, name="frequency_hz")
        omega = 2.0 * math.pi * frequency_hz
        input_shunt = Abcd.shunt(
            _branch_admittance(
                self.input_shunt_inductance_h,
                self.input_shunt_capacitance_f,
                omega,
                self.q_factor,
            )
        )
        series = Abcd.series(
            _branch_impedance(
                self.series_inductance_h,
                self.series_capacitance_f,
                omega,
                self.q_factor,
            )
        )
        output_shunt = Abcd.shunt(
            _branch_admittance(
                self.output_shunt_inductance_h,
                self.output_shunt_capacitance_f,
                omega,
                self.q_factor,
            )
        )
        return input_shunt @ series @ output_shunt


@dataclass(frozen=True, slots=True)
class TNetwork:
    """A T network with optional component loss: input series, shunt, output series."""

    input_series_inductance_h: float = 0.0
    input_series_capacitance_f: float = 0.0
    shunt_inductance_h: float = 0.0
    shunt_capacitance_f: float = 0.0
    output_series_inductance_h: float = 0.0
    output_series_capacitance_f: float = 0.0
    q_factor: float | None = None

    def __post_init__(self) -> None:
        _validate_q(self.q_factor)
        _validate_branch(
            "input_series", self.input_series_inductance_h, self.input_series_capacitance_f
        )
        _validate_branch("shunt", self.shunt_inductance_h, self.shunt_capacitance_f)
        _validate_branch(
            "output_series", self.output_series_inductance_h, self.output_series_capacitance_f
        )
        if not any(
            _active(*pair)
            for pair in (
                (self.input_series_inductance_h, self.input_series_capacitance_f),
                (self.shunt_inductance_h, self.shunt_capacitance_f),
                (self.output_series_inductance_h, self.output_series_capacitance_f),
            )
        ):
            raise ValueError("a T network needs at least one non-zero element")

    @property
    def is_active(self) -> bool:
        return any(
            _active(*pair)
            for pair in (
                (self.input_series_inductance_h, self.input_series_capacitance_f),
                (self.shunt_inductance_h, self.shunt_capacitance_f),
                (self.output_series_inductance_h, self.output_series_capacitance_f),
            )
        )

    def input_impedance(self, load_impedance_ohm: complex, frequency_hz: float) -> complex:
        ensure_positive(frequency_hz, name="frequency_hz")
        if not self.is_active:
            return load_impedance_ohm
        omega = 2.0 * math.pi * frequency_hz
        output_series = _branch_impedance(
            self.output_series_inductance_h,
            self.output_series_capacitance_f,
            omega,
            self.q_factor,
        )
        shunt = _branch_admittance(
            self.shunt_inductance_h, self.shunt_capacitance_f, omega, self.q_factor
        )
        input_series = _branch_impedance(
            self.input_series_inductance_h,
            self.input_series_capacitance_f,
            omega,
            self.q_factor,
        )
        return input_series + 1.0 / (shunt + 1.0 / (output_series + load_impedance_ohm))

    def abcd(self, frequency_hz: float) -> Abcd:
        ensure_positive(frequency_hz, name="frequency_hz")
        omega = 2.0 * math.pi * frequency_hz
        input_series = Abcd.series(
            _branch_impedance(
                self.input_series_inductance_h,
                self.input_series_capacitance_f,
                omega,
                self.q_factor,
            )
        )
        shunt = Abcd.shunt(
            _branch_admittance(
                self.shunt_inductance_h,
                self.shunt_capacitance_f,
                omega,
                self.q_factor,
            )
        )
        output_series = Abcd.series(
            _branch_impedance(
                self.output_series_inductance_h,
                self.output_series_capacitance_f,
                omega,
                self.q_factor,
            )
        )
        return input_series @ shunt @ output_series


@dataclass(frozen=True, slots=True)
class TransformerNetwork:
    """Primary-referred transformer parasitics and matching elements.

    The ideal impedance ratio is applied before this network.  This block
    models the primary leakage inductance in series with a shunt combination
    of the external matching capacitor, the secondary winding capacitance
    referred to the primary, and the magnetizing inductance.
    """

    series_inductance_h: float = 0.0
    input_shunt_capacitance_f: float = 0.0
    input_shunt_inductance_h: float = 0.0

    def __post_init__(self) -> None:
        ensure_non_negative(self.series_inductance_h, name="series_inductance_h")
        ensure_non_negative(
            self.input_shunt_capacitance_f,
            name="input_shunt_capacitance_f",
        )
        ensure_non_negative(
            self.input_shunt_inductance_h,
            name="input_shunt_inductance_h",
        )
        if not self.is_active:
            raise ValueError("a transformer network needs at least one non-zero element")

    @property
    def is_active(self) -> bool:
        return (
            self.series_inductance_h > 0.0
            or self.input_shunt_capacitance_f > 0.0
            or self.input_shunt_inductance_h > 0.0
        )

    def _shunt_admittance(self, omega: float) -> complex:
        admittance = complex(0.0, 0.0)
        if self.input_shunt_capacitance_f:
            admittance += complex(0.0, omega * self.input_shunt_capacitance_f)
        if self.input_shunt_inductance_h:
            admittance += complex(0.0, -1.0 / (omega * self.input_shunt_inductance_h))
        return admittance

    def input_impedance(self, load_impedance_ohm: complex, frequency_hz: float) -> complex:
        ensure_positive(frequency_hz, name="frequency_hz")
        omega = 2.0 * math.pi * frequency_hz
        series = complex(0.0, omega * self.series_inductance_h)
        return 1.0 / (self._shunt_admittance(omega) + 1.0 / (series + load_impedance_ohm))

    def abcd(self, frequency_hz: float) -> Abcd:
        ensure_positive(frequency_hz, name="frequency_hz")
        omega = 2.0 * math.pi * frequency_hz
        return Abcd.shunt(self._shunt_admittance(omega)) @ Abcd.series(
            complex(0.0, omega * self.series_inductance_h)
        )


MatchingNetwork = LNetwork | PiNetwork | TNetwork | TransformerNetwork


def input_shunt_l_network_swr_floor(
    network: MatchingNetwork,
    load_impedance_ohm: complex,
    source_impedance_ohm: float,
) -> float | None:
    """Return the SWR floor for an input-shunt L-section that cannot match.

    The series branch sits between the load and a shunt branch on the source
    side.  The real part of the input admittance is
    ``R / (R**2 + (X + Xs)**2)``, whose maximum is ``1 / R``.  Matching a
    source resistance therefore requires ``R <= source``.  When the load
    resistance is higher, even ideal lossless reactances cannot reach a
    conjugate match and the best possible SWR is ``R / source``.  Return
    ``None`` when the network is not an input-shunt L-section or when the load
    resistance is at or below the source resistance.
    """

    ensure_positive(source_impedance_ohm, name="source_impedance_ohm")
    if isinstance(network, LNetwork):
        if not network.shunt_at_input:
            return None
        shunt_active = _active(network.shunt_inductance_h, network.shunt_capacitance_f)
        series_active = _active(network.series_inductance_h, network.series_capacitance_f)
    elif isinstance(network, PiNetwork):
        if _active(
            network.output_shunt_inductance_h,
            network.output_shunt_capacitance_f,
        ):
            return None
        shunt_active = _active(
            network.input_shunt_inductance_h,
            network.input_shunt_capacitance_f,
        )
        series_active = _active(network.series_inductance_h, network.series_capacitance_f)
    else:
        return None
    if not shunt_active or not series_active:
        return None
    resistance = load_impedance_ohm.real
    if resistance <= 0.0 or resistance <= source_impedance_ohm:
        return None
    return resistance / source_impedance_ohm


def design_l_network(
    load_impedance_ohm: complex,
    frequency_hz: float,
    *,
    source_impedance_ohm: float = 50.0,
) -> LNetwork | None:
    """Return a lossless L-network matching the load to a real source."""

    ensure_positive(frequency_hz, name="frequency_hz")
    ensure_positive(source_impedance_ohm, name="source_impedance_ohm")
    r_load = load_impedance_ohm.real
    x_load = load_impedance_ohm.imag
    if r_load <= 0.0:
        return None
    if abs(load_impedance_ohm - source_impedance_ohm) < 1e-9:
        return None
    omega = 2.0 * math.pi * frequency_hz

    def components(
        series_reactance: float,
        shunt_susceptance: float,
        at_input: bool,
    ) -> LNetwork | None:
        series_l = max(series_reactance, 0.0) / omega
        series_c = max(-series_reactance, 0.0) / omega
        shunt_c = max(shunt_susceptance, 0.0) / omega
        shunt_l = max(-shunt_susceptance, 0.0) / omega
        if (series_l == 0.0 and series_c == 0.0) or (shunt_l == 0.0 and shunt_c == 0.0):
            return None
        return LNetwork(
            series_inductance_h=series_l,
            series_capacitance_f=series_c,
            shunt_inductance_h=shunt_l,
            shunt_capacitance_f=shunt_c,
            shunt_at_input=at_input,
        )

    if r_load <= source_impedance_ohm:
        root = math.sqrt(max(r_load * (source_impedance_ohm - r_load), 0.0))
        network = components(
            root - x_load,
            root / (r_load * source_impedance_ohm),
            True,
        )
        if network is not None:
            return network

    admittance = 1.0 / load_impedance_ohm
    conductance = admittance.real
    susceptance = admittance.imag
    if conductance <= 1.0 / source_impedance_ohm:
        root = math.sqrt(max(conductance * (1.0 / source_impedance_ohm - conductance), 0.0))
        network = components(
            root * source_impedance_ohm / conductance,
            root - susceptance,
            False,
        )
        if network is not None:
            return network
    return None


def _minimum_loaded_q(resistance_a_ohm: float, resistance_b_ohm: float) -> float:
    high = max(resistance_a_ohm, resistance_b_ohm)
    low = min(resistance_a_ohm, resistance_b_ohm)
    if low <= 0.0:
        return math.inf
    return math.sqrt(max(high / low - 1.0, 0.0))


def _bisect_virtual_resistance(
    function: Callable[[float], float],
    lower: float,
    upper: float,
) -> float:
    """Find the single root of a monotonic loaded-Q equation."""

    value_lower = function(lower)
    value_upper = function(upper)
    if value_lower == 0.0:
        return lower
    if value_upper == 0.0:
        return upper
    if value_lower * value_upper > 0.0:
        raise ValueError("the loaded-Q equation has no root in the interval")
    for _ in range(200):
        midpoint = (lower + upper) / 2.0
        value_midpoint = function(midpoint)
        if abs(value_midpoint) < 1e-12 or upper - lower <= 1e-12 * max(1.0, abs(midpoint)):
            return midpoint
        if value_lower * value_midpoint <= 0.0:
            upper = midpoint
            value_upper = value_midpoint
        else:
            lower = midpoint
            value_lower = value_midpoint
    return (lower + upper) / 2.0


def _loaded_q_for_design(
    loaded_q: float | None,
    minimum_loaded_q: float,
) -> float | None:
    if loaded_q is None or loaded_q <= 0.0:
        return max(2.0, minimum_loaded_q * 1.5)
    if loaded_q <= minimum_loaded_q + 1e-9:
        return None
    return loaded_q


def design_pi_network(
    load_impedance_ohm: complex,
    frequency_hz: float,
    *,
    source_impedance_ohm: float = 50.0,
    loaded_q: float | None = None,
) -> PiNetwork | None:
    """Return a lossless Pi network matching the load to a real source.

    ``loaded_q`` is the total design Q (the sum of the input and output
    L-section Q values). A value of ``None`` or ``0`` selects a starting Q of
    ``max(2, 1.5 x Q_min)``. A requested Q below ``Q_min`` has no physical
    solution and returns ``None``. The design uses the low-pass branch signs
    (shunt capacitors and a series inductor) when the load permits them; a
    complex load can move an individual branch to the opposite sign.
    """

    ensure_positive(frequency_hz, name="frequency_hz")
    ensure_positive(source_impedance_ohm, name="source_impedance_ohm")
    if loaded_q is not None:
        ensure_non_negative(loaded_q, name="loaded_q")
    resistance = load_impedance_ohm.real
    if resistance <= 0.0:
        return None
    admittance = 1.0 / load_impedance_ohm
    conductance = admittance.real
    if conductance <= 0.0:
        return None
    effective_resistance = 1.0 / conductance
    minimum_q = _minimum_loaded_q(source_impedance_ohm, effective_resistance)
    selected_q = _loaded_q_for_design(loaded_q, minimum_q)
    if selected_q is None:
        return None

    lower_resistance = min(source_impedance_ohm, effective_resistance)
    lower = lower_resistance * 1e-12
    upper = lower_resistance * (1.0 - 1e-12)

    def equation(virtual_resistance: float) -> float:
        return (
            math.sqrt(source_impedance_ohm / virtual_resistance - 1.0)
            + math.sqrt(effective_resistance / virtual_resistance - 1.0)
            - selected_q
        )

    try:
        virtual_resistance = _bisect_virtual_resistance(equation, lower, upper)
    except ValueError:
        return None
    input_q = math.sqrt(source_impedance_ohm / virtual_resistance - 1.0)
    input_susceptance = input_q / source_impedance_ohm
    output_susceptance = math.sqrt(max(conductance * (1.0 / virtual_resistance - conductance), 0.0))
    load_susceptance = admittance.imag
    input_series_reactance = input_q * virtual_resistance
    output_series_reactance = output_susceptance * virtual_resistance / conductance
    series_reactance = input_series_reactance + output_series_reactance
    output_shunt_susceptance = output_susceptance - load_susceptance
    omega = 2.0 * math.pi * frequency_hz
    network = PiNetwork(
        input_shunt_inductance_h=max(-input_susceptance, 0.0) / omega,
        input_shunt_capacitance_f=max(input_susceptance, 0.0) / omega,
        series_inductance_h=max(series_reactance, 0.0) / omega,
        series_capacitance_f=max(-series_reactance, 0.0) / omega,
        output_shunt_inductance_h=max(-output_shunt_susceptance, 0.0) / omega,
        output_shunt_capacitance_f=max(output_shunt_susceptance, 0.0) / omega,
    )
    matched = network.input_impedance(load_impedance_ohm, frequency_hz)
    if abs(matched - source_impedance_ohm) > max(1e-6, source_impedance_ohm * 1e-6):
        return None
    return network


def design_t_network(
    load_impedance_ohm: complex,
    frequency_hz: float,
    *,
    source_impedance_ohm: float = 50.0,
    loaded_q: float | None = None,
) -> TNetwork | None:
    """Return a lossless T network matching the load to a real source.

    ``loaded_q`` has the same meaning as in :func:`design_pi_network`. The
    design uses series inductors and a shunt capacitor when the load permits
    them; a complex load can move an individual branch to the opposite sign.
    """

    ensure_positive(frequency_hz, name="frequency_hz")
    ensure_positive(source_impedance_ohm, name="source_impedance_ohm")
    if loaded_q is not None:
        ensure_non_negative(loaded_q, name="loaded_q")
    resistance = load_impedance_ohm.real
    reactance = load_impedance_ohm.imag
    if resistance <= 0.0:
        return None
    minimum_q = _minimum_loaded_q(source_impedance_ohm, resistance)
    selected_q = _loaded_q_for_design(loaded_q, minimum_q)
    if selected_q is None:
        return None

    highest_resistance = max(source_impedance_ohm, resistance)

    def equation(virtual_resistance: float) -> float:
        return (
            math.sqrt(virtual_resistance / source_impedance_ohm - 1.0)
            + math.sqrt(virtual_resistance / resistance - 1.0)
            - selected_q
        )

    lower = highest_resistance * (1.0 + 1e-12)
    upper = highest_resistance * 2.0
    while equation(upper) < 0.0 and upper < highest_resistance * 1e12:
        upper *= 2.0
    try:
        virtual_resistance = _bisect_virtual_resistance(equation, lower, upper)
    except ValueError:
        return None
    input_q = math.sqrt(virtual_resistance / source_impedance_ohm - 1.0)
    input_series_reactance = input_q * source_impedance_ohm
    output_series_reactance_base = math.sqrt(
        max(resistance * virtual_resistance - resistance * resistance, 0.0)
    )
    output_series_reactance = output_series_reactance_base - reactance
    output_shunt_susceptance = output_series_reactance_base / (resistance * virtual_resistance)
    input_shunt_susceptance = input_q / virtual_resistance
    shunt_susceptance = input_shunt_susceptance + output_shunt_susceptance
    omega = 2.0 * math.pi * frequency_hz
    network = TNetwork(
        input_series_inductance_h=max(input_series_reactance, 0.0) / omega,
        input_series_capacitance_f=max(-input_series_reactance, 0.0) / omega,
        shunt_inductance_h=max(-shunt_susceptance, 0.0) / omega,
        shunt_capacitance_f=max(shunt_susceptance, 0.0) / omega,
        output_series_inductance_h=max(output_series_reactance, 0.0) / omega,
        output_series_capacitance_f=max(-output_series_reactance, 0.0) / omega,
    )
    matched = network.input_impedance(load_impedance_ohm, frequency_hz)
    if abs(matched - source_impedance_ohm) > max(1e-6, source_impedance_ohm * 1e-6):
        return None
    return network
