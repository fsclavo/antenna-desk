# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.load import SeriesLoad
from antennadesk.domain.antennas.transmission_line import TransmissionLine
from antennadesk.domain.measurement import Measurement, MeasurementPoint
from antennadesk.domain.optimization.summary import OptimizationMode, OptimizationSummary
from antennadesk.domain.projects.project import DesignVariant, Project


def _summary() -> OptimizationSummary:
    return OptimizationSummary(
        mode=OptimizationMode.SINGLE,
        objective="min_swr",
        status="converged",
        budget_profile="balanced",
        evaluations=12,
        seed=0,
        best_values={"total_length_m": 20.0},
        best_metrics={"swr": 1.1},
        completed_at=datetime(2026, 11, 7, tzinfo=UTC),
    )


def test_sample_project_is_valid(sample_project: Project) -> None:
    assert len(sample_project.designs) == 1
    design = sample_project.designs[0]
    assert design.antenna_type == "wire_dipole"
    assert design.antenna == design.parameters.to_antenna(name=design.antenna.name)


def test_design_rejects_inconsistent_antenna(sample_project: Project) -> None:
    design = sample_project.designs[0]
    changed_parameters = design.parameters.with_length(19.0)

    with pytest.raises(ValueError, match="inconsistent"):
        DesignVariant(
            id=design.id,
            name=design.name,
            antenna_type=design.antenna_type,
            parameters=changed_parameters,
            antenna=design.antenna,
        )


def test_design_with_parameters_returns_a_new_value(sample_project: Project) -> None:
    design = sample_project.designs[0]
    edited = design.with_parameters(design.parameters.with_length(19.5))

    assert edited is not design
    assert edited.id == design.id
    assert edited.name == design.name
    assert edited.parameters.total_length_m == pytest.approx(19.5)
    assert edited.antenna.wires[0].length_m == pytest.approx(19.5)
    assert design.parameters.total_length_m == pytest.approx(20.0)


def test_parameter_change_clears_a_stale_optimization_summary(
    sample_project: Project,
) -> None:
    design = sample_project.designs[0]
    optimized = design.with_optimization_summary(_summary())

    edited = optimized.with_parameters(design.parameters.with_length(19.5))

    assert edited.optimization_summary is None


def test_identical_parameters_preserve_the_optimization_summary(
    sample_project: Project,
) -> None:
    design = sample_project.designs[0]
    summary = _summary()
    optimized = design.with_optimization_summary(summary)

    replayed = optimized.with_parameters(design.parameters)

    assert replayed.optimization_summary == summary
    assert optimized.with_loads(optimized.antenna.loads).optimization_summary == summary
    assert (
        optimized.with_transmission_lines(optimized.antenna.transmission_lines).optimization_summary
        == summary
    )


def test_attachment_changes_clear_a_stale_optimization_summary(
    sample_project: Project,
) -> None:
    design = sample_project.designs[0]
    optimized = design.with_optimization_summary(_summary())
    wire_id = optimized.antenna.wires[0].id
    load = SeriesLoad(
        id="extra-load",
        wire_id=wire_id,
        offset_m=1.0,
        resistance_ohm=1.0,
    )
    line = TransmissionLine(
        id="extra-line",
        start_wire_id=wire_id,
        start_offset_m=1.0,
        end_wire_id=wire_id,
        end_offset_m=2.0,
        characteristic_impedance_ohm=50.0,
        length_m=5.0,
    )

    with_load = optimized.with_loads((*optimized.antenna.loads, load))
    with_line = optimized.with_transmission_lines((*optimized.antenna.transmission_lines, line))

    assert with_load.optimization_summary is None
    assert with_line.optimization_summary is None


def test_project_rejects_duplicate_design_ids(sample_project: Project) -> None:
    design = sample_project.designs[0]
    duplicate = replace(design, name="Second variant")

    with pytest.raises(ValueError, match="duplicate design id"):
        Project(
            id=sample_project.id,
            name=sample_project.name,
            description=sample_project.description,
            created_at=sample_project.created_at,
            updated_at=sample_project.updated_at,
            designs=(design, duplicate),
        )


def test_project_rejects_duplicate_design_names(sample_project: Project) -> None:
    design = sample_project.designs[0]
    duplicate = replace(design, id=uuid4())

    with pytest.raises(ValueError, match="duplicate design name"):
        Project(
            id=sample_project.id,
            name=sample_project.name,
            description=sample_project.description,
            created_at=sample_project.created_at,
            updated_at=sample_project.updated_at,
            designs=(design, duplicate),
        )


