# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""As-built record integration in the main window."""

from __future__ import annotations

from uuid import uuid4

import pytest
from PySide6.QtWidgets import QDialog

from antennadesk.domain.projects.construction import (
    AsBuiltDimension,
    ConstructionRecord,
)
from antennadesk.ui.dialogs.construction_record_dialog import ConstructionRecordDialog
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


def _record() -> ConstructionRecord:
    return ConstructionRecord(
        as_built_notes="Built in the back yard",
        dimensions=(
            AsBuiltDimension(
                id=uuid4(),
                label="Radiator length",
                design_value_m=20.0,
                actual_value_m=19.9,
            ),
        ),
    )


def test_construction_record_action_is_available_and_retranslates(
    window: MainWindow,
) -> None:
    assert window._construction_record_action.isEnabled()
    assert window._construction_record_action.text() == "As-Built / Checklist..."

    window._set_language(Language.SPANISH)

    assert window._construction_record_action.text() == "As-built / lista de control..."
    window._set_language(Language.ENGLISH)


def test_edit_construction_record_persists_and_undoes(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = _record()
    monkeypatch.setattr(
        ConstructionRecordDialog,
        "exec",
        lambda self: QDialog.DialogCode.Accepted,
    )
    monkeypatch.setattr(ConstructionRecordDialog, "record", lambda self: record)

    window.edit_construction_record()

    assert window._project is not None
    assert window._project.construction_record == record
    assert window._dirty is True
    assert window._last_status_key == "status.construction_record"

    window._undo_stack.undo()

    assert window._project is not None
    assert window._project.construction_record is None
    window._dirty = False
