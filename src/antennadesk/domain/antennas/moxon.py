# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parametric Moxon rectangle."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from ..common import units
from ..common.units import ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .materials import ALUMINUM, COPPER, ConductorMaterial
from .polarization import Polarization
from .wire import Wire

ANTENNA_TYPE_MOXON = "moxon"
REFLECTOR_ID = "reflector"
DRIVEN_ID = "driven"

# Geometry-validity envelope, not a performance target. The reference is the
# Cebik 20 m Moxon (14.17 MHz, 25.00 ft width, 9.57 ft depth, 4.85/4.00 ft
# tips, gap/lambda 0.0104, gap/depth 0.075, gap/width 0.029). The exploratory
# 2.4 GHz high-frequency control has gap/lambda 0.039, gap/depth 0.282, and
# gap/width 0.108. The limits below keep both inside with margin and reject the
# old 0.67 lambda failure mode. Do not use this envelope as a gain/SWR claim.
MOXON_GAP_MIN_WAVELENGTH_RATIO = 0.004
MOXON_GAP_MAX_WAVELENGTH_RATIO = 0.10
MOXON_GAP_MIN_DEPTH_RATIO = 0.03
MOXON_GAP_MAX_DEPTH_RATIO = 0.40
MOXON_GAP_MIN_WIDTH_RATIO = 0.01
MOXON_GAP_MAX_WIDTH_RATIO = 0.15
MOXON_WIDTH_MIN_DEPTH_RATIO = 1.5
MOXON_WIDTH_MAX_DEPTH_RATIO = 4.5
MOXON_REFLECTOR_TIP_MIN_DEPTH_RATIO = 0.20
MOXON_REFLECTOR_TIP_MAX_DEPTH_RATIO = 0.75
MOXON_DRIVEN_TIP_MIN_DEPTH_RATIO = 0.20
MOXON_DRIVEN_TIP_MAX_DEPTH_RATIO = 0.75
MOXON_TIPS_SUM_MIN_DEPTH_RATIO = 0.50
MOXON_TIPS_SUM_MAX_DEPTH_RATIO = 0.97


class MoxonGeometryIssueKind(StrEnum):
    POSITIVE = "positive"
    GAP_POSITIVE = "gap_positive"
    GAP_CLEARANCE = "gap_clearance"
    GAP_WAVELENGTH = "gap_wavelength"
    GAP_DEPTH = "gap_depth"
    GAP_WIDTH = "gap_width"
    WIDTH_DEPTH = "width_depth"
    REFLECTOR_TIP_DEPTH = "reflector_tip_depth"
    DRIVEN_TIP_DEPTH = "driven_tip_depth"
    TIPS_SUM_DEPTH = "tips_sum_depth"


@dataclass(frozen=True, slots=True)
class MoxonGeometryIssue:
    """One violated Moxon geometry-validity limit."""

    field: str
    kind: MoxonGeometryIssueKind
    actual: float
    minimum: float = 0.0
    maximum: float = 0.0

    @property
    def message_key(self) -> str:
        return f"moxon.constraint.{self.kind.value}"

    def message_values(self) -> dict[str, object]:
        values: dict[str, object] = {"actual": self.actual}
        if self.kind is not MoxonGeometryIssueKind.POSITIVE:
            values["minimum"] = self.minimum
        if self.kind not in {
            MoxonGeometryIssueKind.POSITIVE,
            MoxonGeometryIssueKind.GAP_POSITIVE,
            MoxonGeometryIssueKind.GAP_CLEARANCE,
        }:
            values["maximum"] = self.maximum
        return values

    def describe(self) -> str:
        if self.kind is MoxonGeometryIssueKind.POSITIVE:
            return f"Moxon {self.field} must be positive"
        if self.kind is MoxonGeometryIssueKind.GAP_POSITIVE:
            return "Moxon tip lengths must leave a positive gap between elements"
        if self.kind is MoxonGeometryIssueKind.GAP_CLEARANCE:
            return (
                f"Moxon gap {self.actual:.6g} m must exceed the conductor "
                f"diameter {self.minimum:.6g} m"
            )
        return (
            f"Moxon {self.field} ratio {self.actual:.6g} is outside "
            f"[{self.minimum:.6g}, {self.maximum:.6g}]"
        )


