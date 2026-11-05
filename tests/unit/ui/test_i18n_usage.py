# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Every user-visible string in the UI must resolve through the translator.

The UI is maintained in two languages by hand. A literal passed to a Qt text
setter bypasses the translation tables, and a missing key renders as the raw
key. These tests catch both cases statically, without instantiating widgets.
"""

from __future__ import annotations

import ast
from pathlib import Path

from antennadesk.ui.i18n import _TRANSLATIONS

UI_ROOT = Path(__file__).resolve().parents[3] / "src" / "antennadesk" / "ui"

# Methods whose first string argument is user-visible.
TEXT_ARG_INDEX = {
    "setText": 0,
    "setWindowTitle": 0,
    "setPlaceholderText": 0,
    "setToolTip": 0,
    "setStatusTip": 0,
    "setWhatsThis": 0,
    "setTitle": 0,
    "setSubTitle": 0,
    "setLabelText": 0,
    "setInformativeText": 0,
    "setApplicationDisplayName": 0,
    "setApplicationName": 0,
    "setOrganizationName": 0,
    "addMenu": 0,
    "addItem": 0,
}
# Qt methods where the text is not the first argument.
SECOND_TEXT_ARG = {"addTab", "setItemText", "setTabText"}
# Widget constructors whose first argument can be a visible label.
CONSTRUCTORS = {
    "QAction",
    "QCheckBox",
    "QGroupBox",
    "QLabel",
    "QListWidgetItem",
    "QPushButton",
    "QTableWidgetItem",
}
# MessageBox helpers: title and text follow the parent widget.
MESSAGE_BOXES = {"information", "warning", "question", "critical"}

# Symbols, units, technical labels, and brand names that are not translated.
ALLOWED_LITERALS = frozenset(
    {
        "",
        " ",
        "—",
        "X",
        "Y",
        "dBi",
        "L",
        "Pi",
        "T",
        "l",
        "pi",
        "t",
        "1/4 λ",
        "1/2 λ",
        "5/8 λ",
        "bottom",
        "left",
        "top",
        "right",
        "MHz",
        "kHz",
        "Hz",
        "mm",
        "cm",
        "m",
        "ft",
        "in",
        "°",
        "Ω",
        "µH",
        "pF",
        "S/m",
        "%",
        "dB",
        "dB/100m",
        "dB/100 m",
        "AntennaDesk",
        "7.1, 14.1, 21.0",
    }
)


def _literal_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return None


def _translation_key_calls() -> list[tuple[Path, int, str]]:
    keys: list[tuple[Path, int, str]] = []
    for path in sorted(UI_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = _call_name(node)
            index: int | None = None
            if name in {"t", "_label"}:
                index = 0
            elif name == "_add_row":
                index = 1
            if index is None or len(node.args) <= index:
                continue
            key = _literal_string(node.args[index])
            if key is not None:
                keys.append((path, node.lineno, key))
    return keys


def _visible_literals() -> list[tuple[Path, int, str]]:
    literals: list[tuple[Path, int, str]] = []
    for path in sorted(UI_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = _call_name(node)
            if name is None:
                continue
            values: list[str] = []
            if name == "drawText":
                values = [value for arg in node.args if (value := _literal_string(arg)) is not None]
            elif name in MESSAGE_BOXES:
                values = [
                    value for arg in node.args[1:3] if (value := _literal_string(arg)) is not None
                ]
            elif name in TEXT_ARG_INDEX:
                index = TEXT_ARG_INDEX[name]
                if len(node.args) > index:
                    value = _literal_string(node.args[index])
                    if value is not None:
                        values = [value]
            elif name in SECOND_TEXT_ARG:
                if len(node.args) > 1:
                    value = _literal_string(node.args[1])
                    if value is not None:
                        values = [value]
            elif name in CONSTRUCTORS and node.args:
                value = _literal_string(node.args[0])
                if value is not None:
                    values = [value]
            for value in values:
                if value not in ALLOWED_LITERALS:
                    literals.append((path, node.lineno, value))
    return literals


def test_every_translation_key_used_in_ui_exists() -> None:
    missing = [
        (path, line, key)
        for path, line, key in _translation_key_calls()
        if key not in _TRANSLATIONS
    ]

    assert not missing, "\n".join(
        f"{path}:{line}: missing translation key {key!r}" for path, line, key in missing
    )


def test_every_user_visible_literal_is_technical_or_translated() -> None:
    untranslated = _visible_literals()

    assert not untranslated, "\n".join(
        f"{path}:{line}: untranslated visible literal {value!r}"
        for path, line, value in untranslated
    )
