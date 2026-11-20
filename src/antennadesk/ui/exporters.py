# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""File dialogs and writers for result, geometry, and report exports."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from PySide6.QtWidgets import QFileDialog, QWidget

from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.band_result import BandAnalysisResult
from ..domain.simulation.result import SimulationResult
from ..presentation.units import DisplayUnits
from ..reporting.csv_export import (
    write_band_analysis_csv,
    write_band_analysis_pattern_csv,
    write_band_analysis_sources_csv,
    write_csv,
    write_pattern_csv,
    write_sources_csv,
)
from ..reporting.html_report import write_html_report
from ..reporting.touchstone import format_touchstone_s1p
from ..reporting.wire_schedule import write_bom_csv, write_wire_schedule_csv
from .i18n import Translator
from .report_pdf import write_report_pdf
from .widgets.geometry_view import GeometryView


class ExportFailure(Exception):
    """An export cannot be completed; the key is a user-facing message."""

    def __init__(self, message_key: str = "error.export", *, detail: str = "") -> None:
        self.message_key = message_key
        self.detail = detail
        super().__init__(detail or message_key)


class GeometrySaver(Protocol):
    def save_image(self, path: Path) -> None: ...
    def save_svg(self, path: Path) -> None: ...
    def save_pdf(self, path: Path) -> None: ...
    def save_dxf(self, path: Path) -> None: ...


class PatternSaver(Protocol):
    def save_pattern_image(self, path: Path) -> bool: ...
    def save_band_pattern_images(self, paths: tuple[Path, ...]) -> bool: ...


@dataclass(frozen=True, slots=True)
class ExportContext:
    parent: QWidget
    translator: Translator
    project: Project
    design: DesignVariant
    display_units: DisplayUnits
    result: SimulationResult | None = None
    band_analysis: BandAnalysisResult | None = None
    include_3d: bool = True
    include_band_3d: bool = False


def safe_file_name(value: str) -> str:
    return value.replace("/", "-").replace("\\", "-").replace(":", "-")


def _safe_stem(context: ExportContext) -> str:
    return f"{safe_file_name(context.project.name)}-{safe_file_name(context.design.name)}"


def _require_result(context: ExportContext) -> SimulationResult:
    if context.result is None:
        raise ExportFailure("error.no_result")
    return context.result


def _save_path(
    context: ExportContext,
    *,
    title_key: str,
    filter_key: str,
    suggested: str,
    suffix: str,
    accepted: tuple[str, ...] | None = None,
) -> Path | None:
    filename, _ = QFileDialog.getSaveFileName(
        context.parent,
        context.translator.t(title_key),
        str(Path.home() / suggested),
        context.translator.t(filter_key),
    )
    if not filename:
        return None
    path = Path(filename)
    accepted_suffixes = accepted or (suffix,)
    if path.suffix.lower() not in accepted_suffixes:
        path = path.with_suffix(suffix)
    return path


def export_frequency_csv(context: ExportContext) -> Path | None:
    result = _require_result(context)
    path = _save_path(
        context,
        title_key="dialog.csv_title",
        filter_key="dialog.csv_filter",
        suggested=f"{_safe_stem(context)}.csv",
        suffix=".csv",
    )
    if path is None:
        return None
    if context.band_analysis is not None:
        write_band_analysis_csv(context.band_analysis, path)
    else:
        write_csv(result, path)
    return path


def export_sources_csv(context: ExportContext) -> Path | None:
    result = _require_result(context)
    path = _save_path(
        context,
        title_key="dialog.sources_csv_title",
        filter_key="dialog.csv_filter",
        suggested=f"{_safe_stem(context)}-sources.csv",
        suffix=".csv",
    )
    if path is None:
        return None
    if context.band_analysis is not None:
        write_band_analysis_sources_csv(context.band_analysis, path)
    else:
        write_sources_csv(result, path)
    return path


def export_pattern_csv(context: ExportContext) -> Path | None:
    result = _require_result(context)
    path = _save_path(
        context,
        title_key="dialog.pattern_csv_title",
        filter_key="dialog.csv_filter",
        suggested=f"{_safe_stem(context)}-pattern.csv",
        suffix=".csv",
    )
    if path is None:
        return None
    if context.band_analysis is not None:
        write_band_analysis_pattern_csv(context.band_analysis, path)
    else:
        write_pattern_csv(result, path)
    return path


def export_touchstone(context: ExportContext) -> Path | None:
    result = _require_result(context)
    path = _save_path(
        context,
        title_key="dialog.touchstone_title",
        filter_key="dialog.touchstone_filter",
        suggested=f"{_safe_stem(context)}.s1p",
        suffix=".s1p",
    )
    if path is None:
        return None
    text = format_touchstone_s1p(
        [(frequency.frequency_hz, frequency.impedance_ohm) for frequency in result.frequencies],
        result.spec.reference_impedance_ohm,
        comments=(f"Project: {context.project.name}", f"Design: {context.design.name}"),
    )
    path.write_text(text, encoding="utf-8")
    return path


def export_wire_schedule_csv(context: ExportContext) -> Path | None:
    path = _save_path(
        context,
        title_key="dialog.wire_schedule_csv_title",
        filter_key="dialog.csv_filter",
        suggested=f"{_safe_stem(context)}-wire-schedule.csv",
        suffix=".csv",
    )
    if path is None:
        return None
    write_wire_schedule_csv(context.design, path)
    return path


