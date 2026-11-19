# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real NEC2C convergence ladders for representative wire models."""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path

import pytest

from antennadesk.application.use_cases.run_convergence_study import (
    RunConvergenceStudy,
    RunConvergenceStudyCommand,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.antennas.yagi import nbs_five_element
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.nec2.solver import Nec2cSolver

NEC2C = os.environ.get("NEC2C")
pytestmark = [
    pytest.mark.solver,
    pytest.mark.science,
    pytest.mark.skipif(
        not NEC2C or not Path(NEC2C).is_file(),
        reason="NEC2C must point to a nec2c executable",
    ),
]


def _dipole() -> AntennaModel:
    return DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    ).to_antenna()


def _vertical() -> AntennaModel:
    return VerticalParameters(
        frequency_hz=14_100_000.0,
        height_m=5.0,
        base_height_m=0.25,
        radial_count=4,
        radial_length_m=2.5,
    ).to_antenna()


def _yagi() -> AntennaModel:
    return nbs_five_element(
        frequency_hz=14_100_000.0,
        height_m=10.0,
    ).to_antenna()


def _custom() -> AntennaModel:
    return CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(
            Wire(
                id="wire",
                start=Point3D(-10.0, 0.0, 8.0),
                end=Point3D(10.0, 0.0, 8.0),
                radius_m=0.001,
                material=COPPER,
            ),
        ),
        feed=FeedPoint("wire", 10.0),
    ).to_antenna()


@pytest.mark.parametrize(
    "factory",
    [_dipole, _vertical, _yagi, _custom],
    ids=["dipole", "vertical-radials", "yagi", "custom"],
)
def test_convergence_ladder_runs_real_nec2c(
    factory: Callable[[], AntennaModel],
) -> None:
    assert NEC2C is not None
    model = factory()
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(model.design_frequency_hz),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        far_field=FarFieldRequest(enabled=False),
        include_conductor_losses=False,
    )

    result = RunConvergenceStudy(Nec2cSolver(Path(NEC2C))).execute(
        RunConvergenceStudyCommand(
            model=model,
            base_spec=spec,
            densities=(0.1, 0.05, 0.025),
        )
    )

    assert result.error is None
    assert len(result.points) == 3
    assert len(result.valid_points) == 3
    assert result.points[0].total_segments < result.points[-1].total_segments
    assert result.verdict.value in {"converged", "marginal", "not_converged"}
