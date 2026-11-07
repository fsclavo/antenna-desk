# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the renderer-neutral construction scene from an antenna model."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ...domain.antennas.antenna import AntennaModel
from ...domain.antennas.custom import ANTENNA_TYPE_CUSTOM, CustomAntennaParameters
from ...domain.antennas.dipole import ANTENNA_TYPE_WIRE_DIPOLE, DipoleParameters
from ...domain.antennas.endfed import ANTENNA_TYPE_ENDFED, EndFedParameters
from ...domain.antennas.fan_dipole import (
    ANTENNA_TYPE_FAN_DIPOLE,
    FanDipoleParameters,
)
from ...domain.antennas.folded_dipole import (
    ANTENNA_TYPE_FOLDED_DIPOLE,
    FoldedDipoleParameters,
)
from ...domain.antennas.geometry import Point3D
from ...domain.antennas.inverted_l import (
    ANTENNA_TYPE_INVERTED_L,
    HORIZONTAL_ID,
    VERTICAL_ID,
    InvertedLParameters,
)
from ...domain.antennas.inverted_v import ANTENNA_TYPE_INVERTED_V, InvertedVParameters
from ...domain.antennas.j_pole import ANTENNA_TYPE_J_POLE, JPoleParameters
from ...domain.antennas.loop import (
    ANTENNA_TYPE_LOOP,
    LoopOrientation,
    LoopParameters,
)
from ...domain.antennas.magnetic_loop import (
    ANTENNA_TYPE_MAGNETIC_LOOP,
    CAPACITOR_WIRE_ID,
    MagneticLoopParameters,
)
from ...domain.antennas.moxon import ANTENNA_TYPE_MOXON, MoxonParameters
from ...domain.antennas.ocfd import ANTENNA_TYPE_OCFD, OCFDParameters
from ...domain.antennas.polarization import Polarization
from ...domain.antennas.ringo import ANTENNA_TYPE_RINGO, RingoParameters
from ...domain.antennas.t2fd import ANTENNA_TYPE_T2FD, T2FDParameters
from ...domain.antennas.trap_dipole import (
    ANTENNA_TYPE_TRAP_DIPOLE,
    TrapDipoleParameters,
)
from ...domain.antennas.vertical import ANTENNA_TYPE_VERTICAL, VerticalParameters
from ...domain.antennas.wire import Wire
from ...domain.antennas.yagi import ANTENNA_TYPE_YAGI, YagiParameters
from ...domain.antennas.zepp import (
    ZEPP_MATCHING_FEED_ID,
    ZEPP_MATCHING_OPEN_ID,
    ZEPP_RADIATOR_ID,
    parallel_wire_impedance_ohm,
)
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_unit_key
from .scene import (
    AngularDimension,
    Dimension,
    GeometryScene,
    SceneInset,
    SceneMarker,
    ScenePoint,
    ScenePolyline,
)
from .views import (
    GeometryViewMode,
    Projection,
    front_projection,
    is_planar,
    plan_projection,
)

ZEPP_PRESENTATION_TYPE = "zepp"

_TYPE_KEYS: dict[str, str] = {
    ANTENNA_TYPE_WIRE_DIPOLE: "antenna_type.wire_dipole",
    ANTENNA_TYPE_FOLDED_DIPOLE: "antenna_type.folded_dipole",
    ANTENNA_TYPE_LOOP: "antenna_type.loop",
    ANTENNA_TYPE_OCFD: "catalog.ocfd",
    ANTENNA_TYPE_VERTICAL: "catalog.vertical",
    ANTENNA_TYPE_INVERTED_V: "catalog.inverted_v",
    ANTENNA_TYPE_INVERTED_L: "catalog.inverted_l",
    ANTENNA_TYPE_MAGNETIC_LOOP: "catalog.magnetic_loop",
    ANTENNA_TYPE_YAGI: "catalog.yagi",
    ANTENNA_TYPE_MOXON: "catalog.moxon",
    ANTENNA_TYPE_FAN_DIPOLE: "catalog.fan_dipole",
    ANTENNA_TYPE_ENDFED: "catalog.endfed",
    ANTENNA_TYPE_J_POLE: "catalog.j_pole",
    ANTENNA_TYPE_RINGO: "catalog.ringo",
    ANTENNA_TYPE_TRAP_DIPOLE: "catalog.trap_dipole",
    ANTENNA_TYPE_T2FD: "catalog.t2fd",
    ZEPP_PRESENTATION_TYPE: "catalog.zepp",
}

SUPPORTED_PRESENTATION_TYPES = frozenset({*_TYPE_KEYS, ANTENNA_TYPE_CUSTOM})


def effective_antenna_type(
    antenna_type: str | None,
    parameters: object | None,
) -> str | None:
    """Return the presentation type, including legacy generator metadata."""

    if isinstance(parameters, CustomAntennaParameters):
        generator = parameters.generator_id
        if generator == "slim_jim":
            return ANTENNA_TYPE_J_POLE
        if generator == "zepp":
            return ZEPP_PRESENTATION_TYPE
        if generator in {"g5rv", "zs6bkw"}:
            return ANTENNA_TYPE_WIRE_DIPOLE
        if generator in {
            "j_pole",
            "ringo",
            "yagi",
            "moxon",
            "fan_dipole",
            "inverted_v",
            "inverted_l",
            "magnetic_loop",
            "vertical",
            "ocfd",
            "endfed",
            "t2fd",
        }:
            return generator
    return antenna_type


def is_folded_j_pole(parameters: object | None, model: AntennaModel) -> bool:
    if isinstance(parameters, JPoleParameters):
        return parameters.folded
    if isinstance(parameters, CustomAntennaParameters):
        return parameters.generator_id == "slim_jim"
    return any(wire.id == "top-connector" for wire in model.wires)


def _type_key(
    antenna_type: str | None,
    parameters: object | None,
    display_name: str | None,
) -> str:
    if antenna_type == ANTENNA_TYPE_J_POLE:
        folded = (isinstance(parameters, JPoleParameters) and parameters.folded) or (
            isinstance(parameters, CustomAntennaParameters)
            and parameters.generator_id == "slim_jim"
        )
        if display_name:
            return display_name
        return "catalog.slim_jim" if folded else "catalog.j_pole"
    if antenna_type == ANTENNA_TYPE_LOOP and isinstance(parameters, LoopParameters):
        if parameters.sides == 3:
            return "catalog.delta_loop"
        if parameters.sides == 4:
            return "catalog.quad_loop"
    return _TYPE_KEYS.get(antenna_type or "", "catalog.custom")


def type_label(
    translator: Translator,
    antenna_type: str | None,
    parameters: object | None,
    display_name: str | None = None,
) -> str:
    key = _type_key(antenna_type, parameters, display_name)
    if key == (display_name or ""):
        return key
    return translator.t(key)


def _format_length(value_m: float, translator: Translator, unit_system: UnitSystem) -> str:
    display = length_from_m(value_m, unit_system)
    decimals = 3 if abs(display) < 0.1 else 2
    unit = translator.t(length_unit_key(unit_system))
    return f"{display:.{decimals}f} {unit}"


def _wire_point(wire: Wire, ratio: float) -> Point3D:
    ratio = min(max(ratio, 0.0), 1.0)
    return Point3D(
        x_m=wire.start.x_m + (wire.end.x_m - wire.start.x_m) * ratio,
        y_m=wire.start.y_m + (wire.end.y_m - wire.start.y_m) * ratio,
        z_m=wire.start.z_m + (wire.end.z_m - wire.start.z_m) * ratio,
    )


@dataclass(slots=True)
class _Factory:
    projection: Projection
    exaggeration: float
    translator: Translator
    unit_system: UnitSystem

    def project(self, point: Point3D) -> ScenePoint:
        x_m, y_m = self.projection.project(point)
        if self.projection.vertical:
            y_m *= self.exaggeration
        return ScenePoint(x_m, y_m)

    def y_for_z(self, z_m: float) -> float:
        if not self.projection.vertical:
            return z_m
        return (z_m - self.projection.origin[2]) * self.exaggeration

    def dimension(
        self,
        first: Point3D,
        second: Point3D,
        value_m: float,
        *,
        side: str = "auto",
        priority: int = 50,
    ) -> Dimension:
        return Dimension(
            start=self.project(first),
            end=self.project(second),
            text=_format_length(value_m, self.translator, self.unit_system),
            side=side,
            priority=priority,
        )

    def vertical_dimension(
        self,
        x_scene: float,
        z_start_m: float,
        z_end_m: float,
        value_m: float,
        *,
        side: str = "auto",
        priority: int = 50,
    ) -> Dimension:
        return Dimension(
            start=ScenePoint(x_scene, self.y_for_z(z_start_m)),
            end=ScenePoint(x_scene, self.y_for_z(z_end_m)),
            text=_format_length(value_m, self.translator, self.unit_system),
            side=side,
            priority=priority,
        )

    def horizontal_dimension(
        self,
        y_scene: float,
        x_start_scene: float,
        x_end_scene: float,
        value_m: float,
        *,
        side: str = "auto",
        priority: int = 50,
    ) -> Dimension:
        return Dimension(
            start=ScenePoint(x_start_scene, y_scene),
            end=ScenePoint(x_end_scene, y_scene),
            text=_format_length(value_m, self.translator, self.unit_system),
            side=side,
            priority=priority,
        )

    def between_scene(
        self,
        first: ScenePoint,
        second: ScenePoint,
        value_m: float,
        *,
        side: str = "auto",
        priority: int = 50,
    ) -> Dimension:
        return Dimension(
            start=first,
            end=second,
            text=_format_length(value_m, self.translator, self.unit_system),
            side=side,
            priority=priority,
        )


