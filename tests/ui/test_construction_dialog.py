# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from PySide6.QtGui import QColor, QImage
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


def test_construction_dialog_embeds_a_construction_figure(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    image = QImage(200, 100, QImage.Format.Format_RGB32)
    image.fill(QColor("white"))
    dialog = ConstructionDialog(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        None,
        figure_image=image,
    )
    qtbot.addWidget(dialog)

    assert dialog._figure_data_uri is not None
    assert dialog._figure_data_uri.startswith("data:image/png;base64,")
    assert "construction-figure" in dialog._browser.toHtml()
