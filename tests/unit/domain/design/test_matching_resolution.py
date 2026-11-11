# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Matching-network precedence between internal EFHW and project networks."""

from __future__ import annotations

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.matching_network import LNetwork
from antennadesk.domain.design.matching_resolution import resolve_matching_network


def _endfed(*, internal: bool) -> EndFedParameters:
    return EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        matching_capacitance_f=100e-12 if internal else 0.0,
        transformer_leakage_inductance_h=0.198e-6 if internal else 0.0,
    )


def _project() -> LNetwork:
    return LNetwork(
        series_inductance_h=1e-6,
        shunt_capacitance_f=100e-12,
    )


def test_internal_matching_is_effective_without_a_project_network() -> None:
    resolution = resolve_matching_network(_endfed(internal=True), None)

    assert resolution.internal is not None
    assert resolution.project is None
    assert resolution.effective is resolution.internal
    assert resolution.override_active is False
    assert resolution.project_active is False


def test_project_network_overrides_active_internal_matching() -> None:
    project = _project()

    resolution = resolve_matching_network(_endfed(internal=True), project)

    assert resolution.internal is not None
    assert resolution.project is project
    assert resolution.effective is project
    assert resolution.override_active is True
    assert resolution.project_active is True


def test_project_network_is_used_when_the_internal_matching_is_inactive() -> None:
    project = _project()

    resolution = resolve_matching_network(_endfed(internal=False), project)

    assert resolution.internal is None
    assert resolution.project is project
    assert resolution.effective is project
    assert resolution.override_active is False
    assert resolution.project_active is True


def test_inactive_project_network_keeps_the_internal_matching() -> None:
    inactive = LNetwork()

    resolution = resolve_matching_network(_endfed(internal=True), inactive)

    assert resolution.project is inactive
    assert resolution.effective is resolution.internal
    assert resolution.override_active is False
    assert resolution.project_active is False


def test_non_endfed_design_uses_the_project_network_without_an_override() -> None:
    project = _project()
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )

    resolution = resolve_matching_network(parameters, project)

    assert resolution.internal is None
    assert resolution.effective is project
    assert resolution.override_active is False