def _scene_extents(points: tuple[ScenePoint, ...]) -> tuple[float, float, float, float] | None:
    if not points:
        return None
    return (
        min(point.x_m for point in points),
        max(point.x_m for point in points),
        min(point.y_m for point in points),
        max(point.y_m for point in points),
    )


def _model_z_extents(model: AntennaModel) -> tuple[float, float]:
    zs = [point.z_m for wire in model.wires for point in (wire.start, wire.end)]
    return min(zs), max(zs)


def _perpendicular_distance(first: Wire, second: Wire) -> float:
    dx = first.end.x_m - first.start.x_m
    dy = first.end.y_m - first.start.y_m
    length = math.hypot(dx, dy)
    if length <= 1e-12:
        return 0.0
    return abs(
        (second.start.x_m - first.start.x_m) * (-dy / length)
        + (second.start.y_m - first.start.y_m) * (dx / length)
    )


def _load_markers(model: AntennaModel, factory: _Factory) -> tuple[SceneMarker, ...]:
    markers: list[SceneMarker] = []
    for index, load in enumerate(model.loads, start=1):
        wire = model.wire_by_id(load.wire_id)
        ratio = min(max(load.offset_m / wire.length_m, 0.0), 1.0)
        markers.append(
            SceneMarker(
                point=factory.project(_wire_point(wire, ratio)),
                kind="load",
                label=f"L{index}",
                priority=60,
            )
        )
    return tuple(markers)


def _feed_marker(model: AntennaModel, factory: _Factory, translator: Translator) -> SceneMarker:
    feed_wire = model.feed_wire
    ratio = min(max(model.feed.offset_m / feed_wire.length_m, 0.0), 1.0)
    return SceneMarker(
        point=factory.project(_wire_point(feed_wire, ratio)),
        kind="feed",
        label=translator.t("geometry.feed"),
        priority=90,
    )


def _add_single_wire_dimensions(
    model: AntennaModel,
    factory: _Factory,
    dimensions: list[Dimension],
) -> None:
    wire = model.wires[0]
    min_z, max_z = _model_z_extents(model)
    feed_wire = model.feed_wire
    feed_ratio = model.feed.offset_m / feed_wire.length_m
    feed_z = feed_wire.start.z_m + (feed_wire.end.z_m - feed_wire.start.z_m) * feed_ratio
    start = factory.project(wire.start)
    end = factory.project(wire.end)
    if wire.length_m > 1e-9:
        dimensions.append(
            factory.dimension(wire.start, wire.end, wire.length_m, side="auto", priority=85)
        )
    if factory.projection.vertical:
        dimensions.append(
            factory.vertical_dimension(
                max(start.x_m, end.x_m),
                0.0,
                max_z,
                max_z,
                side="right",
                priority=75,
            )
        )
        if min_z > 1e-6 and min_z < max_z - 1e-6:
            dimensions.append(
                factory.vertical_dimension(
                    min(start.x_m, end.x_m),
                    0.0,
                    min_z,
                    min_z,
                    side="left",
                    priority=65,
                )
            )
        if abs(feed_z - min_z) > 1e-6 and abs(feed_z - max_z) > 1e-6:
            dimensions.append(
                factory.vertical_dimension(
                    min(start.x_m, end.x_m),
                    0.0,
                    feed_z,
                    feed_z,
                    side="left",
                    priority=60,
                )
            )
    else:
        feed_point = factory.project(_wire_point(feed_wire, feed_ratio))
        if feed_ratio > 1e-6 and feed_ratio < 1.0 - 1e-6:
            feed_offset = feed_wire.length_m * feed_ratio
            dimensions.append(
                factory.dimension(
                    wire.start,
                    _wire_point(feed_wire, feed_ratio),
                    feed_offset,
                    side="below",
                    priority=65,
                )
            )
        if abs(feed_point.x_m - min(start.x_m, end.x_m)) > 1e-6:
            dimensions.append(
                factory.dimension(
                    _wire_point(feed_wire, feed_ratio),
                    wire.end,
                    feed_wire.length_m * (1.0 - feed_ratio),
                    side="below",
                    priority=55,
                )
            )


def _add_folded_dimensions(
    model: AntennaModel,
    factory: _Factory,
    dimensions: list[Dimension],
    insets: list[SceneInset],
    translator: Translator,
) -> None:
    long_wires = sorted(model.wires, key=lambda wire: wire.length_m, reverse=True)[:2]
    if len(long_wires) < 2:
        return
    element, other = long_wires
    spacing = _perpendicular_distance(element, other)
    min_z, max_z = _model_z_extents(model)
    dimensions.append(
        factory.dimension(element.start, element.end, element.length_m, side="auto", priority=80)
    )
    if factory.projection.vertical:
        dimensions.append(
            factory.vertical_dimension(
                max(factory.project(element.start).x_m, factory.project(element.end).x_m),
                0.0,
                max_z,
                max_z,
                side="right",
                priority=70,
            )
        )
        if min_z > 1e-6 and min_z < max_z - 1e-6:
            dimensions.append(
                factory.vertical_dimension(
                    min(factory.project(other.start).x_m, factory.project(other.end).x_m),
                    0.0,
                    min_z,
                    min_z,
                    side="left",
                    priority=60,
                )
            )
    else:
        dimensions.append(
            factory.dimension(
                _wire_point(element, 0.5),
                _wire_point(other, 0.5),
                spacing,
                side="below",
                priority=75,
            )
        )
        if element.length_m > 1e-9 and spacing / element.length_m < 0.02:
            height = max(spacing * 3.0, 0.1)
            polylines = (
                ScenePolyline(
                    (ScenePoint(-spacing / 2.0, 0.0), ScenePoint(-spacing / 2.0, height)),
                    role="wire",
                ),
                ScenePolyline(
                    (ScenePoint(spacing / 2.0, 0.0), ScenePoint(spacing / 2.0, height)),
                    role="wire",
                ),
            )
            insets.append(
                SceneInset(
                    label=translator.t("geometry.detail_spacing"),
                    polylines=polylines,
                    dimensions=(
                        Dimension(
                            start=ScenePoint(-spacing / 2.0, 0.0),
                            end=ScenePoint(spacing / 2.0, 0.0),
                            text=_format_length(
                                spacing,
                                translator,
                                factory.unit_system,
                            ),
                            side="below",
                            priority=90,
                        ),
                    ),
                )
            )


def _add_loop_dimensions(
    model: AntennaModel,
    parameters: LoopParameters | None,
    factory: _Factory,
    dimensions: list[Dimension],
    notes: list[str],
) -> None:
    projected = tuple(
        factory.project(point) for wire in model.wires for point in (wire.start, wire.end)
    )
    extents = _scene_extents(projected)
    if extents is None:
        return
    min_x, max_x, min_y, max_y = extents
    min_z, max_z = _model_z_extents(model)
    horizontal_loop = (
        parameters is not None and parameters.orientation is LoopOrientation.HORIZONTAL
    )
    if factory.projection.vertical:
        dimensions.append(
            factory.horizontal_dimension(
                min_y,
                min_x,
                max_x,
                max_x - min_x,
                side="below",
                priority=65,
            )
        )
        if horizontal_loop:
            dimensions.append(
                factory.vertical_dimension(
                    max_x,
                    0.0,
                    min_z,
                    min_z,
                    side="right",
                    priority=75,
                )
            )
            notes.append(factory.translator.t("geometry.horizontal_plane_edge_on"))
        else:
            dimensions.append(
                factory.vertical_dimension(
                    max_x,
                    min_z,
                    max_z,
                    max_z - min_z,
                    side="right",
                    priority=60,
                )
            )
            dimensions.append(
                factory.vertical_dimension(
                    min_x,
                    0.0,
                    min_z,
                    min_z,
                    side="left",
                    priority=75,
                )
            )
            if len(model.wires) <= 12:
                first = model.wires[0]
                dimensions.append(
                    factory.dimension(
                        first.start,
                        first.end,
                        first.length_m,
                        side="auto",
                        priority=35,
                    )
                )
    else:
        dimensions.append(
            factory.horizontal_dimension(
                min_y,
                min_x,
                max_x,
                max_x - min_x,
                side="below",
                priority=70,
            )
        )
        dimensions.append(
            factory.between_scene(
                ScenePoint(min_x, min_y),
                ScenePoint(min_x, max_y),
                max_y - min_y,
                side="left",
                priority=60,
            )
        )
        if not horizontal_loop and max_y - min_y <= 1e-9:
            notes.append(factory.translator.t("geometry.edge_on"))
    if parameters is not None and parameters.sides > 8:
        notes.append(factory.translator.t("geometry.sides_note", sides=parameters.sides))


