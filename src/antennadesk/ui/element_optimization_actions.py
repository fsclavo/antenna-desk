# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Element-optimization dialogs for the family editors."""

from __future__ import annotations

from dataclasses import replace

from PySide6.QtWidgets import QDialog, QWidget

from ..application.ports.antenna_solver import AntennaSolver
from ..application.use_cases.optimize_elements import ElementOptimizationObjective
from ..domain.antennas.custom import CustomAntennaParameters
from ..domain.antennas.fan_dipole import FanDipoleParameters
from ..domain.antennas.inverted_v import InvertedVParameters
from ..domain.antennas.loop import LoopParameters
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.ringo import RingoParameters
from ..domain.antennas.vertical import VerticalParameters
from ..domain.antennas.yagi import YagiParameters
from ..domain.antennas.zs6bkw import ZS6BKW_DIPOLE_ID, zs6bkw_with_dimensions
from ..domain.design.formulas import frequency_for_half_wave_length
from ..domain.simulation.bands import amateur_band_by_id, amateur_band_for
from ..domain.simulation.spec import SimulationSpec
from .dialogs.element_optimization_dialog import (
    ElementOptimizationBand,
    ElementOptimizationDialog,
    ElementOptimizationVariable,
)
from .i18n import Translator
from .units import UnitSystem

YAGI_OPTIMIZATION_MIN_GAP_M = 0.1

OBJECTIVES = (
    ElementOptimizationObjective.TARGET_IMPEDANCE,
    ElementOptimizationObjective.MAX_GAIN,
    ElementOptimizationObjective.MAX_FRONT_TO_BACK,
    ElementOptimizationObjective.MULTI_OBJECTIVE,
)


def _accepted(dialog: ElementOptimizationDialog) -> bool:
    return dialog.exec() == QDialog.DialogCode.Accepted


def optimize_yagi_elements(
    parent: QWidget,
    translator: Translator,
    unit_system: UnitSystem,
    solver: AntennaSolver,
    parameters: YagiParameters,
    base_spec: SimulationSpec,
) -> YagiParameters | None:
    elements = parameters.elements
    variables: list[ElementOptimizationVariable] = []
    for index, element in enumerate(elements):
        variables.append(
            ElementOptimizationVariable(
                f"length_{index}",
                f"{translator.t('yagi.element')} {index + 1} · {translator.t('yagi.length')}",
                element.length_m,
            )
        )
    for index in range(1, len(elements)):
        variables.append(
            ElementOptimizationVariable(
                f"gap_{index}",
                f"{translator.t('yagi.element')} {index + 1} · "
                f"{translator.t('yagi_optimize.current_gap')}",
                elements[index].position_m - elements[index - 1].position_m,
                minimum=YAGI_OPTIMIZATION_MIN_GAP_M,
            )
        )

    def build(values: dict[str, float]) -> YagiParameters:
        frequency_hz = values.get("__frequency_hz", parameters.frequency_hz)
        updated = list(elements)
        for index, element in enumerate(updated):
            if (name := f"length_{index}") in values:
                updated[index] = replace(element, length_m=values[name])
        positions = [updated[0].position_m]
        for index in range(1, len(updated)):
            default_gap = updated[index].position_m - updated[index - 1].position_m
            positions.append(positions[-1] + values.get(f"gap_{index}", default_gap))
        updated = [
            replace(element, position_m=positions[index]) for index, element in enumerate(updated)
        ]
        return replace(parameters, frequency_hz=frequency_hz, elements=tuple(updated))

    dialog = ElementOptimizationDialog(
        translator,
        unit_system,
        solver,
        base_spec,
        title_key="element_optimize.yagi_title",
        hint_key="element_optimize.yagi_hint",
        variables=tuple(variables),
        build_parameters=build,
        objectives=OBJECTIVES,
        default_frequency_hz=parameters.frequency_hz,
        parent=parent,
    )
    if not _accepted(dialog):
        return None
    selected = dialog.selected_parameters()
    return selected if isinstance(selected, YagiParameters) else None


