# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Consistency checks for the English/Spanish translation tables.

The UI is maintained in two languages by hand, so these tests guard the
invariants that a missing or malformed entry breaks: every key has both
languages, no entry is blank, placeholders match, and the literal has no
duplicate keys that would silently overwrite a translation.
"""

from __future__ import annotations

import ast
from pathlib import Path
from string import Formatter

from antennadesk.ui import i18n
from antennadesk.ui.i18n import _TRANSLATIONS, Language, Translator


def _fields(formatter: Formatter, text: str) -> set[str]:
    return {name for _, name, _, _ in formatter.parse(text) if name}


def _translation_dict_node() -> ast.Dict:
    tree = ast.parse(Path(i18n.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.AnnAssign):
            continue
        target = node.target
        if isinstance(target, ast.Name) and target.id == "_TRANSLATIONS":
            assert isinstance(node.value, ast.Dict)
            return node.value
    raise AssertionError("_TRANSLATIONS assignment not found")


def test_every_key_has_every_language() -> None:
    expected = set(Language)
    for key, translations in _TRANSLATIONS.items():
        assert set(translations) == expected, key


def test_no_translation_is_blank() -> None:
    for key, translations in _TRANSLATIONS.items():
        for language, text in translations.items():
            assert text.strip(), f"{key} is blank in {language.value}"


def test_placeholders_match_across_languages() -> None:
    formatter = Formatter()
    for key, translations in _TRANSLATIONS.items():
        reference = _fields(formatter, translations[Language.ENGLISH])
        for language, text in translations.items():
            assert _fields(formatter, text) == reference, f"{key} in {language.value}"


def test_translation_literal_has_no_duplicate_keys() -> None:
    node = _translation_dict_node()
    keys = [key.value for key in node.keys if isinstance(key, ast.Constant)]
    duplicates = {key for key in keys if keys.count(key) > 1}
    assert not duplicates, f"duplicate translation keys: {sorted(duplicates)}"


def test_unknown_key_falls_back_to_the_key() -> None:
    assert Translator(Language.SPANISH).t("missing.key") == "missing.key"


def test_optional_returns_none_instead_of_a_raw_key() -> None:
    translator = Translator(Language.SPANISH)

    assert translator.optional("missing.key") is None
    assert translator.optional("help.field.frequency") is not None


def test_translator_formats_placeholders() -> None:
    text = Translator(Language.ENGLISH).t("app.about", version="1.2.3")
    assert "AntennaDesk 1.2.3" in text