def _add_magnetic_loop_dimensions(
    model: AntennaModel,
    parameters: MagneticLoopParameters,
    factory: _Factory,
    dimensions: list[Dimension],
    notes: list[str],
) -> None:
    projected = tuple(
        factory.project(point) for wire in model.wires for point in (wire.start, wire.end)
    )
    extents = _scene_extents(projected)
    if extents is None:
        return
    min_x, max_x, min_y, max_y = extents
    min_z, max_z = _model_z_extents(model)
    if factory.projection.vertical:
        dimensions.append(
            factory.horizontal_dimension(
                min_y,
                min_x,
                max_x,
                parameters.diameter_m,
                side="below",
                priority=70,
            )
        )
        dimensions.append(
            factory.vertical_dimension(
                max_x,
                0.0,
                min_z,
                parameters.height_m,
                side="right",
                priority=75,
            )
        )
        dimensions.append(
            factory.vertical_dimension(
                min_x,
                0.0,
                max_z,
                parameters.top_height_m,
                side="left",
                priority=60,
            )
        )
        capacitor = next(
            (wire for wire in model.wires if wire.id == CAPACITOR_WIRE_ID),
            None,
        )
        if capacitor is not None:
            dimensions.append(
                factory.dimension(
                    capacitor.start,
                    capacitor.end,
                    parameters.gap_length_m,
                    side="above",
                    priority=50,
                )
            )
    else:
        dimensions.append(
            factory.horizontal_dimension(
                min_y,
                min_x,
                max_x,
                parameters.diameter_m,
                side="below",
                priority=70,
            )
        )
        dimensions.append(
            factory.between_scene(
                ScenePoint(min_x, min_y),
                ScenePoint(min_x, max_y),
                max_y - min_y,
                side="left",
                priority=60,
            )
        )
        notes.append(factory.translator.t("geometry.vertical_plane_edge_on"))


def _add_j_pole_dimensions(
    model: AntennaModel,
    parameters: object | None,
    factory: _Factory,
    dimensions: list[Dimension],
    insets: list[SceneInset],
    translator: Translator,
) -> None:
    verticals = tuple(
        wire
        for wire in model.wires
        if math.hypot(
            wire.end.x_m - wire.start.x_m,
            wire.end.y_m - wire.start.y_m,
        )
        <= 1e-9
    )
    if len(verticals) < 2:
        return
    folded = is_folded_j_pole(parameters, model)
    if folded:
        radiator = next((wire for wire in verticals if wire.id == "right-upper"), None)
        stub = next((wire for wire in verticals if wire.id == "right-lower"), None)
    else:
        radiator = max(verticals, key=lambda wire: wire.length_m)
        stub = min(verticals, key=lambda wire: wire.length_m)
    if radiator is None or stub is None:
        return
    min_z, max_z = _model_z_extents(model)
    radiator_x = factory.project(radiator.start).x_m
    stub_x = factory.project(stub.start).x_m
    if not factory.projection.vertical:
        vertical_xs = [factory.project(wire.start).x_m for wire in verticals]
        left_x = min(vertical_xs)
        right_x = max(vertical_xs)
        base_y = factory.project(radiator.start).y_m
        dimensions.append(
            factory.between_scene(
                ScenePoint(left_x, base_y),
                ScenePoint(right_x, base_y),
                abs(right_x - left_x),
                side="below",
                priority=80,
            )
        )
        return
    dimensions.append(
        factory.vertical_dimension(
            radiator_x,
            min(radiator.start.z_m, radiator.end.z_m),
            max(radiator.start.z_m, radiator.end.z_m),
            radiator.length_m,
            side="right",
            priority=85,
        )
    )
    dimensions.append(
        factory.vertical_dimension(
            stub_x,
            min(stub.start.z_m, stub.end.z_m),
            max(stub.start.z_m, stub.end.z_m),
            stub.length_m,
            side="left",
            priority=80,
        )
    )
    dimensions.append(
        factory.vertical_dimension(
            min(radiator_x, stub_x),
            0.0,
            min_z,
            min_z,
            side="left",
            priority=75,
        )
    )
    vertical_xs = [factory.project(wire.start).x_m for wire in verticals]
    left_x = min(vertical_xs)
    right_x = max(vertical_xs)
    spacing = abs(right_x - left_x)
    base_z = min_z
    dimensions.append(
        factory.horizontal_dimension(
            factory.y_for_z(base_z) - max(spacing * 0.35, 0.08),
            left_x,
            right_x,
            spacing,
            side="below",
            priority=70,
        )
    )
    if folded:
        gap_bottom = min(stub.start.z_m, stub.end.z_m)
        gap_top = max(stub.start.z_m, stub.end.z_m)
        for wire in model.wires:
            if wire.id == "right-upper":
                gap_top = min(wire.start.z_m, wire.end.z_m)
            if wire.id == "right-lower":
                gap_bottom = max(wire.start.z_m, wire.end.z_m)
        gap = max(gap_top - gap_bottom, 0.0)
        if gap > 0.0:
            dimensions.append(
                factory.vertical_dimension(
                    max(radiator_x, stub_x),
                    gap_bottom,
                    gap_top,
                    gap,
                    side="right",
                    priority=90,
                )
            )
            insets.append(
                _j_pole_gap_inset(
                    model,
                    parameters,
                    factory,
                    translator,
                    gap_bottom,
                    gap_top,
                    spacing,
                )
            )
    dimensions.append(
        factory.vertical_dimension(
            min(radiator_x, stub_x),
            min_z,
            max_z,
            max_z - min_z,
            side="left",
            priority=55,
        )
    )


def _j_pole_gap_inset(
    model: AntennaModel,
    parameters: object | None,
    factory: _Factory,
    translator: Translator,
    gap_bottom_z: float,
    gap_top_z: float,
    spacing: float,
) -> SceneInset:
    gap = max(gap_top_z - gap_bottom_z, 1e-6)
    x = max(
        (factory.project(wire.start).x_m for wire in model.wires),
        default=spacing,
    )
    low = gap_bottom_z - 3.0 * gap
    high = gap_top_z + 3.0 * gap
    polylines = (
        ScenePolyline(
            (ScenePoint(x, low), ScenePoint(x, gap_bottom_z)),
            role="wire",
        ),
        ScenePolyline(
            (ScenePoint(x, gap_top_z), ScenePoint(x, high)),
            role="wire",
        ),
        ScenePolyline(
            (
                ScenePoint(x - spacing * 0.35, gap_bottom_z),
                ScenePoint(x + spacing * 0.35, gap_bottom_z),
            ),
            role="construction",
            style="dashed",
            width=1.0,
        ),
        ScenePolyline(
            (ScenePoint(x - spacing * 0.35, gap_top_z), ScenePoint(x + spacing * 0.35, gap_top_z)),
            role="construction",
            style="dashed",
            width=1.0,
        ),
    )
    dimensions = (
        Dimension(
            start=ScenePoint(x, gap_bottom_z),
            end=ScenePoint(x, gap_top_z),
            text=_format_length(gap, translator, factory.unit_system),
            side="right",
            priority=100,
        ),
    )
    return SceneInset(
        label=translator.t("geometry.detail_gap"),
        polylines=polylines,
        dimensions=dimensions,
    )


