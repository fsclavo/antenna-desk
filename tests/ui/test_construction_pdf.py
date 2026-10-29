# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pathlib import Path

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
