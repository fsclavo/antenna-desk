# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Band-analysis storage preflight."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QMessageBox

from antennadesk.domain.design.band_plan import BandPlan, BandSelection
from antennadesk.domain.simulation.bands import amateur_band_by_id
from antennadesk.domain.simulation.budget import PatternBudget
from antennadesk.persistence.constants import (
    MAX_PROJECT_SIZE_BYTES,
    PROJECT_SIZE_WARNING_BYTES,
)
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.main_window import MainWindow, project_size_action


def _budget(estimated_bytes: int) -> PatternBudget:
    return PatternBudget(
        pattern_step_deg=None,
        estimated_project_bytes=estimated_bytes,
        estimated_json_bytes=estimated_bytes * 6,
        far_field_points_per_frequency=0,
        pattern_frequency_count=0,
        requested_step_deg=None,
        far_field_enabled=False,
        reduced=True,
    )


def _plan() -> BandPlan:
    band = amateur_band_by_id("40m")
    assert band is not None
    return BandPlan((BandSelection(band, 100),))


def test_project_size_action_uses_the_warning_and_hard_limits() -> None:
    assert project_size_action(10 * 1024 * 1024) == "ok"
    assert project_size_action(PROJECT_SIZE_WARNING_BYTES + 1) == "warn"
    assert project_size_action(MAX_PROJECT_SIZE_BYTES + 1) == "block"


def test_band_analysis_blocks_above_the_hard_project_limit(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    design = window._project.designs[0]
    errors: list[str] = []

    def fake_fit(
        model: object,
        specs: tuple[object, ...],
    ) -> tuple[tuple[object, ...], PatternBudget]:
        del model
        budget = _budget(MAX_PROJECT_SIZE_BYTES + 1)
        window._custom_last_budget = budget
        return specs, budget

    monkeypatch.setattr(window, "_fit_band_specs_to_budget", fake_fit)
    monkeypatch.setattr(window, "_show_error", lambda text: errors.append(text))

    window._start_band_analysis(design, _plan())

    assert errors
    assert "project limit" in errors[0].lower()
    assert not window._runner.is_running
    assert window._simulating is False
    window._dirty = False


def test_band_analysis_can_be_cancelled_at_the_warning_threshold(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    design = window._project.designs[0]

    def fake_fit(
        model: object,
        specs: tuple[object, ...],
    ) -> tuple[tuple[object, ...], PatternBudget]:
        del model
        budget = _budget(PROJECT_SIZE_WARNING_BYTES + 1)
        window._custom_last_budget = budget
        return specs, budget

    monkeypatch.setattr(window, "_fit_band_specs_to_budget", fake_fit)
    monkeypatch.setattr(
        main_window_module.QMessageBox,
        "warning",
        lambda *args, **kwargs: QMessageBox.StandardButton.No,
    )

    window._start_band_analysis(design, _plan())

    assert not window._runner.is_running
    assert window._simulating is False
    window._dirty = False
