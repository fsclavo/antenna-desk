# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optional label translation for reports without a Qt dependency.

Reporting modules are deliberately Qt-free.  They build English documents by
default and accept a caller-supplied ``labeler`` when the UI wants another
language.  The callback receives the English source text and optional named
format values, so a translation can reorder placeholders without the report
knowing about the target language.
"""

from __future__ import annotations

import html
import re
from collections.abc import Iterable
from typing import Protocol


class Labeler(Protocol):
    """Translate one English report label or template."""

    def __call__(self, text: str, /, **values: object) -> str: ...


def identity_labeler(text: str, /, **values: object) -> str:
    """Return the English source text, formatting named placeholders."""

    return text.format(**values) if values else text


def localize_rows(
    rows: Iterable[tuple[str, str]],
    labeler: Labeler | None,
) -> tuple[tuple[str, str], ...]:
    """Translate both the label and the value of report rows.

    Values are usually numbers or units, which the labeler returns unchanged.
    Translating them too covers generated names such as ``yes``, ``Copper``,
    or ``horizontal`` without duplicating a value table in every renderer.
    """

    if labeler is None:
        return tuple(rows)
    return tuple((labeler(label), labeler(value)) for label, value in rows)


_LABEL_TAG = re.compile(
    r"<(?P<tag>th|h2|figcaption)(?P<attributes>[^>]*)>"
    r"(?P<text>[^<]*)"
    r"</(?P=tag)>"
)


def localize_html_labels(markup: str, labeler: Labeler | None) -> str:
    """Translate text nodes of table headers, section headings, and captions.

    Only these structural elements are touched.  Cell values, user project
    names, wire identifiers, and numbers keep their canonical form.
    """

    if labeler is None:
        return markup

    def replace(match: re.Match[str]) -> str:
        raw = match.group("text").strip()
        if not raw or "<" in raw:
            return match.group(0)
        text = html.unescape(raw)
        translated = labeler(text)
        if translated == text:
            return match.group(0)
        return (
            f"<{match.group('tag')}{match.group('attributes')}>"
            f"{html.escape(translated, quote=False)}"
            f"</{match.group('tag')}>"
        )

    return _LABEL_TAG.sub(replace, markup)
