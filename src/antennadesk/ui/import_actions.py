# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Import dialogs and parsing for VNA, NEC-2, and MMANA files."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

from PySide6.QtWidgets import QDialog, QFileDialog, QInputDialog, QMessageBox, QWidget

from ..application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from ..domain.common.time import utc_now
from ..domain.measurement import Measurement
from ..domain.projects.project import Project
from ..importers import read_import_text
from ..importers.mmana import parse_mmana_file
from ..importers.nec2_deck import parse_nec2_deck
from ..importers.vna import ParsedVnaData, parse_vna_data
from ..importers.vna_csv import VnaColumnMapping, VnaCsvError, vna_csv_headers
from .dialogs.measurement_details_dialog import MeasurementDetailsDialog
from .dialogs.vna_mapping_dialog import VnaMappingDialog
from .i18n import Translator


@dataclass(frozen=True, slots=True)
class MeasurementImportResult:
    project: Project
    imported: int
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ImportedProject:
    project: Project
    warnings: tuple[str, ...]


def choose_vna_paths(
    parent: QWidget,
    translator: Translator,
) -> tuple[Path, ...] | None:
    filenames, _ = QFileDialog.getOpenFileNames(
        parent,
        translator.t("dialog.vna_title"),
        str(Path.home()),
        translator.t("dialog.vna_filter"),
    )
    if not filenames:
        return None
    return tuple(Path(filename) for filename in filenames)


def _choose_s2p_port(
    parent: QWidget,
    translator: Translator,
    name: str,
) -> int | None:
    choice, accepted = QInputDialog.getItem(
        parent,
        translator.t("dialog.vna_title"),
        translator.t("dialog.vna_s2p_port", name=name),
        [
            translator.t("vna.s2p_port1"),
            translator.t("vna.s2p_port2"),
        ],
        0,
        False,
    )
    if not accepted:
        return None
    return 1 if choice == translator.t("vna.s2p_port1") else 2


def _measurement_target(
    project: Project,
    parent: QWidget,
    translator: Translator,
    name: str,
) -> tuple[str | None, UUID | None]:
    existing = next(
        (measurement for measurement in project.measurements if measurement.name == name),
        None,
    )
    if existing is None:
        return name, None
    answer = QMessageBox.question(
        parent,
        translator.t("dialog.vna_title"),
        translator.t("dialog.vna_duplicate", name=name),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    if answer == QMessageBox.StandardButton.Yes:
        return name, existing.id
    candidate = f"{name} (2)"
    index = 2
    names = {measurement.name for measurement in project.measurements}
    while candidate in names:
        index += 1
        candidate = f"{name} ({index})"
    return candidate, None


def _parse_vna_with_mapping(
    parent: QWidget,
    translator: Translator,
    mappings: dict[tuple[str, ...], VnaColumnMapping],
    text: str,
    path: Path,
    s2p_port: int,
) -> ParsedVnaData:
    headers = vna_csv_headers(text) if path.suffix.lower() in {".csv", ".txt"} else ()
    mapping = mappings.get(headers) if headers else None
    try:
        return parse_vna_data(
            text,
            suffix=path.suffix,
            s2p_port=s2p_port,
            mapping=mapping,
        )
    except VnaCsvError as exc:
        if not headers or "column" not in str(exc).lower():
            raise
        dialog = VnaMappingDialog(
            translator,
            headers,
            parent,
            initial=mapping,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            raise
        mapping = dialog.mapping()
        mappings[headers] = mapping
        return parse_vna_data(
            text,
            suffix=path.suffix,
            s2p_port=s2p_port,
            mapping=mapping,
        )


def import_vna_paths(
    *,
    parent: QWidget,
    translator: Translator,
    project: Project,
    paths: Sequence[Path],
    mappings: dict[tuple[str, ...], VnaColumnMapping],
    show_error: Callable[[str], None],
) -> MeasurementImportResult | None:
    if not paths:
        return None
    imported = 0
    warnings: list[str] = []
    for path in paths:
        try:
            text = read_import_text(path, errors="replace")
            s2p_port = 1
            if path.suffix.lower() == ".s2p":
                selected = _choose_s2p_port(parent, translator, path.name)
                if selected is None:
                    continue
                s2p_port = selected
            parsed = _parse_vna_with_mapping(
                parent,
                translator,
                mappings,
                text,
                path,
                s2p_port,
            )
            details = MeasurementDetailsDialog(
                translator,
                path.stem,
                parent,
                sessions=project.measurement_sessions,
            )
            if details.exec() != QDialog.DialogCode.Accepted:
                continue
            name, existing_id = _measurement_target(
                project,
                parent,
                translator,
                details.name() or path.stem,
            )
            if name is None:
                continue
            measurement = Measurement(
                id=existing_id or uuid4(),
                name=name,
                created_at=utc_now(),
                reference_impedance_ohm=parsed.reference_impedance_ohm,
                points=parsed.points,
                source=(
                    f"{path} · {parsed.profile}"
                    + (f" · {parsed.mapping}" if parsed.mapping else "")
                ),
                calibration=details.calibration(),
                reference_plane=details.reference_plane(),
                feed_line=details.feed_line(),
                notes=details.notes(),
                session_id=details.session_id(),
            )
            if existing_id is None:
                project = project.with_measurement(measurement, updated_at=utc_now())
            else:
                project = project.with_updated_measurement(measurement, updated_at=utc_now())
            imported += 1
            warnings.extend(parsed.warnings)
        except Exception as exc:
            show_error(
                translator.t(
                    "error.import_vna_file",
                    name=path.name,
                    message=str(exc),
                )
            )
            continue
    if imported == 0:
        return None
    return MeasurementImportResult(
        project=project,
        imported=imported,
        warnings=tuple(warnings),
    )


def choose_and_import_nec(
    parent: QWidget,
    translator: Translator,
) -> ImportedProject | None:
    filename, _ = QFileDialog.getOpenFileName(
        parent,
        translator.t("dialog.nec_title"),
        str(Path.home()),
        translator.t("dialog.nec_filter"),
    )
    if not filename:
        return None
    path = Path(filename)
    result = parse_nec2_deck(read_import_text(path))
    project = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name=path.stem,
            variant_name="Imported",
            parameters=result.parameters,
        )
    )
    return ImportedProject(project=project, warnings=result.warnings)


def choose_and_import_mmana(
    parent: QWidget,
    translator: Translator,
) -> ImportedProject | None:
    filename, _ = QFileDialog.getOpenFileName(
        parent,
        translator.t("dialog.mmana_title"),
        str(Path.home()),
        translator.t("dialog.mmana_filter"),
    )
    if not filename:
        return None
    path = Path(filename)
    result = parse_mmana_file(read_import_text(path))
    project = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name=path.stem,
            variant_name="Imported",
            parameters=result.parameters,
        )
    )
    return ImportedProject(project=project, warnings=result.warnings)
