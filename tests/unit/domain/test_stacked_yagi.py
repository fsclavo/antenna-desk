# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Stacked-Yagi domain prototype tests."""

from __future__ import annotations

from dataclasses import replace

import pytest

from antennadesk.domain.antennas.stacked_yagi import StackedYagiParameters
from antennadesk.domain.antennas.yagi import nbs_five_element


def test_two_level_stack_duplicates_wires_and_adds_a_source() -> None:
    yagi = nbs_five_element(frequency_hz=50_100_000.0, height_m=8.0)
    stack = StackedYagiParameters(
        yagi=yagi,
        count=2,
        spacing_m=3.0,
        phase_step_deg=180.0,
    )

    model = stack.to_antenna()

    assert len(model.wires) == 2 * len(yagi.to_antenna().wires)
    assert model.feed.wire_id.startswith("level-1-")
    assert len(model.sources) == 1
    assert model.sources[0].wire_id.startswith("level-2-")
    assert model.sources[0].phase_deg == pytest.approx(180.0)
    assert model.wires[0].start.z_m == pytest.approx(8.0)
    assert model.wires[len(model.wires) // 2].start.z_m == pytest.approx(11.0)


def test_stack_requires_two_to_four_levels_and_positive_spacing() -> None:
    yagi = nbs_five_element(frequency_hz=50_100_000.0, height_m=8.0)

    with pytest.raises(ValueError):
        StackedYagiParameters(yagi, count=1, spacing_m=3.0)
    with pytest.raises(ValueError):
        StackedYagiParameters(yagi, count=5, spacing_m=3.0)
    with pytest.raises(ValueError):
        StackedYagiParameters(yagi, count=2, spacing_m=0.0)


def test_stack_rejects_support_structures_until_they_are_shared() -> None:
    yagi = nbs_five_element(frequency_hz=50_100_000.0, height_m=8.0)
    with_mast = replace(yagi, mast_diameter_m=0.05, mast_offset_m=1.5)

    with pytest.raises(ValueError, match="mast or guy"):
        StackedYagiParameters(with_mast, count=2, spacing_m=3.0)
