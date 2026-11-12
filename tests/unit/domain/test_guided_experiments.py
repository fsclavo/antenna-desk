# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Curated guided-experiment presets over the sweep engine."""

from __future__ import annotations

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.design.guided_experiments import (
    GuidedExperimentKey,
    guided_experiments,
)
from antennadesk.domain.design.sweep import SweepMetric
from antennadesk.domain.optimization.descriptor import (
    AntennaOptimizerDescriptor,
    FamilyOptimizationObjective,
)
from antennadesk.domain.optimization.registry import optimizer_availability
from antennadesk.domain.optimization.variables import OptimizationVariable


def _dipole() -> DipoleParameters:
    return DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )


def _vertical() -> VerticalParameters:
    return VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=0.5,
        radial_count=8,
        radial_length_m=5.0,
    )


def _descriptor(parameters: DipoleParameters | VerticalParameters):
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    return availability.descriptor


def test_dipole_experiments_use_length_and_height() -> None:
    descriptor = _descriptor(_dipole())
    experiments = guided_experiments(descriptor, 7_100_000.0)
    resonance, height, interaction = experiments

    assert [entry.key for entry in experiments] == [
        GuidedExperimentKey.RESONANCE,
        GuidedExperimentKey.GROUND_HEIGHT,
        GuidedExperimentKey.INTERACTION,
    ]
    assert resonance.experiment is not None
    assert resonance.experiment.plan.x_axis.name == "total_length_m"
    assert resonance.experiment.plan.x_axis.label_key == "field.length"
    assert resonance.experiment.plan.x_axis.count == 21
    assert resonance.experiment.plan.metric is SweepMetric.REACTANCE
    assert resonance.experiment.plan.target_frequency_hz == 7_100_000.0

    assert height.experiment is not None
    assert height.experiment.plan.x_axis.name == "height_m"
    assert height.experiment.plan.x_axis.count == 15
    assert height.experiment.plan.metric is SweepMetric.RESISTANCE

    assert interaction.experiment is not None
    plan = interaction.experiment.plan
    assert plan.x_axis.name == "total_length_m"
    assert plan.y_axis is not None
    assert plan.y_axis.name == "height_m"
    assert plan.x_axis.count == 9
    assert plan.y_axis.count == 7
    assert plan.point_count == 63
    assert plan.metric is SweepMetric.SWR


def test_dipole_experiment_axes_span_the_optimizer_limits() -> None:
    descriptor = _descriptor(_dipole())
    variables = {variable.name: variable for variable in descriptor.variables}
    resonance = guided_experiments(descriptor, 7_100_000.0)[0].experiment
    assert resonance is not None

    axis = resonance.plan.x_axis
    variable = variables["total_length_m"]

    assert axis.values[0] == variable.minimum
    assert axis.values[-1] == variable.maximum
    assert axis.unit == "m"


def test_vertical_uses_base_height_as_the_ground_dimension() -> None:
    descriptor = _descriptor(_vertical())
    resonance, ground, interaction = guided_experiments(descriptor, 7_100_000.0)

    assert resonance.experiment is not None
    assert resonance.experiment.plan.x_axis.name == "height_m"
    assert ground.experiment is not None
    assert ground.experiment.plan.x_axis.name == "base_height_m"
    assert interaction.experiment is not None
    assert interaction.experiment.plan.x_axis.name == "height_m"
    assert interaction.experiment.plan.y_axis is not None
    assert interaction.experiment.plan.y_axis.name == "base_height_m"


def test_experiments_report_explicit_unavailable_reasons() -> None:
    parameters = _dipole()
    descriptor = AntennaOptimizerDescriptor(
        key="test_radius_only",
        variables=(
            OptimizationVariable(
                "wire_radius_m",
                "field.wire_radius",
                "optimize.group.conductor",
                5e-4,
                2e-3,
                unit="radius",
                step=1e-4,
            ),
        ),
        initial_values={"wire_radius_m": 1e-3},
        build_parameters=lambda values: parameters,
        validate=lambda values: (),
        objectives=frozenset({FamilyOptimizationObjective.TARGET_IMPEDANCE}),
    )

    experiments = guided_experiments(descriptor, 7_100_000.0)

    assert all(not entry.available for entry in experiments)
    assert [entry.reason_key for entry in experiments] == [
        "guided.reason.primary",
        "guided.reason.height",
        "guided.reason.interaction",
    ]
    assert all(entry.experiment is None for entry in experiments)