def validate_moxon_geometry(
    *,
    frequency_hz: float,
    width_m: float,
    depth_m: float,
    reflector_tip_m: float,
    driven_tip_m: float,
    wire_radius_m: float,
) -> tuple[MoxonGeometryIssue, ...]:
    """Return every geometry-validity violation for a Moxon rectangle.

    The limits are anchored to the Cebik 20 m reference and the exploratory
    2.4 GHz control described in ADR-0046. They are construction-validity
    limits, not published performance values.
    """

    for field, value in (
        ("frequency_hz", frequency_hz),
        ("width_m", width_m),
        ("depth_m", depth_m),
        ("reflector_tip_m", reflector_tip_m),
        ("driven_tip_m", driven_tip_m),
        ("wire_radius_m", wire_radius_m),
    ):
        if not math.isfinite(value) or value <= 0.0:
            return (MoxonGeometryIssue(field, MoxonGeometryIssueKind.POSITIVE, value),)

    gap = depth_m - reflector_tip_m - driven_tip_m
    if gap <= 0.0:
        return (MoxonGeometryIssue("gap_m", MoxonGeometryIssueKind.GAP_POSITIVE, gap),)

    issues: list[MoxonGeometryIssue] = []
    clearance = 2.0 * wire_radius_m
    if gap <= clearance:
        issues.append(
            MoxonGeometryIssue(
                "gap_m",
                MoxonGeometryIssueKind.GAP_CLEARANCE,
                gap,
                minimum=clearance,
            )
        )

    wavelength = units.SPEED_OF_LIGHT_M_PER_S / frequency_hz
    checks = (
        (
            "gap_m",
            MoxonGeometryIssueKind.GAP_WAVELENGTH,
            gap / wavelength,
            MOXON_GAP_MIN_WAVELENGTH_RATIO,
            MOXON_GAP_MAX_WAVELENGTH_RATIO,
        ),
        (
            "gap_m",
            MoxonGeometryIssueKind.GAP_DEPTH,
            gap / depth_m,
            MOXON_GAP_MIN_DEPTH_RATIO,
            MOXON_GAP_MAX_DEPTH_RATIO,
        ),
        (
            "gap_m",
            MoxonGeometryIssueKind.GAP_WIDTH,
            gap / width_m,
            MOXON_GAP_MIN_WIDTH_RATIO,
            MOXON_GAP_MAX_WIDTH_RATIO,
        ),
        (
            "width_m",
            MoxonGeometryIssueKind.WIDTH_DEPTH,
            width_m / depth_m,
            MOXON_WIDTH_MIN_DEPTH_RATIO,
            MOXON_WIDTH_MAX_DEPTH_RATIO,
        ),
        (
            "reflector_tip_m",
            MoxonGeometryIssueKind.REFLECTOR_TIP_DEPTH,
            reflector_tip_m / depth_m,
            MOXON_REFLECTOR_TIP_MIN_DEPTH_RATIO,
            MOXON_REFLECTOR_TIP_MAX_DEPTH_RATIO,
        ),
        (
            "driven_tip_m",
            MoxonGeometryIssueKind.DRIVEN_TIP_DEPTH,
            driven_tip_m / depth_m,
            MOXON_DRIVEN_TIP_MIN_DEPTH_RATIO,
            MOXON_DRIVEN_TIP_MAX_DEPTH_RATIO,
        ),
        (
            "reflector_tip_m",
            MoxonGeometryIssueKind.TIPS_SUM_DEPTH,
            (reflector_tip_m + driven_tip_m) / depth_m,
            MOXON_TIPS_SUM_MIN_DEPTH_RATIO,
            MOXON_TIPS_SUM_MAX_DEPTH_RATIO,
        ),
    )
    for field, kind, actual, minimum, maximum in checks:
        if actual < minimum or actual > maximum:
            issues.append(
                MoxonGeometryIssue(
                    field,
                    kind,
                    actual,
                    minimum=minimum,
                    maximum=maximum,
                )
            )
    return tuple(issues)