def _add_ringo_dimensions(
    model: AntennaModel,
    factory: _Factory,
    dimensions: list[Dimension],
    insets: list[SceneInset],
    translator: Translator,
) -> None:
    radiator = next((wire for wire in model.wires if wire.id == "radiator"), None)
    if radiator is None:
        radiator = max(
            model.wires,
            key=lambda wire: abs(wire.end.z_m - wire.start.z_m),
        )
    ring_wires = tuple(wire for wire in model.wires if wire.id.startswith("ring-"))
    ring_z = min((wire.start.z_m for wire in ring_wires), default=radiator.start.z_m)
    min_z, max_z = _model_z_extents(model)
    radiator_x = factory.project(radiator.start).x_m
    if not factory.projection.vertical:
        xs = [point.x_m for wire in model.wires for point in (wire.start, wire.end)]
        ys = [point.y_m for wire in model.wires for point in (wire.start, wire.end)]
        dimensions.append(
            Dimension(
                start=ScenePoint(min(xs), min(ys)),
                end=ScenePoint(max(xs), min(ys)),
                text=_format_length(max(xs) - min(xs), translator, factory.unit_system),
                side="below",
                priority=85,
            )
        )
        return
    dimensions.append(
        factory.vertical_dimension(
            radiator_x,
            min(radiator.start.z_m, radiator.end.z_m),
            max(radiator.start.z_m, radiator.end.z_m),
            radiator.length_m,
            side="right",
            priority=85,
        )
    )
    dimensions.append(
        factory.vertical_dimension(
            radiator_x,
            0.0,
            ring_z,
            ring_z,
            side="left",
            priority=70,
        )
    )
    if abs(max_z - max(radiator.start.z_m, radiator.end.z_m)) > 1e-6:
        dimensions.append(
            factory.vertical_dimension(
                radiator_x,
                min_z,
                max_z,
                max_z - min_z,
                side="left",
                priority=55,
            )
        )

    plan_points = tuple(ScenePoint(wire.start.x_m, wire.start.y_m) for wire in model.wires) + tuple(
        ScenePoint(wire.end.x_m, wire.end.y_m) for wire in model.wires
    )
    extents = _scene_extents(plan_points)
    plan_polylines = tuple(
        ScenePolyline(
            (
                ScenePoint(wire.start.x_m, wire.start.y_m),
                ScenePoint(wire.end.x_m, wire.end.y_m),
            ),
            role="wire",
        )
        for wire in model.wires
    )
    plan_dimensions: list[Dimension] = []
    if extents is not None:
        min_x, max_x, min_y, max_y = extents
        diameter = max(max_x - min_x, max_y - min_y)
        plan_dimensions.append(
            Dimension(
                start=ScenePoint(min_x, min_y),
                end=ScenePoint(max_x, min_y),
                text=_format_length(diameter, translator, factory.unit_system),
                side="above",
                priority=85,
            )
        )
    insets.append(
        SceneInset(
            label=translator.t("geometry.top_view"),
            polylines=plan_polylines,
            dimensions=tuple(plan_dimensions),
        )
    )


def _is_vertical_array(parameters: object | None) -> bool:
    return isinstance(parameters, (YagiParameters, MoxonParameters)) and (
        parameters.polarization is Polarization.VERTICAL
    )


def _array_wire(model: AntennaModel, wire_id: str, index: int) -> Wire | None:
    wire = next((item for item in model.wires if item.id == wire_id), None)
    if wire is None and index < len(model.wires):
        return model.wires[index]
    return wire


def _add_array_dimensions(
    model: AntennaModel,
    parameters: object | None,
    factory: _Factory,
    dimensions: list[Dimension],
    notes: list[str],
    translator: Translator,
) -> None:
    min_z, max_z = _model_z_extents(model)
    vertical_array = _is_vertical_array(parameters)
    if not factory.projection.vertical:
        if vertical_array:
            notes.append(translator.t("geometry.vertical_plane_edge_on"))
            if isinstance(parameters, YagiParameters) and len(parameters.elements) >= 2:
                positions = [element.position_m for element in parameters.elements]
                dimensions.append(
                    factory.dimension(
                        _wire_point(model.wires[0], 0.5),
                        _wire_point(model.wires[-1], 0.5),
                        max(positions) - min(positions),
                        side="below",
                        priority=60,
                    )
                )
            elif isinstance(parameters, MoxonParameters):
                reflector = next(
                    (wire for wire in model.wires if wire.id == "reflector"),
                    None,
                )
                driven = next((wire for wire in model.wires if wire.id == "driven"), None)
                if reflector is not None and driven is not None:
                    dimensions.append(
                        factory.dimension(
                            _wire_point(reflector, 0.5),
                            _wire_point(driven, 0.5),
                            parameters.depth_m,
                            side="below",
                            priority=70,
                        )
                    )
                reflector_tip = next(
                    (wire for wire in model.wires if wire.id == "reflector-tip-1"),
                    None,
                )
                driven_tip = next(
                    (wire for wire in model.wires if wire.id == "driven-tip-1"),
                    None,
                )
                if reflector_tip is not None:
                    dimensions.append(
                        factory.dimension(
                            reflector_tip.start,
                            reflector_tip.end,
                            parameters.reflector_tip_m,
                            side="above",
                            priority=45,
                        )
                    )
                if reflector_tip is not None and driven_tip is not None:
                    dimensions.append(
                        factory.between_scene(
                            factory.project(reflector_tip.end),
                            factory.project(driven_tip.end),
                            parameters.gap_m,
                            side="above",
                            priority=55,
                        )
                    )
            return
        if isinstance(parameters, YagiParameters):
            for index, element in enumerate(model.wires):
                wire = (
                    model.wire_by_id(f"element-{index + 1}")
                    if any(item.id == f"element-{index + 1}" for item in model.wires)
                    else element
                )
                dimensions.append(
                    factory.dimension(
                        wire.start,
                        wire.end,
                        wire.length_m,
                        side="above" if index % 2 == 0 else "below",
                        priority=70
                        if index in {0, parameters.driven_index, len(model.wires) - 1}
                        else 35,
                    )
                )
            if parameters is not None and len(parameters.elements) >= 2:
                positions = [element.position_m for element in parameters.elements]
                dimensions.append(
                    factory.dimension(
                        _wire_point(model.wires[0], 0.5),
                        _wire_point(model.wires[-1], 0.5),
                        max(positions) - min(positions),
                        side="below",
                        priority=60,
                    )
                )
        elif isinstance(parameters, MoxonParameters):
            for wire in model.wires[:1]:
                dimensions.append(
                    factory.dimension(wire.start, wire.end, wire.length_m, side="auto", priority=80)
                )
            for wire_id in ("reflector-tip-1", "driven-tip-1"):
                tip = next((wire for wire in model.wires if wire.id == wire_id), None)
                if tip is not None:
                    dimensions.append(
                        factory.dimension(
                            tip.start,
                            tip.end,
                            tip.length_m,
                            side="above",
                            priority=45,
                        )
                    )
            if len(model.wires) >= 4:
                dimensions.append(
                    factory.dimension(
                        _wire_point(model.wires[0], 0.5),
                        _wire_point(model.wires[3], 0.5),
                        parameters.depth_m,
                        side="below",
                        priority=55,
                    )
                )
                reflector_tip = next(
                    (wire for wire in model.wires if wire.id == "reflector-tip-1"),
                    None,
                )
                driven_tip = next(
                    (wire for wire in model.wires if wire.id == "driven-tip-1"),
                    None,
                )
                if reflector_tip is not None and driven_tip is not None:
                    dimensions.append(
                        factory.between_scene(
                            factory.project(reflector_tip.end),
                            factory.project(driven_tip.end),
                            parameters.gap_m,
                            side="below",
                            priority=60,
                        )
                    )
        else:
            projected = tuple(
                factory.project(point) for wire in model.wires for point in (wire.start, wire.end)
            )
            extents = _scene_extents(projected)
            if extents is not None:
                min_x, max_x, min_y, max_y = extents
                dimensions.append(
                    factory.horizontal_dimension(
                        min_y,
                        min_x,
                        max_x,
                        max_x - min_x,
                        side="below",
                        priority=55,
                    )
                )
                dimensions.append(
                    factory.between_scene(
                        ScenePoint(min_x, min_y),
                        ScenePoint(min_x, max_y),
                        max_y - min_y,
                        side="left",
                        priority=50,
                    )
                )
        return

    if vertical_array and isinstance(parameters, YagiParameters):
        for index, yagi_element in enumerate(parameters.elements):
            array_wire = _array_wire(model, f"element-{index + 1}", index)
            if array_wire is None:
                continue
            dimensions.append(
                factory.dimension(
                    array_wire.start,
                    array_wire.end,
                    yagi_element.length_m,
                    side="right" if index % 2 == 0 else "left",
                    priority=70
                    if index in {0, parameters.driven_index, len(parameters.elements) - 1}
                    else 35,
                )
            )
        if len(parameters.elements) >= 2:
            positions = [element.position_m for element in parameters.elements]
            first = _array_wire(model, "element-1", 0)
            last = _array_wire(model, f"element-{len(parameters.elements)}", len(model.wires) - 1)
            if first is not None and last is not None:
                dimensions.append(
                    factory.dimension(
                        _wire_point(first, 0.5),
                        _wire_point(last, 0.5),
                        max(positions) - min(positions),
                        side="above",
                        priority=65,
                    )
                )
    elif vertical_array and isinstance(parameters, MoxonParameters):
        reflector = next((wire for wire in model.wires if wire.id == "reflector"), None)
        driven = next((wire for wire in model.wires if wire.id == "driven"), None)
        if reflector is not None:
            dimensions.append(
                factory.dimension(
                    reflector.start,
                    reflector.end,
                    parameters.width_m,
                    side="left",
                    priority=85,
                )
            )
        if reflector is not None and driven is not None:
            dimensions.append(
                factory.dimension(
                    _wire_point(reflector, 0.5),
                    _wire_point(driven, 0.5),
                    parameters.depth_m,
                    side="below",
                    priority=75,
                )
            )
        reflector_tip = next(
            (wire for wire in model.wires if wire.id == "reflector-tip-1"),
            None,
        )
        driven_tip = next(
            (wire for wire in model.wires if wire.id == "driven-tip-1"),
            None,
        )
        if reflector_tip is not None:
            dimensions.append(
                factory.dimension(
                    reflector_tip.start,
                    reflector_tip.end,
                    parameters.reflector_tip_m,
                    side="above",
                    priority=45,
                )
            )
        if reflector_tip is not None and driven_tip is not None:
            dimensions.append(
                factory.between_scene(
                    factory.project(reflector_tip.end),
                    factory.project(driven_tip.end),
                    parameters.gap_m,
                    side="above",
                    priority=55,
                )
            )

    if vertical_array and isinstance(parameters, (YagiParameters, MoxonParameters)):
        height_m = parameters.height_m
    else:
        height_m = max_z
    dimensions.append(
        factory.vertical_dimension(
            min(factory.project(wire.start).x_m for wire in model.wires),
            0.0,
            height_m,
            height_m,
            side="right",
            priority=80 if vertical_array else 75,
        )
    )
    if isinstance(parameters, (YagiParameters, MoxonParameters)) and not vertical_array:
        notes.append(translator.t("geometry.front_overlap"))
    if min_z > 1e-6 and min_z < max_z - 1e-6:
        dimensions.append(
            factory.vertical_dimension(
                min(factory.project(wire.start).x_m for wire in model.wires),
                0.0,
                min_z,
                min_z,
                side="left",
                priority=60,
            )
        )


