# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Ideal L, Pi, and T matching networks evaluated at the antenna feedpoint."""

from __future__ import annotations

import math
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


MatchingNetwork = LNetwork | PiNetwork | TNetwork


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
