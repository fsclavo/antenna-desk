# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parametric Yagi-Uda geometry generated as an editable custom-wire design."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .materials import COPPER, ConductorMaterial
from .polarization import Polarization
from .wire import Wire

YAGI_ELEMENT_ID_PREFIX = "element"
ANTENNA_TYPE_YAGI = "yagi"
YAGI_ELEMENT_LENGTH_MIN_FACTOR = 0.35
YAGI_ELEMENT_LENGTH_MAX_FACTOR = 0.65


class YagiMatchType(StrEnum):
    NONE = "none"
    BETA_HAIRPIN = "beta_hairpin"


@dataclass(frozen=True, slots=True)
class YagiElement:
    """One straight element placed along the boom.

    ``position_m`` is measured from the reflector toward the directors.
    ``length_m`` is the full tip-to-tip element length.
    """

    position_m: float
    length_m: float
    radius_m: float

    def __post_init__(self) -> None:
        ensure_non_negative(self.position_m, name="position_m")
        ensure_positive(self.length_m, name="length_m")
        ensure_positive(self.radius_m, name="radius_m")


@dataclass(frozen=True, slots=True)
class YagiParameters:
    """A Yagi-Uda geometry with arbitrary element lengths and spacings."""

    frequency_hz: float
    elements: tuple[YagiElement, ...]
    height_m: float
    driven_index: int = 1
    driven_folded: bool = False
    driven_fold_spacing_m: float = 0.1
    match_type: YagiMatchType = YagiMatchType.NONE
    match_length_m: float = 0.2
    match_spacing_m: float = 0.1
    azimuth_deg: float = 0.0
    polarization: Polarization = Polarization.HORIZONTAL
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_non_negative(self.height_m, name="height_m")
        elements = tuple(sorted(self.elements, key=lambda element: element.position_m))
        object.__setattr__(self, "elements", elements)
        if len(elements) < 2:
            raise ValueError("a Yagi requires at least a reflector and a driven element")
        for index, element in enumerate(elements):
            if index > 0 and math.isclose(
                element.position_m,
                elements[index - 1].position_m,
                rel_tol=0.0,
                abs_tol=1e-9,
            ):
                raise ValueError("Yagi element positions must be distinct")
        if not 0 <= self.driven_index < len(elements):
            raise ValueError("driven_index is outside the element list")
        ensure_non_negative(self.driven_fold_spacing_m, name="driven_fold_spacing_m")
        if self.driven_folded:
            ensure_positive(self.driven_fold_spacing_m, name="driven_fold_spacing_m")
        object.__setattr__(self, "match_type", YagiMatchType(self.match_type))
        if self.match_type is not YagiMatchType.NONE:
            ensure_positive(self.match_length_m, name="match_length_m")
            ensure_positive(self.match_spacing_m, name="match_spacing_m")
            if self.driven_folded:
                raise ValueError("a matching harness needs a straight driven element")
            if self.match_spacing_m >= elements[self.driven_index].length_m:
                raise ValueError("match_spacing_m must be shorter than the driven element")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )
        object.__setattr__(self, "polarization", Polarization(self.polarization))
        if self.polarization is Polarization.VERTICAL and self.lowest_tip_m <= 0.0:
            raise ValueError(
                "vertical Yagi elements would extend below ground; "
                "increase height_m or reduce the longest element"
            )

    @property
    def lowest_tip_m(self) -> float:
        """Return the height of the lowest point of the longest element."""

        if self.polarization is Polarization.HORIZONTAL:
            return self.height_m
        return self.height_m - max(element.length_m for element in self.elements) / 2.0

    @property
    def wavelength_m(self) -> float:
        return units.wavelength_m(self.frequency_hz)

    @classmethod
    def from_custom_parameters(
        cls,
        parameters: CustomAntennaParameters,
    ) -> YagiParameters:
        if any(wire.id.endswith("-hairpin-a") for wire in parameters.wires):
            return cls._from_custom_hairpin(parameters)
        if any(_folded_wire_number(wire.id) is not None for wire in parameters.wires):
            return cls._from_custom_folded(parameters)
        if len(parameters.wires) < 2:
            raise ValueError("a Yagi requires at least two wires")
        wires = parameters.wires
        z_values = [point.z_m for wire in wires for point in (wire.start, wire.end)]
        horizontal = max(z_values) - min(z_values) <= 1e-6
        vertical = all(
            math.isclose(wire.start.x_m, wire.end.x_m, abs_tol=1e-6)
            and math.isclose(wire.start.y_m, wire.end.y_m, abs_tol=1e-6)
            for wire in wires
        )
        if not horizontal and not vertical:
            raise ValueError("Yagi elements must be all horizontal or all vertical")
        if vertical:
            centers_z = [(wire.start.z_m + wire.end.z_m) / 2.0 for wire in wires]
            if max(centers_z) - min(centers_z) > 1e-6:
                raise ValueError("vertical Yagi elements must share a boom height")
            polarization = Polarization.VERTICAL
            height_m = centers_z[0]
        else:
            polarization = Polarization.HORIZONTAL
            height_m = wires[0].start.z_m

        first = wires[0]
        first_dx = first.end.x_m - first.start.x_m
        first_dy = first.end.y_m - first.start.y_m
        first_length = math.hypot(first_dx, first_dy)
        if not horizontal:
            first_length = abs(first.end.z_m - first.start.z_m)
        if first_length <= 1e-9:
            raise ValueError("Yagi elements must have a positive length")

        midpoints: list[tuple[float, float]] = []
        if horizontal:
            direction_x = first_dx / first_length
            direction_y = first_dy / first_length
            for wire in wires:
                dx = wire.end.x_m - wire.start.x_m
                dy = wire.end.y_m - wire.start.y_m
                length = math.hypot(dx, dy)
                if length <= 1e-9:
                    raise ValueError("Yagi elements must be horizontal")
                if abs(direction_x * dy - direction_y * dx) > 1e-6 * length:
                    raise ValueError("Yagi elements must be parallel")
                midpoints.append(
                    (
                        (wire.start.x_m + wire.end.x_m) / 2.0,
                        (wire.start.y_m + wire.end.y_m) / 2.0,
                    )
                )
        else:
            for wire in wires:
                midpoints.append((wire.start.x_m, wire.start.y_m))

        boom_x = midpoints[1][0] - midpoints[0][0]
        boom_y = midpoints[1][1] - midpoints[0][1]
        boom_length = math.hypot(boom_x, boom_y)
        if boom_length <= 1e-9:
            raise ValueError("Yagi elements must have distinct boom positions")
        boom_x /= boom_length
        boom_y /= boom_length
        raw_positions = [
            (midpoint[0] - midpoints[0][0]) * boom_x + (midpoint[1] - midpoints[0][1]) * boom_y
            for midpoint in midpoints
        ]
        offset = min(raw_positions)
        elements_with_index = [
            (
                index,
                YagiElement(
                    position_m=position - offset,
                    length_m=wire.length_m,
                    radius_m=wire.radius_m,
                ),
            )
            for index, (position, wire) in enumerate(zip(raw_positions, wires, strict=True))
        ]
        elements_with_index.sort(key=lambda item: item[1].position_m)
        driven_index = next(
            index
            for index, (wire_index, _element) in enumerate(elements_with_index)
            if wires[wire_index].id == parameters.feed.wire_id
        )
        return cls(
            frequency_hz=parameters.frequency_hz,
            elements=tuple(element for _index, element in elements_with_index),
            height_m=height_m,
            driven_index=driven_index,
            azimuth_deg=math.degrees(math.atan2(boom_y, boom_x)),
            polarization=polarization,
            material=first.material,
            ground=parameters.ground,
        )

    @classmethod
    def _from_custom_hairpin(
        cls,
        parameters: CustomAntennaParameters,
    ) -> YagiParameters:
        feed_wire = next((wire for wire in parameters.wires if wire.id.endswith("-feed")), None)
        if feed_wire is None:
            raise ValueError("the beta/hairpin feed wire is missing")
        feed_parts = feed_wire.id.split("-")
        try:
            driven_number = int(feed_parts[1])
        except (IndexError, ValueError) as exc:
            raise ValueError("the beta/hairpin feed wire id is invalid") from exc
        left = next(
            (wire for wire in parameters.wires if wire.id == f"element-{driven_number}-left"),
            None,
        )
        right = next(
            (wire for wire in parameters.wires if wire.id == f"element-{driven_number}-right"),
            None,
        )
        hairpin_a = next(
            (wire for wire in parameters.wires if wire.id == f"element-{driven_number}-hairpin-a"),
            None,
        )
        if left is None or right is None or hairpin_a is None:
            raise ValueError("the beta/hairpin driven element is incomplete")
        element_data: dict[int, tuple[float, float, Point3D, Wire]] = {}
        for wire in parameters.wires:
            parts = wire.id.split("-")
            if len(parts) != 2 or parts[0] != YAGI_ELEMENT_ID_PREFIX:
                continue
            try:
                number = int(parts[1])
            except ValueError:
                continue
            element_data[number] = (
                wire.length_m,
                wire.radius_m,
                _midpoint(wire),
                wire,
            )
        element_data[driven_number] = (
            left.length_m + feed_wire.length_m + right.length_m,
            left.radius_m,
            Point3D(
                x_m=(left.start.x_m + right.end.x_m) / 2.0,
                y_m=(left.start.y_m + right.end.y_m) / 2.0,
                z_m=(left.start.z_m + right.end.z_m) / 2.0,
            ),
            left,
        )
        if len(element_data) < 2:
            raise ValueError("a beta/hairpin Yagi requires at least two main elements")
        main_indices = sorted(element_data)
        orientation_wires = [element_data[index][3] for index in main_indices]
        horizontal = all(
            math.isclose(wire.start.z_m, wire.end.z_m, abs_tol=1e-6) for wire in orientation_wires
        )
        vertical = all(
            math.isclose(wire.start.x_m, wire.end.x_m, abs_tol=1e-6)
            and math.isclose(wire.start.y_m, wire.end.y_m, abs_tol=1e-6)
            for wire in orientation_wires
        )
        if not horizontal and not vertical:
            raise ValueError("beta/hairpin Yagi elements must be all horizontal or vertical")
        if horizontal:
            height_m = orientation_wires[0].start.z_m
        else:
            centers = [(wire.start.z_m + wire.end.z_m) / 2.0 for wire in orientation_wires]
            if max(centers) - min(centers) > 1e-6:
                raise ValueError("vertical Yagi elements must share a boom height")
            height_m = centers[0]
        midpoints = [element_data[index][2] for index in main_indices]
        boom_x = midpoints[1].x_m - midpoints[0].x_m
        boom_y = midpoints[1].y_m - midpoints[0].y_m
        boom_length = math.hypot(boom_x, boom_y)
        if boom_length <= 1e-9:
            raise ValueError("Yagi elements must have distinct boom positions")
        boom_x /= boom_length
        boom_y /= boom_length
        raw_positions = [
            (midpoint.x_m - midpoints[0].x_m) * boom_x + (midpoint.y_m - midpoints[0].y_m) * boom_y
            for midpoint in midpoints
        ]
        offset = min(raw_positions)
        elements_with_number = sorted(
            (
                (
                    number,
                    YagiElement(
                        position_m=position - offset,
                        length_m=element_data[number][0],
                        radius_m=element_data[number][1],
                    ),
                )
                for number, position in zip(main_indices, raw_positions, strict=True)
            ),
            key=lambda item: item[1].position_m,
        )
        driven_index = next(
            index
            for index, (number, _element) in enumerate(elements_with_number)
            if number == driven_number
        )
        return cls(
            frequency_hz=parameters.frequency_hz,
            elements=tuple(element for _number, element in elements_with_number),
            height_m=height_m,
            driven_index=driven_index,
            match_type=YagiMatchType.BETA_HAIRPIN,
            match_length_m=hairpin_a.length_m,
            match_spacing_m=feed_wire.length_m,
            azimuth_deg=math.degrees(math.atan2(boom_y, boom_x)),
            polarization=Polarization.VERTICAL if vertical else Polarization.HORIZONTAL,
            material=left.material,
            ground=parameters.ground,
        )

    @classmethod
    def _from_custom_folded(
        cls,
        parameters: CustomAntennaParameters,
    ) -> YagiParameters:
        main_wires: dict[int, Wire] = {}
        for wire in parameters.wires:
            if not wire.id.startswith(f"{YAGI_ELEMENT_ID_PREFIX}-"):
                continue
            parts = wire.id.split("-")
            if len(parts) == 2 or (len(parts) == 3 and parts[2] == "a"):
                try:
                    main_wires[int(parts[1])] = wire
                except ValueError:
                    continue
        if len(main_wires) < 2:
            raise ValueError("a folded Yagi requires at least two main elements")
        main_indices = sorted(main_wires)
        main = [main_wires[index] for index in main_indices]
        horizontal = all(math.isclose(wire.start.z_m, wire.end.z_m, abs_tol=1e-6) for wire in main)
        vertical = all(
            math.isclose(wire.start.x_m, wire.end.x_m, abs_tol=1e-6)
            and math.isclose(wire.start.y_m, wire.end.y_m, abs_tol=1e-6)
            for wire in main
        )
        if not horizontal and not vertical:
            raise ValueError("folded Yagi main elements must be all horizontal or vertical")
        driven_number = _folded_wire_number(parameters.feed.wire_id)
        if driven_number is None or driven_number not in main_wires:
            raise ValueError("the folded Yagi feed must be on element-N-a")
        driven_wire = main_wires[driven_number]
        folded_partner = next(
            (
                wire
                for wire in parameters.wires
                if wire.id == f"{YAGI_ELEMENT_ID_PREFIX}-{driven_number}-b"
            ),
            None,
        )
        if folded_partner is None:
            raise ValueError("the folded driven element is missing its second conductor")
        spacing_m = _midpoint(driven_wire).distance_to(_midpoint(folded_partner))
        midpoints: list[Point3D] = []
        for index, wire in zip(main_indices, main, strict=True):
            if index == driven_number:
                first_midpoint = _midpoint(driven_wire)
                second_midpoint = _midpoint(folded_partner)
                midpoints.append(
                    Point3D(
                        x_m=(first_midpoint.x_m + second_midpoint.x_m) / 2.0,
                        y_m=(first_midpoint.y_m + second_midpoint.y_m) / 2.0,
                        z_m=(first_midpoint.z_m + second_midpoint.z_m) / 2.0,
                    )
                )
            else:
                midpoints.append(_midpoint(wire))
        if horizontal:
            height_m = main[0].start.z_m
        else:
            centers = [(wire.start.z_m + wire.end.z_m) / 2.0 for wire in main]
            if max(centers) - min(centers) > 1e-6:
                raise ValueError("vertical Yagi elements must share a boom height")
            height_m = centers[0]
        boom_x = midpoints[1].x_m - midpoints[0].x_m
        boom_y = midpoints[1].y_m - midpoints[0].y_m
        boom_length = math.hypot(boom_x, boom_y)
        if boom_length <= 1e-9:
            raise ValueError("Yagi elements must have distinct boom positions")
        boom_x /= boom_length
        boom_y /= boom_length
        raw_positions = [
            (midpoint.x_m - midpoints[0].x_m) * boom_x + (midpoint.y_m - midpoints[0].y_m) * boom_y
            for midpoint in midpoints
        ]
        offset = min(raw_positions)
        elements_with_number = sorted(
            (
                (
                    index,
                    YagiElement(
                        position_m=position - offset,
                        length_m=wire.length_m,
                        radius_m=wire.radius_m,
                    ),
                )
                for index, position, wire in zip(
                    main_indices,
                    raw_positions,
                    main,
                    strict=True,
                )
            ),
            key=lambda item: item[1].position_m,
        )
        driven_index = next(
            index
            for index, (number, _element) in enumerate(elements_with_number)
            if number == driven_number
        )
        return cls(
            frequency_hz=parameters.frequency_hz,
            elements=tuple(element for _number, element in elements_with_number),
            height_m=height_m,
            driven_index=driven_index,
            driven_folded=True,
            driven_fold_spacing_m=spacing_m,
            azimuth_deg=math.degrees(math.atan2(boom_y, boom_x)),
            polarization=Polarization.VERTICAL if vertical else Polarization.HORIZONTAL,
            material=main[0].material,
            ground=parameters.ground,
        )

    def to_antenna(self, *, name: str = "Yagi") -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        def rotate(local: Point3D) -> Point3D:
            return Point3D(
                x_m=local.x_m * cos_angle - local.y_m * sin_angle,
                y_m=local.x_m * sin_angle + local.y_m * cos_angle,
                z_m=local.z_m,
            )

        def wire(wire_id: str, local_start: Point3D, local_end: Point3D, radius: float) -> Wire:
            return Wire(
                id=wire_id,
                start=rotate(local_start),
                end=rotate(local_end),
                radius_m=radius,
                material=self.material,
            )

        wires: list[Wire] = []
        driven_wire_id = ""
        half_spacing = self.driven_fold_spacing_m / 2.0
        for index, element in enumerate(self.elements):
            half_length = element.length_m / 2.0
            if index == self.driven_index and self.match_type is YagiMatchType.BETA_HAIRPIN:
                half_gap = self.match_spacing_m / 2.0
                prefix = f"{YAGI_ELEMENT_ID_PREFIX}-{index + 1}"
                if self.polarization is Polarization.HORIZONTAL:
                    left_start = Point3D(element.position_m, -half_length, self.height_m)
                    left_end = Point3D(element.position_m, -half_gap, self.height_m)
                    right_start = Point3D(element.position_m, half_gap, self.height_m)
                    right_end = Point3D(element.position_m, half_length, self.height_m)
                    hairpin_a_end = Point3D(
                        element.position_m + self.match_length_m,
                        -half_gap,
                        self.height_m,
                    )
                    hairpin_b_end = Point3D(
                        element.position_m + self.match_length_m,
                        half_gap,
                        self.height_m,
                    )
                else:
                    left_start = Point3D(element.position_m, 0.0, self.height_m - half_length)
                    left_end = Point3D(element.position_m, 0.0, self.height_m - half_gap)
                    right_start = Point3D(element.position_m, 0.0, self.height_m + half_gap)
                    right_end = Point3D(element.position_m, 0.0, self.height_m + half_length)
                    hairpin_a_end = Point3D(
                        element.position_m + self.match_length_m,
                        0.0,
                        self.height_m - half_gap,
                    )
                    hairpin_b_end = Point3D(
                        element.position_m + self.match_length_m,
                        0.0,
                        self.height_m + half_gap,
                    )
                wires.extend(
                    [
                        wire(f"{prefix}-left", left_start, left_end, element.radius_m),
                        wire(f"{prefix}-right", right_start, right_end, element.radius_m),
                        wire(f"{prefix}-feed", left_end, right_start, element.radius_m),
                        wire(f"{prefix}-hairpin-a", left_end, hairpin_a_end, element.radius_m),
                        wire(f"{prefix}-hairpin-b", right_start, hairpin_b_end, element.radius_m),
                        wire(
                            f"{prefix}-hairpin-short",
                            hairpin_a_end,
                            hairpin_b_end,
                            element.radius_m,
                        ),
                    ]
                )
                driven_wire_id = f"{prefix}-feed"
                continue
            if index == self.driven_index and self.driven_folded:
                if self.polarization is Polarization.HORIZONTAL:
                    a_start = Point3D(
                        element.position_m - half_spacing,
                        -half_length,
                        self.height_m,
                    )
                    a_end = Point3D(
                        element.position_m - half_spacing,
                        half_length,
                        self.height_m,
                    )
                    b_start = Point3D(
                        element.position_m + half_spacing,
                        -half_length,
                        self.height_m,
                    )
                    b_end = Point3D(
                        element.position_m + half_spacing,
                        half_length,
                        self.height_m,
                    )
                else:
                    a_start = Point3D(
                        element.position_m - half_spacing,
                        0.0,
                        self.height_m - half_length,
                    )
                    a_end = Point3D(
                        element.position_m - half_spacing,
                        0.0,
                        self.height_m + half_length,
                    )
                    b_start = Point3D(
                        element.position_m + half_spacing,
                        0.0,
                        self.height_m - half_length,
                    )
                    b_end = Point3D(
                        element.position_m + half_spacing,
                        0.0,
                        self.height_m + half_length,
                    )
                prefix = f"{YAGI_ELEMENT_ID_PREFIX}-{index + 1}"
                wires.extend(
                    [
                        wire(f"{prefix}-a", a_start, a_end, element.radius_m),
                        wire(f"{prefix}-b", b_start, b_end, element.radius_m),
                        wire(f"{prefix}-end-1", a_start, b_start, element.radius_m),
                        wire(f"{prefix}-end-2", a_end, b_end, element.radius_m),
                    ]
                )
                driven_wire_id = f"{prefix}-a"
                continue
            if self.polarization is Polarization.HORIZONTAL:
                local_start = Point3D(element.position_m, -half_length, self.height_m)
                local_end = Point3D(element.position_m, half_length, self.height_m)
            else:
                local_start = Point3D(element.position_m, 0.0, self.height_m - half_length)
                local_end = Point3D(element.position_m, 0.0, self.height_m + half_length)
            wire_id = f"{YAGI_ELEMENT_ID_PREFIX}-{index + 1}"
            wires.append(wire(wire_id, local_start, local_end, element.radius_m))
            if index == self.driven_index:
                driven_wire_id = wire_id

        driven = next(wire for wire in wires if wire.id == driven_wire_id)
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(wire_id=driven.id, offset_m=driven.length_m / 2.0),
            ground=self.ground,
            generator_id="yagi",
            generator_name="Yagi",
        )


