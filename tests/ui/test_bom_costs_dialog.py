# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Manual BOM cost dialog."""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.projects.bom_costs import BomCostLine, BomCostRecord
from antennadesk.domain.projects.project import Project
from antennadesk.reporting.bom_costs import hardware_cost_key
from antennadesk.reporting.wire_schedule import conductor_bom_rows
from antennadesk.ui.dialogs.bom_costs_dialog import BomCostsDialog
from antennadesk.ui.i18n import Language, Translator


def _project_with_costs(sample_project: Project) -> Project:
    conductor = conductor_bom_rows(sample_project.designs[0].antenna)[0]
    record = BomCostRecord(
        currency="USD",
        lines=(
            BomCostLine(conductor.cost_key, 2.5),
            BomCostLine(hardware_cost_key("end_insulators"), 1.0),
        ),
    )
    return sample_project.with_bom_costs(record, updated_at=sample_project.updated_at)


def _dialog(
    qtbot: QtBot,
    project: Project,
    translator: Translator | None = None,
) -> BomCostsDialog:
    dialog = BomCostsDialog(
        translator or Translator(Language.ENGLISH),
        project,
        project.designs[0],
    )
    qtbot.addWidget(dialog)
    return dialog


def test_dialog_loads_existing_costs_and_total(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    project = _project_with_costs(sample_project)
    dialog = _dialog(qtbot, project)

    assert dialog._currency.text() == "USD"
    assert len(dialog._cost_spins) == 12
    assert dialog._cost_spins[0][1].value() == pytest.approx(2.5)
    assert dialog._cost_spins[1][1].value() == pytest.approx(1.0)
    assert "52.00 USD" in dialog._total_label.text()
    assert dialog._table.toolTip()
    assert dialog._cost_spins[0][1].toolTip()
    assert dialog._total_label.toolTip()


def test_dialog_edits_currency_and_costs(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    dialog = _dialog(qtbot, sample_project)
    dialog._currency.setText("ARS")
    dialog._cost_spins[0][1].setValue(2.5)
    dialog._cost_spins[1][1].setValue(1.0)

    assert "52.00 ARS" in dialog._total_label.text()
    dialog.accept()

    result = dialog.result_bom_costs()
    assert result is not None
    assert result.currency == "ARS"
    assert result.cost_for(dialog._cost_spins[0][0].key) == pytest.approx(2.5)
    assert result.cost_for(hardware_cost_key("end_insulators")) == pytest.approx(1.0)


def test_dialog_zero_removes_a_current_line_and_preserves_unknown(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    conductor = conductor_bom_rows(sample_project.designs[0].antenna)[0]
    record = BomCostRecord(
        currency="USD",
        lines=(
            BomCostLine(conductor.cost_key, 2.5),
            BomCostLine("hardware:old_design_row", 9.0),
        ),
    )
    project = sample_project.with_bom_costs(record, updated_at=sample_project.updated_at)
    dialog = _dialog(qtbot, project)

    dialog._cost_spins[0][1].setValue(0.0)
    dialog.accept()

    result = dialog.result_bom_costs()
    assert result is not None
    assert result.cost_for(conductor.cost_key) is None
    assert result.cost_for("hardware:old_design_row") == pytest.approx(9.0)


def test_dialog_returns_none_when_empty(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    dialog = _dialog(qtbot, sample_project)
    dialog.accept()

    assert dialog.result_bom_costs() is None


def test_dialog_is_translated_to_spanish(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    dialog = _dialog(qtbot, sample_project, Translator(Language.SPANISH))

    assert dialog.windowTitle() == "Costos del BOM"
    assert dialog._currency_label.text() == "Moneda"
    assert dialog._table.horizontalHeaderItem(3).text() == "Costo unitario"
    assert "Total:" in dialog._total_label.text()