def optimize_fan_dipole_elements(
    parent: QWidget,
    translator: Translator,
    unit_system: UnitSystem,
    solver: AntennaSolver,
    parameters: FanDipoleParameters,
    base_spec: SimulationSpec,
    *,
    selected_band_id: str | None,
) -> FanDipoleParameters | None:
    elements = parameters.elements
    bands: dict[str, ElementOptimizationBand] = {}
    variables: list[ElementOptimizationVariable] = []
    for index, element in enumerate(elements):
        frequency_hz = frequency_for_half_wave_length(element.length_m)
        band = amateur_band_for(frequency_hz, tolerance_fraction=0.01)
        band_id = band.name if band is not None else None
        if band is not None:
            bands[band.name] = ElementOptimizationBand(
                band_id=band.name,
                label=band.name,
                frequency_hz=frequency_hz,
            )
        variables.append(
            ElementOptimizationVariable(
                f"length_{index}",
                f"{translator.t('yagi.element')} {index + 1} · {translator.t('yagi.length')}",
                element.length_m,
                band_id=band_id,
            )
        )
    if selected_band_id not in bands:
        selected_band_id = None
    if selected_band_id is not None:
        default_frequency_hz = bands[selected_band_id].frequency_hz
    elif bands:
        default_frequency_hz = min(
            bands.values(),
            key=lambda band: band.frequency_hz,
        ).frequency_hz
    else:
        default_frequency_hz = parameters.frequency_hz

    def build(values: dict[str, float]) -> FanDipoleParameters:
        updated = list(elements)
        for index in range(len(updated)):
            if (name := f"length_{index}") in values:
                updated[index] = replace(updated[index], length_m=values[name])
        return replace(
            parameters,
            frequency_hz=values.get("__frequency_hz", parameters.frequency_hz),
            elements=tuple(updated),
        )

    dialog = ElementOptimizationDialog(
        translator,
        unit_system,
        solver,
        base_spec,
        title_key="element_optimize.fan_title",
        variables=tuple(variables),
        build_parameters=build,
        objectives=OBJECTIVES,
        default_frequency_hz=default_frequency_hz,
        bands=tuple(sorted(bands.values(), key=lambda band: band.frequency_hz)),
        default_band_id=selected_band_id,
        hint_key="element_optimize.fan_hint",
        parent=parent,
    )
    if not _accepted(dialog):
        return None
    selected = dialog.selected_parameters()
    return selected if isinstance(selected, FanDipoleParameters) else None


def optimize_moxon_elements(
    parent: QWidget,
    translator: Translator,
    unit_system: UnitSystem,
    solver: AntennaSolver,
    parameters: MoxonParameters,
    base_spec: SimulationSpec,
) -> MoxonParameters | None:
    variables = (
        ElementOptimizationVariable("width_m", translator.t("moxon.width"), parameters.width_m),
        ElementOptimizationVariable("depth_m", translator.t("moxon.depth"), parameters.depth_m),
        ElementOptimizationVariable(
            "reflector_tip_m",
            translator.t("moxon.reflector_tip"),
            parameters.reflector_tip_m,
        ),
        ElementOptimizationVariable(
            "driven_tip_m",
            translator.t("moxon.driven_tip"),
            parameters.driven_tip_m,
        ),
    )

    def build(values: dict[str, float]) -> MoxonParameters:
        return replace(
            parameters,
            frequency_hz=values.get("__frequency_hz", parameters.frequency_hz),
            width_m=values.get("width_m", parameters.width_m),
            depth_m=values.get("depth_m", parameters.depth_m),
            reflector_tip_m=values.get("reflector_tip_m", parameters.reflector_tip_m),
            driven_tip_m=values.get("driven_tip_m", parameters.driven_tip_m),
        )

    dialog = ElementOptimizationDialog(
        translator,
        unit_system,
        solver,
        base_spec,
        title_key="element_optimize.moxon_title",
        variables=variables,
        build_parameters=build,
        objectives=OBJECTIVES,
        default_frequency_hz=parameters.frequency_hz,
        parent=parent,
    )
    if not _accepted(dialog):
        return None
    selected = dialog.selected_parameters()
    return selected if isinstance(selected, MoxonParameters) else None


