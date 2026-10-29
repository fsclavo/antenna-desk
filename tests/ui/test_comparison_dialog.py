# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from helpers import make_completed_result
from pytestqt.qtbot import QtBot

from antennadesk.application.use_cases.add_design_variant import (
    AddDesignVariant,
    AddDesignVariantCommand,
)
from antennadesk.domain.projects.project import Project
from antennadesk.ui.dialogs.comparison_dialog import ComparisonDialog
from antennadesk.ui.i18n import Language, Translator


def test_comparison_dialog_shows_two_variants(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    source = sample_project.designs[0]
    project = AddDesignVariant().execute(
        AddDesignVariantCommand(
            project=sample_project,
            source_design_id=source.id,
            name="Second",
        )
    )
    results = {design.id: make_completed_result() for design in project.designs}
    dialog = ComparisonDialog(
        Translator(Language.ENGLISH),
        project,
        results,
    )
    qtbot.addWidget(dialog)
    dialog.show()

    assert dialog._combo_a.count() == 2
    assert dialog._combo_b.count() == 2
    assert dialog._combo_b.currentIndex() == 1
    assert dialog._table.rowCount() > 5
    assert dialog._table.columnCount() == 3
    assert dialog._note.isVisible() is False


def test_comparison_dialog_reports_missing_results(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    project = AddDesignVariant().execute(
        AddDesignVariantCommand(
            project=sample_project,
            source_design_id=sample_project.designs[0].id,
            name="Second",
        )
    )
    dialog = ComparisonDialog(
        Translator(Language.ENGLISH),
        project,
        {},
    )
    qtbot.addWidget(dialog)
    dialog.show()

    assert dialog._note.isVisible() is True
