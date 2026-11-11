# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reusable installation profiles for a project.

A profile records the physical envelope and constraints of a site. It is
metadata: it does not change the antenna model by itself. The advisor,
comparison, and report layers can use the active profile to explain whether a
design fits the available space, height, orientation, and ground assumptions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from ..common.units import (
    ensure_positive,
    normalize_azimuth_degrees,
)
from ..environment.ground import GroundModel

MAX_PROFILE_NAME_LENGTH = 200
MAX_PROFILE_NOTES_LENGTH = 4_000
MAX_PROFILE_IMAGE_REFERENCE_LENGTH = 1_000


class InstallationSupport(StrEnum):
    """The structure that supports the antenna."""

    MAST = "mast"
    TREE = "tree"
    BUILDING = "building"
    FENCE = "fence"
    PORTABLE = "portable"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class InstallationProfile:
    """A named site envelope and its practical constraints.

    ``available_height_m`` and ``available_width_m`` are upper bounds, not the
    design's actual dimensions. ``None`` means the user has not specified a
    limit. ``ground`` is a recommended site ground model; it is not applied to
    the antenna environment automatically.
    """

    id: UUID
    name: str
    available_height_m: float | None = None
    available_width_m: float | None = None
    orientation_deg: float = 0.0
    ground: GroundModel | None = None
    support: InstallationSupport = InstallationSupport.MAST
    notes: str = ""
    image_reference: str = ""

    def __post_init__(self) -> None:
        name = self.name.strip()
        if not name:
            raise ValueError("installation profile name must not be empty")
        if len(name) > MAX_PROFILE_NAME_LENGTH:
            raise ValueError(
                f"installation profile name must be at most {MAX_PROFILE_NAME_LENGTH} characters"
            )
        object.__setattr__(self, "name", name)

        if self.available_height_m is not None:
            ensure_positive(self.available_height_m, name="available_height_m")
        if self.available_width_m is not None:
            ensure_positive(self.available_width_m, name="available_width_m")

        object.__setattr__(
            self,
            "orientation_deg",
            normalize_azimuth_degrees(self.orientation_deg),
        )
        object.__setattr__(self, "support", InstallationSupport(self.support))

        if len(self.notes) > MAX_PROFILE_NOTES_LENGTH:
            raise ValueError(
                f"installation notes must be at most {MAX_PROFILE_NOTES_LENGTH} characters"
            )
        if len(self.image_reference) > MAX_PROFILE_IMAGE_REFERENCE_LENGTH:
            raise ValueError(
                "installation image reference must be at most "
                f"{MAX_PROFILE_IMAGE_REFERENCE_LENGTH} characters"
            )
