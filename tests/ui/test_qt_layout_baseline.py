# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""UX58 deterministic offscreen layout baseline."""

from __future__ import annotations

import math
import os

from PySide6.QtGui import QFontInfo, QFontMetrics, QGuiApplication
from PySide6.QtWidgets import QApplication


def test_qt_layout_baseline_is_documented_and_deterministic() -> None:
    app = QApplication.instance()
    assert isinstance(app, QApplication)
    assert os.environ["QT_FONT_DPI"] == "96"
    assert os.environ["QT_SCALE_FACTOR"] == "1"

    screen = QGuiApplication.primaryScreen()
    assert screen is not None
    font = app.font()
    info = QFontInfo(font)
    metrics = QFontMetrics(font)
    dpi = screen.logicalDotsPerInch()
    ratio = screen.devicePixelRatio()
    available = screen.availableGeometry()
    height = metrics.height()
    advance = metrics.horizontalAdvance("Frecuencia (MHz)")

    # Keep this line visible in the Windows CI log: the layout batch runs with
    # -s so the next environment change is diagnosable from the run itself.
    print(  # noqa: T201 - intentional diagnostic for the Windows CI log
        "UX58 layout baseline: "
        f"family={info.family()!r} point_size={info.pointSizeF():.2f}pt "
        f"pixel_size={info.pixelSize()}px dpi={dpi:.1f} "
        f"device_pixel_ratio={ratio:.2f} style={app.style().name()!r} "
        f"font_height={height}px advance={advance}px "
        f"available={available.width()}x{available.height()}",
        flush=True,
    )

    assert 9.0 <= info.pointSizeF() <= 10.0
    assert info.family()
    assert info.pixelSize() > 0
    assert math.isfinite(dpi)
    assert dpi > 0.0
    assert math.isfinite(ratio)
    assert ratio > 0.0
    assert height > 0
    assert advance > 0
    assert available.width() > 0
    assert available.height() > 0
    assert app.style().name()
