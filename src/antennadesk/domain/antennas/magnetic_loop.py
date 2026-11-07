# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small tuned magnetic loop with a gap capacitor."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .custom import CustomAntennaParameters
from .feed import FeedPoint
from .geometry import Point3D
from .load import SeriesLoad
from .materials import COPPER, ConductorMaterial
from .wire import Wire

ANTENNA_TYPE_MAGNETIC_LOOP = "magnetic_loop"
CAPACITOR_WIRE_ID = "tuning-capacitor"
CAPACITOR_LOAD_ID = "tuning-capacitor-load"
MIN_SIDES = 8
MAX_SIDES = 128
DEFAULT_CAPACITANCE_F = 200e-12


@dataclass(frozen=True, slots=True)
class MagneticLoopParameters:
    """A vertical small loop with a top gap and a series tuning capacitor.

    ``diameter_m`` is the circumscribed diameter of the regular polygon.  The
    gap is centred on the top side and is bridged by a short wire carrying the
    ideal series capacitor and its ESR.  The feed is at the midpoint of the
    bottom side.  Conductor loss is computed by the solver from the material
    and wire radius; a coupling loop and a physical capacitor model are not
    included.
    """

    frequency_hz: float
    diameter_m: float
    tuning_capacitance_f: float = DEFAULT_CAPACITANCE_F
    height_m: float = 1.0
    sides: int = 36
    gap_length_m: float = 0.05
    capacitor_esr_ohm: float = 0.0
    azimuth_deg: float = 0.0
    wire_radius_m: float = 0.005
    material: ConductorMaterial = COPPER
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.diameter_m, name="diameter_m")
        ensure_positive(self.tuning_capacitance_f, name="tuning_capacitance_f")
        ensure_non_negative(self.height_m, name="height_m")
        ensure_positive(self.gap_length_m, name="gap_length_m")
        ensure_non_negative(self.capacitor_esr_ohm, name="capacitor_esr_ohm")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        if not MIN_SIDES <= self.sides <= MAX_SIDES:
            raise ValueError(f"sides must be between {MIN_SIDES} and {MAX_SIDES}")
        if self.sides % 2 != 0:
            raise ValueError("sides must be even so the loop has a top gap")
        if self.gap_length_m >= self.side_length_m:
            raise ValueError("gap_length_m must be shorter than one polygon side")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def radius_m(self) -> float:
        return self.diameter_m / 2.0

    @property
    def step_rad(self) -> float:
        return 2.0 * math.pi / self.sides

    @property
    def side_length_m(self) -> float:
        return 2.0 * self.radius_m * math.sin(math.pi / self.sides)

    @property
    def circumference_m(self) -> float:
        """Polygon path length, including the capacitor gap."""

        return self.sides * self.side_length_m

    @property
    def loop_conductor_length_m(self) -> float:
        """Metal loop length, excluding the capacitor gap."""

        return self.circumference_m - self.gap_length_m

    @property
    def bottom_height_m(self) -> float:
        return self.height_m

    @property
    def top_height_m(self) -> float:
        return self.height_m + self.diameter_m * math.cos(self.step_rad / 2.0)

    @property
    def capacitor_reactance_ohm(self) -> float:
        return 1.0 / (2.0 * math.pi * self.frequency_hz * self.tuning_capacitance_f)

    def to_antenna(self, *, name: str = "Magnetic loop") -> AntennaModel:
        return self.to_custom_parameters().to_antenna(name=name)

    def to_custom_parameters(self) -> CustomAntennaParameters:
        radius = self.radius_m
        step = self.step_rad
        base_angle = units.degrees_to_radians(self.azimuth_deg)
        direction_x = math.cos(base_angle)
        direction_y = math.sin(base_angle)
        center_z = self.height_m + radius * math.cos(step / 2.0)

        def point(theta: float) -> Point3D:
            horizontal = radius * math.cos(theta)
            return Point3D(
                x_m=horizontal * direction_x,
                y_m=horizontal * direction_y,
                z_m=center_z + radius * math.sin(theta),
            )

        vertices = tuple(point(step / 2.0 + index * step) for index in range(self.sides))
        top_index = self.sides // 4 - 1
        bottom_index = (3 * self.sides) // 4 - 1
        half_gap = self.gap_length_m / 2.0
        wires: list[Wire] = []
        feed_wire_id = ""
        for index in range(self.sides):
            start = vertices[index]
            end = vertices[(index + 1) % self.sides]
            if index == top_index:
                direction = _unit_vector(start, end)
                middle = Point3D(
                    x_m=(start.x_m + end.x_m) / 2.0,
                    y_m=(start.y_m + end.y_m) / 2.0,
                    z_m=(start.z_m + end.z_m) / 2.0,
                )
                gap_near_start = Point3D(
                    x_m=middle.x_m - direction.x_m * half_gap,
                    y_m=middle.y_m - direction.y_m * half_gap,
                    z_m=middle.z_m - direction.z_m * half_gap,
                )
                gap_near_end = Point3D(
                    x_m=middle.x_m + direction.x_m * half_gap,
                    y_m=middle.y_m + direction.y_m * half_gap,
                    z_m=middle.z_m + direction.z_m * half_gap,
                )
                wires.extend(
                    [
                        _wire(f"loop-{index}-start", start, gap_near_start, self),
                        _wire(f"loop-{index}-end", gap_near_end, end, self),
                        _wire(CAPACITOR_WIRE_ID, gap_near_start, gap_near_end, self),
                    ]
                )
            else:
                wire_id = f"loop-{index}"
                wires.append(_wire(wire_id, start, end, self))
                if index == bottom_index:
                    feed_wire_id = wire_id

        loads = (
            SeriesLoad(
                id=CAPACITOR_LOAD_ID,
                wire_id=CAPACITOR_WIRE_ID,
                offset_m=self.gap_length_m / 2.0,
                resistance_ohm=self.capacitor_esr_ohm,
                capacitance_f=self.tuning_capacitance_f,
            ),
        )
        return CustomAntennaParameters(
            frequency_hz=self.frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(feed_wire_id, self.side_length_m / 2.0),
            ground=self.ground,
            loads=loads,
            generator_id="magnetic_loop",
            generator_name="Magnetic loop",
        )

    @classmethod
    def from_custom_parameters(
        cls,
        parameters: CustomAntennaParameters,
    ) -> MagneticLoopParameters:
        capacitor_load = next(
            (
                load
                for load in parameters.loads
                if isinstance(load, SeriesLoad) and load.capacitance_f > 0.0
            ),
            None,
        )
        if capacitor_load is None:
            raise ValueError("a magnetic loop needs a series capacitance load")
        capacitor_wire = next(
            (wire for wire in parameters.wires if wire.id == capacitor_load.wire_id),
            None,
        )
        if capacitor_wire is None:
            raise ValueError("the tuning-capacitor wire is missing")
        if parameters.feed.wire_id == capacitor_wire.id:
            raise ValueError("the magnetic-loop feed must be on the loop conductor")
        loop_wires = tuple(wire for wire in parameters.wires if wire.id != capacitor_wire.id)
        if not loop_wires:
            raise ValueError("the magnetic-loop conductor is missing")
        if not any(wire.id == parameters.feed.wire_id for wire in loop_wires):
            raise ValueError("the magnetic-loop feed wire is missing")
        indices: set[int] = set()
        for wire in loop_wires:
            if not wire.id.startswith("loop-"):
                raise ValueError("all loop wires must use the loop-N identifier")
            try:
                indices.add(int(wire.id.split("-")[1]))
            except (IndexError, ValueError) as exc:
                raise ValueError("loop wire identifiers must end in an integer") from exc
        sides = max(indices) + 1
        if not MIN_SIDES <= sides <= MAX_SIDES:
            raise ValueError(f"sides must be between {MIN_SIDES} and {MAX_SIDES}")
        vertex_counts: dict[Point3D, int] = {}
        for wire in loop_wires:
            for point in (wire.start, wire.end):
                vertex_counts[point] = vertex_counts.get(point, 0) + 1
        polygon_points = tuple(point for point, count in vertex_counts.items() if count >= 2)
        if len(polygon_points) != sides:
            raise ValueError("the magnetic loop must have one vertex per side")
        center_x = sum(point.x_m for point in polygon_points) / len(polygon_points)
        center_y = sum(point.y_m for point in polygon_points) / len(polygon_points)
        center_z = sum(point.z_m for point in polygon_points) / len(polygon_points)
        radius = sum(
            math.sqrt(
                (point.x_m - center_x) ** 2
                + (point.y_m - center_y) ** 2
                + (point.z_m - center_z) ** 2
            )
            for point in polygon_points
        ) / len(polygon_points)
        first_wire = next(wire for wire in loop_wires if wire.id.startswith("loop-0"))
        first_point = first_wire.start
        azimuth = math.degrees(math.atan2(first_point.y_m - center_y, first_point.x_m - center_x))
        return cls(
            frequency_hz=parameters.frequency_hz,
            diameter_m=2.0 * radius,
            tuning_capacitance_f=capacitor_load.capacitance_f,
            height_m=min(point.z_m for point in polygon_points),
            sides=sides,
            gap_length_m=capacitor_wire.length_m,
            capacitor_esr_ohm=capacitor_load.resistance_ohm,
            azimuth_deg=azimuth,
            wire_radius_m=(sum(wire.radius_m for wire in loop_wires) / len(loop_wires)),
            material=loop_wires[0].material,
            ground=parameters.ground,
        )


def _wire(
    wire_id: str,
    start: Point3D,
    end: Point3D,
    parameters: MagneticLoopParameters,
) -> Wire:
    return Wire(
        id=wire_id,
        start=start,
        end=end,
        radius_m=parameters.wire_radius_m,
        material=parameters.material,
    )


def _unit_vector(start: Point3D, end: Point3D) -> Point3D:
    dx = end.x_m - start.x_m
    dy = end.y_m - start.y_m
    dz = end.z_m - start.z_m
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 0.0:
        raise ValueError("loop segment must have positive length")
    return Point3D(x_m=dx / length, y_m=dy / length, z_m=dz / length)
