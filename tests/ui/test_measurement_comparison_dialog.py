# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Before/after measurement comparison dialog."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pyqtgraph as pg
from pytestqt.qtbot import QtBot

from antennadesk.domain.measurement import Measurement, MeasurementPoint
from antennadesk.ui.dialogs.measurement_comparison_dialog import (
    MeasurementComparisonDialog,
)
from antennadesk.ui.i18n import Language, Translator

_BEFORE_ID = UUID("00000000-0000-0000-0000-000000000021")
_AFTER_ID = UUID("00000000-0000-0000-0000-000000000022")
_BEFORE_SESSION_ID = UUID("00000000-0000-0000-0000-000000000031")
_AFTER_SESSION_ID = UUID("00000000-0000-0000-0000-000000000032")


def _before() -> Measurement:
    return Measurement(
        id=_BEFORE_ID,
        name="Before",
        created_at=datetime(2026, 11, 12, 14, 0, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(
            MeasurementPoint(7_000_000.0, complex(50.0, -10.0)),
            MeasurementPoint(7_100_000.0, complex(50.0, 0.0)),
            MeasurementPoint(7_200_000.0, complex(50.0, 10.0)),
        ),
        calibration="SOL",
        feed_line="10 m RG-58",
        session_id=_BEFORE_SESSION_ID,
    )


def _after() -> Measurement:
    return Measurement(
        id=_AFTER_ID,
        name="After",
        created_at=datetime(2026, 11, 12, 16, 0, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(
            MeasurementPoint(7_000_000.0, complex(75.0, -10.0)),
            MeasurementPoint(7_100_000.0, complex(75.0, 0.0)),
            MeasurementPoint(7_200_000.0, complex(75.0, 10.0)),
        ),
        calibration="None",
        feed_line="10 m RG-58",
        session_id=_AFTER_SESSION_ID,
    )


def _dialog(qtbot: QtBot, language: Language = Language.ENGLISH):
    dialog = MeasurementComparisonDialog(
        Translator(language),
        (_before(), _after()),
        session_names={
            _BEFORE_SESSION_ID: "Before session",
            _AFTER_SESSION_ID: "After session",
        },
        initial_before_id=_BEFORE_ID,
        initial_after_id=_AFTER_ID,
    )
    qtbot.addWidget(dialog)
    return dialog


def test_comparison_dialog_aligns_points_and_shows_deltas(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    comparison = dialog.comparison()
    assert comparison is not None
    assert comparison.compared_count == 3
    assert dialog._table.rowCount() == 3
    assert "Compared 3 points" in dialog._summary.text()
    assert "mean |ΔZ|" in dialog._summary.text()
    assert "Before session" in dialog._before.currentText()
    assert "After session" in dialog._after.currentText()
    assert (
        len([item for item in dialog._plot.listDataItems() if isinstance(item, pg.PlotDataItem)])
        == 2
    )
    assert "Resonance before" in dialog._resonance.text()
    assert "Resonance after" in dialog._resonance.text()
    assert "Conditions differ" in dialog._conditions.text()
    assert "Calibration" in dialog._conditions.text()


def test_comparison_dialog_reference_changes_swr_values(qtbot: QtBot) -> None:
    before = Measurement(
        id=_BEFORE_ID,
        name="Before",
        created_at=datetime(2026, 11, 12, 14, 0, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(
            MeasurementPoint(7_000_000.0, complex(50.0, 0.0)),
            MeasurementPoint(7_100_000.0, complex(50.0, 0.0)),
        ),
    )
    after = Measurement(
        id=_AFTER_ID,
        name="After",
        created_at=datetime(2026, 11, 12, 16, 0, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(
            MeasurementPoint(7_000_000.0, complex(75.0, 0.0)),
            MeasurementPoint(7_100_000.0, complex(75.0, 0.0)),
        ),
    )
    dialog = MeasurementComparisonDialog(
        Translator(Language.ENGLISH),
        (before, after),
        initial_before_id=_BEFORE_ID,
        initial_after_id=_AFTER_ID,
    )
    qtbot.addWidget(dialog)

    assert dialog._table.item(0, 3).text() == "1.000"
    assert dialog._table.item(0, 6).text() == "1.500"

    dialog._reference.setValue(75.0)

    assert dialog._table.item(0, 3).text() == "1.500"
    assert dialog._table.item(0, 6).text() == "1.000"


def test_comparison_dialog_handles_no_overlap(qtbot: QtBot) -> None:
    far = Measurement(
        id=UUID("00000000-0000-0000-0000-000000000023"),
        name="20 m",
        created_at=datetime(2026, 11, 12, 17, 0, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(
            MeasurementPoint(14_000_000.0, complex(50.0, 0.0)),
            MeasurementPoint(14_100_000.0, complex(50.0, 0.0)),
        ),
    )
    dialog = MeasurementComparisonDialog(
        Translator(Language.ENGLISH),
        (_before(), far),
        initial_before_id=_BEFORE_ID,
        initial_after_id=far.id,
    )
    qtbot.addWidget(dialog)

    assert dialog.comparison() is not None
    assert dialog.comparison().compared_count == 0  # type: ignore[union-attr]
    assert dialog._table.rowCount() == 0
    assert "No overlapping" in dialog._summary.text()


def test_comparison_dialog_retranslates(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot, Language.SPANISH)

    assert dialog.windowTitle() == "Medición antes / después"
    assert dialog._before_label.text() == "Antes"
    assert dialog._after_label.text() == "Después"
    assert dialog._table.horizontalHeaderItem(0).text() == "Frecuencia (MHz)"
    assert "Comparados" in dialog._summary.text()
