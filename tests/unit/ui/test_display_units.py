# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.ui.units import DisplayUnits, LengthPolicy, UnitSystem, length_bounds


def test_metric_auto_selects_by_magnitude() -> None:
    units = DisplayUnits()

    assert units.unit_for(0.0) == "m"
    assert units.unit_for(0.009) == "mm"
    assert units.unit_for(0.01) == "cm"
    assert units.unit_for(0.999) == "cm"
    assert units.unit_for(1.0) == "m"
    assert units.unit_for(-0.007) == "mm"
    assert units.unit_for(-1.0) == "m"


def test_metric_auto_formats_the_spec_examples() -> None:
    units = DisplayUnits()

    assert units.format_length(0.248219) == "24.82 cm"
    assert units.format_length(0.095018) == "9.5 cm"
    assert units.format_length(0.007149) == "7.15 mm"
    assert units.format_length(10.0) == "10 m"
    assert units.format_length(-0.007149) == "-7.15 mm"


def test_imperial_auto_selects_by_magnitude() -> None:
    units = DisplayUnits(UnitSystem.IMPERIAL)

    assert units.unit_for(0.0) == "ft"
    assert units.unit_for(0.3047) == "in"
    assert units.unit_for(0.3048) == "ft"
    assert units.unit_for(20.0) == "ft"
    assert units.format_length(0.007149) == "0.28 in"
    assert units.format_length(20.0) == "65.617 ft"


def test_fixed_policies_use_one_unit() -> None:
    metric = DisplayUnits(UnitSystem.METRIC, LengthPolicy.FIXED)
    imperial = DisplayUnits(UnitSystem.IMPERIAL, LengthPolicy.FIXED)

    assert metric.unit_for(0.007149) == "m"
    assert metric.format_length(0.007149) == "0.007 m"
    assert imperial.unit_for(0.007149) == "ft"
    assert imperial.format_length(0.007149) == "0.023 ft"


def test_format_number_can_keep_fixed_decimals() -> None:
    units = DisplayUnits()

    assert units.format_number(0.248219) == "24.82"
    assert units.format_number(0.248219, unit="m", trim=False) == "0.248"
    assert units.format_number(0.248219, unit="cm", trim=False) == "24.82"


def test_scale_hint_is_used_for_zero_and_ignored_for_other_system() -> None:
    metric = DisplayUnits()
    imperial = DisplayUnits(UnitSystem.IMPERIAL)

    assert metric.unit_for(0.0, scale_hint="cm") == "cm"
    assert metric.unit_for(0.0, scale_hint="ft") == "m"
    assert imperial.unit_for(0.0, scale_hint="in") == "in"


def test_table_unit_uses_the_largest_value() -> None:
    units = DisplayUnits()

    assert units.table_unit([0.0, 3.789, 0.1]) == "m"
    assert units.table_unit([0.248, 0.095, 0.007]) == "cm"
    assert units.table_unit([0.007, 0.005]) == "mm"
    assert units.table_unit([], scale_hint="cm") == "cm"
    assert units.table_unit([0.0]) == "m"


def test_fixed_table_unit_ignores_values() -> None:
    metric = DisplayUnits(UnitSystem.METRIC, LengthPolicy.FIXED)
    imperial = DisplayUnits(UnitSystem.IMPERIAL, LengthPolicy.FIXED)

    assert metric.table_unit([0.007, 20.0]) == "m"
    assert imperial.table_unit([0.007, 20.0]) == "ft"


def test_meters_per_unit_matches_the_canonical_conversions() -> None:
    assert DisplayUnits.meters_per_unit("mm") == pytest.approx(0.001)
    assert DisplayUnits.meters_per_unit("cm") == pytest.approx(0.01)
    assert DisplayUnits.meters_per_unit("m") == pytest.approx(1.0)
    assert DisplayUnits.meters_per_unit("in") == pytest.approx(0.0254)
    assert DisplayUnits.meters_per_unit("ft") == pytest.approx(0.3048)


def test_length_bounds_allow_small_uhf_features() -> None:
    metric_minimum, _ = length_bounds(UnitSystem.METRIC)
    imperial_minimum, _ = length_bounds(UnitSystem.IMPERIAL)

    assert metric_minimum <= 0.001
    assert imperial_minimum <= 0.003
