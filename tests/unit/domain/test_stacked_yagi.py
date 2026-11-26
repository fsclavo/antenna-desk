# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Stacked-Yagi domain prototype tests."""

from __future__ import annotations

from dataclasses import replace

import pytest

from antennadesk.domain.antennas.matching_network import (
    TransformerNetwork,
    design_l_network,
)
from antennadesk.domain.antennas.polarization import Polarization
from antennadesk.domain.antennas.stacked_yagi import (
    STACKED_YAGI_SPLITTER_NODE_ID,
    StackedYagiFeed,
    StackedYagiFeedMode,
    StackedYagiParameters,
)
from antennadesk.domain.antennas.yagi import YagiMatchType, nbs_five_element


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


def test_stack_builds_one_shared_mast_and_guy_set() -> None:
    yagi = nbs_five_element(frequency_hz=50_100_000.0, height_m=8.0)
    with_mast = replace(
        yagi,
        mast_diameter_m=0.05,
        mast_offset_m=1.5,
        guy_count=3,
        guy_anchor_radius_m=4.0,
        guy_diameter_m=0.004,
    )
    stack = StackedYagiParameters(with_mast, count=3, spacing_m=3.0)

    model = stack.to_antenna()

    mast_wires = [wire for wire in model.wires if wire.id == "mast"]
    assert len(mast_wires) == 1
    assert mast_wires[0].start.z_m == pytest.approx(0.0)
    assert mast_wires[0].end.z_m == pytest.approx(stack.top_height_m)
    assert mast_wires[0].start.x_m == pytest.approx(-1.5)
    assert len([wire for wire in model.wires if wire.id.startswith("guy-")]) == 3
    assert not any(
        wire.id.startswith("level-") and ("mast" in wire.id or "guy" in wire.id)
        for wire in model.wires
    )
    assert yagi.to_antenna().wires[-1].end.z_m == pytest.approx(yagi.height_m)


def test_stack_reports_its_vertical_and_boom_envelope() -> None:
    yagi = nbs_five_element(frequency_hz=50_100_000.0, height_m=8.0)
    stack = StackedYagiParameters(
        yagi=yagi,
        count=3,
        spacing_m=3.0,
        phase_step_deg=90.0,
        amplitude_ratio=0.5,
    )

    assert stack.top_height_m == pytest.approx(14.0)
    assert stack.lowest_tip_m == pytest.approx(8.0)
    assert stack.highest_tip_m == pytest.approx(14.0)
    assert stack.element_span_m == pytest.approx(max(e.length_m for e in yagi.elements))
    assert stack.boom_length_m == pytest.approx(max(e.position_m for e in yagi.elements))
    assert stack.wavelength_m == pytest.approx(yagi.wavelength_m)

    model = stack.to_antenna()
    assert len(model.sources) == 2
    assert [source.phase_deg for source in model.sources] == pytest.approx([90.0, 180.0])
    assert [source.amplitude for source in model.sources] == pytest.approx([0.5, 0.5])


def test_vertical_polarized_levels_must_not_overlap() -> None:
    yagi = nbs_five_element(frequency_hz=50_100_000.0, height_m=8.0)
    vertical = replace(
        yagi,
        polarization=Polarization.VERTICAL,
        height_m=30.0,
    )
    span = max(element.length_m for element in vertical.elements)

    with pytest.raises(ValueError, match="overlap"):
        StackedYagiParameters(vertical, count=2, spacing_m=span)

    stack = StackedYagiParameters(vertical, count=2, spacing_m=span + 0.1)
    assert stack.lowest_tip_m == pytest.approx(30.0 - span / 2.0)
    assert stack.highest_tip_m == pytest.approx(30.0 + span + 0.1 + span / 2.0)


def test_stack_rejects_folded_or_transformed_driven_elements_for_now() -> None:
    yagi = nbs_five_element(frequency_hz=50_100_000.0, height_m=8.0)

    with pytest.raises(ValueError, match="folded driven"):
        StackedYagiParameters(replace(yagi, driven_folded=True), count=2, spacing_m=3.0)
    with pytest.raises(ValueError, match="transformer"):
        StackedYagiParameters(
            replace(yagi, transformer_ratio=4.0),
            count=2,
            spacing_m=3.0,
        )


def test_stack_builds_a_beta_match_at_every_level() -> None:
    yagi = nbs_five_element(frequency_hz=50_100_000.0, height_m=8.0)
    matched = replace(
        yagi,
        match_type=YagiMatchType.BETA_HAIRPIN,
        match_length_m=0.3,
        match_spacing_m=0.12,
    )
    stack = StackedYagiParameters(matched, count=2, spacing_m=3.0)

    model = stack.to_antenna()

    assert model.feed.wire_id == "level-1-element-2-feed"
    assert model.sources[0].wire_id == "level-2-element-2-feed"
    for level in (1, 2):
        prefix = f"level-{level}-element-2"
        ids = {wire.id for wire in model.wires}
        assert f"{prefix}-left" in ids
        assert f"{prefix}-right" in ids
        assert f"{prefix}-feed" in ids
        assert f"{prefix}-hairpin-a" in ids
        assert f"{prefix}-hairpin-b" in ids
        assert f"{prefix}-hairpin-short" in ids


