# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Common-basis comparison integration in the main window."""

from __future__ import annotations

from helpers import make_completed_result

from antennadesk.application.use_cases.add_design_variant import (
    AddDesignVariant,
    AddDesignVariantCommand,
)
from antennadesk.application.use_cases.compare_designs import (
    ComparisonDesignResult,
    ComparisonOutcome,
)
from antennadesk.domain.design.comparison import ComparisonBasis
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.ui.main_window import MainWindow


def _basis() -> ComparisonBasis:
    return ComparisonBasis(
        frequency_plan=FrequencyPlan.sweep(7_000_000.0, 7_300_000.0, 31),
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
        reference_height_m=12.0,
        reference_frequency_hz=7_100_000.0,
    )


def test_build_comparison_runs_applies_common_plan_ground_and_height(
    window: MainWindow,
) -> None:
    assert window._project is not None
    project = AddDesignVariant().execute(
        AddDesignVariantCommand(
            project=window._project,
            source_design_id=window._project.designs[0].id,
            name="Second",
        )
    )
    window._project = project
    basis = _basis()

    runs, mapping = window._build_comparison_runs(
        basis,
        tuple(design.id for design in project.designs),
    )

    assert len(runs) == 2
    for run in runs:
        assert run.spec.frequency_plan == basis.frequency_plan
        assert run.spec.pattern_frequencies_hz == (7_100_000.0,)
        assert run.model.environment.ground == basis.ground
        heights = [point.z_m for wire in run.model.wires for point in (wire.start, wire.end)]
        assert max(heights) == 12.0
    assert mapping[project.designs[0].id][0] is True


def test_default_comparison_basis_uses_the_current_design(window: MainWindow) -> None:
    basis = window._default_comparison_basis()

    assert 7_000_000.0 <= basis.reference_frequency_hz <= 7_300_000.0
    assert basis.reference_height_m == 8.0
    assert basis.frequency_plan.count >= 2


def test_comparison_finish_updates_the_open_dialog(window: MainWindow) -> None:
    class FakeDialog:
        def __init__(self) -> None:
            self.calls: list[tuple[object, object]] = []

        def set_results(self, results: object, **kwargs: object) -> None:
            self.calls.append((results, kwargs))

    dialog = FakeDialog()
    window._comparison_dialog = dialog  # type: ignore[assignment]
    window._comparison_basis = _basis()
    window._comparison_height_mapping = {}
    result = make_completed_result()
    outcome = ComparisonOutcome(
        results=(
            ComparisonDesignResult(
                design_id=window._design_id,  # type: ignore[arg-type]
                result=result,
            ),
        )
    )

    window._on_comparison_finished(outcome)

    assert len(dialog.calls) == 1
    results, kwargs = dialog.calls[0]
    assert results == {window._design_id: result}
    assert kwargs["basis"] == window._comparison_basis
