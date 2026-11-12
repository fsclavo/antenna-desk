# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Common comparison basis and height mapping."""

from __future__ import annotations

from uuid import uuid4

import pytest

from antennadesk.domain.antennas.design import antenna_type_for
from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.design.comparison import (
    ComparisonBasis,
    apply_comparison_basis,
    native_height_m,
)
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.projects.project import DesignVariant
from antennadesk.domain.simulation.frequency import FrequencyPlan

AVERAGE_GROUND = GroundModel.finite(
    relative_permittivity=13.0,
    conductivity_s_per_m=0.005,
)


def _basis(
    *,
    reference_height_m: float | None = 12.0,
) -> ComparisonBasis:
    return ComparisonBasis(
        frequency_plan=FrequencyPlan.sweep(7_000_000.0, 7_300_000.0, 31),
        ground=AVERAGE_GROUND,
        reference_height_m=reference_height_m,
        reference_frequency_hz=7_100_000.0,
    )


def _design(parameters: object) -> DesignVariant:
    return DesignVariant(
        id=uuid4(),
        name="Test",
        antenna_type=antenna_type_for(parameters),  # type: ignore[arg-type]
        parameters=parameters,  # type: ignore[arg-type]
        antenna=parameters.to_antenna(name="Test"),  # type: ignore[attr-defined]
    )


def test_basis_rejects_a_reference_frequency_outside_the_plan() -> None:
    with pytest.raises(ValueError, match="inside"):
        ComparisonBasis(
            frequency_plan=FrequencyPlan.sweep(7_000_000.0, 7_300_000.0, 31),
            ground=AVERAGE_GROUND,
            reference_height_m=10.0,
            reference_frequency_hz=14_100_000.0,
        )


def test_direct_height_family_is_moved_and_ground_is_replaced(
    dipole_parameters,  # type: ignore[no-untyped-def]
) -> None:
    design = _design(dipole_parameters)
    application = apply_comparison_basis(design, _basis())

    assert application.height_mapped is True
    assert application.warnings == ()
    assert application.design.parameters.height_m == 12.0  # type: ignore[attr-defined]
    assert application.design.parameters.ground == AVERAGE_GROUND  # type: ignore[attr-defined]


def test_vertical_family_maps_the_top_height_to_the_base() -> None:
    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=0.0,
    )
    application = apply_comparison_basis(_design(parameters), _basis(reference_height_m=15.0))

    assert application.height_mapped is True
    assert application.design.parameters.base_height_m == pytest.approx(5.0)  # type: ignore[attr-defined]
    assert application.design.parameters.height_m == pytest.approx(10.0)  # type: ignore[attr-defined]


def test_vertical_reference_below_the_radiator_keeps_native_height() -> None:
    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=0.0,
    )
    application = apply_comparison_basis(_design(parameters), _basis(reference_height_m=6.0))

    assert application.height_mapped is False
    assert application.warnings == ("height_too_low",)


def test_inverted_v_reference_below_the_end_height_is_rejected_cleanly() -> None:
    parameters = InvertedVParameters(
        frequency_hz=7_100_000.0,
        leg_length_m=10.0,
        apex_height_m=10.0,
        included_angle_deg=120.0,
    )
    application = apply_comparison_basis(_design(parameters), _basis(reference_height_m=4.0))

    assert application.height_mapped is False
    assert application.warnings == ("height_too_low",)


def test_ambiguous_family_keeps_native_height_with_a_warning() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=10.0,
    )
    application = apply_comparison_basis(_design(parameters), _basis())

    assert application.height_mapped is False
    assert application.warnings == ("height_mapping_unavailable",)


def test_native_height_mode_only_changes_the_ground(dipole_parameters) -> None:  # type: ignore[no-untyped-def]
    design = _design(dipole_parameters)
    application = apply_comparison_basis(
        design,
        _basis(reference_height_m=None),
    )

    assert application.height_mapped is False
    assert application.warnings == ("native_height",)
    assert application.design.parameters.height_m == dipole_parameters.height_m  # type: ignore[attr-defined]
    assert application.design.parameters.ground == AVERAGE_GROUND  # type: ignore[attr-defined]


def test_native_height_helper_covers_direct_and_vertical_families(
    dipole_parameters,  # type: ignore[no-untyped-def]
) -> None:
    vertical = VerticalParameters(frequency_hz=7_100_000.0, height_m=10.0, base_height_m=1.0)

    assert native_height_m(dipole_parameters) == dipole_parameters.height_m
    assert native_height_m(vertical) == pytest.approx(11.0)
