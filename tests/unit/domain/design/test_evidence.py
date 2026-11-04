# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Consistency checks for the template evidence registry."""

from __future__ import annotations

from pathlib import Path

import pytest

from antennadesk.domain.design.evidence import (
    EVIDENCE,
    EvidenceLevel,
    evidence_for,
    render_markdown_table,
)
from antennadesk.ui.dialogs.antenna_catalog_dialog import ENTRIES

START = "<!-- evidence-table:start -->"
END = "<!-- evidence-table:end -->"
VALIDATION_PLAN = Path(__file__).resolve().parents[4] / "docs" / "VALIDATION_PLAN.md"


def test_every_catalog_template_has_an_evidence_entry() -> None:
    catalog = {entry.key for entry in ENTRIES}

    assert set(EVIDENCE) == catalog


def test_catalog_keys_are_unique() -> None:
    keys = [entry.key for entry in ENTRIES]

    assert len(keys) == len(set(keys))


def test_entries_are_complete_and_keyed_by_their_template() -> None:
    for key, entry in EVIDENCE.items():
        assert entry.template == key
        assert entry.source.strip()
        assert entry.tolerance.strip()
        assert entry.limitation.strip()


def test_reference_backed_entries_have_a_numeric_tolerance() -> None:
    for entry in EVIDENCE.values():
        if entry.level is not EvidenceLevel.REFERENCE:
            continue
        assert "Not applicable" not in entry.tolerance, entry.template


def test_validation_plan_table_matches_the_registry() -> None:
    text = VALIDATION_PLAN.read_text(encoding="utf-8")
    block = text.split(START)[1].split(END)[0].strip()

    assert block == render_markdown_table()


def test_unknown_template_raises() -> None:
    with pytest.raises(KeyError):
        evidence_for("not-a-template")
