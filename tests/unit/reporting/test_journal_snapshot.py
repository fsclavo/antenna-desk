# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Design snapshots captured by the project journal."""

from __future__ import annotations

from antennadesk.domain.projects.project import Project
from antennadesk.reporting.journal_snapshot import (
    journal_design_snapshot,
    journal_snapshot_rows,
)


def test_snapshot_captures_the_summary_and_model_counts(sample_project: Project) -> None:
    design = sample_project.designs[0]

    snapshot = journal_design_snapshot(sample_project, design)
    rows = dict(snapshot.rows)

    assert snapshot.design_id == design.id
    assert snapshot.design_name == design.name
    assert snapshot.antenna_type == design.antenna_type
    assert snapshot.frequency_hz == design.parameters.frequency_hz
    assert rows["Frequency"] == "7.100000 MHz"
    assert rows["Model wires"] == "1"
    assert rows["Model loads"].isdigit()
    assert rows["Model transmission lines"].isdigit()
    assert rows["Model sources"] == "1"
    assert len(snapshot.rows) == len(rows)


def test_snapshot_rows_localize_labels_and_values(sample_project: Project) -> None:
    design = sample_project.designs[0]
    snapshot = journal_design_snapshot(sample_project, design)
    translations = {
        "Frequency": "Frecuencia",
        "wire dipole": "dipolo de hilo",
    }

    def labeler(text: str, /, **values: object) -> str:
        template = translations.get(text, text)
        return template.format(**values) if values else template

    display = dict(journal_snapshot_rows(snapshot, labeler))

    assert display["Frecuencia"] == "7.100000 MHz"
    assert display["Type"] == "dipolo de hilo"
    assert "Model wires" in display