def test_project_updates_and_removes_a_measurement(sample_project: Project) -> None:
    from datetime import UTC

    measurement = Measurement(
        id=uuid4(),
        name="Field sweep",
        created_at=datetime(2026, 11, 1, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(MeasurementPoint(7_100_000.0, complex(50.0, 0.0)),),
    )
    project = sample_project.with_measurement(
        measurement,
        updated_at=sample_project.updated_at + timedelta(hours=1),
    )
    updated = replace(measurement, name="Edited sweep", notes="after tuning")
    project = project.with_updated_measurement(
        updated,
        updated_at=sample_project.updated_at + timedelta(hours=2),
    )

    assert project.measurements == (updated,)

    project = project.without_measurement(
        measurement.id,
        updated_at=sample_project.updated_at + timedelta(hours=3),
    )
    assert project.measurements == ()


def test_project_rejects_unknown_measurement_updates(sample_project: Project) -> None:
    from datetime import UTC

    measurement = Measurement(
        id=uuid4(),
        name="Field sweep",
        created_at=datetime(2026, 11, 1, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(MeasurementPoint(7_100_000.0, complex(50.0, 0.0)),),
    )

    with pytest.raises(KeyError, match="unknown measurement"):
        sample_project.with_updated_measurement(measurement, updated_at=sample_project.updated_at)
    with pytest.raises(KeyError, match="unknown measurement"):
        sample_project.without_measurement(measurement.id, updated_at=sample_project.updated_at)


def test_project_rejects_naive_timestamps(sample_project: Project) -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        replace(sample_project, created_at=datetime(2026, 10, 29, 12, 0, 0))


def test_project_rejects_inverted_timestamps(sample_project: Project) -> None:
    with pytest.raises(ValueError, match="earlier"):
        replace(
            sample_project,
            updated_at=sample_project.created_at - timedelta(seconds=1),
        )


def test_project_with_design_replaces_without_mutating_original(
    sample_project: Project,
) -> None:
    design = sample_project.designs[0]
    updated_design = design.with_parameters(design.parameters.with_length(19.5))
    updated_at = sample_project.updated_at + timedelta(hours=1)

    edited_project = sample_project.with_design(updated_design, updated_at=updated_at)

    assert edited_project is not sample_project
    assert edited_project.updated_at == updated_at
    assert edited_project.designs[0].parameters.total_length_m == pytest.approx(19.5)
    assert sample_project.designs[0].parameters.total_length_m == pytest.approx(20.0)


def test_project_with_new_design_appends(sample_project: Project) -> None:
    new_id = uuid4()
    new_parameters: DipoleParameters = sample_project.designs[0].parameters.with_length(19.0)
    new_design = DesignVariant(
        id=new_id,
        name="Shortened",
        antenna_type="wire_dipole",
        parameters=new_parameters,
        antenna=new_parameters.to_antenna(name="Shortened"),
    )
    updated_at = sample_project.updated_at + timedelta(hours=1)

    edited_project = sample_project.with_design(new_design, updated_at=updated_at)

    assert len(edited_project.designs) == 2
    assert edited_project.design_by_id(new_id) == new_design


def test_missing_design_raises_key_error(sample_project: Project) -> None:
    with pytest.raises(KeyError):
        sample_project.design_by_id(uuid4())


def _simulation_run(project: Project, *, run_id: object | None = None) -> object:
    from antennadesk.domain.simulation.frequency import FrequencyPlan
    from antennadesk.domain.simulation.result import (
        FrequencyResult,
        SimulationResult,
        SimulationStatus,
    )
    from antennadesk.domain.simulation.run import SimulationRun
    from antennadesk.domain.simulation.solver import SolverMetadata
    from antennadesk.domain.simulation.spec import SimulationSpec

    design = project.designs[0]
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(design.parameters.frequency_hz))
    return SimulationRun(
        id=run_id if run_id is not None else uuid4(),  # type: ignore[arg-type]
        design_id=design.id,
        created_at=project.updated_at,
        result=SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=SolverMetadata(name="nec2c", version="1.3.3"),
            frequencies=(
                FrequencyResult(
                    frequency_hz=design.parameters.frequency_hz,
                    feed_tag=1,
                    feed_segment=11,
                    impedance_ohm=complex(50.0, 0.0),
                    swr=1.0,
                    input_power_w=0.001,
                ),
            ),
        ),
    )


