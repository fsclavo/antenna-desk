# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Curated sweep presets for guided experiments.

The presets only choose existing optimizer variables and sweep ranges. They do
not run a solver, rank antennas, or add a second analysis engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..optimization.descriptor import AntennaOptimizerDescriptor
from ..optimization.variables import OptimizationVariable, VariableKind
from .sweep import SweepAxis, SweepMetric, SweepPlan, axis_values

RESONANCE_POINTS = 21
HEIGHT_POINTS = 15
INTERACTION_X_POINTS = 9
INTERACTION_Y_POINTS = 7

_PRIMARY_LENGTH_NAMES = (
    "total_length_m",
    "driven_length_m",
    "length_m",
    "radiator_height_m",
    "height_m",
    "vertical_height_m",
    "loop_side_m",
    "horizontal_length_m",
    "leg_length_m",
    "radial_length_m",
)
_GROUND_HEIGHT_NAMES = (
    "height_m",
    "base_height_m",
    "feed_height_m",
    "apex_height_m",
)


class GuidedExperimentKey(StrEnum):
    RESONANCE = "resonance"
    GROUND_HEIGHT = "ground_height"
    INTERACTION = "interaction"


@dataclass(frozen=True, slots=True)
class GuidedExperiment:
    key: GuidedExperimentKey
    plan: SweepPlan

    def __post_init__(self) -> None:
        object.__setattr__(self, "key", GuidedExperimentKey(self.key))


@dataclass(frozen=True, slots=True)
class GuidedExperimentAvailability:
    key: GuidedExperimentKey
    experiment: GuidedExperiment | None = None
    reason_key: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "key", GuidedExperimentKey(self.key))

    @property
    def available(self) -> bool:
        return self.experiment is not None


def guided_experiments(
    descriptor: AntennaOptimizerDescriptor,
    target_frequency_hz: float,
) -> tuple[GuidedExperimentAvailability, ...]:
    """Return the three curated experiments with explicit availability."""

    primary = _first_continuous_length(descriptor.variables, _PRIMARY_LENGTH_NAMES)
    ground = _first_continuous_length(
        descriptor.variables,
        _GROUND_HEIGHT_NAMES,
        exclude=primary.name if primary is not None else None,
    )
    entries = [
        _availability(
            GuidedExperimentKey.RESONANCE,
            primary,
            target_frequency_hz,
            RESONANCE_POINTS,
            SweepMetric.REACTANCE,
            reason_key="guided.reason.primary",
        ),
        _availability(
            GuidedExperimentKey.GROUND_HEIGHT,
            ground,
            target_frequency_hz,
            HEIGHT_POINTS,
            SweepMetric.RESISTANCE,
            reason_key="guided.reason.height",
        ),
        _interaction(primary, ground, target_frequency_hz),
    ]
    return tuple(entries)


def _first_continuous_length(
    variables: tuple[OptimizationVariable, ...],
    names: tuple[str, ...],
    *,
    exclude: str | None = None,
) -> OptimizationVariable | None:
    by_name = {variable.name: variable for variable in variables}
    for name in names:
        variable = by_name.get(name)
        if variable is None or variable.name == exclude:
            continue
        if variable.kind is not VariableKind.CONTINUOUS:
            continue
        if variable.unit != "m" or variable.maximum <= variable.minimum:
            continue
        return variable
    return None


def _axis(
    variable: OptimizationVariable,
    count: int,
) -> SweepAxis:
    return SweepAxis(
        name=variable.name,
        label_key=variable.label_key,
        unit=variable.unit,
        values=axis_values(variable, variable.minimum, variable.maximum, count),
    )


def _availability(
    key: GuidedExperimentKey,
    variable: OptimizationVariable | None,
    target_frequency_hz: float,
    count: int,
    metric: SweepMetric,
    *,
    reason_key: str,
) -> GuidedExperimentAvailability:
    if variable is None:
        return GuidedExperimentAvailability(key=key, reason_key=reason_key)
    plan = SweepPlan(
        x_axis=_axis(variable, count),
        y_axis=None,
        metric=metric,
        target_frequency_hz=target_frequency_hz,
    )
    return GuidedExperimentAvailability(
        key=key,
        experiment=GuidedExperiment(key=key, plan=plan),
    )


def _interaction(
    primary: OptimizationVariable | None,
    ground: OptimizationVariable | None,
    target_frequency_hz: float,
) -> GuidedExperimentAvailability:
    if primary is None or ground is None:
        return GuidedExperimentAvailability(
            key=GuidedExperimentKey.INTERACTION,
            reason_key="guided.reason.interaction",
        )
    plan = SweepPlan(
        x_axis=_axis(primary, INTERACTION_X_POINTS),
        y_axis=_axis(ground, INTERACTION_Y_POINTS),
        metric=SweepMetric.SWR,
        target_frequency_hz=target_frequency_hz,
    )
    return GuidedExperimentAvailability(
        key=GuidedExperimentKey.INTERACTION,
        experiment=GuidedExperiment(key=GuidedExperimentKey.INTERACTION, plan=plan),
    )
