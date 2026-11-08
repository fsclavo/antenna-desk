# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Unit switches update every antenna-family form without losing values."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QWidget
from pytestqt.qtbot import QtBot

from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem, length_to_m, radius_to_m
from antennadesk.ui.widgets.beverage_form import BeverageForm
from antennadesk.ui.widgets.biquad_form import BiquadForm
from antennadesk.ui.widgets.endfed_form import EndFedForm
from antennadesk.ui.widgets.fan_dipole_form import FanDipoleForm
from antennadesk.ui.widgets.inverted_v_form import InvertedVForm
from antennadesk.ui.widgets.j_pole_form import JPoleForm
from antennadesk.ui.widgets.loaded_dipole_form import LoadedDipoleForm
from antennadesk.ui.widgets.moxon_form import MoxonForm
from antennadesk.ui.widgets.ocfd_form import OCFDForm
from antennadesk.ui.widgets.ringo_form import RingoForm
from antennadesk.ui.widgets.scv_form import ScvForm
from antennadesk.ui.widgets.t2fd_form import T2FDForm
from antennadesk.ui.widgets.transmission_line_doublet_form import (
    TransmissionLineDoubletForm,
)
from antennadesk.ui.widgets.trap_dipole_form import TrapDipoleForm
from antennadesk.ui.widgets.vertical_form import VerticalForm
from antennadesk.ui.widgets.yagi_form import YagiForm
from antennadesk.ui.widgets.zepp_form import ZeppForm

FORMS = (
    (OCFDForm, ("_length", "_height")),
    (
        VerticalForm,
        (
            "_height",
            "_base_height",
            "_radial_length",
            "_coil_offset",
        ),
    ),
    (InvertedVForm, ("_apex_height", "_leg_length")),
    (YagiForm, ("_height",)),
    (MoxonForm, ("_width", "_depth", "_reflector_tip", "_driven_tip", "_height")),
    (FanDipoleForm, ("_apex_height",)),
    (TrapDipoleForm, ("_inner_length", "_outer_length", "_height")),
    (T2FDForm, ("_length", "_spacing", "_height")),
    (
        EndFedForm,
        (
            "_length",
            "_feed_height",
            "_end_height",
            "_counterpoise_length",
            "_counterpoise_height",
        ),
    ),
    (
        JPoleForm,
        (
            "_radiator_height",
            "_stub_length",
            "_spacing",
            "_feed_offset",
            "_gap",
            "_base_height",
        ),
    ),
    (RingoForm, ("_radiator_height", "_ring_diameter", "_ring_height")),
    (
        ScvForm,
        ("_horizontal_length", "_vertical_height", "_base_height", "_feed_offset"),
    ),
    (
        BiquadForm,
        ("_loop_side", "_base_height", "_reflector_spacing"),
    ),
    (
        BeverageForm,
        ("_length", "_height"),
    ),
    (
        LoadedDipoleForm,
        ("_total_length", "_height", "_link_offset"),
    ),
    (
        TransmissionLineDoubletForm,
        ("_dipole_length", "_height", "_feed_height", "_line_length"),
    ),
    (
        ZeppForm,
        ("_radiator_length", "_matching_length", "_spacing", "_base_height"),
    ),
)


