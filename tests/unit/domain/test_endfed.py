# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.endfed import (
    EndFedParameters,
    EndFedPreset,
    sloper_parameters,
)
from antennadesk.domain.antennas.family import (
    AntennaFamily,
    antenna_family,
    antenna_template_id,
)
from antennadesk.domain.antennas.feed import FeedPoint


def test_endfed_generates_one_wire_with_end_feed() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=5.0,
    )
    custom = parameters.to_custom_parameters()

    assert len(custom.wires) == 1
    assert custom.feed.wire_id == "radiator"
    assert custom.feed.offset_m == 0.0
    assert custom.wires[0].end.z_m == pytest.approx(5.0)
    assert custom.wires[0].length_m == pytest.approx(20.0)
    assert custom.generator_name == "End-fed"
    assert antenna_family(custom) is AntennaFamily.DIPOLE


def test_endfed_rejects_below_ground_heights() -> None:
    with pytest.raises(ValueError, match="end_height"):
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=20.0,
            end_height_m=-1.0,
        )


def test_sloper_reference_matches_the_chameleon_lefs_geometry() -> None:
    parameters = sloper_parameters()

    assert parameters.preset is EndFedPreset.SLOPER
    assert parameters.length_m == pytest.approx(66.5 * 0.3048, rel=0.01)
    assert parameters.feed_height_m == pytest.approx(3.0 * 0.3048, rel=0.05)
    assert parameters.end_height_m == pytest.approx(25.0 * 0.3048, rel=0.05)
    assert parameters.transformer_ratio == pytest.approx(49.0)


def test_endfed_rejects_a_slope_steeper_than_the_wire() -> None:
    with pytest.raises(ValueError, match="height difference"):
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=5.0,
            feed_height_m=1.0,
            end_height_m=10.0,
        )


def test_endfed_counterpoise_adds_a_drop_and_horizontal_wire() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=5.0,
        azimuth_deg=0.0,
        counterpoise_length_m=3.0,
        counterpoise_height_m=0.2,
    )
    custom = parameters.to_custom_parameters()

    assert [wire.id for wire in custom.wires] == [
        "radiator",
        "counterpoise-drop",
        "counterpoise",
    ]
    drop, counterpoise = custom.wires[1], custom.wires[2]
    assert drop.start.z_m == pytest.approx(10.0)
    assert drop.end.z_m == pytest.approx(0.2)
    assert drop.length_m == pytest.approx(9.8)
    assert counterpoise.start == drop.end
    assert counterpoise.end.x_m == pytest.approx(-3.0)
    assert counterpoise.end.y_m == pytest.approx(0.0, abs=1e-12)
    assert counterpoise.length_m == pytest.approx(3.0)
    assert custom.feed == FeedPoint("radiator", 0.0)


def test_endfed_counterpoise_is_optional() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        counterpoise_length_m=0.0,
    )

    assert len(parameters.to_custom_parameters().wires) == 1


def test_endfed_counterpoise_azimuth_defaults_opposite_the_radiator() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        azimuth_deg=30.0,
        counterpoise_length_m=2.0,
    )

    assert parameters.effective_counterpoise_azimuth_deg == pytest.approx(210.0)


def test_endfed_rejects_an_invalid_transformer_ratio() -> None:
    with pytest.raises(ValueError, match="transformer_ratio"):
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=20.0,
            transformer_ratio=0.0,
        )


def test_efhw_presets_use_the_published_arrl_lengths() -> None:
    from antennadesk.domain.antennas.endfed import efhw_parameters

    expected = {"40m": 66.0 * 0.3048, "20m": 33.0 * 0.3048, "10m": 16.0 * 0.3048}
    for band_id, length_m in expected.items():
        parameters = efhw_parameters(band_id)

        assert parameters.length_m == pytest.approx(length_m)
        assert parameters.transformer_ratio == pytest.approx(49.0)
        assert parameters.counterpoise_length_m > 0.0
        assert parameters.preset is EndFedPreset.STANDARD


def test_efhw_presets_reject_an_unknown_band() -> None:
    from antennadesk.domain.antennas.endfed import efhw_parameters

    with pytest.raises(ValueError, match="unsupported EFHW"):
        efhw_parameters("30m")


def test_endfed_presets_keep_their_generator_name_and_template_id() -> None:
    sloper = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=2.0,
        preset=EndFedPreset.SLOPER,
    )
    random_wire = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=17.0,
        transformer_ratio=9.0,
        preset=EndFedPreset.RANDOM_WIRE,
    )

    assert sloper.to_custom_parameters().generator_name == "Sloper"
    assert random_wire.to_custom_parameters().generator_name == "Random wire"
    assert antenna_template_id(sloper) == "sloper"
    assert antenna_template_id(random_wire) == "random_wire"
    assert antenna_family(sloper) is AntennaFamily.DIPOLE
    assert antenna_family(random_wire) is AntennaFamily.DIPOLE
