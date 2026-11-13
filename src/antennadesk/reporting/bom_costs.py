# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Join the BOM rows with the project's manual unit costs."""

from __future__ import annotations

from dataclasses import dataclass

from ..domain.projects.project import DesignVariant, Project
from .construction_package import hardware_bom_items
from .localization import Labeler, identity_labeler
from .wire_schedule import conductor_bom_rows


@dataclass(frozen=True, slots=True)
class BomCostEntry:
    """One BOM row with its optional manual cost."""

    key: str
    label: str
    quantity: float
    unit: str
    unit_cost: float | None
    line_total: float | None
    note: str = ""


def hardware_cost_key(row_key: str) -> str:
    """Return the stable project key for one hardware BOM row."""

    return f"hardware:{row_key}"


def bom_cost_entries(
    project: Project,
    design: DesignVariant,
    labeler: Labeler | None = None,
) -> tuple[BomCostEntry, ...]:
    """Return every costable BOM row in display order.

    The hardware ``Antenna conductor`` line is intentionally excluded because
    the conductor BOM rows above it already carry the material/diameter cost.
    """

    tr = labeler or identity_labeler
    costs = project.bom_costs
    entries: list[BomCostEntry] = []
    for row in conductor_bom_rows(design.antenna):
        unit_cost = costs.cost_for(row.cost_key) if costs is not None else None
        entries.append(
            BomCostEntry(
                key=row.cost_key,
                label=tr(
                    "{material} Ø{diameter:.3f} mm",
                    material=tr(row.material),
                    diameter=row.diameter_mm,
                ),
                quantity=row.total_length_m,
                unit="m",
                unit_cost=unit_cost,
                line_total=(
                    row.total_length_m * unit_cost
                    if unit_cost is not None and row.total_length_m > 0.0
                    else None
                ),
                note=tr("From the conductor BOM"),
            )
        )
    for hardware_row in hardware_bom_items(project, design):
        if hardware_row.key == "antenna_conductor":
            continue
        key = hardware_cost_key(hardware_row.key)
        unit_cost = costs.cost_for(key) if costs is not None else None
        try:
            quantity = float(hardware_row.quantity)
        except ValueError:
            quantity = 0.0
        entries.append(
            BomCostEntry(
                key=key,
                label=tr(hardware_row.label),
                quantity=quantity,
                unit=hardware_row.unit,
                unit_cost=unit_cost,
                line_total=(
                    quantity * unit_cost if unit_cost is not None and quantity > 0.0 else None
                ),
                note=tr(hardware_row.note),
            )
        )
    return tuple(entries)


def bom_cost_total(entries: tuple[BomCostEntry, ...]) -> float | None:
    """Return the sum of the entered line costs, or ``None`` when empty."""

    values = [entry.line_total for entry in entries if entry.line_total is not None]
    return sum(values) if values else None


def format_cost(amount: float | None, currency: str) -> str:
    """Format a cost value with the project's free-form currency label."""

    if amount is None:
        return "—"
    return f"{amount:.2f} {currency}".strip()
