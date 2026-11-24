# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project-level second-medium/cliff ground profile (far-field only)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..common.units import ensure_non_negative, ensure_positive

MAX_SITE_LABEL_LENGTH = 80
MAX_SITE_NOTES_LENGTH = 500


class EdgeShape(StrEnum):
    """How the second medium joins the first medium."""

    LINEAR = "linear"
    CIRCULAR = "circular"


@dataclass(frozen=True, slots=True)
class SiteGroundProfile:
    """A bounded cliff/second-medium profile.

    The first medium remains the design's ``GroundModel``. This profile only
    changes the far-field pattern; it does not change impedance, currents, or
    SWR. The native NEC radial-screen approximation is deliberately not
    represented here.
    """

    second_medium_relative_permittivity: float
    second_medium_conductivity_s_per_m: float
    edge_distance_m: float
    edge_shape: EdgeShape = EdgeShape.LINEAR
    edge_height_m: float = 0.0
    label: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        permittivity = ensure_positive(
            self.second_medium_relative_permittivity,
            name="second_medium_relative_permittivity",
        )
        if permittivity < 1.0:
            raise ValueError("second_medium_relative_permittivity must be at least 1")
        ensure_positive(
            self.second_medium_conductivity_s_per_m,
            name="second_medium_conductivity_s_per_m",
        )
        ensure_non_negative(self.edge_distance_m, name="edge_distance_m")
        ensure_non_negative(self.edge_height_m, name="edge_height_m")
        object.__setattr__(self, "edge_shape", EdgeShape(self.edge_shape))
        label = self.label.strip()
        notes = self.notes.strip()
        if len(label) > MAX_SITE_LABEL_LENGTH:
            raise ValueError(f"site label is longer than {MAX_SITE_LABEL_LENGTH} characters")
        if len(notes) > MAX_SITE_NOTES_LENGTH:
            raise ValueError(f"site notes are longer than {MAX_SITE_NOTES_LENGTH} characters")
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "notes", notes)

    @property
    def is_far_field_only(self) -> bool:
        return True
