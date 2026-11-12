# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build a single printable construction package (ZIP)."""

from __future__ import annotations

import base64
import tempfile
import zipfile
from pathlib import Path

from PySide6.QtGui import QImage

from ..domain.design.preflight import PreflightReport, PreflightStatus
from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.result import SimulationResult
from ..reporting.construction_package import (
    as_built_rows,
    checklist_rows,
    coil_trap_rows,
    hardware_bom_rows,
)
from ..reporting.construction_sheet import write_construction_sheet
from ..reporting.localization import (
    PREFLIGHT_CATEGORY_LABELS,
    localize_preflight_message,
)
from ..reporting.wire_schedule import write_bom_csv, write_wire_schedule_csv
from .construction_pdf import write_construction_pdf
from .i18n import Translator


def _png_data_uri(image: QImage | None) -> str | None:
    if image is None or image.isNull():
        return None
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
        image_path = Path(handle.name)
    try:
        if not image.save(str(image_path)):
            return None
        return "data:image/png;base64," + base64.b64encode(image_path.read_bytes()).decode("ascii")
    finally:
        image_path.unlink(missing_ok=True)


def _notes_text(
    project: Project,
    design: DesignVariant,
    translator: Translator,
) -> str:
    record = project.construction_record
    lines = [
        f"{project.name} — {design.name}",
        "",
        translator.t("construction.as_built"),
    ]
    if record is not None and record.as_built_notes.strip():
        lines.append(record.as_built_notes)
    for label, design_value, actual_value, difference, notes in as_built_rows(
        record,
        translator.report,
    ):
        lines.append(f"- {label}: {design_value} -> {actual_value} ({difference}) {notes}")
    lines.extend(("", translator.t("construction.hardware_bom")))
    for item, quantity, unit, note in hardware_bom_rows(project, design, translator.report):
        lines.append(f"- {item}: {quantity} {unit} · {note}")
    coil_rows = coil_trap_rows(design, translator.report)
    if coil_rows:
        lines.extend(("", translator.t("construction.coils_traps")))
        for kind, wire_id, position, inductance, capacitance, resistance, note in coil_rows:
            lines.append(
                f"- {kind} {wire_id} @ {position}: "
                f"{inductance} / {capacitance} / {resistance} · {note}"
            )
    lines.extend(("", translator.t("construction.checklist")))
    for label, checked in checklist_rows(record, translator.report):
        lines.append(f"[{'x' if checked else ' '}] {label}")
    return "\n".join(lines) + "\n"


def _preflight_text(report: PreflightReport, translator: Translator) -> str:
    if report.status is PreflightStatus.ERROR:
        status = translator.report("Not ready to build: fix the errors below.")
    elif report.status is PreflightStatus.WARNING:
        status = translator.report("Ready to build with warnings.")
    else:
        status = translator.report("Ready to build.")
    lines = [
        translator.report("Construction pre-flight"),
        f"{translator.report('Status')}: {status}",
        "",
    ]
    if not report.findings:
        lines.append(translator.report("No pre-flight issues found."))
    for finding in report.sorted_findings():
        severity = translator.report(finding.severity.value.title())
        category = translator.report(PREFLIGHT_CATEGORY_LABELS[finding.category])
        message = localize_preflight_message(finding, translator.report)
        where = finding.subject or finding.field or "—"
        lines.append(f"[{severity}] {category}: {message} ({where})")
    return "\n".join(lines) + "\n"


def write_construction_package(
    translator: Translator,
    project: Project,
    design: DesignVariant,
    result: SimulationResult | None,
    path: Path,
    *,
    figure_image: QImage | None = None,
    auxiliary_image: QImage | None = None,
    isometric_image: QImage | None = None,
    figure_svg: bytes | None = None,
    auxiliary_svg: bytes | None = None,
    isometric_svg: bytes | None = None,
    auxiliary_kind: str | None = None,
    preflight: PreflightReport | None = None,
) -> None:
    """Write HTML, PDF, CSVs, and build notes into one ZIP archive."""

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        html_path = root / "construction-sheet.html"
        pdf_path = root / "construction-sheet.pdf"
        notes_path = root / "build-notes.txt"
        preflight_path = root / "preflight.txt"
        write_construction_sheet(
            project,
            design,
            result,
            html_path,
            figure_png_data_uri=_png_data_uri(figure_image),
            auxiliary_png_data_uri=_png_data_uri(auxiliary_image),
            isometric_png_data_uri=_png_data_uri(isometric_image),
            auxiliary_kind=auxiliary_kind,
            labeler=translator.report,
            language=translator.language.value,
            preflight=preflight,
        )
        write_construction_pdf(
            translator,
            project,
            design,
            result,
            pdf_path,
            figure_image=figure_image,
            auxiliary_image=auxiliary_image,
            isometric_image=isometric_image,
            figure_svg=figure_svg,
            auxiliary_svg=auxiliary_svg,
            isometric_svg=isometric_svg,
            auxiliary_kind=auxiliary_kind,
            preflight=preflight,
        )
        write_wire_schedule_csv(design, root / "wire-schedule.csv")
        write_bom_csv(design, root / "bom.csv")
        notes_path.write_text(
            _notes_text(project, design, translator),
            encoding="utf-8",
            newline="\n",
        )
        entries = [
            html_path,
            pdf_path,
            root / "wire-schedule.csv",
            root / "bom.csv",
            notes_path,
        ]
        if preflight is not None:
            preflight_path.write_text(
                _preflight_text(preflight, translator),
                encoding="utf-8",
                newline="\n",
            )
            entries.append(preflight_path)
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for entry in entries:
                archive.write(entry, arcname=entry.name)
