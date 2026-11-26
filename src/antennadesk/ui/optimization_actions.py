# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dialogs for family optimization, primary-dimension search, and synthesis."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QDialog, QWidget

from ..application.ports.antenna_solver import AntennaSolver
from ..application.use_cases.optimize_antenna import OptimizeAntennaResult
from ..domain.antennas.design import AntennaDesignParameters
from ..domain.optimization.descriptor import AntennaOptimizerDescriptor
from ..domain.optimization.summary import OptimizationSummary
from ..domain.simulation.spec import SimulationSpec
from .dialogs.family_optimization_dialog import BandPlanSource, FamilyOptimizationDialog
from .dialogs.optimization_dialog import OptimizationDialog
from .dialogs.synthesis_dialog import SynthesisDialog
from .i18n import Translator
from .units import UnitSystem


def run_family_optimization_dialog(
    parent: QWidget,
    translator: Translator,
    unit_system: UnitSystem,
    solver: AntennaSolver,
    descriptor: AntennaOptimizerDescriptor,
    base_spec: SimulationSpec,
    *,
    topology_label: str,
    target_band_label: str | None,
    band_edges_hz: tuple[float, ...],
    band_plan_source: BandPlanSource,
    band_plan_bands: int,
    operating_frequencies_hz: tuple[float, ...],
    last_summary: OptimizationSummary | None,
    candidate_spec_builder: Callable[[AntennaDesignParameters], SimulationSpec] | None = None,
) -> tuple[AntennaDesignParameters, OptimizeAntennaResult | None] | None:
    dialog = FamilyOptimizationDialog(
        translator,
        unit_system,
        solver,
        descriptor,
        base_spec,
        parent,
        topology_label=topology_label,
        target_band_label=target_band_label,
        band_edges_hz=band_edges_hz,
        band_plan_source=band_plan_source,
        band_plan_bands=band_plan_bands,
        operating_frequencies_hz=operating_frequencies_hz,
        last_summary=last_summary,
        candidate_spec_builder=candidate_spec_builder,
    )
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    selected = dialog.selected_parameters()
    if selected is None:
        return None
    return selected, getattr(dialog, "selected_result", lambda: None)()


def run_length_optimization_dialog(
    parent: QWidget,
    translator: Translator,
    unit_system: UnitSystem,
    solver: AntennaSolver,
    parameters: AntennaDesignParameters,
    base_spec: SimulationSpec,
) -> float | None:
    dialog = OptimizationDialog(
        translator,
        unit_system,
        solver,
        parameters,
        base_spec,
        parent,
    )
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.selected_dimension_m()


def run_synthesis_dialog(
    parent: QWidget,
    translator: Translator,
    unit_system: UnitSystem,
    solver: AntennaSolver,
    parameters: AntennaDesignParameters,
    spec: SimulationSpec,
) -> AntennaDesignParameters | None:
    dialog = SynthesisDialog(
        translator,
        unit_system,
        solver,
        parameters,
        spec,
        parent,
    )
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.selected_parameters()
