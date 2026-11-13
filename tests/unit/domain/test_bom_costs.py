# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Manual BOM cost records."""

from __future__ import annotations

import pytest

from antennadesk.domain.projects.bom_costs import (
    MAX_BOM_COST_LINES,
    MAX_BOM_CURRENCY_LENGTH,
    BomCostLine,
    BomCostRecord,
)
from antennadesk.domain.projects.project import Project


def test_record_normalizes_currency_and_finds_costs() -> None:
    record = BomCostRecord(
        currency="  USD  ",
        lines=(
            BomCostLine("conductor:copper:2.000", 2.5),
            BomCostLine("hardware:end_insulators", 1.0),
        ),
    )

    assert record.currency == "USD"
    assert record.cost_for("conductor:copper:2.000") == pytest.approx(2.5)
    assert record.cost_for("missing") is None
    assert record.is_empty is False


def test_record_rejects_invalid_costs_and_keys() -> None:
    with pytest.raises(ValueError, match="currency"):
        BomCostRecord(currency="X" * (MAX_BOM_CURRENCY_LENGTH + 1))
    with pytest.raises(ValueError, match="key"):
        BomCostLine("   ", 1.0)
    with pytest.raises(ValueError, match="unit_cost"):
        BomCostLine("key", -1.0)
    with pytest.raises(ValueError, match="unique"):
        BomCostRecord(
            lines=(BomCostLine("key", 1.0), BomCostLine("key", 2.0)),
        )
    with pytest.raises(ValueError, match="at most"):
        BomCostRecord(
            lines=tuple(BomCostLine(f"key-{index}", 1.0) for index in range(MAX_BOM_COST_LINES + 1))
        )


def test_empty_record_is_detected() -> None:
    assert BomCostRecord().is_empty is True
    assert BomCostRecord(currency="USD").is_empty is False


def test_project_updates_bom_costs(sample_project: Project) -> None:
    record = BomCostRecord(
        currency="ARS",
        lines=(BomCostLine("hardware:coax_connector", 3.0),),
    )

    updated = sample_project.with_bom_costs(record, updated_at=sample_project.updated_at)

    assert updated.bom_costs == record
    assert sample_project.bom_costs is None
