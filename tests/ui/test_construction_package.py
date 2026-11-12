# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Printable construction package (ZIP)."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

from pytestqt.qtbot import QtBot

from antennadesk.domain.common.validation import Severity
from antennadesk.domain.design.preflight import (
    PreflightAction,
    PreflightCategory,
    PreflightFinding,
    PreflightReport,
)
from antennadesk.domain.projects.project import Project
from antennadesk.ui.construction_package import write_construction_package
from antennadesk.ui.i18n import Language, Translator


def test_construction_package_contains_html_pdf_csv_and_notes(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "package.zip"

    write_construction_package(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        None,
        path,
    )

    assert path.is_file()
    with ZipFile(path) as archive:
        names = set(archive.namelist())
        assert names == {
            "construction-sheet.html",
            "construction-sheet.pdf",
            "wire-schedule.csv",
            "bom.csv",
            "build-notes.txt",
        }
        html = archive.read("construction-sheet.html").decode("utf-8")
        pdf = archive.read("construction-sheet.pdf")
        notes = archive.read("build-notes.txt").decode("utf-8")
    assert "Hardware BOM" in html
    assert "Construction checklist" in html
    assert pdf.startswith(b"%PDF")
    assert "Hardware BOM" in notes
    assert "check_dimensions" not in notes
    assert "[x]" in notes or "[ ]" in notes


def test_construction_package_adds_a_preflight_file(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    report = PreflightReport(
        (
            PreflightFinding(
                code="supports.height_exceeded",
                category=PreflightCategory.SUPPORTS,
                severity=Severity.ERROR,
                message="the design is too tall",
                subject="Small yard",
                action=PreflightAction.EDIT_SUPPORTS,
                values=(("top", "8.000"), ("available", "5.000")),
            ),
        )
    )
    path = tmp_path / "package-preflight.zip"

    write_construction_package(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        None,
        path,
        preflight=report,
    )

    with ZipFile(path) as archive:
        names = set(archive.namelist())
        preflight = archive.read("preflight.txt").decode("utf-8")
        html = archive.read("construction-sheet.html").decode("utf-8")
    assert "preflight.txt" in names
    assert "Not ready to build" in preflight
    assert "the design is too tall" in preflight
    assert "Construction pre-flight" in html
    assert "the design is too tall" in html
