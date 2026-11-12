# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Default optimizer scope for installation context and feed placement."""

from __future__ import annotations

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.endfed import EndFedParameters, EndFedPreset
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.scv import ScvKind, scv_parameters
from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.optimization.variables import (
    OptimizationVariable,
    apply_default_locks,
)

CONTEXT_NAMES = (
    "total_length_m",
    "height_m",
    "apex_height_m",
    "base_height_m",
    "feed_height_m",
    "end_height_m",
    "counterpoise_height_m",
    "feed_ratio",
    "feed_offset_m",
    "transformer_ratio",
    "wire_radius_m",
    "ring_height_m",
    "phase_step_deg",
)

EXPECTED_LOCKED = {
    "height_m",
    "apex_height_m",
    "base_height_m",
    "feed_height_m",
    "end_height_m",
    "counterpoise_height_m",
    "feed_ratio",
    "feed_offset_m",
    "transformer_ratio",
    "wire_radius_m",
    "ring_height_m",
}


def _locked_names(parameters: object) -> set[str]:
    availability = optimizer_availability(parameters)  # type: ignore[arg-type]
    assert availability.descriptor is not None
    return {
        variable.name
        for variable in availability.descriptor.variables
        if variable.locked_by_default
    }


def test_default_lock_policy_covers_context_and_exempts_radiator_height() -> None:
    variables = tuple(
        OptimizationVariable(name, "label", "group", 0.0, 1.0) for name in CONTEXT_NAMES
    )

    locked = {
        variable.name
        for variable in apply_default_locks("ocfd", variables)
        if variable.locked_by_default
    }
    vertical_locked = {
        variable.name
        for variable in apply_default_locks("vertical", variables)
        if variable.locked_by_default
    }

    assert locked == EXPECTED_LOCKED
    assert vertical_locked == EXPECTED_LOCKED - {"height_m"}
    assert "phase_step_deg" not in locked
    assert "total_length_m" not in locked


@pytest.mark.parametrize(
    ("parameters", "expected"),
    [
        (
            DipoleParameters(frequency_hz=7_100_000.0, total_length_m=20.0, height_m=8.0),
            {"height_m", "wire_radius_m"},
        ),
        (
            OCFDParameters(frequency_hz=7_100_000.0, total_length_m=20.4, height_m=10.0),
            {"feed_ratio", "height_m", "wire_radius_m", "transformer_ratio"},
        ),
        (
            VerticalParameters(frequency_hz=14_100_000.0, height_m=5.0),
            {"base_height_m", "wire_radius_m"},
        ),
        (
            EndFedParameters(
                frequency_hz=7_100_000.0,
                length_m=12.0,
                transformer_ratio=49.0,
                preset=EndFedPreset.SHORTENED_40_10,
            ),
            {"feed_height_m", "end_height_m", "wire_radius_m", "transformer_ratio"},
        ),
        (
            TrapDipoleParameters(
                frequency_hz=7_100_000.0,
                high_band_frequency_hz=14_100_000.0,
                inner_length_m=10.0,
                outer_length_m=5.0,
                trap_frequency_hz=14_100_000.0,
                trap_inductance_h=10e-6,
                height_m=12.0,
            ),
            {"height_m", "wire_radius_m"},
        ),
        (
            T2FDParameters(
                frequency_hz=1_800_000.0,
                highest_frequency_hz=30_000_000.0,
                length_m=50.8,
                spacing_m=1.69,
            ),
            {"height_m", "transformer_ratio", "wire_radius_m"},
        ),
        (
            LoopParameters(
                frequency_hz=7_100_000.0,
                circumference_m=21.5,
                height_m=2.0,
            ),
            {"height_m", "transformer_ratio", "wire_radius_m"},
        ),
        (
            scv_parameters(ScvKind.HALF_SQUARE, 7_150_000.0),
            {"base_height_m", "feed_offset_m", "wire_radius_m"},
        ),
    ],
    ids=[
        "dipole",
        "ocfd",
        "vertical",
        "endfed-shortened",
        "trap-dipole",
        "t2fd",
        "loop",
        "half-square",
    ],
)
def test_descriptor_defaults_lock_context_variables(parameters: object, expected: set[str]) -> None:
    assert _locked_names(parameters) == expected


@pytest.mark.parametrize(
    ("parameters", "unlocked"),
    [
        (
            OCFDParameters(frequency_hz=7_100_000.0, total_length_m=20.4, height_m=10.0),
            {"total_length_m"},
        ),
        (
            VerticalParameters(frequency_hz=14_100_000.0, height_m=5.0),
            {"height_m"},
        ),
        (
            EndFedParameters(
                frequency_hz=7_100_000.0,
                length_m=12.0,
                transformer_ratio=49.0,
                preset=EndFedPreset.SHORTENED_40_10,
            ),
            {"length_m"},
        ),
        (
            TrapDipoleParameters(
                frequency_hz=7_100_000.0,
                high_band_frequency_hz=14_100_000.0,
                inner_length_m=10.0,
                outer_length_m=5.0,
                trap_frequency_hz=14_100_000.0,
                trap_inductance_h=10e-6,
                height_m=12.0,
            ),
            {"inner_length_m", "outer_length_m"},
        ),
    ],
    ids=["ocfd", "vertical", "endfed-shortened", "trap-dipole"],
)
def test_core_geometry_remains_enabled_by_default(
    parameters: object,
    unlocked: set[str],
) -> None:
    availability = optimizer_availability(parameters)  # type: ignore[arg-type]
    assert availability.descriptor is not None
    enabled = {
        variable.name
        for variable in availability.descriptor.variables
        if not variable.locked_by_default
    }

    assert unlocked <= enabled