MOXON_GUARD_MARGIN = 0.05


def moxon_geometry_near_limit(
    parameters: MoxonParameters,
    *,
    margin: float = MOXON_GUARD_MARGIN,
) -> bool:
    """Return whether a valid Moxon sits close to a geometry-envelope edge.

    This is an Apply Best confirmation guard, not a validity check. The
    reference geometry stays comfortably inside the envelope; a design within
    ``margin`` of a boundary, or with less than two conductor diameters of gap,
    asks the user to confirm.
    """

    if not 0.0 < margin < 0.5:
        raise ValueError("margin must be between 0 and 0.5")
    wavelength = units.SPEED_OF_LIGHT_M_PER_S / parameters.frequency_hz
    gap = parameters.gap_m
    ratios = (
        (
            gap / wavelength,
            MOXON_GAP_MIN_WAVELENGTH_RATIO,
            MOXON_GAP_MAX_WAVELENGTH_RATIO,
        ),
        (
            gap / parameters.depth_m,
            MOXON_GAP_MIN_DEPTH_RATIO,
            MOXON_GAP_MAX_DEPTH_RATIO,
        ),
        (
            gap / parameters.width_m,
            MOXON_GAP_MIN_WIDTH_RATIO,
            MOXON_GAP_MAX_WIDTH_RATIO,
        ),
        (
            parameters.width_m / parameters.depth_m,
            MOXON_WIDTH_MIN_DEPTH_RATIO,
            MOXON_WIDTH_MAX_DEPTH_RATIO,
        ),
        (
            parameters.reflector_tip_m / parameters.depth_m,
            MOXON_REFLECTOR_TIP_MIN_DEPTH_RATIO,
            MOXON_REFLECTOR_TIP_MAX_DEPTH_RATIO,
        ),
        (
            parameters.driven_tip_m / parameters.depth_m,
            MOXON_DRIVEN_TIP_MIN_DEPTH_RATIO,
            MOXON_DRIVEN_TIP_MAX_DEPTH_RATIO,
        ),
        (
            (parameters.reflector_tip_m + parameters.driven_tip_m) / parameters.depth_m,
            MOXON_TIPS_SUM_MIN_DEPTH_RATIO,
            MOXON_TIPS_SUM_MAX_DEPTH_RATIO,
        ),
    )
    for actual, minimum, maximum in ratios:
        span = maximum - minimum
        if actual < minimum + margin * span or actual > maximum - margin * span:
            return True
    return gap < 4.0 * parameters.wire_radius_m