def optimize_loop_elements(
    parent: QWidget,
    translator: Translator,
    unit_system: UnitSystem,
    solver: AntennaSolver,
    parameters: LoopParameters,
    base_spec: SimulationSpec,
) -> LoopParameters | None:
    variables = (
        ElementOptimizationVariable(
            "circumference_m",
            translator.t("field.circumference"),
            parameters.circumference_m,
        ),
    )

    def build(values: dict[str, float]) -> LoopParameters:
        return replace(
            parameters,
            frequency_hz=values.get("__frequency_hz", parameters.frequency_hz),
            circumference_m=values.get("circumference_m", parameters.circumference_m),
        )

    dialog = ElementOptimizationDialog(
        translator,
        unit_system,
        solver,
        base_spec,
        title_key="element_optimize.loop_title",
        hint_key="element_optimize.loop_hint",
        variables=variables,
        build_parameters=build,
        objectives=OBJECTIVES,
        default_frequency_hz=parameters.frequency_hz,
        default_target_resistance_ohm=50.0,
        parent=parent,
    )
    if not _accepted(dialog):
        return None
    selected = dialog.selected_parameters()
    return selected if isinstance(selected, LoopParameters) else None


def optimize_vertical_elements(
    parent: QWidget,
    translator: Translator,
    unit_system: UnitSystem,
    solver: AntennaSolver,
    parameters: VerticalParameters,
    base_spec: SimulationSpec,
) -> VerticalParameters | None:
    variables = [
        ElementOptimizationVariable("height_m", translator.t("field.height"), parameters.height_m)
    ]
    if parameters.radial_count > 0:
        variables.append(
            ElementOptimizationVariable(
                "radial_length_m",
                translator.t("vertical.radial_length"),
                parameters.radial_length_m,
            )
        )
        variables.append(
            ElementOptimizationVariable(
                "radial_count",
                translator.t("vertical.radial_count"),
                float(parameters.radial_count),
                integer=True,
            )
        )

    def build(values: dict[str, float]) -> VerticalParameters:
        return replace(
            parameters,
            frequency_hz=values.get("__frequency_hz", parameters.frequency_hz),
            height_m=values.get("height_m", parameters.height_m),
            radial_length_m=values.get("radial_length_m", parameters.radial_length_m),
            radial_count=round(values.get("radial_count", parameters.radial_count)),
        )

    dialog = ElementOptimizationDialog(
        translator,
        unit_system,
        solver,
        base_spec,
        title_key="element_optimize.vertical_title",
        variables=tuple(variables),
        build_parameters=build,
        objectives=OBJECTIVES,
        default_frequency_hz=parameters.frequency_hz,
        parent=parent,
    )
    if not _accepted(dialog):
        return None
    selected = dialog.selected_parameters()
    return selected if isinstance(selected, VerticalParameters) else None


def optimize_inverted_v_elements(
    parent: QWidget,
    translator: Translator,
    unit_system: UnitSystem,
    solver: AntennaSolver,
    parameters: InvertedVParameters,
    base_spec: SimulationSpec,
) -> InvertedVParameters | None:
    def build(values: dict[str, float]) -> InvertedVParameters:
        return replace(
            parameters,
            frequency_hz=values.get("__frequency_hz", parameters.frequency_hz),
            leg_length_m=values.get("leg_length_m", parameters.leg_length_m),
        )

    dialog = ElementOptimizationDialog(
        translator,
        unit_system,
        solver,
        base_spec,
        title_key="element_optimize.inverted_v_title",
        variables=(
            ElementOptimizationVariable(
                "leg_length_m",
                translator.t("inverted_v.leg_length"),
                parameters.leg_length_m,
            ),
        ),
        build_parameters=build,
        objectives=OBJECTIVES,
        default_frequency_hz=parameters.frequency_hz,
        parent=parent,
    )
    if not _accepted(dialog):
        return None
    selected = dialog.selected_parameters()
    return selected if isinstance(selected, InvertedVParameters) else None