def test_phase_line_feed_derives_the_source_phase_from_the_line_increment() -> None:
    yagi = nbs_five_element(frequency_hz=14_100_000.0, height_m=10.0)
    wavelength = yagi.wavelength_m
    feed = StackedYagiFeed(
        mode=StackedYagiFeedMode.PHASE_LINES,
        reference_length_m=2.0,
        line_increment_m=wavelength / 4.0,
        velocity_factor=0.8,
        characteristic_impedance_ohm=75.0,
        splitter_loss_db=0.4,
    )
    stack = StackedYagiParameters(
        yagi=yagi,
        count=3,
        spacing_m=10.0,
        phase_step_deg=90.0,
        feed=feed,
    )

    assert stack.effective_phase_step_deg == pytest.approx(-112.5)
    assert feed.line_length_for_level(0) == pytest.approx(2.0)
    assert feed.line_length_for_level(2) == pytest.approx(2.0 + 2 * wavelength / 4.0)
    model = stack.to_antenna()
    assert [source.phase_deg for source in model.sources] == pytest.approx([247.5, 135.0])


def test_phase_line_feed_rejects_invalid_lines_and_loss() -> None:
    with pytest.raises(ValueError):
        StackedYagiFeed(velocity_factor=0.0)
    with pytest.raises(ValueError):
        StackedYagiFeed(velocity_factor=1.1)
    with pytest.raises(ValueError):
        StackedYagiFeed(characteristic_impedance_ohm=0.0)
    with pytest.raises(ValueError):
        StackedYagiFeed(line_increment_m=-0.1)
    with pytest.raises(ValueError):
        StackedYagiFeed(splitter_loss_db=-0.1)
    with pytest.raises(ValueError):
        StackedYagiFeed(line_loss_db_per_100m=-0.1)
    with pytest.raises(ValueError, match="L, Pi, or T"):
        StackedYagiFeed(
            mode=StackedYagiFeedMode.WILKINSON,
            reference_length_m=2.0,
            level_matching_networks=(TransformerNetwork(series_inductance_h=1e-6),),
        )


def test_stacked_yagi_rejects_a_level_matching_length_mismatch() -> None:
    yagi = nbs_five_element(frequency_hz=14_100_000.0, height_m=10.0)
    matching = design_l_network(100.0 + 0.0j, 14_100_000.0, source_impedance_ohm=50.0)
    assert matching is not None

    with pytest.raises(ValueError, match="one entry per level"):
        StackedYagiParameters(
            yagi=yagi,
            count=2,
            spacing_m=10.0,
            feed=StackedYagiFeed(level_matching_networks=(matching,)),
        )


def test_network_mode_builds_lossless_phase_lines_and_no_ideal_sources() -> None:
    yagi = nbs_five_element(frequency_hz=14_100_000.0, height_m=10.0)
    feed = StackedYagiFeed(
        mode=StackedYagiFeedMode.NETWORK,
        reference_length_m=2.0,
        line_increment_m=2.65,
        velocity_factor=0.8,
        characteristic_impedance_ohm=75.0,
        splitter_loss_db=0.4,
    )
    stack = StackedYagiParameters(
        yagi=yagi,
        count=3,
        spacing_m=10.0,
        feed=feed,
    )

    model = stack.to_antenna()

    assert model.sources == ()
    assert len(model.transmission_lines) == 3
    assert [line.length_m for line in model.transmission_lines] == pytest.approx([2.0, 4.65, 7.3])
    assert all(
        line.characteristic_impedance_ohm == pytest.approx(75.0)
        for line in model.transmission_lines
    )
    assert all(
        line.start_wire_id == STACKED_YAGI_SPLITTER_NODE_ID for line in model.transmission_lines
    )
    assert model.feed.wire_id == STACKED_YAGI_SPLITTER_NODE_ID
    assert any(wire.id == STACKED_YAGI_SPLITTER_NODE_ID for wire in model.wires)

    with pytest.raises(ValueError, match="positive line_increment"):
        StackedYagiFeed(
            mode=StackedYagiFeedMode.NETWORK,
            reference_length_m=2.0,
            line_increment_m=0.0,
        )
    with pytest.raises(ValueError, match="positive reference_length"):
        StackedYagiFeed(
            mode=StackedYagiFeedMode.NETWORK,
            line_increment_m=2.0,
        )


def test_phase_line_loss_is_scaled_by_the_physical_length() -> None:
    feed = StackedYagiFeed(
        reference_length_m=2.0,
        line_increment_m=2.5,
        line_loss_db_per_100m=1.5,
    )

    assert feed.line_loss_for_level(0) == pytest.approx(0.03)
    assert feed.line_loss_for_level(2) == pytest.approx(0.105)