@pytest.mark.parametrize("form_type", [item[0] for item in FORMS])
def test_unit_switch_preserves_wire_radius(
    qtbot: QtBot,
    form_type: type[QWidget],
) -> None:
    form = form_type(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    before_m = radius_to_m(form._radius.value(), UnitSystem.METRIC)
    changes: list[bool] = []
    form.changed.connect(lambda: changes.append(True))

    form.set_unit_system(UnitSystem.IMPERIAL)

    assert form._radius.suffix().strip() == "in"
    assert radius_to_m(form._radius.value(), UnitSystem.IMPERIAL) == pytest.approx(
        before_m,
        rel=1e-3,
        abs=0.002,
    )
    assert changes == []

    form.set_unit_system(UnitSystem.METRIC)

    assert form._radius.suffix().strip() == "mm"
    assert radius_to_m(form._radius.value(), UnitSystem.METRIC) == pytest.approx(
        before_m,
        rel=1e-3,
        abs=0.002,
    )
    assert changes == []


@pytest.mark.parametrize(("form_type", "length_fields"), FORMS)
def test_unit_switch_preserves_physical_lengths(
    qtbot: QtBot,
    form_type: type[QWidget],
    length_fields: tuple[str, ...],
) -> None:
    translator = Translator(Language.ENGLISH)
    form = form_type(translator, UnitSystem.METRIC)
    qtbot.addWidget(form)

    before = {
        name: length_to_m(getattr(form, name).value(), UnitSystem.METRIC) for name in length_fields
    }
    changes: list[bool] = []
    form.changed.connect(lambda: changes.append(True))

    form.set_unit_system(UnitSystem.IMPERIAL)

    for name, meters in before.items():
        box = getattr(form, name)
        assert box.suffix().strip() == "ft"
        assert length_to_m(box.value(), UnitSystem.IMPERIAL) == pytest.approx(
            meters,
            rel=1e-3,
            abs=0.002,
        )
    assert changes == []

    form.set_unit_system(UnitSystem.METRIC)

    for name, meters in before.items():
        box = getattr(form, name)
        assert box.suffix().strip() == "m"
        assert length_to_m(box.value(), UnitSystem.METRIC) == pytest.approx(
            meters,
            rel=1e-3,
            abs=0.002,
        )
    assert changes == []


def test_vertical_top_hat_radius_converts(qtbot: QtBot) -> None:
    form = VerticalForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    form._top_hat_enabled.setChecked(True)
    form._top_hat_radius.setValue(0.5)
    before_m = length_to_m(form._top_hat_radius.value(), UnitSystem.METRIC)

    form.set_unit_system(UnitSystem.IMPERIAL)

    assert form._top_hat_radius.suffix().strip() == "ft"
    assert length_to_m(
        form._top_hat_radius.value(),
        UnitSystem.IMPERIAL,
    ) == pytest.approx(before_m, rel=1e-3, abs=0.002)


def test_fan_dipole_table_lengths_convert(qtbot: QtBot) -> None:
    form = FanDipoleForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    before_m = length_to_m(
        float(form._table.item(0, 0).text()),
        UnitSystem.METRIC,
    )

    form.set_unit_system(UnitSystem.IMPERIAL)

    after_m = length_to_m(
        float(form._table.item(0, 0).text()),
        UnitSystem.IMPERIAL,
    )
    assert after_m == pytest.approx(before_m, rel=1e-3)


def test_yagi_table_lengths_convert(qtbot: QtBot) -> None:
    form = YagiForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    before_m = length_to_m(
        float(form._table.item(0, 2).text()),
        UnitSystem.METRIC,
    )

    form.set_unit_system(UnitSystem.IMPERIAL)

    after_m = length_to_m(
        float(form._table.item(0, 2).text()),
        UnitSystem.IMPERIAL,
    )
    assert after_m == pytest.approx(before_m, rel=1e-3)


def test_yagi_table_radius_converts(qtbot: QtBot) -> None:
    form = YagiForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    before_m = radius_to_m(
        float(form._table.item(0, 3).text()),
        UnitSystem.METRIC,
    )

    form.set_unit_system(UnitSystem.IMPERIAL)

    after_m = radius_to_m(
        float(form._table.item(0, 3).text()),
        UnitSystem.IMPERIAL,
    )
    assert after_m == pytest.approx(before_m, rel=1e-3)


def test_main_window_unit_switch_updates_all_forms(window: MainWindow) -> None:
    window._dirty = False

    window._set_unit_system(UnitSystem.IMPERIAL)

    assert window._ocfd_form._length.suffix().strip() == "ft"
    assert window._yagi_form._height.suffix().strip() == "ft"
    assert window._endfed_form._length.suffix().strip() == "ft"
    assert window._dirty is False
