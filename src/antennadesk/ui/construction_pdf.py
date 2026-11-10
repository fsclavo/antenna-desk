# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Native PDF construction sheet."""

from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import QByteArray, QMarginsF, QRectF, QSize, Qt
from PySide6.QtGui import QFont, QImage, QPageLayout, QPageSize, QPainter, QPdfWriter
from PySide6.QtSvg import QSvgRenderer

from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.resonance import find_resonances
from ..domain.simulation.result import SimulationResult
from ..reporting.design_summary import (
    design_evidence_rows,
    design_provenance_rows,
    design_summary_rows,
    load_summary_rows,
    optimization_summary_rows,
)
from ..reporting.localization import localize_rows
from ..reporting.wire_schedule import (
    bom_summary_rows,
    conductor_bom_rows,
    wire_schedule_lines,
)
from .i18n import Translator


def _wrap(painter: QPainter, text: str, width: float) -> float:
    rect = painter.boundingRect(
        QRectF(0.0, 0.0, width, 10_000.0),
        Qt.TextFlag.TextWordWrap,
        text,
    )
    return rect.height()


def _svg_renderer(svg: bytes | None) -> QSvgRenderer | None:
    if not svg:
        return None
    renderer = QSvgRenderer(QByteArray(svg))
    return renderer if renderer.isValid() else None


def _figure_size(image: QImage | None, svg: bytes | None) -> QSize | None:
    renderer = _svg_renderer(svg)
    if renderer is not None:
        size = renderer.defaultSize()
        if not size.isEmpty():
            return size
        box = renderer.viewBoxF()
        if not box.isEmpty():
            return QSize(round(box.width()), round(box.height()))
    if image is not None and not image.isNull():
        return image.size()
    return None


def _draw_figure(
    painter: QPainter,
    rect: QRectF,
    image: QImage | None,
    svg: bytes | None,
) -> None:
    renderer = _svg_renderer(svg)
    if renderer is not None:
        renderer.render(painter, rect)
        return
    if image is not None and not image.isNull():
        painter.drawImage(rect, image)


