# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Construction package rows: as-built, hardware BOM, coils, and checklist."""

from __future__ import annotations

from dataclasses import dataclass

from ..domain.antennas.load import ParallelLoad, SeriesLoad
from ..domain.environment.ground import GroundKind
from ..domain.projects.construction import (
    CONSTRUCTION_CHECKLIST_KEYS,
    ConstructionRecord,
)
from ..domain.projects.project import DesignVariant, Project
from .localization import Labeler, identity_labeler

BEAM_TYPES = frozenset({"yagi", "moxon", "hexbeam", "trap_yagi", "quad_beam"})

CHECKLIST_LABELS_EN: dict[str, str] = {
    "prepare_drawings": "Prepare the construction drawing and wire schedule.",
    "check_dimensions": "Check every dimension against the design before cutting.",
    "inspect_insulators": "Inspect insulators, supports, and hardware for damage.",
    "check_feedpoint": "Check the feedpoint, balun/unun, and strain relief.",
    "seal_connectors": "Seal outdoor connectors and route the coax safely.",
    "check_supports": "Check mast, guy lines, and clearances.",
    "verify_grounding": "Verify station and antenna grounding.",
    "measure_swr": "Measure SWR and resonance with the installed feed line.",
    "record_measurement": "Record the measurement session in the project.",
    "update_as_built": "Update the as-built dimensions and notes.",
}


@dataclass(frozen=True, slots=True)
class HardwareBomRow:
    """One practical hardware line with a stable cost key."""

    key: str
    label: str
    quantity: str
    unit: str
    note: str


def as_built_rows(
    record: ConstructionRecord | None,
    labeler: Labeler | None = None,
) -> tuple[tuple[str, str, str, str, str], ...]:
    """Return measured dimension rows for the construction sheet."""

    if record is None:
        return ()
    tr = labeler or identity_labeler
    rows: list[tuple[str, str, str, str, str]] = []
    for dimension in record.dimensions:
        design = (
            f"{dimension.design_value_m:.3f} m" if dimension.design_value_m is not None else "—"
        )
        actual = (
            f"{dimension.actual_value_m:.3f} m" if dimension.actual_value_m is not None else "—"
        )
        difference = "—"
        if dimension.design_value_m is not None and dimension.actual_value_m is not None:
            difference = f"{dimension.actual_value_m - dimension.design_value_m:+.3f} m"
        rows.append(
            (
                dimension.label,
                design,
                actual,
                difference,
                tr(dimension.notes),
            )
        )
    return tuple(rows)


def hardware_bom_items(
    project: Project,
    design: DesignVariant,
) -> tuple[HardwareBomRow, ...]:
    """Return the practical hardware BOM with stable cost keys."""

    parameters = design.parameters
    beam = design.antenna_type in BEAM_TYPES
    wires = design.antenna.wires
    loads = design.antenna.loads
    trap_count = sum(isinstance(load, ParallelLoad) for load in loads)
    coil_count = sum(isinstance(load, SeriesLoad) and load.inductance_h > 0.0 for load in loads)
    radial_count = int(getattr(parameters, "radial_count", 0) or 0)
    ground = getattr(parameters, "ground", None)
    ground_rod = "1" if ground is not None and ground.kind is GroundKind.FINITE else "0"
    rows: list[HardwareBomRow] = [
        HardwareBomRow(
            key="antenna_conductor",
            label="Antenna conductor",
            quantity=f"{sum(w.length_m for w in wires):.2f}",
            unit="m",
            note="From the conductor BOM",
        ),
        HardwareBomRow(
            key="element_clamps" if beam else "end_insulators",
            label="Element clamps" if beam else "End insulators",
            quantity=str(len(wires)) if beam else "2",
            unit="pcs",
            note="Starting estimate",
        ),
        HardwareBomRow(
            key="boom",
            label="Boom",
            quantity="1" if beam else "0",
            unit="pcs",
            note="Starting estimate" if beam else "—",
        ),
        HardwareBomRow(
            key="feedpoint_support",
            label="Feedpoint support / insulator",
            quantity="1",
            unit="pcs",
            note="—",
        ),
        HardwareBomRow(
            key="mast",
            label="Mast or support",
            quantity="1",
            unit="pcs",
            note="—",
        ),
        HardwareBomRow(
            key="coax_connector",
            label="Coaxial connector",
            quantity="2",
            unit="pcs",
            note="—",
        ),
        HardwareBomRow(
            key="balun",
            label="Balun / unun",
            quantity=(
                "1"
                if project.balun_loss is not None
                or float(getattr(parameters, "transformer_ratio", 1.0)) != 1.0
                else "0"
            ),
            unit="pcs",
            note="Use the transformer or balun in the design",
        ),
        HardwareBomRow(
            key="radial_wire",
            label="Radial wire",
            quantity=str(radial_count),
            unit="wires",
            note="Radial system" if radial_count else "—",
        ),
        HardwareBomRow(
            key="ground_rod",
            label="Ground rod",
            quantity=ground_rod,
            unit="pcs",
            note="Verify the local grounding requirement",
        ),
        HardwareBomRow(
            key="trap",
            label="Trap",
            quantity=str(trap_count),
            unit="pcs",
            note="From the load table",
        ),
        HardwareBomRow(
            key="loading_coil",
            label="Loading coil",
            quantity=str(coil_count),
            unit="pcs",
            note="From the load table",
        ),
        HardwareBomRow(
            key="guy_line",
            label="Guy line / support rope",
            quantity="1",
            unit="set",
            note="Starting estimate",
        ),
    ]
    return tuple(rows)


def hardware_bom_rows(
    project: Project,
    design: DesignVariant,
    labeler: Labeler | None = None,
) -> tuple[tuple[str, str, str, str], ...]:
    """Return the translated practical hardware BOM for the design."""

    tr = labeler or identity_labeler
    return tuple(
        (tr(row.label), row.quantity, row.unit, tr(row.note))
        for row in hardware_bom_items(project, design)
    )


def coil_trap_rows(
    design: DesignVariant,
    labeler: Labeler | None = None,
) -> tuple[tuple[str, str, str, str, str, str, str], ...]:
    """Return target values for every loading coil and trap."""

    tr = labeler or identity_labeler
    rows: list[tuple[str, str, str, str, str, str, str]] = []
    for load in design.antenna.loads:
        if isinstance(load, ParallelLoad):
            kind = tr("Trap")
            capacitance = f"{load.capacitance_f * 1e12:.3f} pF"
        elif isinstance(load, SeriesLoad) and load.inductance_h > 0.0:
            kind = tr("Loading coil")
            capacitance = "—"
        else:
            continue
        rows.append(
            (
                kind,
                load.wire_id,
                f"{load.offset_m:.3f} m",
                f"{load.inductance_h * 1e6:.3f} µH",
                capacitance,
                f"{load.resistance_ohm:.3f} Ω",
                tr("Target value; verify with the solver and a measurement"),
            )
        )
    return tuple(rows)


def checklist_rows(
    record: ConstructionRecord | None,
    labeler: Labeler | None = None,
) -> tuple[tuple[str, bool], ...]:
    """Return the construction checklist in stable order."""

    tr = labeler or identity_labeler
    checked = record.checked_keys() if record is not None else frozenset()
    return tuple(
        (
            tr(CHECKLIST_LABELS_EN[key]),
            key in checked,
        )
        for key in CONSTRUCTION_CHECKLIST_KEYS
    )