def _midpoint(wire: Wire) -> Point3D:
    return Point3D(
        x_m=(wire.start.x_m + wire.end.x_m) / 2.0,
        y_m=(wire.start.y_m + wire.end.y_m) / 2.0,
        z_m=(wire.start.z_m + wire.end.z_m) / 2.0,
    )


def _folded_wire_number(wire_id: str) -> int | None:
    parts = wire_id.split("-")
    if len(parts) != 3 or parts[0] != YAGI_ELEMENT_ID_PREFIX or parts[2] not in {"a", "b"}:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def yagi_element_length_mismatch(parameters: YagiParameters) -> bool:
    """Return True when element lengths do not look like a Yagi at the design frequency."""

    wavelength = units.wavelength_m(parameters.frequency_hz)
    minimum = wavelength * YAGI_ELEMENT_LENGTH_MIN_FACTOR
    maximum = wavelength * YAGI_ELEMENT_LENGTH_MAX_FACTOR
    return any(not minimum <= element.length_m <= maximum for element in parameters.elements)


def nbs_five_element(
    *,
    frequency_hz: float,
    height_m: float,
    azimuth_deg: float = 0.0,
    polarization: Polarization = Polarization.HORIZONTAL,
    material: ConductorMaterial = COPPER,
    ground: GroundModel = FREE_SPACE,
    radius_m: float | None = None,
    folded_driven: bool = False,
    folded_spacing_m: float = 0.1,
    match_type: YagiMatchType = YagiMatchType.NONE,
    match_length_m: float = 0.2,
    match_spacing_m: float = 0.1,
) -> YagiParameters:
    """Return the NBS TN-688 5-element, 0.8 wavelength starting design.

    The dimensions are scaled from the published 50.1 MHz example.  The
    reference measured gain is 9.2 dBd over a half-wave dipole.  The published
    design uses a folded driven element; the default here keeps a straight
    driven element for backward compatibility.  Set ``folded_driven=True`` to
    model the folded version.  Gain and pattern remain the relevant comparison;
    the feed impedance is not the reference impedance in either case.
    """

    wavelength = units.wavelength_m(frequency_hz)
    radius = radius_m if radius_m is not None else 0.0021 * wavelength
    return YagiParameters(
        frequency_hz=frequency_hz,
        elements=(
            YagiElement(position_m=0.0, length_m=0.490 * wavelength, radius_m=radius),
            YagiElement(position_m=0.2 * wavelength, length_m=0.500 * wavelength, radius_m=radius),
            YagiElement(position_m=0.4 * wavelength, length_m=0.447 * wavelength, radius_m=radius),
            YagiElement(position_m=0.6 * wavelength, length_m=0.443 * wavelength, radius_m=radius),
            YagiElement(position_m=0.8 * wavelength, length_m=0.447 * wavelength, radius_m=radius),
        ),
        height_m=height_m,
        driven_index=1,
        driven_folded=folded_driven,
        driven_fold_spacing_m=folded_spacing_m,
        match_type=match_type,
        match_length_m=match_length_m,
        match_spacing_m=match_spacing_m,
        azimuth_deg=azimuth_deg,
        polarization=polarization,
        material=material,
        ground=ground,
    )