def _add_inverted_l_dimensions(
    model: AntennaModel,
    parameters: InvertedLParameters,
    factory: _Factory,
    dimensions: list[Dimension],
    notes: list[str],
    translator: Translator,
) -> None:
    vertical = next((wire for wire in model.wires if wire.id == VERTICAL_ID), model.wires[0])
    horizontal = next((wire for wire in model.wires if wire.id == HORIZONTAL_ID), model.wires[-1])
    if factory.projection.vertical:
        dimensions.append(
            factory.dimension(
                vertical.start,
                vertical.end,
                parameters.vertical_height_m,
                side="auto",
                priority=85,
            )
        )
        dimensions.append(
            factory.dimension(
                horizontal.start,
                horizontal.end,
                parameters.horizontal_length_m,
                side="above",
                priority=75,
            )
        )
        dimensions.append(
            factory.vertical_dimension(
                max(
                    factory.project(horizontal.start).x_m,
                    factory.project(horizontal.end).x_m,
                ),
                0.0,
                parameters.top_height_m,
                parameters.top_height_m,
                side="right",
                priority=70,
            )
        )
        if parameters.base_height_m > 0.0:
            dimensions.append(
                factory.vertical_dimension(
                    factory.project(vertical.start).x_m,
                    0.0,
                    parameters.base_height_m,
                    parameters.base_height_m,
                    side="left",
                    priority=55,
                )
            )
    else:
        dimensions.append(
            factory.dimension(
                horizontal.start,
                horizontal.end,
                parameters.horizontal_length_m,
                side="above",
                priority=75,
            )
        )
        notes.append(translator.t("geometry.vertical_plane_edge_on"))


def _add_sloping_array_dimensions(
    model: AntennaModel,
    parameters: object | None,
    factory: _Factory,
    dimensions: list[Dimension],
) -> None:
    min_z, max_z = _model_z_extents(model)
    if factory.projection.vertical:
        first = model.wires[0]
        dimensions.append(
            factory.dimension(first.start, first.end, first.length_m, side="auto", priority=75)
        )
        dimensions.append(
            factory.vertical_dimension(
                min(factory.project(wire.start).x_m for wire in model.wires),
                0.0,
                max_z,
                max_z,
                side="right",
                priority=80,
            )
        )
        if min_z > 1e-6 and min_z < max_z - 1e-6:
            dimensions.append(
                factory.vertical_dimension(
                    min(factory.project(wire.start).x_m for wire in model.wires),
                    0.0,
                    min_z,
                    min_z,
                    side="left",
                    priority=60,
                )
            )
        if isinstance(parameters, (InvertedVParameters, FanDipoleParameters)):
            projected = tuple(
                factory.project(point) for wire in model.wires for point in (wire.start, wire.end)
            )
            extents = _scene_extents(projected)
            if extents is not None:
                min_x, max_x, min_y, _max_y = extents
                dimensions.append(
                    factory.horizontal_dimension(
                        min_y,
                        min_x,
                        max_x,
                        max_x - min_x,
                        side="below",
                        priority=55,
                    )
                )
    else:
        projected = tuple(
            factory.project(point) for wire in model.wires for point in (wire.start, wire.end)
        )
        extents = _scene_extents(projected)
        if extents is not None:
            min_x, max_x, min_y, max_y = extents
            dimensions.append(
                factory.horizontal_dimension(
                    min_y,
                    min_x,
                    max_x,
                    max_x - min_x,
                    side="below",
                    priority=55,
                )
            )
            dimensions.append(
                factory.between_scene(
                    ScenePoint(min_x, min_y),
                    ScenePoint(min_x, max_y),
                    max_y - min_y,
                    side="left",
                    priority=50,
                )
            )


def _shared_endpoint(first: Wire, second: Wire) -> Point3D | None:
    for point in (first.start, first.end):
        if point in (second.start, second.end):
            return point
    return None


def _included_angle(apex: Point3D, first: Point3D, second: Point3D) -> float:
    first_vector = (
        first.x_m - apex.x_m,
        first.y_m - apex.y_m,
        first.z_m - apex.z_m,
    )
    second_vector = (
        second.x_m - apex.x_m,
        second.y_m - apex.y_m,
        second.z_m - apex.z_m,
    )
    first_length = math.sqrt(sum(value * value for value in first_vector))
    second_length = math.sqrt(sum(value * value for value in second_vector))
    if first_length <= 1e-12 or second_length <= 1e-12:
        return 0.0
    cosine = sum(a * b for a, b in zip(first_vector, second_vector, strict=True)) / (
        first_length * second_length
    )
    return math.degrees(math.acos(min(max(cosine, -1.0), 1.0)))


def _angular_dimensions(
    model: AntennaModel,
    effective_type: str | None,
    factory: _Factory,
) -> tuple[AngularDimension, ...]:
    if not factory.projection.vertical:
        return ()
    if effective_type == ANTENNA_TYPE_INVERTED_V:
        if len(model.wires) != 2:
            return ()
        apex = _shared_endpoint(model.wires[0], model.wires[1])
        if apex is None:
            return ()
        first = model.wires[0].end if model.wires[0].start == apex else model.wires[0].start
        second = model.wires[1].end if model.wires[1].start == apex else model.wires[1].start
        angle = _included_angle(apex, first, second)
        return (
            AngularDimension(
                center=factory.project(apex),
                first=factory.project(first),
                second=factory.project(second),
                text=f"{angle:.1f}°",
                priority=85,
            ),
        )
    if effective_type == ANTENNA_TYPE_FAN_DIPOLE:
        dimensions: list[AngularDimension] = []
        for index in range(0, len(model.wires) - 1, 2):
            first_wire = model.wires[index]
            second_wire = model.wires[index + 1]
            apex = _shared_endpoint(first_wire, second_wire)
            if apex is None:
                continue
            first_end = first_wire.end if first_wire.start == apex else first_wire.start
            second_end = second_wire.end if second_wire.start == apex else second_wire.start
            angle = _included_angle(apex, first_end, second_end)
            dimensions.append(
                AngularDimension(
                    center=factory.project(apex),
                    first=factory.project(first_end),
                    second=factory.project(second_end),
                    text=f"{angle:.1f}°",
                    priority=70 - index,
                )
            )
        return tuple(dimensions)
    return ()


