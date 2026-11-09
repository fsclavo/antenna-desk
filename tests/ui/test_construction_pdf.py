# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QColor, QImage
from pytestqt.qtbot import QtBot

from antennadesk.domain.projects.project import Project
from antennadesk.ui.construction_pdf import write_construction_pdf
from antennadesk.ui.i18n import Language, Translator


def test_construction_sheet_pdf_is_written(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sheet.pdf"

    write_construction_pdf(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        None,
        path,
    )

    data = path.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 1_000


def test_construction_sheet_pdf_is_written_in_spanish(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "hoja.pdf"

    write_construction_pdf(
        Translator(Language.SPANISH),
        sample_project,
        sample_project.designs[0],
        None,
        path,
    )

    data = path.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 1_000


def test_construction_sheet_pdf_embeds_the_figure(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    image = QImage(400, 200, QImage.Format.Format_RGB32)
    image.fill(QColor("white"))
    auxiliary = QImage(400, 120, QImage.Format.Format_RGB32)
    auxiliary.fill(QColor("white"))
    path = tmp_path / "sheet-figure.pdf"

    write_construction_pdf(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        None,
        path,
        figure_image=image,
        auxiliary_image=auxiliary,
    )

    data = path.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 1_000
