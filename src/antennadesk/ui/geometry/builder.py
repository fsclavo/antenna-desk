# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the renderer-neutral construction scene from an antenna model."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ...domain.antennas.antenna import AntennaModel
from ...domain.antennas.beverage import (
    ANTENNA_TYPE_BEVERAGE,
    BeverageParameters,
)
from ...domain.antennas.biquad import (
    ANTENNA_TYPE_BIQUAD,
    ANTENNA_TYPE_DOUBLE_BIQUAD,
    BiquadParameters,
)
from ...domain.antennas.custom import ANTENNA_TYPE_CUSTOM, CustomAntennaParameters
from ...domain.antennas.dipole import (
    ANTENNA_TYPE_WIRE_DIPOLE,
    SAG_SEGMENTS,
    DipoleParameters,
)
from ...domain.antennas.discone import ANTENNA_TYPE_DISCONE, DisconeParameters
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
from ...domain.antennas.hexbeam import ANTENNA_TYPE_HEXBEAM, HexbeamParameters
from ...domain.antennas.inverted_l import (
    ANTENNA_TYPE_INVERTED_L,
    HORIZONTAL_ID,
    VERTICAL_ID,
    InvertedLParameters,
)
from ...domain.antennas.inverted_v import ANTENNA_TYPE_INVERTED_V, InvertedVParameters
from ...domain.antennas.j_pole import ANTENNA_TYPE_J_POLE, JPoleParameters
from ...domain.antennas.loaded_dipole import (
    ANTENNA_TYPE_LOADED_DIPOLE,
    LoadedDipoleParameters,
)
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
from ...domain.antennas.phased_vertical import (
    ANTENNA_TYPE_PHASED_VERTICAL,
    PhasedVerticalParameters,
)
from ...domain.antennas.polarization import Polarization
from ...domain.antennas.quad_beam import (
    ANTENNA_TYPE_QUAD_BEAM,
    DRIVEN_ELEMENT_INDEX,
    QuadBeamParameters,
)
from ...domain.antennas.ringo import ANTENNA_TYPE_RINGO, RingoParameters
from ...domain.antennas.scv import (
    ANTENNA_TYPE_BOBTAIL_CURTAIN,
    ANTENNA_TYPE_HALF_SQUARE,
    ScvParameters,
)
from ...domain.antennas.t2fd import ANTENNA_TYPE_T2FD, T2FDParameters
from ...domain.antennas.transmission_line_doublet import (
    ANTENNA_TYPE_G5RV,
    ANTENNA_TYPE_ZS6BKW,
    TransmissionLineDoubletParameters,
)
from ...domain.antennas.trap_dipole import (
    ANTENNA_TYPE_TRAP_DIPOLE,
    TrapDipoleParameters,
)
from ...domain.antennas.trap_yagi import ANTENNA_TYPE_TRAP_YAGI, TrapYagiParameters
from ...domain.antennas.vertical import ANTENNA_TYPE_VERTICAL, VerticalParameters
from ...domain.antennas.wire import Wire
from ...domain.antennas.yagi import ANTENNA_TYPE_YAGI, YagiMatchType, YagiParameters
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
    construction_view,
    front_projection,
    is_planar,
    plan_projection,
)

ZEPP_PRESENTATION_TYPE = "zepp"

