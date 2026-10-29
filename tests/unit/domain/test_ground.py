from __future__ import annotations

import pytest

from antennadesk.domain.environment.environment import Environment
from antennadesk.domain.environment.ground import (
    FREE_SPACE,
    PERFECT_GROUND,
    GroundKind,
    GroundModel,
)


def test_free_space_and_perfect_ground() -> None:
    assert FREE_SPACE.kind is GroundKind.FREE_SPACE
    assert FREE_SPACE.relative_permittivity is None
    assert PERFECT_GROUND.kind is GroundKind.PERFECT


def test_finite_ground() -> None:
    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    assert ground.kind is GroundKind.FINITE
    assert ground.is_finite is True
    assert ground.relative_permittivity == pytest.approx(13.0)
    assert ground.conductivity_s_per_m == pytest.approx(0.005)


def test_finite_ground_requires_parameters() -> None:
    with pytest.raises(ValueError, match="requires"):
        GroundModel(kind=GroundKind.FINITE)


def test_free_space_rejects_parameters() -> None:
    with pytest.raises(ValueError, match="does not accept"):
        GroundModel(
            kind=GroundKind.FREE_SPACE,
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        )


def test_relative_permittivity_must_be_at_least_one() -> None:
    with pytest.raises(ValueError, match="greater than or equal to 1"):
        GroundModel.finite(relative_permittivity=0.5, conductivity_s_per_m=0.005)


def test_conductivity_must_be_positive() -> None:
    with pytest.raises(ValueError, match="positive"):
        GroundModel.finite(relative_permittivity=13.0, conductivity_s_per_m=0.0)


def test_environment_can_replace_ground() -> None:
    ground = GroundModel.perfect()
    environment = Environment().with_ground(ground)
    assert environment.ground == ground
