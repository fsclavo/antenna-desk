# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import re

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.fingerprint import model_fingerprint


def _model(length_m: float = 20.0) -> AntennaModel:
    return DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=length_m,
        height_m=8.0,
    ).to_antenna()


def _spec() -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
    )


def test_fingerprint_is_deterministic() -> None:
    first = model_fingerprint(_model(), _spec())
    second = model_fingerprint(_model(), _spec())

    assert first == second
    assert re.fullmatch(r"[0-9a-f]{64}", first) is not None


def test_fingerprint_changes_with_model() -> None:
    assert model_fingerprint(_model(20.0), _spec()) != model_fingerprint(_model(19.5), _spec())


def test_fingerprint_changes_with_spec() -> None:
    first = model_fingerprint(_model(), _spec())
    changed = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_200_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        include_conductor_losses=False,
        far_field=FarFieldRequest(enabled=False),
    )
    assert first != model_fingerprint(_model(), changed)


def test_fingerprint_changes_with_conductor_loss_setting() -> None:
    first = model_fingerprint(_model(), _spec())
    changed = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        include_conductor_losses=True,
        far_field=FarFieldRequest(enabled=False),
    )
    assert first != model_fingerprint(_model(), changed)
