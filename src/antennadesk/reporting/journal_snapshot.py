# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build comparable, language-neutral snapshots of a design for the journal."""

from __future__ import annotations

from ..domain.projects.journal import JournalDesignSnapshot
from ..domain.projects.project import DesignVariant, Project
from .design_summary import design_summary_rows
from .localization import Labeler, identity_labeler


def journal_design_snapshot(project: Project, design: DesignVariant) -> JournalDesignSnapshot:
    """Capture the design summary plus canonical model counts.

    Rows are stored in the canonical English report form so a project can be
    reopened in another UI language. Present them through
    :func:`journal_snapshot_rows` when the journal is rendered.
    """

    rows = list(
        design_summary_rows(
            design.parameters,
            project_network=project.matching_network,
        )
    )
    known = {label for label, _ in rows}
    model = design.antenna
    counts = (
        ("Model wires", len(model.wires)),
        ("Model loads", len(model.loads)),
        ("Model transmission lines", len(model.transmission_lines)),
        ("Model sources", len(model.effective_sources)),
    )
    rows.extend((label, str(count)) for label, count in counts if label not in known)
    return JournalDesignSnapshot(
        design_id=design.id,
        design_name=design.name,
        antenna_type=design.antenna_type,
        frequency_hz=design.parameters.frequency_hz,
        rows=tuple(rows),
    )


def journal_snapshot_rows(
    snapshot: JournalDesignSnapshot,
    labeler: Labeler | None = None,
) -> tuple[tuple[str, str], ...]:
    """Return display rows, translating canonical labels and values."""

    tr = labeler or identity_labeler
    return tuple((tr(label), tr(value)) for label, value in snapshot.rows)
