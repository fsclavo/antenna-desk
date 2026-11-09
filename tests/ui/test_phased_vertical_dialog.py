# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.phased_vertical_dialog import PhasedVerticalDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog() -> PhasedVerticalDialog:
    return PhasedVerticalDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)


def test_phased_vertical_dialog_builds_the_default_array(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Phased Vertical Array Generator"
    assert parameters.element_count == 2
    assert len(parameters.to_antenna().sources) == 1
    assert "2 verticals" in dialog._form._geometry.text()


def test_phased_vertical_dialog_warns_about_overlapping_radial_screens(
    qtbot: QtBot,
) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    assert dialog._form._overlap_warning.isHidden() is False
    assert "overlap" in dialog._form._overlap_warning.text().lower()

    dialog._form._radial_length.setValue(2.0)

    assert dialog._form._overlap_warning.isHidden() is True


def test_phased_vertical_dialog_updates_the_pattern_of_sources(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._element_count.setValue(3)
    dialog._form._phase_step.setValue(120.0)
    dialog._form._amplitude_taper.setValue(0.3)

    parameters = dialog.parameters()
    sources = parameters.to_antenna().sources

    assert parameters.element_count == 3
    assert [source.phase_deg for source in sources] == pytest.approx([120.0, 240.0])
    assert [source.amplitude for source in sources] == pytest.approx([0.85, 0.7])
    assert "3 verticals" in dialog._form._geometry.text()


def test_phased_vertical_dialog_sets_the_requested_frequency(qtbot: QtBot) -> None:
    dialog = PhasedVerticalDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=3_500_000.0,
    )
    qtbot.addWidget(dialog)

    assert dialog.parameters().frequency_hz == pytest.approx(3_500_000.0)


def test_phased_vertical_form_converts_units(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._height.setValue(5.0)
    dialog._form._spacing.setValue(6.0)

    dialog._form.set_unit_system(UnitSystem.IMPERIAL)
    parameters = dialog.parameters()

    assert parameters.height_m == pytest.approx(5.0, rel=1e-3)
    assert parameters.spacing_m == pytest.approx(6.0, rel=1e-3)
    assert dialog._form._height.suffix().strip() == "ft"