_TYPE_KEYS: dict[str, str] = {
    ANTENNA_TYPE_WIRE_DIPOLE: "antenna_type.wire_dipole",
    ANTENNA_TYPE_DISCONE: "catalog.discone",
    ANTENNA_TYPE_HEXBEAM: "catalog.hexbeam",
    ANTENNA_TYPE_TRAP_YAGI: "catalog.trap_yagi",
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
    ANTENNA_TYPE_HALF_SQUARE: "catalog.half_square",
    ANTENNA_TYPE_BOBTAIL_CURTAIN: "catalog.bobtail_curtain",
    ANTENNA_TYPE_BIQUAD: "catalog.biquad",
    ANTENNA_TYPE_DOUBLE_BIQUAD: "catalog.double_biquad",
    ANTENNA_TYPE_BEVERAGE: "catalog.beverage",
    ANTENNA_TYPE_LOADED_DIPOLE: "catalog.loaded_dipole",
    ANTENNA_TYPE_PHASED_VERTICAL: "catalog.phased_vertical",
    ANTENNA_TYPE_QUAD_BEAM: "catalog.quad_beam",
    ANTENNA_TYPE_TRAP_DIPOLE: "catalog.trap_dipole",
    ANTENNA_TYPE_T2FD: "catalog.t2fd",
    ANTENNA_TYPE_G5RV: "catalog.g5rv",
    ANTENNA_TYPE_ZS6BKW: "catalog.zs6bkw",
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
            "half_square",
            "bobtail_curtain",
            "biquad",
            "double_biquad",
            "beverage",
            "loaded_dipole",
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
        label: str | None = None,
    ) -> Dimension:
        return Dimension(
            start=self.project(first),
            end=self.project(second),
            text=_format_length(value_m, self.translator, self.unit_system),
            side=side,
            priority=priority,
            label=label,
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
        label: str | None = None,
    ) -> Dimension:
        return Dimension(
            start=ScenePoint(x_scene, self.y_for_z(z_start_m)),
            end=ScenePoint(x_scene, self.y_for_z(z_end_m)),
            text=_format_length(value_m, self.translator, self.unit_system),
            side=side,
            priority=priority,
            label=label,
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
        label: str | None = None,
    ) -> Dimension:
        return Dimension(
            start=ScenePoint(x_start_scene, y_scene),
            end=ScenePoint(x_end_scene, y_scene),
            text=_format_length(value_m, self.translator, self.unit_system),
            side=side,
            priority=priority,
            label=label,
        )

    def between_scene(
        self,
        first: ScenePoint,
        second: ScenePoint,
        value_m: float,
        *,
        side: str = "auto",
        priority: int = 50,
        label: str | None = None,
    ) -> Dimension:
        return Dimension(
            start=first,
            end=second,
            text=_format_length(value_m, self.translator, self.unit_system),
            side=side,
            priority=priority,
            label=label,
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


def _source_markers(model: AntennaModel, factory: _Factory) -> tuple[SceneMarker, ...]:
    markers: list[SceneMarker] = []
    for index, source in enumerate(model.sources, start=2):
        wire = model.wire_by_id(source.wire_id)
        ratio = min(max(source.offset_m / wire.length_m, 0.0), 1.0)
        markers.append(
            SceneMarker(
                point=factory.project(_wire_point(wire, ratio)),
                kind="source",
                label=f"S{index} {source.amplitude * 100.0:.0f}% {source.phase_deg:.0f}°",
                priority=80,
            )
        )
    return tuple(markers)


def _add_feed_and_load_dimensions(
    model: AntennaModel,
    wire: Wire,
    factory: _Factory,
    dimensions: list[Dimension],
    translator: Translator | None,
    side: str,
    *,
    load_datum: str = "start",
) -> None:
    feed_wire = model.feed_wire
    feed_point = _wire_point(feed_wire, 0.0)
    if feed_wire.length_m > 1e-9:
        feed_ratio = min(max(model.feed.offset_m / feed_wire.length_m, 0.0), 1.0)
        feed_point = _wire_point(feed_wire, feed_ratio)
        if 1e-6 < feed_ratio < 1.0 - 1e-6:
            dimensions.append(
                factory.dimension(
                    feed_wire.start,
                    feed_point,
                    feed_wire.length_m * feed_ratio,
                    side=side,
                    priority=80,
                    label=translator.t("geometry.feed_offset") if translator else None,
                )
            )
    datum = feed_point if load_datum == "feed" else wire.start
    for load_index, load in enumerate(model.loads, start=1):
        if load.wire_id != wire.id:
            continue
        load_point = _wire_point(wire, load.offset_m / wire.length_m)
        value_m = (
            abs(load.offset_m - model.feed.offset_m) if load_datum == "feed" else load.offset_m
        )
        dimensions.append(
            factory.dimension(
                datum,
                load_point,
                value_m,
                side=side,
                priority=70,
                label=f"L{load_index}",
            )
        )


def _add_single_wire_dimensions(
    model: AntennaModel,
    factory: _Factory,
    dimensions: list[Dimension],
    notes: list[str] | None = None,
    translator: Translator | None = None,
) -> None:
    wire = model.wires[0]
    min_z, max_z = _model_z_extents(model)
    feed_wire = model.feed_wire
    feed_ratio = model.feed.offset_m / feed_wire.length_m
    feed_z = feed_wire.start.z_m + (feed_wire.end.z_m - feed_wire.start.z_m) * feed_ratio
    start = factory.project(wire.start)
    end = factory.project(wire.end)
    projected_length = start.distance_to(end)
    if wire.length_m > 1e-9:
        value_m = wire.length_m
        if projected_length > 1e-9 and abs(projected_length - wire.length_m) > 1e-6:
            value_m = projected_length
            if notes is not None and translator is not None:
                notes.append(
                    translator.t(
                        "geometry.projected_length_note",
                        length=_format_length(wire.length_m, translator, factory.unit_system),
                        projected=_format_length(
                            projected_length,
                            translator,
                            factory.unit_system,
                        ),
                    )
                )
        dimensions.append(
            factory.dimension(wire.start, wire.end, value_m, side="auto", priority=85)
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
        offset_side = "below" if abs(wire.end.z_m - wire.start.z_m) < 1e-9 else "left"
        _add_feed_and_load_dimensions(
            model,
            wire,
            factory,
            dimensions,
            translator,
            offset_side,
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
                    priority=85,
                    label=factory.translator.t("geometry.gap"),
                )
            )
    else:
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
    notes.append(
        factory.translator.t(
            "magnetic_loop.diameter_note",
            diameter=_format_length(
                parameters.diameter_m,
                factory.translator,
                factory.unit_system,
            ),
        )
    )


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
            label=translator.t("geometry.upper_section" if folded else "geometry.radiator"),
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
            label=translator.t("geometry.lower_section" if folded else "geometry.stub"),
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
            label=translator.t("field.base_height"),
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
            label=translator.t("field.spacing"),
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
                    label=translator.t("geometry.gap"),
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
    feed_wire = model.feed_wire
    feed_ratio = min(max(model.feed.offset_m / feed_wire.length_m, 0.0), 1.0)
    feed_point = _wire_point(feed_wire, feed_ratio)
    feed_base_z = min(feed_wire.start.z_m, feed_wire.end.z_m)
    feed_offset = abs(feed_point.z_m - feed_base_z)
    if feed_offset > 1e-6:
        dimensions.append(
            factory.vertical_dimension(
                max(radiator_x, stub_x),
                feed_base_z,
                feed_point.z_m,
                feed_offset,
                side="right",
                priority=90,
                label=translator.t("geometry.feed_offset"),
            )
        )
    if folded:
        dimensions.append(
            factory.vertical_dimension(
                min(radiator_x, stub_x),
                min_z,
                max_z,
                max_z - min_z,
                side="left",
                priority=55,
                label=translator.t("geometry.left_leg"),
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


def _add_scv_dimensions(
    model: AntennaModel,
    parameters: ScvParameters | None,
    factory: _Factory,
    dimensions: list[Dimension],
    notes: list[str],
    translator: Translator,
) -> None:
    min_z, max_z = _model_z_extents(model)
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
    top_points = [wire.start if wire.start.z_m >= wire.end.z_m else wire.end for wire in verticals]
    top_pairs = [
        (first, second)
        for index, first in enumerate(top_points)
        for second in top_points[index + 1 :]
    ]
    left_top, right_top = max(
        top_pairs,
        key=lambda pair: factory.project(pair[0]).distance_to(factory.project(pair[1])),
    )
    if isinstance(parameters, ScvParameters):
        horizontal_length = parameters.horizontal_length_m
        vertical_height = parameters.vertical_height_m
    else:
        horizontal_length = max(
            math.hypot(
                point.x_m - other.x_m,
                point.y_m - other.y_m,
            )
            for wire in verticals
            for point in (wire.start, wire.end)
            for other_wire in verticals
            for other in (other_wire.start, other_wire.end)
            if math.isclose(point.z_m, max_z, abs_tol=1e-6)
            and math.isclose(other.z_m, max_z, abs_tol=1e-6)
        )
        vertical_height = max_z - min_z
    if factory.projection.vertical:
        dimensions.append(
            factory.dimension(
                left_top,
                right_top,
                horizontal_length,
                side="below",
                priority=90,
                label=translator.t("geometry.span"),
            )
        )
        dimensions.append(
            factory.vertical_dimension(
                factory.project(right_top).x_m,
                min_z,
                max_z,
                vertical_height,
                side="right",
                priority=80,
            )
        )
        if min_z > 1e-6:
            dimensions.append(
                factory.vertical_dimension(
                    factory.project(left_top).x_m,
                    0.0,
                    min_z,
                    min_z,
                    side="left",
                    priority=60,
                )
            )
        feed_wire = model.feed_wire
        if feed_wire.length_m > 1e-9:
            feed_ratio = min(max(model.feed.offset_m / feed_wire.length_m, 0.0), 1.0)
            feed_point = _wire_point(feed_wire, feed_ratio)
            feed_offset = max_z - feed_point.z_m
            if feed_offset > 1e-6:
                dimensions.append(
                    factory.vertical_dimension(
                        factory.project(feed_wire.start).x_m,
                        feed_point.z_m,
                        max_z,
                        feed_offset,
                        side="right",
                        priority=70,
                        label=translator.t("scv.feed_offset"),
                    )
                )
    else:
        dimensions.append(
            factory.dimension(
                left_top,
                right_top,
                horizontal_length,
                side="above",
                priority=80,
            )
        )
        notes.append(translator.t("geometry.vertical_plane_edge_on"))


def _add_biquad_dimensions(
    model: AntennaModel,
    parameters: BiquadParameters | None,
    factory: _Factory,
    dimensions: list[Dimension],
    notes: list[str],
    translator: Translator,
) -> None:
    min_z, max_z = _model_z_extents(model)
    rails = tuple(
        wire
        for wire in model.wires
        if math.isclose(wire.start.z_m, wire.end.z_m, abs_tol=1e-9)
        and math.hypot(
            wire.end.x_m - wire.start.x_m,
            wire.end.y_m - wire.start.y_m,
        )
        > 1e-9
    )
    if not rails:
        return
    top = max(
        (wire for wire in rails if math.isclose(wire.start.z_m, max_z, abs_tol=1e-9)),
        key=lambda wire: math.hypot(
            wire.end.x_m - wire.start.x_m,
            wire.end.y_m - wire.start.y_m,
        ),
    )
    left = top.start if top.start.x_m <= top.end.x_m else top.end
    right = top.end if top.start.x_m <= top.end.x_m else top.start
    width = math.hypot(
        top.end.x_m - top.start.x_m,
        top.end.y_m - top.start.y_m,
    )
    if factory.projection.vertical:
        dimensions.append(factory.dimension(left, right, width, side="above", priority=90))
        dimensions.append(
            factory.vertical_dimension(
                factory.project(right).x_m,
                min_z,
                max_z,
                max_z - min_z,
                side="right",
                priority=85,
            )
        )
        if min_z > 1e-6:
            dimensions.append(
                factory.vertical_dimension(
                    factory.project(left).x_m,
                    0.0,
                    min_z,
                    min_z,
                    side="left",
                    priority=60,
                )
            )
        if parameters is not None:
            right_side = next(
                (
                    wire
                    for wire in model.wires
                    if wire.id == f"biquad-right-{parameters.loop_count - 1}"
                ),
                None,
            )
            if right_side is not None:
                dimensions.append(
                    factory.dimension(
                        right_side.start,
                        right_side.end,
                        parameters.loop_side_m,
                        side="left",
                        priority=75,
                        label=translator.t("biquad.loop_side"),
                    )
                )
            notes.append(
                translator.t(
                    "biquad.reflector_spacing_note",
                    spacing=_format_length(
                        parameters.reflector_spacing_m,
                        translator,
                        factory.unit_system,
                    ),
                )
            )
        return
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
    if parameters is not None and parameters.reflector_enabled:
        dimensions.append(
            Dimension(
                start=ScenePoint(max(xs), min(ys)),
                end=ScenePoint(max(xs), max(ys)),
                text=_format_length(
                    parameters.reflector_spacing_m,
                    translator,
                    factory.unit_system,
                ),
                side="right",
                priority=80,
            )
        )
    notes.append(translator.t("geometry.vertical_plane_edge_on"))


def _add_beverage_dimensions(
    model: AntennaModel,
    parameters: BeverageParameters | None,
    factory: _Factory,
    dimensions: list[Dimension],
    notes: list[str],
    translator: Translator,
) -> None:
    wire = model.feed_wire
    near = wire.point_at(model.feed.offset_m)
    far = wire.end if near.distance_to(wire.end) >= near.distance_to(wire.start) else wire.start
    length = wire.length_m
    height = near.z_m
    dimensions.append(factory.dimension(near, far, length, side="above", priority=90))
    if factory.projection.vertical:
        x_scene = factory.project(far).x_m
        dimensions.append(
            factory.vertical_dimension(
                x_scene,
                0.0,
                height,
                height,
                side="right",
                priority=80,
            )
        )
    if parameters is not None and parameters.termination_enabled:
        notes.append(
            translator.t(
                "beverage.termination_note",
                resistance=f"{parameters.termination_resistance_ohm:.1f} Ω",
            )
        )


def _add_loaded_dipole_dimensions(
    model: AntennaModel,
    parameters: LoadedDipoleParameters | None,
    factory: _Factory,
    dimensions: list[Dimension],
    notes: list[str],
    translator: Translator,
) -> None:
    wire = model.feed_wire
    horizontal = abs(wire.end.z_m - wire.start.z_m) < 1e-9
    if factory.projection.vertical:
        dimensions.append(
            factory.dimension(
                wire.start,
                wire.end,
                wire.length_m,
                side="below" if horizontal else "right",
                priority=90,
                label=translator.t("field.length"),
            )
        )
        if wire.start.z_m > 1e-6:
            dimensions.append(
                factory.vertical_dimension(
                    factory.project(wire.start).x_m,
                    0.0,
                    wire.start.z_m,
                    wire.start.z_m,
                    side="left",
                    priority=60,
                )
            )
    else:
        dimensions.append(
            factory.dimension(
                wire.start,
                wire.end,
                wire.length_m,
                side="above",
                priority=85,
                label=translator.t("field.length"),
            )
        )
        dimensions.append(
            factory.vertical_dimension(
                factory.project(wire.end).x_m,
                0.0,
                wire.start.z_m,
                wire.start.z_m,
                side="right",
                priority=60,
            )
        )
    offset_side = "below" if abs(wire.end.z_m - wire.start.z_m) < 1e-9 else "left"
    _add_feed_and_load_dimensions(
        model,
        wire,
        factory,
        dimensions,
        translator,
        offset_side,
        load_datum="feed",
    )
    if parameters is not None and parameters.coil_active:
        notes.append(
            translator.t(
                "loaded_dipole.coil_note",
                inductance=parameters.loading_coil_inductance_h * 1e6,
                offset=_format_length(
                    parameters.link_offset_m,
                    translator,
                    factory.unit_system,
                ),
            )
        )


def _add_phased_vertical_dimensions(
    model: AntennaModel,
    parameters: PhasedVerticalParameters | None,
    factory: _Factory,
    dimensions: list[Dimension],
    notes: list[str],
    translator: Translator,
) -> None:
    verticals = tuple(wire for wire in model.wires if wire.id.startswith("phased-vertical-"))
    if not verticals:
        verticals = tuple(wire for wire in model.wires if abs(wire.end.z_m - wire.start.z_m) > 1e-9)
    if not verticals:
        return
    primary = verticals[0]
    height = primary.length_m
    base_height = min(primary.start.z_m, primary.end.z_m)
    if factory.projection.vertical:
        x_scene = factory.project(primary.start).x_m
        dimensions.append(
            factory.vertical_dimension(
                x_scene,
                min(primary.start.z_m, primary.end.z_m),
                max(primary.start.z_m, primary.end.z_m),
                height,
                side="right",
                priority=90,
            )
        )
        if base_height > 1e-6:
            dimensions.append(
                factory.vertical_dimension(
                    x_scene,
                    0.0,
                    base_height,
                    base_height,
                    side="left",
                    priority=60,
                )
            )
        if parameters is not None and len(verticals) > 1:
            first_scene = factory.project(primary.start)
            second_scene = factory.project(verticals[1].start)
            dimensions.append(
                factory.between_scene(
                    first_scene,
                    second_scene,
                    parameters.spacing_m,
                    side="below",
                    priority=75,
                )
            )
    else:
        first_scene = factory.project(verticals[0].start)
        last_scene = factory.project(verticals[-1].start)
        if parameters is not None:
            dimensions.append(
                factory.between_scene(
                    first_scene,
                    last_scene,
                    parameters.spacing_m * max(len(verticals) - 1, 1),
                    side="below",
                    priority=90,
                )
            )
            if len(verticals) > 1:
                dimensions.append(
                    factory.between_scene(
                        first_scene,
                        factory.project(verticals[1].start),
                        parameters.spacing_m,
                        side="below",
                        priority=80,
                    )
                )
    if parameters is not None:
        notes.append(
            translator.t(
                "phased_vertical.phase_note",
                phase=f"{parameters.phase_step_deg:.1f}",
                taper=f"{parameters.amplitude_taper * 100.0:.0f}",
            )
        )


def _add_hexbeam_dimensions(
    model: AntennaModel,
    parameters: HexbeamParameters | None,
    factory: _Factory,
    dimensions: list[Dimension],
    angular_dimensions: list[AngularDimension],
    insets: list[SceneInset],
    notes: list[str],
    translator: Translator,
) -> None:
    if parameters is None:
        return
    driver_left_inner = next(
        (wire for wire in model.wires if wire.id == "hexbeam-driver-left-inner"),
        None,
    )
    driver_left = next(
        (wire for wire in model.wires if wire.id == "hexbeam-driver-left-tip"),
        None,
    )
    driver_right = next(
        (wire for wire in model.wires if wire.id == "hexbeam-driver-right-tip"),
        None,
    )
    reflector_left_inner = next(
        (wire for wire in model.wires if wire.id == "hexbeam-reflector-left-inner"),
        None,
    )
    reflector_left = next(
        (wire for wire in model.wires if wire.id == "hexbeam-reflector-left-tip"),
        None,
    )
    reflector_right = next(
        (wire for wire in model.wires if wire.id == "hexbeam-reflector-right-tip"),
        None,
    )
    span_left = driver_left
    span_right = driver_right
    if (
        reflector_left is not None
        and reflector_right is not None
        and parameters.reflector_tip_half_span_m > parameters.driver_tip_half_span_m
    ):
        span_left = reflector_left
        span_right = reflector_right
    if span_left is not None and span_right is not None:
        dimensions.append(
            factory.between_scene(
                factory.project(span_left.end),
                factory.project(span_right.end),
                parameters.overall_span_m,
                side="left",
                priority=95,
                label=translator.t("geometry.span"),
            )
        )
    if driver_left is not None and reflector_left is not None and not factory.projection.vertical:
        clear_gap = driver_left.end.distance_to(reflector_left.end)
        gap_start = driver_left.end
        gap_end = reflector_left.end
        if driver_right is not None and reflector_right is not None:
            right_gap = driver_right.end.distance_to(reflector_right.end)
            if right_gap < clear_gap:
                clear_gap = right_gap
                gap_start = driver_right.end
                gap_end = reflector_right.end
        dimensions.append(
            factory.between_scene(
                factory.project(gap_start),
                factory.project(gap_end),
                clear_gap,
                side="right",
                priority=95,
                label=translator.t("geometry.gap"),
            )
        )
        notes.append(
            translator.t(
                "hexbeam.tip_gap_note",
                published=_format_length(
                    parameters.tip_gap_m,
                    translator,
                    factory.unit_system,
                ),
                clear=_format_length(clear_gap, translator, factory.unit_system),
            )
        )
    if not factory.projection.vertical:
        if reflector_left_inner is not None:
            radius_m = reflector_left_inner.start.distance_to(reflector_left_inner.end)
            dimensions.append(
                factory.dimension(
                    reflector_left_inner.start,
                    reflector_left_inner.end,
                    radius_m,
                    side="left",
                    priority=85,
                    label=translator.t("hexbeam.turning_radius"),
                )
            )
        if driver_left_inner is not None and driver_left is not None:
            feed_wire = next(
                (wire for wire in model.wires if wire.id == "hexbeam-feed"),
                None,
            )
            if feed_wire is not None:
                center = _wire_point(feed_wire, 0.5)
                forward = (
                    feed_wire.end if feed_wire.end.x_m >= feed_wire.start.x_m else feed_wire.start
                )
                apex = driver_left_inner.end
                spreader_angle = _included_angle(center, forward, apex)
                bend_angle = _included_angle(apex, driver_left_inner.start, driver_left.end)
                angular_dimensions.append(
                    AngularDimension(
                        center=factory.project(center),
                        first=factory.project(forward),
                        second=factory.project(apex),
                        text=f"{spreader_angle:.1f}°",
                        priority=90,
                    )
                )
                notes.append(
                    translator.t(
                        "hexbeam.spreader_angle_note",
                        spreader=f"{spreader_angle:.1f}",
                        bend=f"{bend_angle:.1f}",
                    )
                )
            half_specs = (
                (driver_left_inner, "Di", "left"),
                (driver_left, "Do", "right"),
                (reflector_left_inner, "Ri", "left"),
                (reflector_left, "Ro", "right"),
            )
            half_wires = tuple(wire for wire, _label, _side in half_specs if wire is not None)
            half_dimensions: list[Dimension] = []
            for wire, label, side in half_specs:
                if wire is None:
                    continue
                half_dimensions.append(
                    factory.dimension(
                        wire.start,
                        wire.end,
                        wire.length_m,
                        side=side,
                        priority=90,
                        label=label,
                    )
                )
            if driver_left is not None and reflector_left is not None:
                inset_gap = driver_left.end.distance_to(reflector_left.end)
                half_dimensions.append(
                    factory.between_scene(
                        factory.project(driver_left.end),
                        factory.project(reflector_left.end),
                        inset_gap,
                        side="above",
                        priority=100,
                        label=translator.t("geometry.gap"),
                    )
                )
            if len(half_wires) >= 2:
                insets.append(
                    SceneInset(
                        label=translator.t("geometry.detail_half"),
                        polylines=tuple(
                            ScenePolyline(
                                (factory.project(wire.start), factory.project(wire.end)),
                                role="wire",
                            )
                            for wire in half_wires
                        ),
                        dimensions=tuple(half_dimensions),
                    )
                )
    if factory.projection.vertical:
        dimensions.append(
            factory.vertical_dimension(
                factory.project(driver_left.start).x_m if driver_left else 0.0,
                0.0,
                parameters.height_m,
                parameters.height_m,
                side="left",
                priority=60,
                label=translator.t("field.height"),
            )
        )
    notes.append(
        translator.t(
            "hexbeam.geometry_note",
            radius=_format_length(parameters.turning_radius_m, translator, factory.unit_system),
        )
    )


def _add_trap_yagi_dimensions(
    model: AntennaModel,
    parameters: TrapYagiParameters | None,
    factory: _Factory,
    dimensions: list[Dimension],
    insets: list[SceneInset],
    notes: list[str],
    translator: Translator,
) -> None:
    if parameters is None:
        return
    elements = tuple(wire for wire in model.wires if wire.id.startswith("trap-yagi-element-"))
    if len(elements) < 2:
        return
    driven = elements[1]
    roles = (
        translator.t("geometry.reflector_element"),
        translator.t("geometry.driven_element"),
        translator.t("geometry.director_element"),
    )
    for index, (element_wire, length_m) in enumerate(
        zip(elements, parameters.element_lengths_m, strict=True)
    ):
        if index == 0:
            side = "left"
        elif index == len(elements) - 1:
            side = "right"
        else:
            side = "above"
        dimensions.append(
            factory.dimension(
                element_wire.start,
                element_wire.end,
                length_m,
                side=side,
                priority=90,
                label=roles[index] if index < len(roles) else None,
            )
        )
    for index, spacing_m in enumerate(parameters.element_spacings_m):
        if index + 1 >= len(elements):
            break
        first_center = _wire_point(elements[index], 0.5)
        second_center = _wire_point(elements[index + 1], 0.5)
        label = (
            translator.t("geometry.reflector_spacing")
            if index == 0
            else translator.t("geometry.director_spacing")
        )
        dimensions.append(
            factory.dimension(
                first_center,
                second_center,
                spacing_m,
                side="below",
                priority=80,
                label=label,
            )
        )
    if factory.projection.vertical:
        dimensions.append(
            factory.vertical_dimension(
                factory.project(driven.start).x_m,
                0.0,
                parameters.height_m,
                parameters.height_m,
                side="left",
                priority=60,
                label=translator.t("field.height"),
            )
        )
    else:
        shapes = [factory.project(point) for wire in elements for point in (wire.start, wire.end)]
        boom_y = min(point.y_m for point in shapes) - 0.1
        dimensions.append(
            factory.horizontal_dimension(
                boom_y,
                factory.project(elements[0].start).x_m,
                factory.project(elements[-1].start).x_m,
                parameters.boom_length_m,
                side="below",
                priority=55,
                label=translator.t("geometry.boom_length"),
            )
        )
        trap_loads = tuple(load for load in model.loads if load.wire_id == driven.id)
        if trap_loads:
            center = _wire_point(driven, 0.5)
            markers: list[SceneMarker] = []
            trap_dimensions: list[Dimension] = []
            for load in trap_loads:
                ratio = min(max(load.offset_m / driven.length_m, 0.0), 1.0)
                point = _wire_point(driven, ratio)
                markers.append(
                    SceneMarker(
                        point=factory.project(point),
                        kind="load",
                        label="T",
                        priority=80,
                    )
                )
            nearest_load = min(
                trap_loads,
                key=lambda load: abs(load.offset_m - driven.length_m / 2.0),
            )
            ratio = min(max(nearest_load.offset_m / driven.length_m, 0.0), 1.0)
            trap_point = _wire_point(driven, ratio)
            trap_dimensions.append(
                factory.dimension(
                    center,
                    trap_point,
                    abs(nearest_load.offset_m - driven.length_m / 2.0),
                    side="below",
                    priority=90,
                    label=translator.t("geometry.trap_inset_label"),
                )
            )
            insets.append(
                SceneInset(
                    label=translator.t("geometry.detail_trap"),
                    polylines=(
                        ScenePolyline(
                            (factory.project(driven.start), factory.project(driven.end)),
                            role="wire",
                        ),
                    ),
                    markers=tuple(markers),
                    dimensions=tuple(trap_dimensions),
                )
            )
    notes.append(
        translator.t(
            "trap_yagi.geometry_note",
            inset=_format_length(parameters.trap_inset_m, translator, factory.unit_system),
            trap=f"{parameters.trap_frequency_hz / 1_000_000.0:.3f}",
        )
    )


def _add_discone_dimensions(
    model: AntennaModel,
    parameters: DisconeParameters | None,
    factory: _Factory,
    dimensions: list[Dimension],
    angular_dimensions: list[AngularDimension],
    notes: list[str],
    translator: Translator,
) -> None:
    if parameters is None:
        return
    cone_wires = tuple(wire for wire in model.wires if wire.id.startswith("discone-cone-"))
    cone = cone_wires[0] if cone_wires else None
    disc = next(
        (wire for wire in model.wires if wire.id.startswith("discone-disc-")),
        None,
    )
    if cone is not None:
        if factory.projection.vertical:
            cone_x = factory.project(cone.start).x_m
            dimensions.append(
                factory.vertical_dimension(
                    cone_x,
                    parameters.base_height_m,
                    parameters.apex_height_m,
                    parameters.cone_height_m,
                    side="right",
                    priority=90,
                )
            )
            dimensions.append(
                factory.vertical_dimension(
                    cone_x,
                    0.0,
                    parameters.base_height_m,
                    parameters.base_height_m,
                    side="left",
                    priority=60,
                )
            )
        else:
            dimensions.append(
                factory.dimension(
                    cone.start,
                    cone.end,
                    parameters.cone_radius_m,
                    side="below",
                    priority=85,
                )
            )
    if disc is not None and not factory.projection.vertical:
        dimensions.append(
            factory.dimension(
                disc.start,
                disc.end,
                parameters.disc_radius_m,
                side="above",
                priority=80,
            )
        )
    if factory.projection.vertical and len(cone_wires) >= 2 and parameters.wire_count % 2 == 0:
        apex = cone_wires[0].start
        first = cone_wires[0].end
        opposite = cone_wires[parameters.wire_count // 2]
        second = opposite.end
        angle = _included_angle(apex, first, second)
        angular_dimensions.append(
            AngularDimension(
                center=factory.project(apex),
                first=factory.project(first),
                second=factory.project(second),
                text=f"{angle:.1f}°",
                priority=90,
            )
        )
    half_angle = math.degrees(math.atan2(parameters.cone_radius_m, parameters.cone_height_m))
    step = 360.0 / parameters.wire_count
    notes.append(
        translator.t(
            "discone.angle_note",
            half=f"{half_angle:.1f}",
            count=parameters.wire_count,
            step=f"{step:.1f}",
        )
    )
    notes.append(translator.t("discone.geometry_note"))


def _add_quad_beam_dimensions(
    model: AntennaModel,
    parameters: QuadBeamParameters | None,
    factory: _Factory,
    dimensions: list[Dimension],
    insets: list[SceneInset],
    notes: list[str],
    translator: Translator,
) -> None:
    if parameters is None:
        return
    driven_wire = next(
        (wire for wire in model.wires if wire.id == parameters.driven_wire_id),
        None,
    )
    if driven_wire is None:
        return
    driven_x = factory.project(driven_wire.start).x_m
    if factory.projection.vertical:
        dimensions.append(
            factory.vertical_dimension(
                driven_x,
                parameters.height_m,
                parameters.height_m + parameters.loop_side_m,
                parameters.loop_side_m,
                side="right",
                priority=90,
            )
        )
        if parameters.height_m > 1e-6:
            dimensions.append(
                factory.vertical_dimension(
                    driven_x,
                    0.0,
                    parameters.height_m,
                    parameters.height_m,
                    side="left",
                    priority=60,
                )
            )
    reflector_wire = next(
        (wire for wire in model.wires if wire.id.startswith("quad-beam-element-0-")),
        None,
    )
    if reflector_wire is not None:
        reflector_x = factory.project(reflector_wire.start).x_m
        dimensions.append(
            factory.horizontal_dimension(
                factory.y_for_z(0.0) + 0.1,
                reflector_x,
                driven_x,
                parameters.reflector_spacing_m,
                side="below",
                priority=85,
                label=translator.t("geometry.reflector_spacing"),
            )
        )
        dimensions.append(
            factory.horizontal_dimension(
                factory.y_for_z(0.0) + 0.2,
                reflector_x,
                driven_x + parameters.boom_length_m - parameters.reflector_spacing_m,
                parameters.boom_length_m,
                side="below",
                priority=55,
                label=translator.t("geometry.boom_length"),
            )
        )
        if parameters.element_count == 3:
            driven_center = _wire_point(
                model.wire_by_id(f"quad-beam-element-{DRIVEN_ELEMENT_INDEX}-side-0"),
                0.5,
            )
            director_center = _wire_point(
                model.wire_by_id(f"quad-beam-element-{DRIVEN_ELEMENT_INDEX + 1}-side-0"),
                0.5,
            )
            dimensions.append(
                factory.dimension(
                    driven_center,
                    director_center,
                    parameters.director_spacing_m,
                    side="below",
                    priority=80,
                    label=translator.t("geometry.director_spacing"),
                )
            )
    if not factory.projection.vertical:
        loop_labels = (
            translator.t("geometry.reflector_element"),
            translator.t("geometry.driven_element"),
            translator.t("geometry.director_element"),
        )
        for index, side_m in enumerate(parameters.element_sides_m):
            side_wire = model.wire_by_id(f"quad-beam-element-{index}-side-0")
            if index == 0 or index == len(parameters.element_sides_m) - 1:
                side = "right"
            else:
                side = "below"
            dimensions.append(
                factory.dimension(
                    side_wire.start,
                    side_wire.end,
                    side_m,
                    side=side,
                    priority=95 if index == DRIVEN_ELEMENT_INDEX else 90,
                    label=loop_labels[index] if index < len(loop_labels) else None,
                )
            )
        driven_sides = tuple(
            model.wire_by_id(f"quad-beam-element-{DRIVEN_ELEMENT_INDEX}-side-{side_index}")
            for side_index in range(4)
        )
        center_y = sum(point.y_m for wire in driven_sides for point in (wire.start, wire.end)) / 8.0
        center_z = sum(point.z_m for wire in driven_sides for point in (wire.start, wire.end)) / 8.0

        def inset_point(point: Point3D) -> ScenePoint:
            return ScenePoint(point.y_m - center_y, point.z_m - center_z)

        bottom = driven_sides[0]
        right_side = driven_sides[1]
        insets.append(
            SceneInset(
                label=translator.t(
                    "geometry.detail_loop",
                    side=_format_length(
                        parameters.loop_side_m,
                        translator,
                        factory.unit_system,
                    ),
                ),
                polylines=tuple(
                    ScenePolyline(
                        (inset_point(wire.start), inset_point(wire.end)),
                        role="wire",
                    )
                    for wire in driven_sides
                ),
                dimensions=(
                    Dimension(
                        start=inset_point(bottom.start),
                        end=inset_point(bottom.end),
                        text=_format_length(
                            parameters.loop_side_m,
                            translator,
                            factory.unit_system,
                        ),
                        side="below",
                        priority=95,
                        label=translator.t("geometry.driven_loop"),
                    ),
                    Dimension(
                        start=inset_point(right_side.start),
                        end=inset_point(right_side.end),
                        text=_format_length(
                            parameters.loop_side_m,
                            translator,
                            factory.unit_system,
                        ),
                        side="right",
                        priority=95,
                        label=translator.t("biquad.loop_side"),
                    ),
                ),
            )
        )
    notes.append(translator.t("quad_beam.geometry_note"))


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


def _yagi_element_wire(
    model: AntennaModel,
    parameters: YagiParameters,
    index: int,
) -> Wire | None:
    wire_id = f"element-{index + 1}"
    if parameters.is_tapered:
        wire_id = f"{wire_id}-center"
    elif parameters.driven_folded and index == parameters.driven_index:
        wire_id = f"{wire_id}-a"
    return _array_wire(model, wire_id, index)


def _yagi_element_span(
    model: AntennaModel,
    parameters: YagiParameters,
    index: int,
) -> tuple[Point3D, Point3D] | None:
    if index == parameters.driven_index and parameters.match_type is YagiMatchType.BETA_HAIRPIN:
        left = next(
            (wire for wire in model.wires if wire.id == f"element-{index + 1}-left"),
            None,
        )
        right = next(
            (wire for wire in model.wires if wire.id == f"element-{index + 1}-right"),
            None,
        )
        if left is None or right is None:
            return None
        return left.start, right.end
    if parameters.is_tapered:
        left = next(
            (wire for wire in model.wires if wire.id == f"element-{index + 1}-tip-left"),
            None,
        )
        right = next(
            (wire for wire in model.wires if wire.id == f"element-{index + 1}-tip-right"),
            None,
        )
        if left is None or right is None:
            return None
        return left.start, right.end
    wire = _yagi_element_wire(model, parameters, index)
    if wire is None:
        return None
    return wire.start, wire.end


def _yagi_element_center(
    model: AntennaModel,
    parameters: YagiParameters,
    index: int,
) -> Point3D | None:
    if index == parameters.driven_index and parameters.match_type is YagiMatchType.BETA_HAIRPIN:
        left = next(
            (wire for wire in model.wires if wire.id == f"element-{index + 1}-left"),
            None,
        )
        right = next(
            (wire for wire in model.wires if wire.id == f"element-{index + 1}-right"),
            None,
        )
        if left is None or right is None:
            return None
        left_midpoint = _wire_point(left, 0.5)
        right_midpoint = _wire_point(right, 0.5)
        return Point3D(
            x_m=(left_midpoint.x_m + right_midpoint.x_m) / 2.0,
            y_m=(left_midpoint.y_m + right_midpoint.y_m) / 2.0,
            z_m=(left_midpoint.z_m + right_midpoint.z_m) / 2.0,
        )
    if index == parameters.driven_index and parameters.driven_folded:
        first = _yagi_element_wire(model, parameters, index)
        second = _array_wire(model, f"element-{index + 1}-b", index)
        if first is None or second is None:
            return None
        first_midpoint = _wire_point(first, 0.5)
        second_midpoint = _wire_point(second, 0.5)
        return Point3D(
            x_m=(first_midpoint.x_m + second_midpoint.x_m) / 2.0,
            y_m=(first_midpoint.y_m + second_midpoint.y_m) / 2.0,
            z_m=(first_midpoint.z_m + second_midpoint.z_m) / 2.0,
        )
    wire = _yagi_element_wire(model, parameters, index)
    return _wire_point(wire, 0.5) if wire is not None else None


def _add_hairpin_dimensions(
    model: AntennaModel,
    parameters: YagiParameters,
    factory: _Factory,
    dimensions: list[Dimension],
) -> None:
    prefix = f"element-{parameters.driven_index + 1}"
    feed = next((wire for wire in model.wires if wire.id == f"{prefix}-feed"), None)
    hairpin = next((wire for wire in model.wires if wire.id == f"{prefix}-hairpin-a"), None)
    if feed is not None:
        dimensions.append(
            factory.dimension(
                feed.start,
                feed.end,
                parameters.match_spacing_m,
                side="above",
                priority=55,
            )
        )
    if hairpin is not None:
        dimensions.append(
            factory.dimension(
                hairpin.start,
                hairpin.end,
                parameters.match_length_m,
                side="below",
                priority=50,
            )
        )


def _moxon_tip_inset(
    model: AntennaModel,
    parameters: MoxonParameters,
    factory: _Factory,
    translator: Translator,
) -> SceneInset | None:
    reflector_tip = next(
        (wire for wire in model.wires if wire.id == "reflector-tip-1"),
        None,
    )
    driven_tip = next(
        (wire for wire in model.wires if wire.id == "driven-tip-1"),
        None,
    )
    if reflector_tip is None or driven_tip is None:
        return None
    dimensions = [
        factory.dimension(
            reflector_tip.start,
            reflector_tip.end,
            parameters.reflector_tip_m,
            side="above",
            priority=100,
            label="R tip",
        ),
        factory.dimension(
            driven_tip.start,
            driven_tip.end,
            parameters.driven_tip_m,
            side="above",
            priority=95,
            label="D tip",
        ),
        factory.between_scene(
            factory.project(reflector_tip.end),
            factory.project(driven_tip.end),
            parameters.gap_m,
            side="below",
            priority=95,
            label=translator.t("geometry.gap"),
        ),
    ]
    polylines = tuple(
        ScenePolyline(
            (factory.project(wire.start), factory.project(wire.end)),
            role="wire",
        )
        for wire in (reflector_tip, driven_tip)
    )
    return SceneInset(
        label=translator.t("geometry.detail_tip"),
        polylines=polylines,
        dimensions=tuple(dimensions),
    )


def _add_array_dimensions(
    model: AntennaModel,
    parameters: object | None,
    factory: _Factory,
    dimensions: list[Dimension],
    insets: list[SceneInset],
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
                first = _yagi_element_wire(model, parameters, 0)
                last = _yagi_element_wire(model, parameters, len(parameters.elements) - 1)
                if first is not None and last is not None:
                    dimensions.append(
                        factory.dimension(
                            _wire_point(first, 0.5),
                            _wire_point(last, 0.5),
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
            for index, element in enumerate(parameters.elements):
                span = _yagi_element_span(model, parameters, index)
                if span is None:
                    continue
                if index == 0:
                    side = "left"
                elif index == len(parameters.elements) - 1:
                    side = "right"
                else:
                    side = "above" if index % 2 else "below"
                dimensions.append(
                    factory.dimension(
                        span[0],
                        span[1],
                        element.length_m,
                        side=side,
                        priority=90,
                        label=f"E{index + 1}",
                    )
                )
            if len(parameters.elements) >= 2:
                positions = [element.position_m for element in parameters.elements]
                for index in range(len(parameters.elements) - 1):
                    first_center = _yagi_element_center(model, parameters, index)
                    second_center = _yagi_element_center(model, parameters, index + 1)
                    if first_center is None or second_center is None:
                        continue
                    dimensions.append(
                        factory.dimension(
                            first_center,
                            second_center,
                            abs(positions[index + 1] - positions[index]),
                            side="below",
                            priority=80,
                            label=f"{index + 1}-{index + 2}",
                        )
                    )
                first_center = _yagi_element_center(model, parameters, 0)
                last_center = _yagi_element_center(
                    model,
                    parameters,
                    len(parameters.elements) - 1,
                )
                if first_center is not None and last_center is not None:
                    dimensions.append(
                        factory.dimension(
                            first_center,
                            last_center,
                            max(positions) - min(positions),
                            side="below",
                            priority=55,
                            label=translator.t("geometry.boom_length"),
                        )
                    )
            if parameters.is_tapered:
                notes.append(
                    translator.t(
                        "yagi.taper_note",
                        length=_format_length(
                            parameters.taper_tip_length_m,
                            translator,
                            factory.unit_system,
                        ),
                        radius=_format_length(
                            parameters.taper_tip_radius_m,
                            translator,
                            factory.unit_system,
                        ),
                    )
                )
            if parameters.driven_folded:
                driven_a = _yagi_element_wire(model, parameters, parameters.driven_index)
                driven_b = _array_wire(
                    model,
                    f"element-{parameters.driven_index + 1}-b",
                    parameters.driven_index,
                )
                if driven_a is not None and driven_b is not None:
                    dimensions.append(
                        factory.dimension(
                            _wire_point(driven_a, 0.5),
                            _wire_point(driven_b, 0.5),
                            parameters.driven_fold_spacing_m,
                            side="above",
                            priority=55,
                        )
                    )
            if parameters.match_type is YagiMatchType.BETA_HAIRPIN:
                _add_hairpin_dimensions(model, parameters, factory, dimensions)
        elif isinstance(parameters, MoxonParameters):
            reflector = next(
                (wire for wire in model.wires if wire.id == "reflector"),
                None,
            )
            driven = next((wire for wire in model.wires if wire.id == "driven"), None)
            if reflector is not None:
                dimensions.append(
                    factory.dimension(
                        reflector.start,
                        reflector.end,
                        parameters.width_m,
                        side="left",
                        priority=90,
                        label=translator.t("geometry.width"),
                    )
                )
            if reflector is not None and driven is not None:
                dimensions.append(
                    factory.dimension(
                        _wire_point(reflector, 0.5),
                        _wire_point(driven, 0.5),
                        parameters.depth_m,
                        side="below",
                        priority=85,
                        label=translator.t("geometry.depth"),
                    )
                )
            inset = _moxon_tip_inset(model, parameters, factory, translator)
            if inset is not None:
                insets.append(inset)
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
            span = _yagi_element_span(model, parameters, index)
            if span is None:
                continue
            dimensions.append(
                factory.dimension(
                    span[0],
                    span[1],
                    yagi_element.length_m,
                    side="right" if index % 2 == 0 else "left",
                    priority=70
                    if index in {0, parameters.driven_index, len(parameters.elements) - 1}
                    else 35,
                )
            )
        if len(parameters.elements) >= 2:
            positions = [element.position_m for element in parameters.elements]
            first_center = _yagi_element_center(model, parameters, 0)
            last_center = _yagi_element_center(
                model,
                parameters,
                len(parameters.elements) - 1,
            )
            if first_center is not None and last_center is not None:
                dimensions.append(
                    factory.dimension(
                        first_center,
                        last_center,
                        max(positions) - min(positions),
                        side="above",
                        priority=65,
                    )
                )
        if parameters.driven_folded:
            driven_a = _yagi_element_wire(model, parameters, parameters.driven_index)
            driven_b = _array_wire(
                model,
                f"element-{parameters.driven_index + 1}-b",
                parameters.driven_index,
            )
            if driven_a is not None and driven_b is not None:
                dimensions.append(
                    factory.dimension(
                        _wire_point(driven_a, 0.5),
                        _wire_point(driven_b, 0.5),
                        parameters.driven_fold_spacing_m,
                        side="above",
                        priority=55,
                    )
                )
        if parameters.match_type is YagiMatchType.BETA_HAIRPIN:
            _add_hairpin_dimensions(model, parameters, factory, dimensions)
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
                    priority=90,
                    label=translator.t("geometry.width"),
                )
            )
        if reflector is not None and driven is not None:
            dimensions.append(
                factory.dimension(
                    _wire_point(reflector, 0.5),
                    _wire_point(driven, 0.5),
                    parameters.depth_m,
                    side="below",
                    priority=80,
                    label=translator.t("geometry.depth"),
                )
            )
        inset = _moxon_tip_inset(model, parameters, factory, translator)
        if inset is not None:
            insets.append(inset)

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
    translator: Translator,
) -> None:
    min_z, max_z = _model_z_extents(model)
    if factory.projection.vertical:
        if isinstance(parameters, FanDipoleParameters):
            for leg_index in range(0, len(model.wires) - 1, 2):
                leg = model.wires[leg_index]
                dimensions.append(
                    factory.dimension(
                        leg.start,
                        leg.end,
                        leg.length_m,
                        side="left" if leg_index % 4 == 0 else "right",
                        priority=85,
                        label=f"E{leg_index // 2 + 1} leg",
                    )
                )
        else:
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
        if isinstance(parameters, VerticalParameters):
            radiator = next(
                (wire for wire in model.wires if wire.id == "radiator"),
                model.wires[0],
            )
            if parameters.loading_coil_enabled:
                coil = next(
                    (load for load in model.loads if load.wire_id == radiator.id),
                    None,
                )
                if coil is not None and coil.offset_m > 1e-6:
                    coil_point = _wire_point(
                        radiator,
                        min(coil.offset_m / radiator.length_m, 1.0),
                    )
                    base_z = min(radiator.start.z_m, radiator.end.z_m)
                    dimensions.append(
                        factory.vertical_dimension(
                            factory.project(radiator.start).x_m,
                            base_z,
                            coil_point.z_m,
                            abs(coil_point.z_m - base_z),
                            side="left",
                            priority=85,
                            label=translator.t("vertical.loading_coil_offset"),
                        )
                    )
            if parameters.top_hat_enabled:
                top_hat = next(
                    (wire for wire in model.wires if wire.id.startswith("top-hat-")),
                    None,
                )
                if top_hat is not None:
                    dimensions.append(
                        factory.dimension(
                            top_hat.start,
                            top_hat.end,
                            parameters.top_hat_radius_m,
                            side="right",
                            priority=85,
                            label=translator.t("vertical.top_hat_radius"),
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
            base_height_m = parameters.base_height_m
            feed_offset_m = parameters.feed_offset_m
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
            base_height_m = min_z
            feed_wire = model.feed_wire
            feed_ratio = min(max(model.feed.offset_m / feed_wire.length_m, 0.0), 1.0)
            feed_point = _wire_point(feed_wire, feed_ratio)
            feed_offset_m = abs(feed_point.z_m - min(feed_wire.start.z_m, feed_wire.end.z_m))
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
            feed=_format_length(feed_offset_m, translator, unit_system),
            base=_format_length(base_height_m, translator, unit_system),
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
    elif isinstance(parameters, ScvParameters) or antenna_type in {
        ANTENNA_TYPE_HALF_SQUARE,
        ANTENNA_TYPE_BOBTAIL_CURTAIN,
    }:
        if isinstance(parameters, ScvParameters):
            horizontal_length = parameters.horizontal_length_m
            vertical_height = parameters.vertical_height_m
            vertical_count = parameters.vertical_count
        else:
            verticals = tuple(
                wire
                for wire in model.wires
                if math.hypot(
                    wire.end.x_m - wire.start.x_m,
                    wire.end.y_m - wire.start.y_m,
                )
                <= 1e-9
            )
            vertical_count = len(verticals)
            bases = [
                (point.x_m, point.y_m)
                for wire in verticals
                for point in (wire.start, wire.end)
                if math.isclose(point.z_m, min_z, abs_tol=1e-6)
            ]
            horizontal_length = max(
                (
                    math.hypot(first[0] - second[0], first[1] - second[1])
                    for first in bases
                    for second in bases
                ),
                default=0.0,
            )
            vertical_height = max_z - min_z
        parts.extend(
            [
                f"{translator.t('scv.horizontal_length').lower()} "
                f"{_format_length(horizontal_length, translator, unit_system)}",
                f"{translator.t('scv.vertical_height').lower()} "
                f"{_format_length(vertical_height, translator, unit_system)}",
                f"{translator.t('scv.vertical_elements').lower()} {vertical_count}",
                translator.t("scv.feed_top"),
            ]
        )
    elif isinstance(parameters, BiquadParameters) or antenna_type in {
        ANTENNA_TYPE_BIQUAD,
        ANTENNA_TYPE_DOUBLE_BIQUAD,
    }:
        if isinstance(parameters, BiquadParameters):
            loop_count = parameters.loop_count
            side = parameters.loop_side_m
            total_height = parameters.total_height_m
            base_height = parameters.base_height_m
            reflector_spacing = parameters.reflector_spacing_m
            reflector_enabled = parameters.reflector_enabled
        else:
            horizontal_heights = {
                round(wire.start.z_m, 6)
                for wire in model.wires
                if math.isclose(wire.start.z_m, wire.end.z_m, abs_tol=1e-9)
                and math.hypot(
                    wire.end.x_m - wire.start.x_m,
                    wire.end.y_m - wire.start.y_m,
                )
                > 1e-9
            }
            loop_count = max(0, len(horizontal_heights) - 1)
            side = max(
                math.hypot(
                    wire.end.x_m - wire.start.x_m,
                    wire.end.y_m - wire.start.y_m,
                )
                for wire in model.wires
            )
            total_height = max_z - min_z
            base_height = min_z
            reflector_spacing = 0.0
            reflector_enabled = False
        parts.extend(
            [
                f"{translator.t('biquad.loops').lower()} {loop_count}",
                f"{translator.t('biquad.loop_side').lower()} "
                f"{_format_length(side, translator, unit_system)}",
                f"{translator.t('biquad.height').lower()} "
                f"{_format_length(total_height, translator, unit_system)}",
                f"{translator.t('field.base_height').lower()} "
                f"{_format_length(base_height, translator, unit_system)}",
                f"{translator.t('biquad.reflector').lower()} "
                + (
                    _format_length(reflector_spacing, translator, unit_system)
                    if reflector_enabled
                    else translator.t("biquad.reflector_off")
                ),
            ]
        )
    elif isinstance(parameters, BeverageParameters) or antenna_type == ANTENNA_TYPE_BEVERAGE:
        if isinstance(parameters, BeverageParameters):
            length = parameters.length_m
            height = parameters.height_m
            termination = (
                f"{parameters.termination_resistance_ohm:.1f} Ω"
                if parameters.termination_enabled
                else translator.t("beverage.termination_off")
            )
        else:
            length = max(
                math.hypot(
                    wire.end.x_m - wire.start.x_m,
                    wire.end.y_m - wire.start.y_m,
                )
                for wire in model.wires
            )
            height = max_z
            termination = translator.t("beverage.termination_off")
        parts.extend(
            [
                f"{translator.t('field.length').lower()} "
                f"{_format_length(length, translator, unit_system)}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(height, translator, unit_system)}",
                f"{translator.t('beverage.termination').lower()} {termination}",
            ]
        )
    elif (
        isinstance(parameters, LoadedDipoleParameters) or antenna_type == ANTENNA_TYPE_LOADED_DIPOLE
    ):
        if isinstance(parameters, LoadedDipoleParameters):
            active_length = parameters.active_length_m
            total_length = parameters.total_length_m
            offset = parameters.link_offset_m
            if parameters.link_open:
                state = translator.t("loaded_dipole.state_linked")
            elif parameters.coil_active:
                q_value = parameters.coil_q
                state = translator.t(
                    "loaded_dipole.state_loaded",
                    inductance=parameters.loading_coil_inductance_h * 1e6,
                    q="—" if q_value is None else f"{q_value:.1f}",
                )
            else:
                state = translator.t("loaded_dipole.state_plain")
        else:
            active_length = max(
                math.hypot(
                    wire.end.x_m - wire.start.x_m,
                    wire.end.y_m - wire.start.y_m,
                    wire.end.z_m - wire.start.z_m,
                )
                for wire in model.wires
            )
            total_length = active_length
            offset = 0.0
            state = translator.t("loaded_dipole.state_plain")
        parts.extend(
            [
                f"{translator.t('loaded_dipole.active_length').lower()} "
                f"{_format_length(active_length, translator, unit_system)}",
                f"{translator.t('loaded_dipole.full_length').lower()} "
                f"{_format_length(total_length, translator, unit_system)}",
                f"{translator.t('loaded_dipole.link_offset').lower()} "
                f"{_format_length(offset, translator, unit_system)}",
                f"{translator.t('loaded_dipole.state').lower()} {state}",
            ]
        )
    elif (
        isinstance(parameters, PhasedVerticalParameters)
        or antenna_type == ANTENNA_TYPE_PHASED_VERTICAL
    ):
        verticals = tuple(wire for wire in model.wires if wire.id.startswith("phased-vertical-"))
        if isinstance(parameters, PhasedVerticalParameters):
            element_count = parameters.element_count
            spacing = parameters.spacing_m
            height = parameters.height_m
            base_height = parameters.base_height_m
            phase = f"{parameters.phase_step_deg:.1f}°"
            taper = f"{parameters.amplitude_taper * 100.0:.0f}%"
            radial_count = parameters.radial_count
        else:
            element_count = len(verticals)
            spacing = 0.0
            height = max_z - min_z
            base_height = min_z
            phase = "—"
            taper = "—"
            radial_count = 0
        parts.extend(
            [
                f"{translator.t('phased_vertical.element_count').lower()} {element_count}",
                f"{translator.t('phased_vertical.spacing').lower()} "
                f"{_format_length(spacing, translator, unit_system)}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(height, translator, unit_system)}",
                f"{translator.t('field.base_height').lower()} "
                f"{_format_length(base_height, translator, unit_system)}",
                f"{translator.t('phased_vertical.phase_step').lower()} {phase}",
                f"{translator.t('phased_vertical.amplitude_taper').lower()} {taper}",
                f"{translator.t('vertical.radial_count').lower()} {radial_count}",
            ]
        )
    elif isinstance(parameters, HexbeamParameters) or antenna_type == ANTENNA_TYPE_HEXBEAM:
        if isinstance(parameters, HexbeamParameters):
            driver_half = parameters.driver_half_length_m
            reflector_half = parameters.reflector_half_length_m
            span = parameters.overall_span_m
            radius = parameters.turning_radius_m
            gap = parameters.tip_gap_m
            height = parameters.height_m
        else:
            driver_half = max(wire.length_m for wire in model.wires)
            reflector_half = driver_half
            span = 0.0
            radius = 0.0
            gap = 0.0
            height = min_z
        parts.extend(
            [
                f"{translator.t('hexbeam.driver_half').lower()} "
                f"{_format_length(driver_half, translator, unit_system)}",
                f"{translator.t('hexbeam.reflector_half').lower()} "
                f"{_format_length(reflector_half, translator, unit_system)}",
                f"{translator.t('hexbeam.turning_radius').lower()} "
                f"{_format_length(radius, translator, unit_system)}",
                f"{translator.t('hexbeam.tip_gap').lower()} "
                f"{_format_length(gap, translator, unit_system)}",
                f"{translator.t('geometry.span').lower()} "
                f"{_format_length(span, translator, unit_system)}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(height, translator, unit_system)}",
            ]
        )
    elif isinstance(parameters, TrapYagiParameters) or antenna_type == ANTENNA_TYPE_TRAP_YAGI:
        if isinstance(parameters, TrapYagiParameters):
            count = parameters.element_count
            driven = parameters.driven_length_m
            boom = parameters.boom_length_m
            inset = parameters.trap_inset_m
            trap = f"{parameters.trap_frequency_hz / 1_000_000.0:.3f} MHz"
            height = parameters.height_m
        else:
            count = len(model.wires)
            driven = max(wire.length_m for wire in model.wires)
            xs = [point.x_m for wire in model.wires for point in (wire.start, wire.end)]
            boom = max(xs) - min(xs)
            inset = 0.0
            trap = "—"
            height = min_z
        parts.extend(
            [
                f"{translator.t('geometry.elements').lower()} {count}",
                f"{translator.t('trap_yagi.driven_length').lower()} "
                f"{_format_length(driven, translator, unit_system)}",
                f"{translator.t('geometry.boom_length').lower()} "
                f"{_format_length(boom, translator, unit_system)}",
                f"{translator.t('trap_yagi.trap_inset').lower()} "
                f"{_format_length(inset, translator, unit_system)}",
                f"{translator.t('trap_yagi.trap_frequency').lower()} {trap}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(height, translator, unit_system)}",
            ]
        )
    elif isinstance(parameters, DisconeParameters) or antenna_type == ANTENNA_TYPE_DISCONE:
        if isinstance(parameters, DisconeParameters):
            count = parameters.wire_count
            cone_height = parameters.cone_height_m
            cone_radius = parameters.cone_radius_m
            disc_radius = parameters.disc_radius_m
            base_height = parameters.base_height_m
            top_height = parameters.top_height_m
        else:
            count = 0
            cone_height = max_z - min_z
            cone_radius = max(math.hypot(wire.end.x_m, wire.end.y_m) for wire in model.wires)
            disc_radius = cone_radius
            base_height = min_z
            top_height = max_z
        parts.extend(
            [
                f"{translator.t('discone.wire_count').lower()} {count}",
                f"{translator.t('discone.cone_height').lower()} "
                f"{_format_length(cone_height, translator, unit_system)}",
                f"{translator.t('discone.cone_radius').lower()} "
                f"{_format_length(cone_radius, translator, unit_system)}",
                f"{translator.t('discone.disc_radius').lower()} "
                f"{_format_length(disc_radius, translator, unit_system)}",
                f"{translator.t('field.base_height').lower()} "
                f"{_format_length(base_height, translator, unit_system)}",
                f"{translator.t('geometry.top_height').lower()} "
                f"{_format_length(top_height, translator, unit_system)}",
            ]
        )
    elif isinstance(parameters, QuadBeamParameters) or antenna_type == ANTENNA_TYPE_QUAD_BEAM:
        if isinstance(parameters, QuadBeamParameters):
            element_count = parameters.element_count
            driven_side = parameters.loop_side_m
            reflector_side = parameters.reflector_side_m
            director_side = parameters.director_side_m
            spacing = parameters.reflector_spacing_m
            director_spacing = parameters.director_spacing_m
            height = parameters.height_m
            boom = parameters.boom_length_m
        else:
            element_count = 2
            driven_side = max(
                math.hypot(
                    wire.end.x_m - wire.start.x_m,
                    wire.end.y_m - wire.start.y_m,
                )
                for wire in model.wires
            )
            reflector_side = driven_side
            director_side = driven_side
            spacing = 0.0
            director_spacing = 0.0
            height = min_z
            boom = 0.0
        parts.extend(
            [
                f"{translator.t('quad_beam.element_count').lower()} {element_count}",
                f"{translator.t('quad_beam.loop_side').lower()} "
                f"{_format_length(driven_side, translator, unit_system)}",
                f"{translator.t('quad_beam.reflector_spacing').lower()} "
                f"{_format_length(spacing, translator, unit_system)}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(height, translator, unit_system)}",
                f"{translator.t('geometry.boom_length').lower()} "
                f"{_format_length(boom, translator, unit_system)}",
            ]
        )
        if element_count == 3:
            parts.append(
                f"{translator.t('quad_beam.director_spacing').lower()} "
                f"{_format_length(director_spacing, translator, unit_system)}"
            )
            parts.append(
                f"{translator.t('quad_beam.director_scale').lower()} "
                f"{director_side / driven_side:.3f}"
            )
        parts.append(
            f"{translator.t('quad_beam.reflector_scale').lower()} "
            f"{reflector_side / driven_side:.3f}"
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
        if isinstance(parameters, YagiParameters) and parameters.is_tapered:
            parts.append(
                f"{translator.t('yagi.taper_summary').lower()} "
                f"{_format_length(parameters.taper_tip_length_m, translator, unit_system)}"
            )
        if isinstance(parameters, YagiParameters):
            if parameters.polarization is Polarization.VERTICAL:
                parts.append(
                    f"{translator.t('field.polarization').lower()} "
                    f"{translator.t('orientation.vertical').lower()}"
                )
            if parameters.driven_folded:
                parts.append(
                    f"{translator.t('yagi.folded_driven').lower()} "
                    f"{_format_length(parameters.driven_fold_spacing_m, translator, unit_system)}"
                )
            if parameters.match_type is YagiMatchType.BETA_HAIRPIN:
                parts.append(
                    f"{translator.t('yagi.match_beta_hairpin').lower()} "
                    f"{_format_length(parameters.match_length_m, translator, unit_system)} "
                    f"· {_format_length(parameters.match_spacing_m, translator, unit_system)}"
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
        angles = ", ".join(f"{element.included_angle_deg:.1f}°" for element in parameters.elements)
        parts.extend(
            [
                f"{translator.t('geometry.elements').lower()} {len(parameters.elements)}",
                f"{translator.t('inverted_v.included_angle').lower()} {angles}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(parameters.apex_height_m, translator, unit_system)}",
            ]
        )
    elif isinstance(parameters, TransmissionLineDoubletParameters):
        parts.extend(
            [
                f"{translator.t('field.length').lower()} "
                f"{_format_length(parameters.dipole_total_length_m, translator, unit_system)}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(parameters.height_m, translator, unit_system)}",
                f"{translator.t('g5rv.line_impedance').lower()} "
                f"{parameters.line_impedance_ohm:g} Ω",
                f"{translator.t('g5rv.line_length').lower()} "
                f"{_format_length(parameters.line_length_m, translator, unit_system)}",
            ]
        )
    elif antenna_type in {ANTENNA_TYPE_G5RV, ANTENNA_TYPE_ZS6BKW}:
        longest = max(model.wires, key=lambda wire: wire.length_m, default=None)
        line = model.transmission_lines[0] if model.transmission_lines else None
        parts.extend(
            [
                f"{translator.t('field.length').lower()} "
                f"{_format_length(longest.length_m, translator, unit_system)}"
                if longest is not None
                else f"{len(model.wires)} {translator.t('geometry.wires')}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(max_z, translator, unit_system)}",
                f"{translator.t('g5rv.line_impedance').lower()} "
                f"{line.characteristic_impedance_ohm:g} Ω"
                if line is not None
                else f"{translator.t('geometry.wires')} {len(model.wires)}",
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
        if isinstance(parameters, VerticalParameters) and parameters.top_hat_enabled:
            parts.append(
                f"{translator.t('vertical.top_hat').lower()} "
                f"{parameters.top_hat_wire_count} x "
                f"{_format_length(parameters.top_hat_radius_m, translator, unit_system)}"
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
        height_value = (
            parameters.height_m if parameters.orientation.value == "horizontal" else max_z
        )
        parts.extend(
            [
                f"{translator.t('field.length').lower()} "
                f"{_format_length(parameters.total_length_m, translator, unit_system)}",
                f"{translator.t('field.height').lower()} "
                f"{_format_length(height_value, translator, unit_system)}",
            ]
        )
        if parameters.sag_m > 0.0:
            parts.append(
                f"{translator.t('field.sag').lower()} "
                f"{_format_length(parameters.sag_m, translator, unit_system)}"
            )
            notes.append(
                translator.t(
                    "geometry.sag_note",
                    segments=SAG_SEGMENTS,
                )
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
    if mode is GeometryViewMode.CONSTRUCTION:
        mode = construction_view(model, antenna_type=effective_type)
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
    markers.extend(_source_markers(model, factory))
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
    elif effective_type in {ANTENNA_TYPE_HALF_SQUARE, ANTENNA_TYPE_BOBTAIL_CURTAIN}:
        _add_scv_dimensions(
            model,
            parameters if isinstance(parameters, ScvParameters) else None,
            factory,
            dimensions,
            notes,
            translator,
        )
    elif effective_type in {ANTENNA_TYPE_BIQUAD, ANTENNA_TYPE_DOUBLE_BIQUAD}:
        _add_biquad_dimensions(
            model,
            parameters if isinstance(parameters, BiquadParameters) else None,
            factory,
            dimensions,
            notes,
            translator,
        )
    elif effective_type == ANTENNA_TYPE_BEVERAGE:
        _add_beverage_dimensions(
            model,
            parameters if isinstance(parameters, BeverageParameters) else None,
            factory,
            dimensions,
            notes,
            translator,
        )
    elif effective_type == ANTENNA_TYPE_LOADED_DIPOLE:
        _add_loaded_dipole_dimensions(
            model,
            parameters if isinstance(parameters, LoadedDipoleParameters) else None,
            factory,
            dimensions,
            notes,
            translator,
        )
    elif effective_type == ANTENNA_TYPE_PHASED_VERTICAL:
        _add_phased_vertical_dimensions(
            model,
            parameters if isinstance(parameters, PhasedVerticalParameters) else None,
            factory,
            dimensions,
            notes,
            translator,
        )
    elif effective_type == ANTENNA_TYPE_QUAD_BEAM:
        _add_quad_beam_dimensions(
            model,
            parameters if isinstance(parameters, QuadBeamParameters) else None,
            factory,
            dimensions,
            insets,
            notes,
            translator,
        )
    elif effective_type == ANTENNA_TYPE_DISCONE:
        _add_discone_dimensions(
            model,
            parameters if isinstance(parameters, DisconeParameters) else None,
            factory,
            dimensions,
            angular_dimensions,
            notes,
            translator,
        )
    elif effective_type == ANTENNA_TYPE_TRAP_YAGI:
        _add_trap_yagi_dimensions(
            model,
            parameters if isinstance(parameters, TrapYagiParameters) else None,
            factory,
            dimensions,
            insets,
            notes,
            translator,
        )
    elif effective_type == ANTENNA_TYPE_HEXBEAM:
        _add_hexbeam_dimensions(
            model,
            parameters if isinstance(parameters, HexbeamParameters) else None,
            factory,
            dimensions,
            angular_dimensions,
            insets,
            notes,
            translator,
        )
    elif effective_type in {ANTENNA_TYPE_YAGI, ANTENNA_TYPE_MOXON}:
        _add_array_dimensions(
            model,
            parameters,
            factory,
            dimensions,
            insets,
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
            _add_sloping_array_dimensions(model, parameters, factory, dimensions, translator)
    elif effective_type in {
        ANTENNA_TYPE_INVERTED_V,
        ANTENNA_TYPE_FAN_DIPOLE,
        ANTENNA_TYPE_VERTICAL,
    }:
        _add_sloping_array_dimensions(model, parameters, factory, dimensions, translator)
    elif len(model.wires) == 1:
        _add_single_wire_dimensions(model, factory, dimensions, notes, translator)
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