def _summary(
    translator: Translator,
    unit_system: UnitSystem,
    model: AntennaModel,
    parameters: object | None,
    antenna_type: str | None,
    display_name: str | None,
    mode: GeometryViewMode,
    notes: list[str],
) -> str:
    label = type_label(translator, antenna_type, parameters, display_name)
    plan_label = f"{label} {translator.t('geometry.top_view')}"
    parts: list[str] = []
    min_z, max_z = _model_z_extents(model)
    if isinstance(parameters, LoopParameters) or antenna_type == ANTENNA_TYPE_LOOP:
        if isinstance(parameters, LoopParameters):
            circumference_m = parameters.circumference_m
            diameter_m = parameters.diameter_m
            sides = parameters.sides
        else:
            circumference_m = sum(wire.length_m for wire in model.wires)
            sides = len(model.wires)
            side_length = circumference_m / sides if sides else 0.0
            diameter_m = side_length / math.sin(math.pi / sides) if sides > 1 else 0.0
        parts.extend(
            [
                f"{translator.t('field.circumference').lower()} "
                f"{_format_length(circumference_m, translator, unit_system)}",
                f"{translator.t('geometry.equivalent_diameter').lower()} "
                f"{_format_length(diameter_m, translator, unit_system)}",
                f"{translator.t('field.sides').lower()} {sides}",
            ]
        )
        if isinstance(parameters, LoopParameters):
            horizontal = parameters.orientation is LoopOrientation.HORIZONTAL
            orientation = translator.t(
                "orientation.horizontal" if horizontal else "orientation.vertical"
            ).lower()
            parts.append(f"{translator.t('field.orientation').lower()} {orientation}")
            if horizontal:
                parts.append(
                    f"{translator.t('field.height').lower()} "
                    f"{_format_length(parameters.height_m, translator, unit_system)}"
                )
            else:
                parts.extend(
                    [
                        f"{translator.t('field.base_height').lower()} "
                        f"{_format_length(parameters.height_m, translator, unit_system)}",
                        f"{translator.t('geometry.top_height').lower()} "
                        f"{_format_length(parameters.top_height_m, translator, unit_system)}",
                    ]
                )
    elif isinstance(parameters, MagneticLoopParameters):
        parts.extend(
            [
                f"{translator.t('magnetic_loop.diameter').lower()} "
                f"{_format_length(parameters.diameter_m, translator, unit_system)}",
                f"{translator.t('field.circumference').lower()} "
                f"{_format_length(parameters.circumference_m, translator, unit_system)}",
                f"{translator.t('field.sides').lower()} {parameters.sides}",
                f"{translator.t('magnetic_loop.gap').lower()} "
                f"{_format_length(parameters.gap_length_m, translator, unit_system)}",
                f"{translator.t('magnetic_loop.capacitance').lower()} "
                f"{parameters.tuning_capacitance_f * 1e12:.3f} pF",
                f"{translator.t('magnetic_loop.esr').lower()} {parameters.capacitor_esr_ohm:.3f} Ω",
            ]
        )
    elif isinstance(parameters, FoldedDipoleParameters):
        parts.extend(
            [
                f"{translator.t('field.element_length').lower()} "
                f"{_format_length(parameters.total_length_m, translator, unit_system)}",
                f"{translator.t('field.spacing').lower()} "
                f"{_format_length(parameters.spacing_m, translator, unit_system)}",
                f"{translator.t('geometry.total_conductor').lower()} "
                f"{_format_length(parameters.total_conductor_length_m, translator, unit_system)}",
            ]
        )
    elif isinstance(parameters, JPoleParameters) or antenna_type == ANTENNA_TYPE_J_POLE:
        folded = is_folded_j_pole(parameters, model)
        template = display_name or translator.t("catalog.slim_jim" if folded else "catalog.j_pole")
        verticals = tuple(
            wire
            for wire in model.wires
            if math.hypot(
                wire.end.x_m - wire.start.x_m,
                wire.end.y_m - wire.start.y_m,
            )
            <= 1e-9
        )
        if isinstance(parameters, JPoleParameters):
            radiator_length = parameters.radiator_height_m
            stub_length = parameters.stub_length_m
            spacing_m = parameters.spacing_m
            folded_gap = parameters.gap_m if folded else 0.0
        else:
            radiator_wire = (
                next((wire for wire in verticals if wire.id == "right-upper"), None)
                if folded
                else max(verticals, key=lambda wire: wire.length_m, default=None)
            )
            stub_wire = (
                next((wire for wire in verticals if wire.id == "right-lower"), None)
                if folded
                else min(verticals, key=lambda wire: wire.length_m, default=None)
            )
            radiator_length = radiator_wire.length_m if radiator_wire else 0.0
            stub_length = stub_wire.length_m if stub_wire else 0.0
            xs = [wire.start.x_m for wire in verticals]
            spacing_m = max(xs) - min(xs) if len(xs) >= 2 else 0.0
            folded_gap = 0.0
            if folded:
                upper = next((wire for wire in verticals if wire.id == "right-upper"), None)
                lower = next((wire for wire in verticals if wire.id == "right-lower"), None)
                if upper and lower:
                    folded_gap = max(
                        min(upper.start.z_m, upper.end.z_m) - max(lower.start.z_m, lower.end.z_m),
                        0.0,
                    )
        if mode is GeometryViewMode.PLAN:
            return translator.t(
                "geometry.j_pole_plan",
                template=template,
                spacing=_format_length(spacing_m, translator, unit_system),
            )
        key = "geometry.slim_jim_elevation" if folded else "geometry.j_pole_elevation"
        return translator.t(
            key,
            template=template,
            radiator=_format_length(radiator_length, translator, unit_system),
            stub=_format_length(stub_length, translator, unit_system),
            gap=_format_length(folded_gap, translator, unit_system),
            spacing=_format_length(spacing_m, translator, unit_system),
        )
    elif antenna_type == ZEPP_PRESENTATION_TYPE:
        radiator = next((wire for wire in model.wires if wire.id == ZEPP_RADIATOR_ID), None)
        stub = next((wire for wire in model.wires if wire.id == ZEPP_MATCHING_FEED_ID), None)
        open_stub = next((wire for wire in model.wires if wire.id == ZEPP_MATCHING_OPEN_ID), None)
        if radiator is not None and stub is not None and open_stub is not None:
            spacing_m = math.hypot(
                open_stub.start.x_m - stub.start.x_m,
                open_stub.start.y_m - stub.start.y_m,
            )
            impedance_ohm = parallel_wire_impedance_ohm(spacing_m, stub.radius_m)
            return translator.t(
                "geometry.zepp_summary",
                template=label,
                radiator=_format_length(radiator.length_m, translator, unit_system),
                stub=_format_length(stub.length_m, translator, unit_system),
                spacing=_format_length(spacing_m, translator, unit_system),
                impedance=f"{impedance_ohm:.0f}",
            )
        parts.extend(
            [
                f"{len(model.wires)} {translator.t('geometry.wires')}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(max_z, translator, unit_system)}",
            ]
        )
    elif isinstance(parameters, RingoParameters) or antenna_type == ANTENNA_TYPE_RINGO:
        if isinstance(parameters, RingoParameters):
            radiator_length = parameters.radiator_height_m
            ring_diameter = parameters.ring_diameter_m
            ring_height = parameters.ring_height_m
        else:
            radiator_wire = next(
                (wire for wire in model.wires if wire.id == "radiator"),
                max(
                    model.wires,
                    key=lambda wire: abs(wire.end.z_m - wire.start.z_m),
                    default=None,
                ),
            )
            radiator_length = radiator_wire.length_m if radiator_wire else 0.0
            xs = [point.x_m for wire in model.wires for point in (wire.start, wire.end)]
            ys = [point.y_m for wire in model.wires for point in (wire.start, wire.end)]
            ring_diameter = max(max(xs) - min(xs), max(ys) - min(ys))
            ring_wires = [wire for wire in model.wires if wire.id.startswith("ring-")]
            ring_height = min(wire.start.z_m for wire in ring_wires) if ring_wires else 0.0
        parts.extend(
            [
                f"{translator.t('geometry.radiator').lower()} "
                f"{_format_length(radiator_length, translator, unit_system)}",
                f"{translator.t('geometry.diameter').lower()} "
                f"{_format_length(ring_diameter, translator, unit_system)}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(ring_height, translator, unit_system)}",
            ]
        )
    elif isinstance(parameters, YagiParameters) or antenna_type == ANTENNA_TYPE_YAGI:
        if isinstance(parameters, YagiParameters):
            positions = [element.position_m for element in parameters.elements]
            element_count = len(parameters.elements)
            boom_m = max(positions) - min(positions)
            height_m = parameters.height_m
        else:
            element_count = len(model.wires)
            boom_m = (
                _wire_point(model.wires[0], 0.5).distance_to(_wire_point(model.wires[-1], 0.5))
                if len(model.wires) >= 2
                else 0.0
            )
            height_m = max_z
        parts.extend(
            [
                f"{translator.t('geometry.elements').lower()} {element_count}",
                f"{translator.t('geometry.boom_length').lower()} "
                f"{_format_length(boom_m, translator, unit_system)}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(height_m, translator, unit_system)}",
            ]
        )
        if isinstance(parameters, YagiParameters) and (
            parameters.polarization is Polarization.VERTICAL
        ):
            parts.append(
                f"{translator.t('field.polarization').lower()} "
                f"{translator.t('orientation.vertical').lower()}"
            )
    elif isinstance(parameters, MoxonParameters):
        parts.extend(
            [
                f"{translator.t('geometry.width').lower()} "
                f"{_format_length(parameters.width_m, translator, unit_system)}",
                f"{translator.t('geometry.depth').lower()} "
                f"{_format_length(parameters.depth_m, translator, unit_system)}",
                f"{translator.t('geometry.gap').lower()} "
                f"{_format_length(parameters.gap_m, translator, unit_system)}",
            ]
        )
        if parameters.polarization is Polarization.VERTICAL:
            parts.extend(
                [
                    f"{translator.t('field.height').lower()} "
                    f"{_format_length(parameters.height_m, translator, unit_system)}",
                    f"{translator.t('field.polarization').lower()} "
                    f"{translator.t('orientation.vertical').lower()}",
                ]
            )
    elif isinstance(parameters, InvertedLParameters):
        parts.extend(
            [
                f"{translator.t('inverted_l.vertical_height').lower()} "
                f"{_format_length(parameters.vertical_height_m, translator, unit_system)}",
                f"{translator.t('inverted_l.horizontal_length').lower()} "
                f"{_format_length(parameters.horizontal_length_m, translator, unit_system)}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(parameters.top_height_m, translator, unit_system)}",
            ]
        )
    elif isinstance(parameters, InvertedVParameters):
        parts.extend(
            [
                f"{translator.t('geometry.leg_length').lower()} "
                f"{_format_length(parameters.leg_length_m, translator, unit_system)}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(parameters.apex_height_m, translator, unit_system)}",
                f"{translator.t('geometry.end_height').lower()} "
                f"{_format_length(parameters.end_height_m, translator, unit_system)}",
                f"{translator.t('inverted_v.included_angle').lower()} "
                f"{parameters.included_angle_deg:.1f}°",
            ]
        )
    elif isinstance(parameters, FanDipoleParameters):
        parts.extend(
            [
                f"{translator.t('geometry.elements').lower()} {len(parameters.elements)}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(parameters.apex_height_m, translator, unit_system)}",
            ]
        )
    elif isinstance(parameters, EndFedParameters) or antenna_type == ANTENNA_TYPE_ENDFED:
        if isinstance(parameters, EndFedParameters):
            feed_height = parameters.feed_height_m
            end_height = parameters.end_height_m
        else:
            feed_wire = model.feed_wire
            feed_ratio = model.feed.offset_m / feed_wire.length_m
            feed_height = (
                feed_wire.start.z_m + (feed_wire.end.z_m - feed_wire.start.z_m) * feed_ratio
            )
            end_height = max(
                feed_wire.start.z_m,
                feed_wire.end.z_m,
            )
        parts.extend(
            [
                f"{translator.t('geometry.wire_length').lower()} "
                f"{_format_length(model.wires[0].length_m, translator, unit_system)}",
                f"{translator.t('geometry.feed_height').lower()} "
                f"{_format_length(feed_height, translator, unit_system)}",
                f"{translator.t('geometry.end_height').lower()} "
                f"{_format_length(end_height, translator, unit_system)}",
            ]
        )
    elif isinstance(parameters, OCFDParameters) or antenna_type == ANTENNA_TYPE_OCFD:
        if isinstance(parameters, OCFDParameters):
            length_m = parameters.total_length_m
            feed_offset = parameters.feed_offset_m
            height_m = parameters.height_m
        else:
            wire = model.wires[0]
            length_m = wire.length_m
            feed_offset = (
                wire.length_m * model.feed.offset_m / wire.length_m if wire.length_m > 0.0 else 0.0
            )
            height_m = max_z
        parts.extend(
            [
                f"{translator.t('field.length').lower()} "
                f"{_format_length(length_m, translator, unit_system)}",
                f"{translator.t('geometry.feed_offset').lower()} "
                f"{_format_length(feed_offset, translator, unit_system)}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(height_m, translator, unit_system)}",
            ]
        )
    elif isinstance(parameters, VerticalParameters) or antenna_type == ANTENNA_TYPE_VERTICAL:
        if isinstance(parameters, VerticalParameters):
            height_m = parameters.height_m
            base_height = parameters.base_height_m
            radial_count = parameters.radial_count
            radial_length = parameters.radial_length_m
        else:
            height_m = max_z - min_z
            base_height = min_z
            radial_wires = [wire for wire in model.wires if wire.id.startswith("radial-")]
            radial_count = len(radial_wires)
            radial_length = (
                max(math.hypot(wire.end.x_m, wire.end.y_m) for wire in radial_wires)
                if radial_wires
                else 0.0
            )
        parts.extend(
            [
                f"{translator.t('field.height').lower()} "
                f"{_format_length(height_m, translator, unit_system)}",
                f"{translator.t('field.base_height').lower()} "
                f"{_format_length(base_height, translator, unit_system)}",
            ]
        )
        if radial_count:
            parts.append(
                f"{translator.t('geometry.radials').lower()} {radial_count} x "
                f"{_format_length(radial_length, translator, unit_system)}"
            )
        if isinstance(parameters, VerticalParameters) and parameters.loading_coil_enabled:
            parts.append(
                f"{translator.t('vertical.loading_coil').lower()} "
                f"{parameters.loading_coil_inductance_h * 1e6:.3f} µH @ "
                f"{_format_length(parameters.loading_coil_offset_m, translator, unit_system)}"
            )
    elif isinstance(parameters, T2FDParameters):
        height_label = (
            translator.t("field.base_height")
            if parameters.orientation.value == "vertical"
            else translator.t("field.height")
        )
        parts.extend(
            [
                f"{translator.t('t2fd.length').lower()} "
                f"{_format_length(parameters.length_m, translator, unit_system)}",
                f"{translator.t('t2fd.spacing').lower()} "
                f"{_format_length(parameters.spacing_m, translator, unit_system)}",
                f"{translator.t('t2fd.termination').lower()} "
                f"{parameters.termination_resistance_ohm:g} Ω",
                f"{height_label.lower()} "
                f"{_format_length(parameters.height_m, translator, unit_system)}",
            ]
        )
    elif isinstance(parameters, TrapDipoleParameters):
        height_label = (
            translator.t("field.base_height")
            if parameters.orientation.value == "vertical"
            else translator.t("field.height")
        )
        parts.extend(
            [
                f"{translator.t('geometry.total_length').lower()} "
                f"{_format_length(parameters.total_length_m, translator, unit_system)}",
                f"{translator.t('geometry.center').lower()} "
                f"{_format_length(parameters.inner_length_m, translator, unit_system)}",
                f"{translator.t('geometry.traps').lower()} 2",
                f"{height_label.lower()} "
                f"{_format_length(parameters.height_m, translator, unit_system)}",
            ]
        )
    elif isinstance(parameters, DipoleParameters):
        parts.extend(
            [
                f"{translator.t('field.length').lower()} "
                f"{_format_length(parameters.total_length_m, translator, unit_system)}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(max_z, translator, unit_system)}",
            ]
        )
    else:
        parts.extend(
            [
                f"{len(model.wires)} {translator.t('geometry.wires')}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(max_z, translator, unit_system)}",
            ]
        )
        if isinstance(parameters, CustomAntennaParameters):
            notes.append(translator.t("geometry.arbitrary_geometry"))
    if (
        mode is GeometryViewMode.ELEVATION
        and abs(max_z - min_z) < 1e-9
        and len(model.wires) > 1
        and translator.t("geometry.front_overlap") not in notes
    ):
        notes.append(translator.t("geometry.front_overlap"))
    if mode is GeometryViewMode.PLAN:
        label = plan_label
    if notes:
        return f"{label} · " + " · ".join([*parts, *notes])
    return f"{label} · " + " · ".join(parts)


