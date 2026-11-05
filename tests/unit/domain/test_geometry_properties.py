# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Property-based checks for the canonical geometry invariants.

The estimators are the main entry point for new geometry, so every supported
family must produce a model that satisfies the same structural contract:
finite coordinates, non-zero wires, unique IDs, a feed point on a real wire,
and no model-level errors.
"""

from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleOrientation
from antennadesk.domain.antennas.polarization import Polarization
from antennadesk.domain.common.validation import Severity
from antennadesk.domain.design import (
    DesignIntent,
    LoopShape,
    VerticalForm,
    estimate_intent,
)
from antennadesk.domain.design.estimators import SUPPORTED_ESTIMATOR_TYPES
from antennadesk.domain.environment.ground import GroundModel

FREQUENCY_HZ = st.floats(
    min_value=1_800_000.0,
    max_value=450_000_000.0,
    allow_nan=False,
    allow_infinity=False,
)
HF_FREQUENCY_HZ = st.floats(
    min_value=1_800_000.0,
    max_value=30_000_000.0,
    allow_nan=False,
    allow_infinity=False,
)
HEIGHT_M = st.floats(
    min_value=0.0,
    max_value=40.0,
    allow_nan=False,
    allow_infinity=False,
)
RADIUS_M = st.floats(
    min_value=1e-4,
    max_value=1e-2,
    allow_nan=False,
    allow_infinity=False,
)
AZIMUTH_DEG = st.floats(
    min_value=-720.0,
    max_value=720.0,
    allow_nan=False,
    allow_infinity=False,
)
INCLUDED_ANGLE_DEG = st.floats(
    min_value=20.0,
    max_value=170.0,
    allow_nan=False,
    allow_infinity=False,
)
GROUND = st.one_of(
    st.just(GroundModel.free_space()),
    st.just(GroundModel.perfect()),
    st.builds(
        GroundModel.finite,
        relative_permittivity=st.floats(
            min_value=1.0,
            max_value=80.0,
            allow_nan=False,
            allow_infinity=False,
        ),
        conductivity_s_per_m=st.floats(
            min_value=1e-5,
            max_value=1e-1,
            allow_nan=False,
            allow_infinity=False,
        ),
    ),
)


def _assert_valid_model(model: AntennaModel) -> None:
    assert model.wires
    ids = [wire.id for wire in model.wires]
    assert len(set(ids)) == len(ids)
    for wire in model.wires:
        assert wire.length_m > 0.0
        for point in (wire.start, wire.end):
            assert math.isfinite(point.x_m)
            assert math.isfinite(point.y_m)
            assert math.isfinite(point.z_m)
    assert model.feed.wire_id in ids
    feed_wire = model.wire_by_id(model.feed.wire_id)
    assert 0.0 <= model.feed.offset_m <= feed_wire.length_m
    errors = [
        diagnostic for diagnostic in model.validate() if diagnostic.severity is Severity.ERROR
    ]
    assert not errors


@pytest.mark.parametrize("family", sorted(SUPPORTED_ESTIMATOR_TYPES))
@settings(max_examples=50, deadline=None)
@given(data=st.data())
def test_estimated_family_geometry_satisfies_model_invariants(
    family: str,
    data: st.DataObject,
) -> None:
    if family == "fan_dipole":
        frequency_hz = data.draw(HF_FREQUENCY_HZ)
        fan_bands = tuple(sorted({frequency_hz, frequency_hz * 1.5, frequency_hz * 2.0}))
    else:
        frequency_hz = data.draw(FREQUENCY_HZ)
        fan_bands = ()

    polarization = data.draw(st.sampled_from(list(Polarization)))
    if family in {"moxon", "yagi"} and polarization is Polarization.VERTICAL:
        # Vertical arrays need a height above half the longest element; the
        # dedicated rejection tests cover the invalid case.
        height_m = data.draw(
            st.floats(
                min_value=50.0,
                max_value=80.0,
                allow_nan=False,
                allow_infinity=False,
            )
        )
    else:
        height_m = data.draw(HEIGHT_M)

    intent = DesignIntent(
        frequency_hz=frequency_hz,
        antenna_type=family,
        height_m=height_m,
        base_height_m=data.draw(
            st.floats(
                min_value=0.01,
                max_value=5.0,
                allow_nan=False,
                allow_infinity=False,
            )
        ),
        orientation=data.draw(st.sampled_from(list(DipoleOrientation))),
        polarization=polarization,
        azimuth_deg=data.draw(AZIMUTH_DEG),
        wire_radius_m=data.draw(RADIUS_M),
        ground=data.draw(GROUND),
        loop_shape=data.draw(st.sampled_from(list(LoopShape))),
        vertical_form=data.draw(st.sampled_from(list(VerticalForm))),
        folded=data.draw(st.booleans()),
        included_angle_deg=data.draw(INCLUDED_ANGLE_DEG),
        radial_count=data.draw(st.integers(min_value=0, max_value=12)),
        gap_m=data.draw(
            st.floats(
                min_value=1e-3,
                max_value=0.1,
                allow_nan=False,
                allow_infinity=False,
            )
        ),
        fan_bands_hz=fan_bands,
        yagi_elements=data.draw(st.integers(min_value=2, max_value=12)),
        end_height_m=None,
        highest_frequency_hz=(
            frequency_hz
            * data.draw(
                st.floats(
                    min_value=1.5,
                    max_value=10.0,
                    allow_nan=False,
                    allow_infinity=False,
                )
            )
            if family == "t2fd"
            else None
        ),
    )

    estimate = estimate_intent(intent)
    model = estimate.parameters.to_antenna()

    _assert_valid_model(model)
    assert model == estimate.parameters.to_antenna()
