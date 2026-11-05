# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Published 94-foot doublet starting design."""

from __future__ import annotations

from ..environment.ground import FREE_SPACE, GroundModel
from .dipole import DipoleOrientation, DipoleParameters
from .feed_line import FeedLine
from .materials import COPPER, ConductorMaterial

# VU3DXR, "94-Foot Multi Band Doublet Antenna": 94 ft total, 41 ft of 450-ohm
# ladder line, 1:1 current balun, and a tuner.
DOUBLET_REFERENCE_TOTAL_LENGTH_M = 94.0 * 0.3048
DOUBLET_REFERENCE_FEED_LINE_LENGTH_M = 41.0 * 0.3048
DOUBLET_REFERENCE_FEED_LINE_IMPEDANCE_OHM = 450.0
DOUBLET_REFERENCE_FREQUENCY_HZ = 3_500_000.0


def doublet_parameters(
    *,
    frequency_hz: float = DOUBLET_REFERENCE_FREQUENCY_HZ,
    height_m: float = 10.0,
    orientation: DipoleOrientation = DipoleOrientation.HORIZONTAL,
    azimuth_deg: float = 0.0,
    wire_radius_m: float = 0.001,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> DipoleParameters:
    """Return the published 94-ft doublet radiator."""

    return DipoleParameters(
        frequency_hz=frequency_hz,
        total_length_m=DOUBLET_REFERENCE_TOTAL_LENGTH_M,
        height_m=height_m,
        orientation=orientation,
        azimuth_deg=azimuth_deg,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )


def doublet_feed_line(
    *,
    characteristic_impedance_ohm: float = DOUBLET_REFERENCE_FEED_LINE_IMPEDANCE_OHM,
    length_m: float = DOUBLET_REFERENCE_FEED_LINE_LENGTH_M,
    velocity_factor: float = 0.9,
    matched_loss_db_per_100m: float = 0.2,
) -> FeedLine:
    """Return the published 450-ohm, 41-ft doublet feed line.

    The source specifies the line impedance and length but not its velocity
    factor or loss; those remain application starting points.
    """

    return FeedLine(
        characteristic_impedance_ohm=characteristic_impedance_ohm,
        length_m=length_m,
        velocity_factor=velocity_factor,
        matched_loss_db_per_100m=matched_loss_db_per_100m,
    )
