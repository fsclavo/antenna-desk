# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Native PDF construction sheet."""

from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import QMarginsF, QRectF, Qt
from PySide6.QtGui import QFont, QPageLayout, QPageSize, QPainter, QPdfWriter

from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.resonance import find_resonances
from ..domain.simulation.result import SimulationResult
from ..reporting.design_summary import design_summary_rows, load_summary_rows
from .i18n import Translator


def _wrap(painter: QPainter, text: str, width: float) -> float:
    rect = painter.boundingRect(
        QRectF(0.0, 0.0, width, 10_000.0),
        Qt.TextFlag.TextWordWrap,
        text,
    )
    return rect.height()


def write_construction_pdf(
    translator: Translator,
    project: Project,
    design: DesignVariant,
    result: SimulationResult | None,
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

    section(translator.t("construction.dimensions"))
    for label, value in (
        *design_summary_rows(design.parameters),
        *load_summary_rows(design.antenna.loads),
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