def write_construction_pdf(
    translator: Translator,
    project: Project,
    design: DesignVariant,
    result: SimulationResult | None,
    path: Path,
    *,
    figure_image: QImage | None = None,
    auxiliary_image: QImage | None = None,
    figure_svg: bytes | None = None,
    auxiliary_svg: bytes | None = None,
    auxiliary_kind: str | None = None,
) -> None:
    writer = QPdfWriter(str(path))
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(QMarginsF(12.0, 12.0, 12.0, 12.0), QPageLayout.Unit.Millimeter)
    writer.setResolution(96)
    painter = QPainter(writer)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    width = writer.width()
    left = 32.0
    right = width - 32.0
    y = 40.0
    title_font = QFont("Sans Serif", 16, QFont.Weight.Bold)
    section_font = QFont("Sans Serif", 11, QFont.Weight.Bold)
    body_font = QFont("Sans Serif", 9)
    small_font = QFont("Sans Serif", 8)
    painter.setPen(Qt.GlobalColor.black)

    def ensure_space(height: float) -> None:
        nonlocal y
        if y + height > writer.height() - 40.0:
            writer.newPage()
            y = 40.0

    def section(title: str) -> None:
        nonlocal y
        ensure_space(34.0)
        painter.setFont(section_font)
        painter.drawText(QRectF(left, y, right - left, 20.0), title)
        y += 24.0
        painter.setPen(Qt.GlobalColor.gray)
        painter.drawLine(int(left), int(y - 8.0), int(right), int(y - 8.0))
        painter.setPen(Qt.GlobalColor.black)

    def row(label: str, value: str) -> None:
        nonlocal y
        painter.setFont(body_font)
        label_width = 150.0
        height = max(
            _wrap(painter, label, label_width),
            _wrap(painter, value, right - left - label_width - 8.0),
        )
        ensure_space(height + 5.0)
        painter.drawText(QRectF(left, y, label_width, height), label)
        painter.drawText(
            QRectF(left + label_width + 8.0, y, right - left - label_width - 8.0, height),
            value,
        )
        y += height + 5.0

    painter.setFont(title_font)
    painter.drawText(
        QRectF(left, y, right - left, 30.0),
        f"{project.name} — {design.name}",
    )
    y += 30.0
    painter.setFont(small_font)
    painter.setPen(Qt.GlobalColor.darkGray)
    painter.drawText(QRectF(left, y, right - left, 18.0), translator.t("construction.pdf_subtitle"))
    painter.setPen(Qt.GlobalColor.black)
    y += 30.0

    antenna_label = getattr(
        design.parameters,
        "template_name",
        design.antenna_type.replace("_", " ").title(),
    )
    row(translator.t("construction.project"), project.name)
    row(translator.t("construction.design"), design.name)
    row(translator.t("construction.antenna"), str(antenna_label))
    row(
        translator.t("construction.frequency"),
        f"{design.parameters.frequency_hz / 1e6:.6f} MHz",
    )
    row(translator.t("construction.units"), "SI (m, MHz, Ω)")
    row(translator.t("construction.updated"), project.updated_at.strftime("%Y-%m-%d"))
    y += 8.0

    def draw_figure(
        source_size: QSize,
        image: QImage | None,
        svg: bytes | None,
        max_fraction: float,
    ) -> None:
        nonlocal y
        available_width = right - left
        max_height = writer.height() * max_fraction
        scale = min(
            available_width / max(source_size.width(), 1),
            max_height / max(source_size.height(), 1),
        )
        draw_width = source_size.width() * scale
        draw_height = source_size.height() * scale
        ensure_space(draw_height + 12.0)
        _draw_figure(
            painter,
            QRectF(
                left + (available_width - draw_width) / 2.0,
                y,
                draw_width,
                draw_height,
            ),
            image,
            svg,
        )
        y += draw_height + 12.0

    figure_size = _figure_size(figure_image, figure_svg)
    if figure_size is not None:
        section(translator.t("construction.view"))
        draw_figure(figure_size, figure_image, figure_svg, 0.55)

    auxiliary_size = _figure_size(auxiliary_image, auxiliary_svg)
    if auxiliary_size is not None:
        auxiliary_key = (
            "construction.top_layout"
            if auxiliary_kind == "top"
            else "construction.installation_view"
        )
        section(translator.t(auxiliary_key))
        draw_figure(auxiliary_size, auxiliary_image, auxiliary_svg, 0.40)

    section(translator.t("construction.dimensions"))
    for label, value in localize_rows(
        (
            *design_summary_rows(design.parameters, labeler=translator.report),
            *optimization_summary_rows(design),
            *design_provenance_rows(design),
            *load_summary_rows(design.antenna.loads, labeler=translator.report),
        ),
        translator.report,
    ):
        row(label, value)
    if design.antenna.feed_wire is not None:
        feed_wire = design.antenna.feed_wire
        feed_ratio = design.antenna.feed.offset_m / feed_wire.length_m
        feed_z = feed_wire.start.z_m + (feed_wire.end.z_m - feed_wire.start.z_m) * feed_ratio
        row(
            translator.t("construction.feed_height"),
            f"{feed_z:.4f} m",
        )
    y += 12.0

    section(translator.t("construction.bom"))
    for row_item in conductor_bom_rows(design.antenna):
        row(
            translator.report(
                "{material} Ø{diameter:.3f} mm",
                material=translator.report(row_item.material),
                diameter=row_item.diameter_mm,
            ),
            translator.report(
                "{count} wires · {length:.4f} m",
                count=row_item.wire_count,
                length=row_item.total_length_m,
            ),
        )
    for label, value in localize_rows(
        bom_summary_rows(design.antenna),
        translator.report,
    ):
        row(label, value)
    y += 12.0

    evidence_rows = localize_rows(design_evidence_rows(design), translator.report)
    if evidence_rows:
        section(translator.t("construction.evidence"))
        for label, value in evidence_rows:
            row(label, value)
        y += 12.0

    section(translator.t("construction.wire_schedule"))
    for line in wire_schedule_lines(design, labeler=translator.report):
        row("", line)
    y += 12.0

    section(translator.t("construction.simulation"))
    if result is None:
        row(translator.t("construction.simulation"), translator.t("construction.no_result"))
    else:
        row(translator.t("construction.solver"), f"{result.solver.name} {result.solver.version}")
        row(translator.t("construction.fingerprint"), result.model_fingerprint)
        target = design.parameters.frequency_hz
        frequency = min(
            result.frequencies, key=lambda item: abs(item.frequency_hz - target), default=None
        )
        if frequency is not None:
            row(
                translator.t("construction.simulated_frequency"),
                f"{frequency.frequency_hz / 1e6:.6f} MHz",
            )
            row(
                translator.t("construction.impedance"),
                f"{frequency.impedance_ohm.real:.3f} {frequency.impedance_ohm.imag:+.3f}j Ω",
            )
            row(
                translator.t("table.swr"),
                "∞" if math.isinf(frequency.swr) else f"{frequency.swr:.3f}",
            )
            gains = [
                point.gain_total_db
                for item in result.frequencies
                for point in item.far_field
                if point.gain_total_db is not None
            ]
            if gains:
                row(translator.t("construction.max_gain"), f"{max(gains):.2f} dBi")
            if frequency.power_budget is not None:
                row(
                    translator.t("construction.efficiency"),
                    f"{frequency.power_budget.efficiency_percent:.2f} %",
                )
        resonances = find_resonances(
            [item.frequency_hz for item in result.frequencies],
            [item.impedance_ohm for item in result.frequencies],
        )
        row(
            translator.t("construction.resonance"),
            " · ".join(
                f"{point.frequency_hz / 1e6:.3f} MHz (R={point.impedance_ohm.real:.1f} Ω)"
                for point in resonances
            )
            or translator.t("construction.no_resonance"),
        )
    y += 12.0

    section(translator.t("construction.notes"))
    painter.setFont(body_font)
    note = translator.t("construction.pdf_notes")
    height = _wrap(painter, note, right - left)
    ensure_space(height + 10.0)
    painter.drawText(QRectF(left, y, right - left, height), Qt.TextFlag.TextWordWrap, note)
    y += height + 16.0

    painter.setFont(small_font)
    painter.setPen(Qt.GlobalColor.darkGray)
    painter.drawText(
        QRectF(left, writer.height() - 28.0, right - left, 16.0),
        translator.t("construction.pdf_footer"),
    )
    painter.end()
