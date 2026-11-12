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


def test_construction_dialog_shows_the_preflight_report(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    from antennadesk.domain.common.validation import Severity
    from antennadesk.domain.design.preflight import (
        PreflightAction,
        PreflightCategory,
        PreflightFinding,
        PreflightReport,
    )

    report = PreflightReport(
        (
            PreflightFinding(
                code="supports.height_exceeded",
                category=PreflightCategory.SUPPORTS,
                severity=Severity.ERROR,
                message="the design is too tall",
                subject="Small yard",
                action=PreflightAction.EDIT_SUPPORTS,
            ),
        )
    )
    dialog = ConstructionDialog(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        None,
        preflight=report,
    )
    qtbot.addWidget(dialog)

    text = dialog._browser.toPlainText()
    assert "Construction pre-flight" in text
    assert "Not ready to build" in text
    assert "the design is too tall" in text


def test_construction_dialog_follows_the_spanish_language(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    dialog = ConstructionDialog(
        Translator(Language.SPANISH),
        sample_project,
        sample_project.designs[0],
        None,
    )
    qtbot.addWidget(dialog)
    dialog.show()

    text = dialog._browser.toPlainText()
    assert "Dimensiones" in text
    assert "Lista de hilos" in text
    assert "Notas de construcción" in text
    assert "Wire schedule" not in text
    assert "Construction notes" not in text


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


def test_construction_dialog_embeds_an_isometric_view(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    image = QImage(200, 150, QImage.Format.Format_RGB32)
    image.fill(QColor("white"))
    dialog = ConstructionDialog(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        None,
        isometric_image=image,
    )
    qtbot.addWidget(dialog)

    assert dialog._isometric_data_uri is not None
    assert dialog._isometric_data_uri.startswith("data:image/png;base64,")
    assert "isometric-view" in dialog._browser.toHtml()


def test_construction_dialog_embeds_an_installation_view(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    figure = QImage(200, 100, QImage.Format.Format_RGB32)
    figure.fill(QColor("white"))
    auxiliary = QImage(200, 60, QImage.Format.Format_RGB32)
    auxiliary.fill(QColor("white"))
    dialog = ConstructionDialog(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        None,
        figure_image=figure,
        auxiliary_image=auxiliary,
    )
    qtbot.addWidget(dialog)

    assert dialog._auxiliary_data_uri is not None
    assert dialog._auxiliary_data_uri.startswith("data:image/png;base64,")
    assert "installation-view" in dialog._browser.toHtml()
