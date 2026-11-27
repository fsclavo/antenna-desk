# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Resolve a usable system font for offscreen layout tests."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QFont, QFontDatabase

_PREFERRED_FAMILIES = (
    "Segoe UI",
    "Arial",
    "Noto Sans",
    "DejaVu Sans",
    "Liberation Sans",
    "Tahoma",
    "Verdana",
)
_FONT_FILE_CANDIDATES = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"),
    Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    Path("C:/Windows/Fonts/segoeui.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("C:/Windows/Fonts/tahoma.ttf"),
)


def _font(family: str, point_size: float) -> QFont:
    font = QFont(family)
    font.setPointSizeF(point_size)
    return font


def resolved_test_font(point_size: float = 10.0) -> QFont:
    """Return a font with a real family and point size on every CI platform.

    The Windows offscreen platform can expose an unresolved default font and
    an empty family list. Prefer a common system family; if Qt has no families
    at all, add a standard system font file before giving up.
    """

    families = set(QFontDatabase.families())
    for family in _PREFERRED_FAMILIES:
        if family in families:
            return _font(family, point_size)
    if families:
        return _font(sorted(families)[0], point_size)

    for path in _FONT_FILE_CANDIDATES:
        if not path.is_file():
            continue
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id < 0:
            continue
        added = QFontDatabase.applicationFontFamilies(font_id)
        if added:
            return _font(added[0], point_size)

    raise RuntimeError("no usable system font is available for offscreen UI tests")
