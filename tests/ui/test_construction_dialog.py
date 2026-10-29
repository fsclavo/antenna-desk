# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.projects.project import Project
from antennadesk.ui.dialogs.construction_dialog import ConstructionDialog
from antennadesk.ui.i18n import Language, Translator


def test_construction_dialog_shows_dimensions(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    dialog = ConstructionDialog(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        None,
    )
    qtbot.addWidget(dialog)
    dialog.show()

    text = dialog._browser.toPlainText()
    assert "Total wire length" in text
    assert "Construction notes" in text
    assert "No result yet." in text
