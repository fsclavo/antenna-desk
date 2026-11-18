# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters
from antennadesk.domain.antennas.moxon import moxon_20m_wire
from antennadesk.ui.geometry.builder import build_scene
from antennadesk.ui.geometry.views import GeometryViewMode
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import DisplayUnits, LengthPolicy, UnitSystem
from antennadesk.ui.widgets.geometry_view import GeometryView

TRANSLATOR = Translator(Language.ENGLISH)
AUTO = DisplayUnits(length_policy=LengthPolicy.AUTO)


def _scene(parameters: object, antenna_type: str):  # type: ignore[no-untyped-def]
    return build_scene(
        parameters.to_antenna(),  # type: ignore[attr-defined]
        antenna_type=antenna_type,
        parameters=parameters,
        display_name=None,
        mode=GeometryViewMode.PLAN,
        translator=TRANSLATOR,
        display_units=AUTO,
    )


def test_moxon_435_scene_uses_cm_and_mm_per_value() -> None:
    scene = _scene(
        moxon_20m_wire(frequency_hz=435_000_000.0, height_m=10.0),
        "moxon",
    )

    assert "width 24.82 cm" in scene.summary
    assert "depth 9.5 cm" in scene.summary
    assert "gap 7.15 mm" in scene.summary
    assert {dimension.text for dimension in scene.dimensions} == {"24.82 cm", "9.5 cm"}

    inset = next(item for item in scene.insets if item.label.startswith("tip detail"))
    assert {dimension.text for dimension in inset.dimensions} == {
        "4.82 cm",
        "3.97 cm",
        "7.15 mm",
    }


def test_moxon_28_scene_uses_m_and_cm_per_value() -> None:
    scene = _scene(
        moxon_20m_wire(frequency_hz=28_500_000.0, height_m=10.0),
        "moxon",
    )

    assert "width 3.789 m" in scene.summary
    assert "gap 10.91 cm" in scene.summary
    assert {dimension.text for dimension in scene.dimensions} == {"3.789 m", "1.45 m"}


def test_dipole_scene_uses_m_for_large_lengths() -> None:
    scene = _scene(
        DipoleParameters(
            frequency_hz=14_100_000.0,
            total_length_m=20.0,
            height_m=10.0,
        ),
        "wire_dipole",
    )

    assert "total length 20 m" in scene.summary
    assert "height 10 m" in scene.summary
    assert "20 m" in {dimension.text for dimension in scene.dimensions}


def test_hexbeam_435_scene_uses_cm_and_keeps_the_small_gap_visible() -> None:
    scene = _scene(
        published_hexbeam_parameters(frequency_hz=435_000_000.0, height_m=10.0),
        "hexbeam",
    )

    assert "driver half-length 18.06 cm" in scene.summary
    assert "tip gap 1.99 cm" in scene.summary
    assert "1.99 cm" in {dimension.text for dimension in scene.dimensions}


def test_scale_bar_unit_follows_the_scene_extent(qtbot: QtBot) -> None:
    metric = GeometryView(
        TRANSLATOR,
        UnitSystem.METRIC,
        display_units=AUTO,
    )
    imperial = GeometryView(
        TRANSLATOR,
        UnitSystem.IMPERIAL,
        display_units=DisplayUnits(UnitSystem.IMPERIAL, LengthPolicy.AUTO),
    )
    qtbot.addWidget(metric)
    qtbot.addWidget(imperial)

    assert metric._scale_unit(20.0) == "m"
    assert metric._scale_unit(0.2) == "cm"
    assert metric._scale_unit(0.005) == "mm"
    assert imperial._scale_unit(10.0) == "ft"
    assert imperial._scale_unit(0.2) == "in"