def export_bom_csv(context: ExportContext) -> Path | None:
    path = _save_path(
        context,
        title_key="dialog.bom_csv_title",
        filter_key="dialog.csv_filter",
        suggested=f"{_safe_stem(context)}-bom.csv",
        suffix=".csv",
    )
    if path is None:
        return None
    write_bom_csv(context.design, path, costs=context.project.bom_costs)
    return path


def _geometry_path(
    context: ExportContext, *, title_key: str, filter_key: str, suffix: str
) -> Path | None:
    return _save_path(
        context,
        title_key=title_key,
        filter_key=filter_key,
        suggested=f"{_safe_stem(context)}-geometry{suffix}",
        suffix=suffix,
    )


def export_geometry_png(context: ExportContext, geometry: GeometrySaver) -> Path | None:
    path = _geometry_path(
        context,
        title_key="dialog.geometry_png_title",
        filter_key="dialog.png_filter",
        suffix=".png",
    )
    if path is None:
        return None
    geometry.save_image(path)
    return path


def export_geometry_svg(context: ExportContext, geometry: GeometrySaver) -> Path | None:
    path = _geometry_path(
        context,
        title_key="dialog.geometry_svg_title",
        filter_key="dialog.svg_filter",
        suffix=".svg",
    )
    if path is None:
        return None
    geometry.save_svg(path)
    return path


def export_geometry_pdf(context: ExportContext, geometry: GeometrySaver) -> Path | None:
    path = _geometry_path(
        context,
        title_key="dialog.geometry_pdf_title",
        filter_key="dialog.pdf_filter",
        suffix=".pdf",
    )
    if path is None:
        return None
    geometry.save_pdf(path)
    return path


def export_geometry_dxf(context: ExportContext, geometry: GeometrySaver) -> Path | None:
    path = _geometry_path(
        context,
        title_key="dialog.geometry_dxf_title",
        filter_key="dialog.dxf_filter",
        suffix=".dxf",
    )
    if path is None:
        return None
    geometry.save_dxf(path)
    return path


def export_pattern_png(context: ExportContext, results: PatternSaver) -> Path | None:
    stem = _safe_stem(context)
    analysis = context.band_analysis
    if analysis is not None and analysis.bands:
        directory = QFileDialog.getExistingDirectory(
            context.parent,
            context.translator.t("dialog.band_pattern_png_title"),
            str(Path.home()),
        )
        if not directory:
            return None
        paths = tuple(
            Path(directory) / f"{stem}-{safe_file_name(band.band.name)}-pattern.png"
            for band in analysis.bands
        )
        if not results.save_band_pattern_images(paths):
            raise ExportFailure("error.no_result")
        return Path(directory)
    _require_result(context)
    path = _save_path(
        context,
        title_key="dialog.pattern_png_title",
        filter_key="dialog.png_filter",
        suggested=f"{stem}-pattern.png",
        suffix=".png",
    )
    if path is None:
        return None
    results.save_pattern_image(path)
    return path


def _report_geometry_svg(context: ExportContext) -> str | None:
    view = GeometryView(
        context.translator,
        context.display_units.system,
        display_units=context.display_units,
    )
    view.set_export_theme()
    view.set_model(
        context.design.antenna,
        antenna_type=context.design.antenna_type,
        display_name=context.design.name,
        parameters=context.design.parameters,
    )
    try:
        return view.construction_svg(1200, 650).decode("utf-8")
    except Exception:
        return None
    finally:
        view.deleteLater()


def export_html_report(context: ExportContext) -> Path | None:
    result = _require_result(context)
    path = _save_path(
        context,
        title_key="dialog.html_title",
        filter_key="dialog.html_filter",
        suggested=f"{_safe_stem(context)}.html",
        suffix=".html",
        accepted=(".html", ".htm"),
    )
    if path is None:
        return None
    write_html_report(
        context.project,
        context.design,
        result,
        path,
        band_analysis=context.band_analysis,
        labeler=context.translator.report,
        language=context.translator.language.value,
        geometry_svg=_report_geometry_svg(context),
        display_units=context.display_units,
        include_pattern_lobe=context.include_3d,
        include_band_pattern_lobes=context.include_band_3d,
    )
    return path


def export_pdf_report(context: ExportContext) -> Path | None:
    result = _require_result(context)
    path = _save_path(
        context,
        title_key="dialog.pdf_title",
        filter_key="dialog.pdf_filter",
        suggested=f"{_safe_stem(context)}.pdf",
        suffix=".pdf",
    )
    if path is None:
        return None
    write_report_pdf(
        context.translator,
        context.project,
        context.design,
        result,
        path,
        band_analysis=context.band_analysis,
        geometry_svg=_report_geometry_svg(context),
        include_pattern_lobe=context.include_3d,
        include_band_pattern_lobes=context.include_band_3d,
    )
    return path


def save_nec_deck(context: ExportContext, text: str) -> Path | None:
    path = _save_path(
        context,
        title_key="dialog.export_nec_title",
        filter_key="dialog.export_nec_filter",
        suggested=f"{_safe_stem(context)}.nec",
        suffix=".nec",
    )
    if path is None:
        return None
    path.write_text(text, encoding="utf-8")
    return path
