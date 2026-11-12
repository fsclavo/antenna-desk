# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Construction package rows: as-built, hardware BOM, coils, and checklist."""

from __future__ import annotations

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


def hardware_bom_rows(
    project: Project,
    design: DesignVariant,
    labeler: Labeler | None = None,
) -> tuple[tuple[str, str, str, str], ...]:
    """Return a practical starting hardware BOM for the design."""

    tr = labeler or identity_labeler
    parameters = design.parameters
    beam = design.antenna_type in BEAM_TYPES
    wires = design.antenna.wires
    loads = design.antenna.loads
    trap_count = sum(isinstance(load, ParallelLoad) for load in loads)
    coil_count = sum(isinstance(load, SeriesLoad) and load.inductance_h > 0.0 for load in loads)
    radial_count = int(getattr(parameters, "radial_count", 0) or 0)
    ground = getattr(parameters, "ground", None)
    ground_rod = "1" if ground is not None and ground.kind is GroundKind.FINITE else "0"
    rows: list[tuple[str, str, str, str]] = [
        (
            "Antenna conductor",
            f"{sum(w.length_m for w in wires):.2f}",
            "m",
            "From the conductor BOM",
        ),
        (
            "Element clamps" if beam else "End insulators",
            str(len(wires)) if beam else "2",
            "pcs",
            "Starting estimate",
        ),
        ("Boom", "1" if beam else "0", "pcs", "Starting estimate" if beam else "—"),
        ("Feedpoint support / insulator", "1", "pcs", "—"),
        ("Mast or support", "1", "pcs", "—"),
        ("Coaxial connector", "2", "pcs", "—"),
        (
            "Balun / unun",
            "1"
            if project.balun_loss is not None
            or float(getattr(parameters, "transformer_ratio", 1.0)) != 1.0
            else "0",
            "pcs",
            "Use the transformer or balun in the design",
        ),
        (
            "Radial wire",
            str(radial_count),
            "wires",
            "Radial system" if radial_count else "—",
        ),
        (
            "Ground rod",
            ground_rod,
            "pcs",
            "Verify the local grounding requirement",
        ),
        ("Trap", str(trap_count), "pcs", "From the load table"),
        ("Loading coil", str(coil_count), "pcs", "From the load table"),
        ("Guy line / support rope", "1", "set", "Starting estimate"),
    ]
    return tuple((tr(item), quantity, unit, tr(note)) for item, quantity, unit, note in rows)


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