def test_project_with_simulation_run(sample_project: Project) -> None:
    run = _simulation_run(sample_project)
    project = sample_project.with_simulation_run(  # type: ignore[arg-type]
        run,
        updated_at=sample_project.updated_at + timedelta(hours=1),
    )

    assert len(project.simulation_runs) == 1
    assert project.latest_simulation_run(sample_project.designs[0].id) == run
    assert len(sample_project.simulation_runs) == 0


def test_project_rejects_run_for_unknown_design(sample_project: Project) -> None:
    from dataclasses import replace

    run = _simulation_run(sample_project)
    invalid = replace(run, design_id=uuid4())  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="unknown design"):
        sample_project.with_simulation_run(  # type: ignore[arg-type]
            invalid,
            updated_at=sample_project.updated_at + timedelta(hours=1),
        )


def test_design_variant_accepts_a_folded_dipole() -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters

    parameters = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    )
    design = DesignVariant(
        id=uuid4(),
        name="Folded",
        antenna_type="folded_dipole",
        parameters=parameters,
        antenna=parameters.to_antenna(name="Folded"),
    )

    assert design.parameters is parameters
    assert len(design.antenna.wires) == 4


def test_design_variant_accepts_a_loop() -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=8,
    )
    design = DesignVariant(
        id=uuid4(),
        name="Loop",
        antenna_type="loop",
        parameters=parameters,
        antenna=parameters.to_antenna(name="Loop"),
    )

    assert design.parameters is parameters
    assert len(design.antenna.wires) == 8


def test_design_variant_rejects_a_mismatched_antenna_type() -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters

    parameters = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )

    with pytest.raises(ValueError, match="does not match"):
        DesignVariant(
            id=uuid4(),
            name="Wrong type",
            antenna_type="wire_dipole",
            parameters=parameters,
            antenna=parameters.to_antenna(name="Wrong type"),
        )


def test_with_parameters_updates_the_antenna_type() -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters

    original = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="40 m dipole",
            variant_name="Initial",
            parameters=DipoleParameters(
                frequency_hz=7_100_000.0,
                total_length_m=20.0,
                height_m=8.0,
            ),
        )
    )
    parameters = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    )

    design = original.designs[0].with_parameters(parameters)

    assert design.antenna_type == "folded_dipole"
    assert design.parameters is parameters
    assert len(design.antenna.wires) == 4


def test_compaction_keeps_only_the_latest_run_per_design(sample_project: Project) -> None:
    first = _simulation_run(sample_project)
    second = _simulation_run(sample_project)
    updated_at = sample_project.updated_at + timedelta(hours=1)
    project = sample_project.with_simulation_run(  # type: ignore[arg-type]
        first,
        updated_at=updated_at,
    ).with_simulation_run(  # type: ignore[arg-type]
        second,
        updated_at=updated_at + timedelta(hours=1),
    )

    compacted = project.with_latest_simulation_runs_only(updated_at=updated_at + timedelta(hours=2))

    assert len(project.simulation_runs) == 2
    assert compacted.simulation_runs == (second,)
    assert compacted.updated_at == updated_at + timedelta(hours=2)


def test_latest_simulation_run_ignores_band_runs(sample_project: Project) -> None:
    single = _simulation_run(sample_project)
    band = replace(  # type: ignore[arg-type]
        _simulation_run(sample_project),
        band_id="40m",
        batch_id=uuid4(),
    )
    updated_at = sample_project.updated_at + timedelta(hours=1)
    project = sample_project.with_simulation_run(  # type: ignore[arg-type]
        single,
        updated_at=updated_at,
    ).with_simulation_run(  # type: ignore[arg-type]
        band,
        updated_at=updated_at,
    )

    assert project.latest_simulation_run(sample_project.designs[0].id) == single
    assert project.latest_simulation_run_for_band(sample_project.designs[0].id, "40m") == band


