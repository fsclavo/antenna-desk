# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QColor, QImage
from pytestqt.qtbot import QtBot

from antennadesk.domain.projects.project import Project
from antennadesk.ui.construction_pdf import write_construction_pdf
from antennadesk.ui.i18n import Language, Translator

_SVG = (
    b'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="200">'
    b'<rect width="400" height="200" fill="#ffffff"/>'
    b'<line x1="10" y1="10" x2="390" y2="190" stroke="#000000" stroke-width="2"/>'
    b"</svg>"
)


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


def test_construction_sheet_pdf_includes_the_construction_record(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from dataclasses import replace
    from uuid import uuid4

    from antennadesk.domain.projects.construction import (
        AsBuiltDimension,
        ConstructionChecklistItem,
        ConstructionRecord,
    )

    record = ConstructionRecord(
        as_built_notes="Built in the back yard",
        dimensions=(
            AsBuiltDimension(
                id=uuid4(),
                label="Radiator length",
                design_value_m=20.0,
                actual_value_m=19.9,
            ),
        ),
        checklist=(ConstructionChecklistItem("measure_swr", checked=True),),
    )
    path = tmp_path / "sheet-record.pdf"

    write_construction_pdf(
        Translator(Language.ENGLISH),
        replace(sample_project, construction_record=record),
        sample_project.designs[0],
        None,
        path,
    )

    assert path.read_bytes().startswith(b"%PDF")


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


def test_construction_sheet_pdf_uses_vector_figures(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sheet-vector.pdf"

    write_construction_pdf(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        None,
        path,
        figure_svg=_SVG,
        auxiliary_svg=_SVG,
        isometric_svg=_SVG,
        auxiliary_kind="top",
    )

    data = path.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 1_000
    assert b"/Subtype /Image" not in data


def test_construction_sheet_pdf_draws_additional_views_with_captions(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "sheet-multi-view.pdf"

    write_construction_pdf(
        Translator(Language.SPANISH),
        sample_project,
        sample_project.designs[0],
        None,
        path,
        figure_svg=_SVG,
        auxiliary_svg=_SVG,
        isometric_svg=_SVG,
        auxiliary_kind="top",
    )

    assert path.read_bytes().startswith(b"%PDF")


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
    assert b"/Subtype /Image" in data
