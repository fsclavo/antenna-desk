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

    assert dialog._design_list.count() == 2
    assert len(dialog._selected_ids()) == 2
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


def test_comparison_dialog_supports_mixed_geometry(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    from dataclasses import replace
    from uuid import uuid4

    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
    from antennadesk.domain.projects.project import DesignVariant

    source = sample_project.designs[0]
    parameters = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    )
    folded = DesignVariant(
        id=uuid4(),
        name="Folded",
        antenna_type="folded_dipole",
        parameters=parameters,
        antenna=parameters.to_antenna(name="Folded"),
    )
    project = replace(
        sample_project,
        designs=(source, folded),
    )
    results = {design.id: make_completed_result() for design in project.designs}
    dialog = ComparisonDialog(
        Translator(Language.ENGLISH),
        project,
        results,
    )
    qtbot.addWidget(dialog)
    dialog.show()

    labels = [dialog._table.item(row, 0).text() for row in range(dialog._table.rowCount())]
    assert "Main dimension" in labels
    assert "Secondary dimension" in labels
    assert dialog._table.item(0, 1).text() == "Wire dipole"
    assert dialog._table.item(0, 2).text() == "Folded dipole"


def test_comparison_dialog_shows_a_band_summary(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    from datetime import UTC, datetime
    from uuid import uuid4

    from antennadesk.domain.simulation.band_result import BandAnalysisResult, BandResult
    from antennadesk.domain.simulation.bands import amateur_band_by_id

    project = AddDesignVariant().execute(
        AddDesignVariantCommand(
            project=sample_project,
            source_design_id=sample_project.designs[0].id,
            name="Second",
        )
    )
    bands = tuple(
        BandResult(amateur_band_by_id(band_id), make_completed_result())
        for band_id in ("40m", "20m")
        if amateur_band_by_id(band_id) is not None
    )
    analyses = {
        design.id: BandAnalysisResult(
            design_id=design.id,
            batch_id=uuid4(),
            created_at=datetime(2026, 11, 3, tzinfo=UTC),
            bands=bands,
        )
        for design in project.designs
    }
    results = {design.id: make_completed_result() for design in project.designs}
    dialog = ComparisonDialog(
        Translator(Language.ENGLISH),
        project,
        results,
        band_analyses=analyses,
    )
    qtbot.addWidget(dialog)
    dialog.show()

    assert dialog._band_table.isVisible() is True
    assert dialog._band_table.rowCount() == 2
    assert dialog._band_table.columnCount() == 3
    assert dialog._band_table.item(0, 0).text() == "40m"
    assert dialog._band_table.item(0, 1).text() == "1.000"


def test_comparison_dialog_emits_the_common_basis(
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
    received: list[tuple[object, object]] = []
    dialog.recompute_requested.connect(lambda basis, ids: received.append((basis, ids)))
    dialog._start.setValue(7.0)
    dialog._stop.setValue(7.3)
    dialog._points.setValue(11)
    dialog._reference_height.setValue(0.0)
    dialog._reference_frequency.setValue(7.15)

    dialog._request_recompute()

    assert len(received) == 1
    basis, ids = received[0]
    assert basis.frequency_plan.count == 11
    assert basis.reference_height_m is None
    assert len(ids) == 2


def test_comparison_dialog_shows_height_mapping_warnings(
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
    results = {design.id: make_completed_result() for design in project.designs}
    mapping = {design.id: (False, ("native_height",)) for design in project.designs}
    dialog = ComparisonDialog(
        Translator(Language.ENGLISH),
        project,
        results,
        height_mapping=mapping,
    )
    qtbot.addWidget(dialog)
    dialog.show()

    assert dialog._note.isVisible() is True
    assert "Native height used" in dialog._note.text()
