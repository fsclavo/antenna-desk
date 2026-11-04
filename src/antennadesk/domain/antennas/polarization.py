# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Linear polarization for planar antenna arrays."""

from __future__ import annotations

from enum import StrEnum


class Polarization(StrEnum):
    """Orientation of the radiating elements relative to the ground plane."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