def test_latest_band_analysis_groups_the_latest_batch(sample_project: Project) -> None:
    design_id = sample_project.designs[0].id
    first_batch = uuid4()
    second_batch = uuid4()
    updated_at = sample_project.updated_at + timedelta(hours=1)
    runs = (
        replace(  # type: ignore[arg-type]
            _simulation_run(sample_project),
            band_id="40m",
            batch_id=first_batch,
            created_at=updated_at,
        ),
        replace(  # type: ignore[arg-type]
            _simulation_run(sample_project),
            band_id="20m",
            batch_id=second_batch,
            created_at=updated_at + timedelta(minutes=1),
        ),
        replace(  # type: ignore[arg-type]
            _simulation_run(sample_project),
            band_id="10m",
            batch_id=second_batch,
            created_at=updated_at + timedelta(minutes=2),
        ),
    )
    project = sample_project
    for run in runs:
        project = project.with_simulation_run(  # type: ignore[arg-type]
            run,
            updated_at=run.created_at,  # type: ignore[attr-defined]
        )

    analysis = project.latest_band_analysis(design_id)

    assert analysis is not None
    assert analysis.batch_id == second_batch
    assert [band.band.name for band in analysis.bands] == ["20m", "10m"]


def test_compaction_keeps_latest_single_run_and_latest_band_batch(
    sample_project: Project,
) -> None:
    batch = uuid4()
    updated_at = sample_project.updated_at + timedelta(hours=1)
    single = _simulation_run(sample_project)
    band_40 = replace(  # type: ignore[arg-type]
        _simulation_run(sample_project),
        band_id="40m",
        batch_id=batch,
    )
    band_20 = replace(  # type: ignore[arg-type]
        _simulation_run(sample_project),
        band_id="20m",
        batch_id=batch,
    )
    project = sample_project
    for run in (single, band_40, band_20):
        project = project.with_simulation_run(  # type: ignore[arg-type]
            run,
            updated_at=updated_at,
        )

    assert project.has_compactable_simulation_history() is False
    compacted = project.with_latest_simulation_runs_only(updated_at=updated_at)
    assert len(compacted.simulation_runs) == 3


def test_compaction_keeps_only_the_latest_band_batch(sample_project: Project) -> None:
    design_id = sample_project.designs[0].id
    old_batch = uuid4()
    new_batch = uuid4()
    updated_at = sample_project.updated_at + timedelta(hours=1)
    runs = (
        replace(  # type: ignore[arg-type]
            _simulation_run(sample_project),
            band_id="40m",
            batch_id=old_batch,
            created_at=updated_at,
        ),
        replace(  # type: ignore[arg-type]
            _simulation_run(sample_project),
            band_id="20m",
            batch_id=old_batch,
            created_at=updated_at + timedelta(minutes=1),
        ),
        replace(  # type: ignore[arg-type]
            _simulation_run(sample_project),
            band_id="40m",
            batch_id=new_batch,
            created_at=updated_at + timedelta(minutes=2),
        ),
    )
    project = sample_project
    for run in runs:
        project = project.with_simulation_run(  # type: ignore[arg-type]
            run,
            updated_at=run.created_at,  # type: ignore[attr-defined]
        )

    assert project.has_compactable_simulation_history() is True
    compacted = project.with_latest_simulation_runs_only(updated_at=updated_at)
    analysis = compacted.latest_band_analysis(design_id)

    assert analysis is not None
    assert analysis.batch_id == new_batch
    assert [band.band.name for band in analysis.bands] == ["40m"]
    assert len(compacted.simulation_runs) == 1


def test_project_matching_design_is_cleared_when_the_network_is_removed(
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.matching_network import LNetwork
    from antennadesk.domain.design.matching_design import MatchingNetworkDesign

    network = LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)
    target = MatchingNetworkDesign(
        frequency_hz=7_100_000.0,
        load_resistance_ohm=100.0,
        load_reactance_ohm=20.0,
    )
    project = sample_project.with_matching_network(
        network,
        updated_at=sample_project.updated_at,
    ).with_matching_network_design(
        target,
        updated_at=sample_project.updated_at,
    )

    assert project.matching_network_design == target

    cleared = project.with_matching_network(
        None,
        updated_at=sample_project.updated_at,
    )

    assert cleared.matching_network is None
    assert cleared.matching_network_design is None


def test_project_records_a_current_balun(sample_project: Project) -> None:
    updated = sample_project.with_current_balun(
        True,
        updated_at=sample_project.updated_at,
    )
    cleared = updated.with_current_balun(
        False,
        updated_at=sample_project.updated_at,
    )

    assert sample_project.current_balun is False
    assert updated.current_balun is True
    assert cleared.current_balun is False