@dataclass(frozen=True, slots=True)
class MoxonParameters:
    """A Moxon rectangle with bent reflector and driven-element tips."""

    frequency_hz: float
    width_m: float
    depth_m: float
    reflector_tip_m: float
    driven_tip_m: float
    height_m: float = 10.0
    azimuth_deg: float = 0.0
    polarization: Polarization = Polarization.HORIZONTAL
    wire_radius_m: float = 0.001
    material: ConductorMaterial = ALUMINUM
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.width_m, name="width_m")
        ensure_positive(self.depth_m, name="depth_m")
        ensure_positive(self.reflector_tip_m, name="reflector_tip_m")
        ensure_positive(self.driven_tip_m, name="driven_tip_m")
        ensure_positive(self.height_m, name="height_m")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        issues = validate_moxon_geometry(
            frequency_hz=self.frequency_hz,
            width_m=self.width_m,
            depth_m=self.depth_m,
            reflector_tip_m=self.reflector_tip_m,
            driven_tip_m=self.driven_tip_m,
            wire_radius_m=self.wire_radius_m,
        )
        if issues:
            raise ValueError(issues[0].describe())
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )
        object.__setattr__(self, "polarization", Polarization(self.polarization))
        if self.polarization is Polarization.VERTICAL:
            lowest_edge = self.height_m - self.width_m / 2.0
            if lowest_edge <= 0.0:
                raise ValueError(
                    "a vertical Moxon would extend below ground; "
                    "increase height_m or reduce width_m"
                )

    @property
    def lowest_edge_m(self) -> float:
        """Return the height of the lowest point of the radiating rectangle."""

        if self.polarization is Polarization.HORIZONTAL:
            return self.height_m
        return self.height_m - self.width_m / 2.0

    @property
    def gap_m(self) -> float:
        return self.depth_m - self.reflector_tip_m - self.driven_tip_m

    def to_antenna(self, *, name: str = "Moxon") -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        half_width = self.width_m / 2.0
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        if self.polarization is Polarization.HORIZONTAL:

            def rotate(boom_m: float, element_m: float) -> Point3D:
                return Point3D(
                    x_m=boom_m * cos_angle - element_m * sin_angle,
                    y_m=boom_m * sin_angle + element_m * cos_angle,
                    z_m=self.height_m,
                )

        else:

            def rotate(boom_m: float, element_m: float) -> Point3D:
                return Point3D(
                    x_m=boom_m * cos_angle,
                    y_m=boom_m * sin_angle,
                    z_m=self.height_m + element_m,
                )

        wires = (
            Wire(
                id=REFLECTOR_ID,
                start=rotate(0.0, -half_width),
                end=rotate(0.0, half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="reflector-tip-1",
                start=rotate(0.0, -half_width),
                end=rotate(self.reflector_tip_m, -half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="reflector-tip-2",
                start=rotate(0.0, half_width),
                end=rotate(self.reflector_tip_m, half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id=DRIVEN_ID,
                start=rotate(self.depth_m, -half_width),
                end=rotate(self.depth_m, half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="driven-tip-1",
                start=rotate(self.depth_m, -half_width),
                end=rotate(self.depth_m - self.driven_tip_m, -half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
            Wire(
                id="driven-tip-2",
                start=rotate(self.depth_m, half_width),
                end=rotate(self.depth_m - self.driven_tip_m, half_width),
                radius_m=self.wire_radius_m,
                material=self.material,
            ),
        )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=wires,
            feed=FeedPoint(DRIVEN_ID, half_width),
            ground=self.ground,
            generator_id="moxon",
            generator_name="Moxon",
        )


FOOT_M = 0.3048
MOXON_REFERENCE_FREQUENCY_HZ = 14_170_000.0


def moxon_20m_wire(
    *,
    frequency_hz: float = MOXON_REFERENCE_FREQUENCY_HZ,
    height_m: float = 10.0,
    azimuth_deg: float = 0.0,
    polarization: Polarization = Polarization.HORIZONTAL,
    wire_radius_m: float = 0.000912,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
) -> MoxonParameters:
    """Return the published 20 m wire Moxon from L. B. Cebik, W4RNL.

    The 14.17 MHz case is the exact published reference: Table 1 (20 m wire),
    using #14 copper wire. The source reports 56-58 ohm feedpoint impedance,
    5.8 dBi free-space gain, and greater than 32 dB front-to-back ratio.
    Other frequencies are scaled linearly from that reference and are a
    heuristic starting point, not an independent reference.
    """

    ensure_positive(frequency_hz, name="frequency_hz")
    scale = MOXON_REFERENCE_FREQUENCY_HZ / frequency_hz
    return MoxonParameters(
        frequency_hz=frequency_hz,
        width_m=25.00 * FOOT_M * scale,
        depth_m=9.57 * FOOT_M * scale,
        reflector_tip_m=4.85 * FOOT_M * scale,
        driven_tip_m=4.00 * FOOT_M * scale,
        height_m=height_m,
        azimuth_deg=azimuth_deg,
        polarization=polarization,
        wire_radius_m=wire_radius_m,
        material=material,
        ground=ground,
    )