def _transmission_line_polylines(
    model: AntennaModel,
    factory: _Factory,
) -> tuple[ScenePolyline, ...]:
    polylines: list[ScenePolyline] = []
    for line in model.transmission_lines:
        start_wire = model.wire_by_id(line.start_wire_id)
        end_wire = model.wire_by_id(line.end_wire_id)
        start = start_wire.point_at(min(line.start_offset_m, start_wire.length_m))
        end = end_wire.point_at(min(line.end_offset_m, end_wire.length_m))
        polylines.append(
            ScenePolyline(
                (factory.project(start), factory.project(end)),
                role="transmission-line",
                style="dashed",
                width=1.5,
            )
        )
    return tuple(polylines)


def _plan_inset(
    model: AntennaModel,
    translator: Translator,
    unit_system: UnitSystem,
    dimensions: tuple[Dimension, ...] = (),
) -> SceneInset:
    polylines = tuple(
        ScenePolyline(
            (
                ScenePoint(wire.start.x_m, wire.start.y_m),
                ScenePoint(wire.end.x_m, wire.end.y_m),
            ),
            role="wire",
        )
        for wire in model.wires
    )
    return SceneInset(
        label=translator.t("geometry.top_view"),
        polylines=polylines,
        dimensions=dimensions,
    )


