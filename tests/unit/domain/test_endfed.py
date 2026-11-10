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


def test_endfed_feed_section_splits_the_wire_and_preserves_the_total_length() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_section_length_m=0.5,
        feed_height_m=10.0,
        end_height_m=5.0,
    )
    custom = parameters.to_custom_parameters()

    assert [wire.id for wire in custom.wires] == ["endfed-feed-section", "radiator"]
    feed_section, radiator = custom.wires
    assert feed_section.length_m == pytest.approx(0.5)
    assert radiator.length_m == pytest.approx(19.5)
    assert feed_section.end == radiator.start
    assert radiator.end.z_m == pytest.approx(5.0)
    assert custom.feed == FeedPoint("endfed-feed-section", 0.0)
    assert feed_section.length_m + radiator.length_m == pytest.approx(20.0)


def test_endfed_rejects_a_feed_section_as_long_as_the_wire() -> None:
    with pytest.raises(ValueError, match="feed_section_length_m"):
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=20.0,
            feed_section_length_m=20.0,
        )


def test_endfed_installation_return_is_used_when_there_is_no_counterpoise() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_section_length_m=0.5,
        installation_return_length_m=0.1,
        feed_height_m=10.0,
        counterpoise_height_m=0.1,
    )
    custom = parameters.to_custom_parameters()

    assert [wire.id for wire in custom.wires] == [
        "endfed-feed-section",
        "radiator",
        "endfed-installation-return-drop",
        "endfed-installation-return",
    ]
    drop, return_wire = custom.wires[2], custom.wires[3]
    assert drop.length_m == pytest.approx(9.9)
    assert return_wire.length_m == pytest.approx(0.1)


def test_endfed_real_counterpoise_takes_precedence_over_the_installation_return() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        installation_return_length_m=0.1,
        counterpoise_length_m=2.0,
        counterpoise_height_m=0.2,
    )
    custom = parameters.to_custom_parameters()

    assert [wire.id for wire in custom.wires] == [
        "radiator",
        "counterpoise-drop",
        "counterpoise",
    ]
    assert not any(wire.id.startswith("endfed-installation") for wire in custom.wires)


def test_endfed_model_warning_keys_flag_legacy_and_missing_return() -> None:
    from antennadesk.domain.antennas.endfed import endfed_model_warning_keys

    legacy = endfed_model_warning_keys(EndFedParameters(frequency_hz=7_100_000.0, length_m=20.0))
    assert legacy == ("endfed.warning.feed_section", "endfed.warning.return")
    complete = endfed_model_warning_keys(
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=20.0,
            feed_section_length_m=0.5,
            installation_return_length_m=0.1,
        )
    )
    assert complete == ()


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


def test_shortened_efhw_80_10_matches_the_published_geometry() -> None:
    from antennadesk.domain.antennas.endfed import (
        ENDFED_LOADING_COIL_ID,
        shortened_efhw_80_10_parameters,
    )

    parameters = shortened_efhw_80_10_parameters()
    custom = parameters.to_custom_parameters()

    assert parameters.preset is EndFedPreset.SHORTENED_80_10
    assert parameters.length_m == pytest.approx(22.74)
    assert parameters.loading_coil_offset_m == pytest.approx(20.35)
    assert parameters.loading_coil_inductance_h == pytest.approx(110e-6)
    assert parameters.loading_coil_top_length_m == pytest.approx(2.39)
    assert parameters.transformer_ratio == pytest.approx(49.0)
    assert parameters.managed_load_ids == frozenset({ENDFED_LOADING_COIL_ID})
    assert len(custom.wires) == 2
    assert [load.id for load in custom.loads] == [ENDFED_LOADING_COIL_ID]
    assert custom.loads[0].wire_id == "radiator"
    assert custom.loads[0].offset_m == pytest.approx(20.35 - 0.5)
    assert custom.loads[0].inductance_h == pytest.approx(110e-6)


def test_shortened_efhw_40_10_matches_the_published_geometry() -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_40_10_parameters

    parameters = shortened_efhw_40_10_parameters()

    assert parameters.preset is EndFedPreset.SHORTENED_40_10
    assert parameters.length_m == pytest.approx(11.86)
    assert parameters.loading_coil_offset_m == pytest.approx(10.01)
    assert parameters.loading_coil_inductance_h == pytest.approx(23e-6)
    assert parameters.loading_coil_top_length_m == pytest.approx(1.85)
    assert len(parameters.to_custom_parameters().loads) == 1


def test_endfed_loaded_coil_requires_a_position_and_inductance() -> None:
    with pytest.raises(ValueError, match="loading_coil_offset_m"):
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=20.0,
            loading_coil_enabled=True,
            loading_coil_offset_m=0.0,
            loading_coil_inductance_h=100e-6,
        )
    with pytest.raises(ValueError, match="loading_coil_inductance_h"):
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=20.0,
            loading_coil_enabled=True,
            loading_coil_offset_m=10.0,
            loading_coil_inductance_h=0.0,
        )


def test_shortened_endfed_optimizer_exposes_the_coil_variables() -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters
    from antennadesk.domain.optimization.registry import optimizer_availability

    availability = optimizer_availability(shortened_efhw_80_10_parameters())

    assert availability.descriptor is not None
    names = {variable.name for variable in availability.descriptor.variables}
    assert {
        "loading_coil_offset_m",
        "loading_coil_inductance_h",
    } <= names


def test_endfed_loaded_coil_q_is_reported_only_with_resistance() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=10.0,
        loading_coil_inductance_h=100e-6,
    )
    assert parameters.loading_coil_q is None

    lossy = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=10.0,
        loading_coil_inductance_h=100e-6,
        loading_coil_resistance_ohm=0.5,
    )
    assert lossy.loading_coil_q is not None
    assert lossy.loading_coil_q > 0.0


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
