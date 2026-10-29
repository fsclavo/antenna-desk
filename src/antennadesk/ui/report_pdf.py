# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Native PDF simulation report."""

from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import QByteArray, QMarginsF, QRectF, Qt
from PySide6.QtGui import (
    QFont,
    QImage,
    QPageLayout,
    QPageSize,
    QPainter,
    QPdfWriter,
)
from PySide6.QtSvg import QSvgRenderer

from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.resonance import find_resonances
from ..domain.simulation.result import SimulationResult
from ..reporting.design_summary import design_summary_rows
from ..reporting.svg_chart import SvgSeries, line_chart_svg
from .i18n import Translator

COLOR_A = "#1f5fa8"
COLOR_B = "#d07b1f"
COLOR_C = "#2e8b57"


def _svg_image(svg: str, width: int = 760, height: int = 260) -> QImage:
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    image.fill("white")
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    return image


def _chart_series(result: SimulationResult) -> tuple[QImage, QImage]:
    x = [frequency.frequency_hz / 1e6 for frequency in result.frequencies]
    resistance = [frequency.impedance_ohm.real for frequency in result.frequencies]
    reactance = [frequency.impedance_ohm.imag for frequency in result.frequencies]
    impedance = line_chart_svg(
        title="Impedance",
        x_label="Frequency (MHz)",
        y_label="Impedance (Ω)",
        series=(
            SvgSeries("R", COLOR_A, tuple(zip(x, resistance, strict=True))),
            SvgSeries("X", COLOR_B, tuple(zip(x, reactance, strict=True))),
        ),
    )
    swr_points = tuple(
        (frequency.frequency_hz / 1e6, frequency.swr)
        for frequency in result.frequencies
        if math.isfinite(frequency.swr)
    )
    swr = line_chart_svg(
        title="SWR",
        x_label="Frequency (MHz)",
        y_label="SWR",
        series=(SvgSeries("SWR", COLOR_C, swr_points),),
    )
    return _svg_image(impedance), _svg_image(swr)


