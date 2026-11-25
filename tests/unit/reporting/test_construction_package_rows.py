# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Construction package rows."""

from __future__ import annotations

from uuid import uuid4

from antennadesk.domain.antennas.load import ParallelLoad, SeriesLoad
from antennadesk.domain.antennas.stacked_yagi import (
    StackedYagiFeed,
    StackedYagiFeedMode,
    StackedYagiParameters,
)
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.projects.construction import (
    AsBuiltDimension,
    ConstructionChecklistItem,
    ConstructionRecord,
)
from antennadesk.domain.projects.project import Project
from antennadesk.reporting.construction_package import (
    as_built_rows,
    checklist_rows,
    coil_trap_rows,
    hardware_bom_rows,
)


def test_hardware_bom_has_a_practical_starting_set(
    sample_project: Project,
) -> None:
    rows = dict(
        (item, (quantity, unit, note))
        for item, quantity, unit, note in hardware_bom_rows(
            sample_project,
            sample_project.designs[0],
        )
    )

    assert rows["Antenna conductor"][0] == "20.00"
    assert rows["End insulators"][0] == "2"
    assert rows["Coaxial connector"][0] == "2"
    assert rows["Balun / unun"][0] == "0"


def test_coil_and_trap_rows_report_target_values(
    sample_project: Project,
) -> None:
    design = sample_project.designs[0]
    design = design.with_loads(
        (
            SeriesLoad(
                id="coil",
                wire_id="radiator",
                offset_m=5.0,
                inductance_h=10e-6,
                resistance_ohm=0.2,
            ),
            ParallelLoad(
                id="trap",
                wire_id="radiator",
                offset_m=7.5,
                inductance_h=5e-6,
                capacitance_f=100e-12,
            ),
        )
    )

    rows = coil_trap_rows(design)

    assert rows[0][0] == "Loading coil"
    assert rows[0][3] == "10.000 µH"
    assert rows[1][0] == "Trap"
    assert rows[1][4] == "100.000 pF"


def test_as_built_and_checklist_rows(sample_project: Project) -> None:
    record = ConstructionRecord(
        as_built_notes="Built in the back yard",
        dimensions=(
            AsBuiltDimension(
                id=uuid4(),
                label="Radiator length",
                design_value_m=20.0,
                actual_value_m=19.9,
                notes="Short by 10 cm",
            ),
        ),
        checklist=(ConstructionChecklistItem("measure_swr", checked=True),),
    )

    dimensions = as_built_rows(record)
    checklist = dict(checklist_rows(record))

    assert dimensions[0][0] == "Radiator length"
    assert dimensions[0][3] == "-0.100 m"
    assert dimensions[0][4] == "Short by 10 cm"
    assert checklist["Measure SWR and resonance with the installed feed line."] is True
    assert checklist["Check every dimension against the design before cutting."] is False


def test_stacked_yagi_phase_line_bom_adds_splitter_and_coax(
    sample_project: Project,
) -> None:
    stack = StackedYagiParameters(
        yagi=YagiParameters(
            frequency_hz=14_100_000.0,
            elements=(
                YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
                YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
            ),
            height_m=10.0,
        ),
        count=2,
        spacing_m=10.6,
        feed=StackedYagiFeed(
            mode=StackedYagiFeedMode.PHASE_LINES,
            reference_length_m=2.0,
            line_increment_m=2.5,
            velocity_factor=0.8,
            characteristic_impedance_ohm=75.0,
            splitter_loss_db=0.4,
        ),
    )
    design = sample_project.designs[0].with_parameters(stack)

    rows = dict(
        (item, (quantity, unit, note))
        for item, quantity, unit, note in hardware_bom_rows(sample_project, design)
    )

    assert rows["Splitter"][0] == "1"
    assert rows["Phase-line coax"][0] == "6.50"
    assert "feed network" in rows["Phase-line coax"][2].lower()