def optimize_ringo_elements(
    parent: QWidget,
    translator: Translator,
    unit_system: UnitSystem,
    solver: AntennaSolver,
    parameters: RingoParameters,
    base_spec: SimulationSpec,
) -> RingoParameters | None:
    variables = (
        ElementOptimizationVariable(
            "radiator_height_m",
            translator.t("ringo.radiator_height"),
            parameters.radiator_height_m,
        ),
        ElementOptimizationVariable(
            "ring_diameter_m",
            translator.t("ringo.ring_diameter"),
            parameters.ring_diameter_m,
        ),
        ElementOptimizationVariable(
            "ring_sides",
            translator.t("ringo.ring_sides"),
            float(parameters.ring_sides),
            integer=True,
        ),
    )

    def build(values: dict[str, float]) -> RingoParameters:
        return replace(
            parameters,
            frequency_hz=values.get("__frequency_hz", parameters.frequency_hz),
            radiator_height_m=values.get("radiator_height_m", parameters.radiator_height_m),
            ring_diameter_m=values.get("ring_diameter_m", parameters.ring_diameter_m),
            ring_sides=round(values.get("ring_sides", parameters.ring_sides)),
        )

    dialog = ElementOptimizationDialog(
        translator,
        unit_system,
        solver,
        base_spec,
        title_key="element_optimize.ringo_title",
        variables=variables,
        build_parameters=build,
        objectives=OBJECTIVES,
        default_frequency_hz=parameters.frequency_hz,
        parent=parent,
    )
    if not _accepted(dialog):
        return None
    selected = dialog.selected_parameters()
    return selected if isinstance(selected, RingoParameters) else None


def optimize_zs6bkw_elements(
    parent: QWidget,
    translator: Translator,
    unit_system: UnitSystem,
    solver: AntennaSolver,
    parameters: CustomAntennaParameters,
    base_spec: SimulationSpec,
) -> CustomAntennaParameters | None:
    dipole = next(wire for wire in parameters.wires if wire.id == ZS6BKW_DIPOLE_ID)
    line = parameters.transmission_lines[0]
    band_ids = ("40m", "20m", "17m", "12m", "10m")
    bands = tuple(
        ElementOptimizationBand(band.name, band.name, band.center_hz)
        for band_id in band_ids
        if (band := amateur_band_by_id(band_id)) is not None
    )
    current_band = amateur_band_for(parameters.frequency_hz, tolerance_fraction=0.02)
    default_band_id = (
        current_band.name if current_band is not None and current_band.name in band_ids else "40m"
    )

    def build(values: dict[str, float]) -> CustomAntennaParameters:
        return zs6bkw_with_dimensions(
            parameters,
            dipole_total_length_m=values.get("dipole_total_length_m", dipole.length_m),
            line_length_m=values.get("line_length_m", line.length_m),
        )

    dialog = ElementOptimizationDialog(
        translator,
        unit_system,
        solver,
        base_spec,
        title_key="element_optimize.zs6bkw_title",
        variables=(
            ElementOptimizationVariable(
                "dipole_total_length_m",
                translator.t("zs6bkw.wire_length"),
                dipole.length_m,
            ),
            ElementOptimizationVariable(
                "line_length_m",
                translator.t("zs6bkw.line_length"),
                line.length_m,
            ),
        ),
        build_parameters=build,
        objectives=OBJECTIVES,
        default_frequency_hz=parameters.frequency_hz,
        default_band_id=default_band_id,
        bands=bands,
        hint_key="element_optimize.zs6bkw_hint",
        parent=parent,
    )
    if not _accepted(dialog):
        return None
    selected = dialog.selected_parameters()
    return selected if isinstance(selected, CustomAntennaParameters) else None