def write_report_pdf(
    translator: Translator,
    project: Project,
    design: DesignVariant,
    result: SimulationResult,
    path: Path,
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
    content_width = right - left
    top = 38.0
    bottom = writer.height() - 42.0
    y = top
    title_font = QFont("Sans Serif", 16, QFont.Weight.Bold)
    section_font = QFont("Sans Serif", 11, QFont.Weight.Bold)
    body_font = QFont("Sans Serif", 9)
    small_font = QFont("Sans Serif", 8)

    def new_page() -> None:
        nonlocal y
        writer.newPage()
        y = top

    def ensure(height: float) -> None:
        if y + height > bottom:
            new_page()

    def section(title: str) -> None:
        nonlocal y
        ensure(34.0)
        painter.setFont(section_font)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(QRectF(left, y, content_width, 20.0), title)
        y += 24.0
        painter.setPen(Qt.GlobalColor.gray)
        painter.drawLine(int(left), int(y - 8.0), int(right), int(y - 8.0))
        y += 4.0

    def row(label: str, value: str) -> None:
        nonlocal y
        painter.setFont(body_font)
        label_width = 170.0
        text_height = max(
            painter.boundingRect(
                QRectF(0, 0, label_width, 10_000), Qt.TextFlag.TextWordWrap, label
            ).height(),
            painter.boundingRect(
                QRectF(0, 0, content_width - label_width - 8.0, 10_000),
                Qt.TextFlag.TextWordWrap,
                value,
            ).height(),
        )
        ensure(text_height + 5.0)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(QRectF(left, y, label_width, text_height), label)
        painter.drawText(
            QRectF(left + label_width + 8.0, y, content_width - label_width - 8.0, text_height),
            value,
        )
        y += text_height + 5.0

    def table(headers: list[str], rows: list[list[str]], widths: list[float]) -> None:
        nonlocal y
        row_height = 18.0
        total = sum(widths)
        columns = [content_width * width / total for width in widths]
        header_font = QFont("Sans Serif", 8, QFont.Weight.Bold)
        painter.setFont(header_font)
        ensure(row_height * 2.0)
        x = left
        for header, column in zip(headers, columns, strict=True):
            painter.drawText(QRectF(x + 2.0, y, column - 4.0, row_height), header)
            x += column
        y += row_height
        painter.setFont(small_font)
        for values in rows:
            if y + row_height > bottom:
                new_page()
                painter.setFont(header_font)
                x = left
                for header, column in zip(headers, columns, strict=True):
                    painter.drawText(QRectF(x + 2.0, y, column - 4.0, row_height), header)
                    x += column
                y += row_height
                painter.setFont(small_font)
            x = left
            for value, column in zip(values, columns, strict=True):
                painter.drawText(QRectF(x + 2.0, y, column - 4.0, row_height), value)
                x += column
            y += row_height
        y += 8.0

    def paragraph(text: str) -> None:
        nonlocal y
        painter.setFont(body_font)
        height = painter.boundingRect(
            QRectF(0, 0, content_width, 10_000), Qt.TextFlag.TextWordWrap, text
        ).height()
        ensure(height + 6.0)
        painter.drawText(QRectF(left, y, content_width, height), Qt.TextFlag.TextWordWrap, text)
        y += height + 6.0

    def chart(image: QImage) -> None:
        nonlocal y
        height = content_width * image.height() / image.width()
        ensure(height + 12.0)
        painter.drawImage(QRectF(left, y, content_width, height), image)
        y += height + 12.0

    painter.setFont(title_font)
    painter.drawText(QRectF(left, y, content_width, 30.0), f"{project.name} — {design.name}")
    y += 30.0
    painter.setFont(small_font)
    painter.setPen(Qt.GlobalColor.darkGray)
    finished = (
        result.finished_at.isoformat(timespec="seconds")
        if result.finished_at is not None
        else translator.t("report.not_recorded")
    )
    painter.drawText(
        QRectF(left, y, content_width, 16.0),
        translator.t("report.pdf_subtitle", finished=finished),
    )
    y += 30.0

    section(translator.t("report.reproducibility"))
    row(translator.t("results.fingerprint"), result.model_fingerprint)
    row(translator.t("results.solver"), f"{result.solver.name} {result.solver.version}")
    row(translator.t("results.status"), translator.t(f"status_value.{result.status.value}"))

    section(translator.t("panel.design"))
    for label, value in design_summary_rows(design.parameters):
        row(label, value)

    section(translator.t("report.configuration"))
    frequency_plan = result.spec.frequency_plan
    if frequency_plan.is_single:
        plan = f"{frequency_plan.start_hz / 1e6:g} MHz"
    else:
        plan = (
            f"{frequency_plan.start_hz / 1e6:g}-{frequency_plan.stop_hz / 1e6:g} MHz, "
            f"{frequency_plan.count} points"
        )
    row(translator.t("report.frequency_plan"), plan)
    row(
        translator.t("report.reference_impedance"),
        f"{result.spec.reference_impedance_ohm:g} Ω",
    )
    row(
        translator.t("report.conductor_losses"),
        translator.t(
            "report.enabled" if result.spec.include_conductor_losses else "report.disabled"
        ),
    )
    row(
        translator.t("report.far_field"),
        translator.t("report.enabled" if result.spec.far_field.enabled else "report.disabled"),
    )

    section(translator.t("tab.impedance"))
    table(
        [
            translator.t("table.frequency"),
            translator.t("table.resistance"),
            translator.t("table.reactance"),
            translator.t("table.impedance"),
            translator.t("table.swr"),
        ],
        [
            [
                f"{frequency.frequency_hz / 1e6:.6f}",
                f"{frequency.impedance_ohm.real:.3f}",
                f"{frequency.impedance_ohm.imag:+.3f}",
                f"{abs(frequency.impedance_ohm):.3f}",
                "∞" if math.isinf(frequency.swr) else f"{frequency.swr:.3f}",
            ]
            for frequency in result.frequencies
        ],
        [1.2, 1.0, 1.0, 1.0, 1.0],
    )

    section(translator.t("report.resonance"))
    resonances = find_resonances(
        [frequency.frequency_hz for frequency in result.frequencies],
        [frequency.impedance_ohm for frequency in result.frequencies],
    )
    if resonances:
        paragraph(
            " · ".join(
                f"{point.frequency_hz / 1e6:.3f} MHz (R={point.impedance_ohm.real:.1f} Ω)"
                for point in resonances
            )
        )
    else:
        paragraph(translator.t("construction.no_resonance"))

    section(translator.t("report.charts"))
    impedance_image, swr_image = _chart_series(result)
    chart(impedance_image)
    chart(swr_image)

    section(translator.t("tab.diagnostics"))
    if result.diagnostics:
        table(
            [
                translator.t("diagnostic.severity"),
                translator.t("diagnostic.code"),
                translator.t("diagnostic.message"),
            ],
            [
                [
                    translator.t(f"severity.{diagnostic.severity.value}"),
                    diagnostic.code,
                    diagnostic.message,
                ]
                for diagnostic in result.diagnostics
            ],
            [0.8, 1.4, 3.0],
        )
    else:
        paragraph(translator.t("diagnostic.none"))

    painter.setFont(small_font)
    painter.setPen(Qt.GlobalColor.darkGray)
    painter.drawText(
        QRectF(left, writer.height() - 28.0, content_width, 16.0),
        translator.t("construction.pdf_footer"),
    )
    painter.end()
