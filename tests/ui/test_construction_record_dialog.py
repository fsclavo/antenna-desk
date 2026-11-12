# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""As-built/checklist dialog."""

from __future__ import annotations

from uuid import uuid4

import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from antennadesk.domain.projects.construction import (
    AsBuiltDimension,
    ConstructionChecklistItem,
    ConstructionRecord,
)
from antennadesk.ui.dialogs.construction_record_dialog import ConstructionRecordDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_empty_record_can_be_built_from_the_form(qtbot: QtBot) -> None:
    dialog = ConstructionRecordDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        None,
    )
    qtbot.addWidget(dialog)
    dialog._notes.setPlainText("Built in the back yard")
    dialog._add_dimension()
    dialog._table.item(0, 0).setText("Radiator length")
    dialog._table.item(0, 1).setText("20.0")
    dialog._table.item(0, 2).setText("19.9")
    dialog._table.item(0, 3).setText("Short by 10 cm")
    dialog._checklist.item(0).setCheckState(Qt.CheckState.Checked)

    record = dialog.record()

    assert record is not None
    assert record.as_built_notes == "Built in the back yard"
    assert record.dimensions[0].actual_value_m == pytest.approx(19.9)
    assert record.dimensions[0].notes == "Short by 10 cm"
    assert "prepare_drawings" in record.checked_keys()


def test_existing_record_is_preloaded(qtbot: QtBot) -> None:
    record = ConstructionRecord(
        as_built_notes="Existing",
        dimensions=(
            AsBuiltDimension(
                id=uuid4(),
                label="Height",
                design_value_m=10.0,
                actual_value_m=9.8,
            ),
        ),
        checklist=(ConstructionChecklistItem("measure_swr", checked=True),),
    )
    dialog = ConstructionRecordDialog(
        Translator(Language.ENGLISH),
        UnitSystem.IMPERIAL,
        record,
    )
    qtbot.addWidget(dialog)

    assert dialog._notes.toPlainText() == "Existing"
    assert "32.808" in dialog._table.item(0, 1).text()
    checked = {
        dialog._checklist.item(row).data(Qt.ItemDataRole.UserRole)
        for row in range(dialog._checklist.count())
        if dialog._checklist.item(row).checkState() is Qt.CheckState.Checked
    }
    assert checked == {"measure_swr"}


def test_empty_form_returns_none(qtbot: QtBot) -> None:
    dialog = ConstructionRecordDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        None,
    )
    qtbot.addWidget(dialog)

    assert dialog.record() is None


def test_invalid_dimension_value_is_reported(qtbot: QtBot) -> None:
    dialog = ConstructionRecordDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        None,
    )
    qtbot.addWidget(dialog)
    dialog._add_dimension()
    dialog._table.item(0, 0).setText("Radiator")
    dialog._table.item(0, 1).setText("not a number")

    with pytest.raises(ValueError, match="valid number"):
        dialog.record()


def test_dialog_retranslates(qtbot: QtBot) -> None:
    dialog = ConstructionRecordDialog(
        Translator(Language.SPANISH),
        UnitSystem.METRIC,
        None,
    )
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Registro as-built y lista de control"
    assert dialog._add.text() == "Agregar dimensión"
    assert dialog._checklist.item(0).text().startswith("Preparar")
