# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Materials reference data integrity."""

from __future__ import annotations

import pytest

from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.domain.design.materials_reference import (
    COAX_REFERENCES,
    FERRITE_REFERENCES,
    INSULATOR_REFERENCES,
    MATERIALS_REFERENCE,
    WIRE_REFERENCES,
    CoaxReference,
    FerriteReference,
    ReferenceSource,
)


def test_reference_keys_are_unique_and_grouped() -> None:
    assert tuple(MATERIALS_REFERENCE) == ("wire", "coax", "ferrite", "insulator")
    for entries in MATERIALS_REFERENCE.values():
        keys = [entry.key for entry in entries]
        assert keys
        assert len(keys) == len(set(keys))


def test_every_reference_has_a_traceable_source() -> None:
    for entries in MATERIALS_REFERENCE.values():
        for entry in entries:
            assert entry.source.label.strip()
            assert entry.source.url.startswith("https://") or entry.source.url.startswith("http://")


def test_wire_references_publish_solver_conductivity() -> None:
    assert tuple(entry.key for entry in WIRE_REFERENCES) == ("copper", "aluminum")
    for entry in WIRE_REFERENCES:
        assert entry.material.conductivity_s_per_m > 0.0
        assert entry.conductivity_ms_per_m == pytest.approx(
            entry.material.conductivity_s_per_m / 1_000_000.0
        )


def test_coax_preset_builds_the_feed_line() -> None:
    for entry in COAX_REFERENCES:
        line = entry.feed_line(12.5)
        assert isinstance(line, FeedLine)
        assert line.characteristic_impedance_ohm == pytest.approx(
            entry.characteristic_impedance_ohm
        )
        assert line.length_m == pytest.approx(12.5)
        assert line.velocity_factor == pytest.approx(entry.velocity_factor)
        assert line.matched_loss_db_per_100m == pytest.approx(entry.matched_loss_db_per_100m)
        assert entry.reference_frequency_hz > 0.0
        assert 0.0 < entry.velocity_factor <= 1.0


def test_ferrite_ranges_and_insulator_keys_are_consistent() -> None:
    for entry in FERRITE_REFERENCES:
        assert entry.frequency_min_mhz < entry.frequency_max_mhz
        assert entry.initial_permeability > 0.0
        assert entry.material_type in {"MnZn", "NiZn"}
    for entry in INSULATOR_REFERENCES:
        assert entry.dielectric_strength.strip()
        assert entry.weather_key in {"excellent", "good", "limited"}


def test_invalid_reference_values_are_rejected() -> None:
    source = ReferenceSource(label="test source")
    with pytest.raises(ValueError):
        CoaxReference(
            key="bad",
            characteristic_impedance_ohm=50.0,
            velocity_factor=1.1,
            matched_loss_db_per_100m=1.0,
            reference_frequency_hz=100_000_000.0,
            source=source,
        )
    with pytest.raises(ValueError):
        FerriteReference(
            key="bad",
            material_type="NiZn",
            initial_permeability=100.0,
            frequency_min_mhz=100.0,
            frequency_max_mhz=100.0,
            source=source,
        )
    with pytest.raises(ValueError):
        ReferenceSource(label=" ")
