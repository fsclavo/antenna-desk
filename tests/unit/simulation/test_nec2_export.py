# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""NEC-2 export provenance and determinism."""

from __future__ import annotations

from antennadesk.domain.antennas.beverage import beverage_parameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.nec2.export import NecDeckExportMetadata, render_nec_deck
from antennadesk.simulation.nec2.input_writer import write_nec2_input


def _metadata(
    *,
    project_name: str = "40 m test",
    design_name: str = "Dipole",
    antenna_type: str = "wire_dipole",
    app_version: str = "0.9.0",
    solver_name: str | None = "nec2c",
    solver_version: str | None = "0.9.0",
) -> NecDeckExportMetadata:
    return NecDeckExportMetadata(
        project_name=project_name,
        design_name=design_name,
        antenna_type=antenna_type,
        app_version=app_version,
        solver_name=solver_name,
        solver_version=solver_version,
    )


def _spec() -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(6_900_000.0, 7_300_000.0, 5),
        segmentation=SegmentationPolicy(
            target_segment_length_wavelengths=0.025,
            min_segments_per_wire=3,
            max_segments_per_wire=500,
        ),
        reference_impedance_ohm=50.0,
        far_field=FarFieldRequest(enabled=False),
    )


def test_export_header_contains_project_plan_ground_and_tool_versions() -> None:
    model = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    ).to_antenna(name="40 m dipole")

    text = render_nec_deck(model, _spec(), _metadata())

    assert text.startswith("CM AntennaDesk NEC-2 export\n")
    assert "CM Project: 40 m test" in text
    assert "CM Design: Dipole" in text
    assert "CM Antenna type: wire_dipole" in text
    assert "CM Application: AntennaDesk 0.9.0" in text
    assert "CM Solver: nec2c 0.9.0" in text
    assert "CM Frequency plan: 6.900000-7.300000 MHz, 5 points, step 0.100000 MHz" in text
    assert "CM Reference impedance: 50 ohm" in text
    assert "CM Ground: finite ground, epsilon_r=13, sigma=0.005 S/m" in text
    assert "CM Segmentation: target 0.025 wavelength, min 3, max 500" in text
    assert "GW " in text
    assert text.rstrip().endswith("EN")


def test_export_uses_the_same_body_as_the_simulation_writer() -> None:
    model = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    ).to_antenna(name="Dipole")
    spec = _spec()

    exported = render_nec_deck(model, spec, _metadata())
    direct_body = write_nec2_input(model, spec).text.split("CE", 1)[1]

    assert direct_body in exported
    assert exported == render_nec_deck(model, spec, _metadata())


def test_export_includes_the_beverage_transformer_and_omits_private_paths() -> None:
    model = beverage_parameters(frequency_hz=7_100_000.0).to_antenna(name="Beverage")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=3),
        far_field=FarFieldRequest(enabled=False),
        feed_transformer_ratio=9.0,
    )

    text = render_nec_deck(
        model,
        spec,
        _metadata(
            project_name="Beverage project",
            design_name="North beverage",
            antenna_type="beverage",
        ),
    )

    assert "CM Feed transformer: 9:1" in text
    assert "/usr/" not in text
    assert "raw_output" not in text
    assert "NEC-2 output" not in text
