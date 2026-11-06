# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dialogs display wire radius and comparison dimensions in the active units."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QWidget
from pytestqt.qtbot import QtBot

from antennadesk.domain.projects.project import Project
from antennadesk.ui.dialogs.comparison_dialog import ComparisonDialog
from antennadesk.ui.dialogs.custom_antenna_dialog import CustomAntennaDialog
from antennadesk.ui.dialogs.doublet_dialog import DoubletDialog
from antennadesk.ui.dialogs.g5rv_dialog import G5RVDialog
from antennadesk.ui.dialogs.zepp_dialog import ZeppDialog
from antennadesk.ui.dialogs.zs6bkw_dialog import ZS6BKWDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem, radius_to_m

RADIUS_DIALOGS = (G5RVDialog, ZS6BKWDialog, ZeppDialog, DoubletDialog)


@pytest.mark.parametrize("dialog_type", RADIUS_DIALOGS)
def test_generator_dialog_uses_selected_radius_units(
    qtbot: QtBot,
    dialog_type: type[QWidget],
) -> None:
    dialog = dialog_type(Translator(Language.ENGLISH), UnitSystem.IMPERIAL)
    qtbot.addWidget(dialog)

    assert dialog._radius.suffix().strip() == "in"
    assert radius_to_m(dialog._radius.value(), UnitSystem.IMPERIAL) == pytest.approx(
        0.001,
        abs=1e-5,
    )

    parameters = dialog.parameters()
    radii = (
        [wire.radius_m for wire in parameters.wires]
        if hasattr(parameters, "wires")
        else [parameters.wire_radius_m]
    )
    assert all(radius == pytest.approx(0.001, abs=1e-6) for radius in radii)


def test_custom_dialog_uses_selected_radius_units(qtbot: QtBot) -> None:
    dialog = CustomAntennaDialog(
        Translator(Language.ENGLISH),
        UnitSystem.IMPERIAL,
    )
    qtbot.addWidget(dialog)

    assert dialog._table.horizontalHeaderItem(7).text().endswith("(in)")
    assert dialog.parameters().wires[0].radius_m == pytest.approx(0.001, abs=1e-6)


def test_comparison_dialog_uses_selected_units(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    dialog = ComparisonDialog(
        Translator(Language.ENGLISH),
        sample_project,
        {},
        unit_system=UnitSystem.IMPERIAL,
    )
    qtbot.addWidget(dialog)

    rows = dict(dialog._rows(sample_project.designs[0], None))
    translator = Translator(Language.ENGLISH)
    assert rows[translator.t("field.primary_dimension")].endswith("ft")
    assert rows[translator.t("field.height")].endswith("ft")
    assert rows[translator.t("field.diameter")].endswith("in")