def build_scene(
    model: AntennaModel,
    *,
    antenna_type: str | None,
    parameters: object | None,
    display_name: str | None,
    mode: GeometryViewMode,
    translator: Translator,
    unit_system: UnitSystem,
    height_exaggeration: float = 1.0,
) -> GeometryScene:
    """Project ``model`` and attach semantic dimensions for the selected view."""

    effective_type = effective_antenna_type(antenna_type, parameters)
    points = tuple(point for wire in model.wires for point in (wire.start, wire.end))
    projection = (
        plan_projection(points) if mode is GeometryViewMode.PLAN else front_projection(points)
    )
    factory = _Factory(
        projection=projection,
        exaggeration=height_exaggeration if projection.vertical else 1.0,
        translator=translator,
        unit_system=unit_system,
    )
    polylines = tuple(
        ScenePolyline(
            (factory.project(wire.start), factory.project(wire.end)),
            role="wire",
            width=2.5,
        )
        for wire in model.wires
    ) + _transmission_line_polylines(model, factory)
    markers: list[SceneMarker] = [_feed_marker(model, factory, translator)]
    markers.extend(_load_markers(model, factory))
    dimensions: list[Dimension] = []
    angular_dimensions: list[AngularDimension] = []
    insets: list[SceneInset] = []
    notes: list[str] = []
    if effective_type == ZEPP_PRESENTATION_TYPE:
        note_key = (
            "geometry.zepp_note"
            if any(wire.id == ZEPP_MATCHING_FEED_ID for wire in model.wires)
            else "geometry.zepp_legacy_note"
        )
        notes.append(translator.t(note_key))
    if model.transmission_lines:
        notes.append(
            translator.t(
                "geometry.transmission_lines",
                count=len(model.transmission_lines),
            )
        )

    if effective_type == ANTENNA_TYPE_LOOP:
        _add_loop_dimensions(
            model,
            parameters if isinstance(parameters, LoopParameters) else None,
            factory,
            dimensions,
            notes,
        )
    elif effective_type == ANTENNA_TYPE_MAGNETIC_LOOP:
        if isinstance(parameters, MagneticLoopParameters):
            _add_magnetic_loop_dimensions(
                model,
                parameters,
                factory,
                dimensions,
                notes,
            )
        else:
            _add_loop_dimensions(model, None, factory, dimensions, notes)
    elif effective_type in {ANTENNA_TYPE_FOLDED_DIPOLE, ANTENNA_TYPE_T2FD}:
        _add_folded_dimensions(model, factory, dimensions, insets, translator)
    elif effective_type == ANTENNA_TYPE_J_POLE:
        _add_j_pole_dimensions(
            model,
            parameters,
            factory,
            dimensions,
            insets,
            translator,
        )
    elif effective_type == ANTENNA_TYPE_RINGO:
        _add_ringo_dimensions(model, factory, dimensions, insets, translator)
    elif effective_type in {ANTENNA_TYPE_YAGI, ANTENNA_TYPE_MOXON}:
        _add_array_dimensions(
            model,
            parameters,
            factory,
            dimensions,
            notes,
            translator,
        )
    elif effective_type == ANTENNA_TYPE_INVERTED_L:
        if isinstance(parameters, InvertedLParameters):
            _add_inverted_l_dimensions(
                model,
                parameters,
                factory,
                dimensions,
                notes,
                translator,
            )
        else:
            _add_sloping_array_dimensions(model, parameters, factory, dimensions)
    elif effective_type in {
        ANTENNA_TYPE_INVERTED_V,
        ANTENNA_TYPE_FAN_DIPOLE,
        ANTENNA_TYPE_VERTICAL,
    }:
        _add_sloping_array_dimensions(model, parameters, factory, dimensions)
    elif len(model.wires) == 1:
        _add_single_wire_dimensions(model, factory, dimensions)
    else:
        projected = tuple(
            factory.project(point) for wire in model.wires for point in (wire.start, wire.end)
        )
        extents = _scene_extents(projected)
        if extents is not None:
            min_x, max_x, min_y, max_y = extents
            dimensions.append(
                factory.horizontal_dimension(
                    min_y,
                    min_x,
                    max_x,
                    max_x - min_x,
                    side="below",
                    priority=50,
                )
            )
            dimensions.append(
                factory.vertical_dimension(
                    max_x,
                    min_y,
                    max_y,
                    max_y - min_y,
                    side="right",
                    priority=45,
                )
            )

    angular_dimensions.extend(_angular_dimensions(model, effective_type, factory))
    if (
        effective_type == ANTENNA_TYPE_VERTICAL
        and isinstance(parameters, VerticalParameters)
        and parameters.radial_count
    ):
        radial_dimensions: tuple[Dimension, ...] = ()
        if parameters.radial_length_m > 0.0:
            radial = next(
                (wire for wire in model.wires if wire.id.startswith("radial-")),
                None,
            )
            if radial is not None:
                radial_dimensions = (
                    Dimension(
                        start=ScenePoint(radial.start.x_m, radial.start.y_m),
                        end=ScenePoint(radial.end.x_m, radial.end.y_m),
                        text=_format_length(
                            parameters.radial_length_m,
                            translator,
                            unit_system,
                        ),
                        side="below",
                        priority=80,
                    ),
                )
        insets.append(
            _plan_inset(
                model,
                translator,
                unit_system,
                radial_dimensions,
            )
        )
    if mode is GeometryViewMode.ELEVATION and not insets and not is_planar(model):
        xs = [point.x_m for wire in model.wires for point in (wire.start, wire.end)]
        ys = [point.y_m for wire in model.wires for point in (wire.start, wire.end)]
        width = max(xs) - min(xs)
        depth = max(ys) - min(ys)
        if min(width, depth) > max(width, depth, 1.0) * 0.05:
            insets.append(_plan_inset(model, translator, unit_system))
    if not notes and isinstance(parameters, CustomAntennaParameters):
        notes.append(translator.t("geometry.arbitrary_geometry"))
    notes = list(dict.fromkeys(notes))
    dimensions = [
        dimension for dimension in dimensions if dimension.start.distance_to(dimension.end) > 1e-9
    ]
    summary = _summary(
        translator,
        unit_system,
        model,
        parameters,
        effective_type,
        display_name,
        mode,
        notes,
    )
    if not math.isclose(factory.exaggeration, 1.0):
        summary = (
            summary
            + " · "
            + translator.t(
                "geometry.vertical_exaggeration",
                factor=f"{factory.exaggeration:g}",
            )
        )
    return GeometryScene(
        polylines=polylines,
        markers=tuple(markers),
        dimensions=tuple(dimensions),
        angular_dimensions=tuple(angular_dimensions),
        summary=summary,
        notes=tuple(notes),
        show_ground=projection.vertical,
        ground_y_m=(factory.project(Point3D(0.0, 0.0, 0.0)).y_m if projection.vertical else None),
        is_plan=mode is GeometryViewMode.PLAN,
        azimuth_deg=_azimuth_degrees(parameters, model),
        insets=tuple(insets),
        height_exaggeration=factory.exaggeration,
        projection_name=projection.name,
        metadata={"antenna_type": effective_type or "custom"},
    )


def _azimuth_degrees(parameters: object | None, model: AntennaModel) -> float | None:
    value = getattr(parameters, "azimuth_deg", None)
    if isinstance(value, (int, float)):
        return float(value)
    for wire in model.wires:
        dx = wire.end.x_m - wire.start.x_m
        dy = wire.end.y_m - wire.start.y_m
        if math.hypot(dx, dy) > 1e-9:
            return math.degrees(math.atan2(dy, dx)) % 360.0
    return None
