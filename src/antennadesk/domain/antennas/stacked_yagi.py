# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Composed stacked-Yagi geometry with ideal multi-source excitation.

This is the DL6 first-slice composed family. It deliberately does not model
the power splitter or the phase-line hardware: each level is driven by an
ideal source with a fixed amplitude and phase progression. The layout and feed
semantics are experimental until a traceable stack reference exists.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum

from ..common.units import ensure_non_negative, ensure_positive, wavelength_m
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .feed import FeedPoint, Source
from .geometry import Point3D
from .matching_network import LNetwork, MatchingNetwork, PiNetwork, TNetwork
from .materials import ALUMINUM, ConductorMaterial
from .polarization import Polarization
from .transmission_line import TransmissionLine
from .wire import Wire
from .yagi import YagiParameters, nbs_five_element

ANTENNA_TYPE_STACKED_YAGI = "stacked_yagi"
STACKED_YAGI_LEVEL_PREFIX = "level-"
STACKED_YAGI_SPLITTER_NODE_ID = "splitter-node"
SPLITTER_NODE_LENGTH_M = 0.01
SPLITTER_NODE_RADIUS_M = 0.0005


class StackedYagiFeedMode(StrEnum):
    IDEAL = "ideal"
    PHASE_LINES = "phase_lines"
    NETWORK = "network"
    WILKINSON = "wilkinson"


@dataclass(frozen=True, slots=True)
class StackedYagiFeed:
    """Ideal splitter and phase-line specification for one stack.

    ``reference_length_m`` is the splitter-to-level-1 line. Every later level
    adds ``line_increment_m`` of the same line. The solver still receives ideal
    voltage sources: in phase-line mode the line lengths set the source phase
    at the design frequency and that phase is held fixed across a frequency
    sweep; in network mode NEC's lossless TL cards use the physical length at
    every solver frequency. The splitter is an ideal parallel junction at a
    numerical node; the reference line is included as a lossless TL to level 1.
    ``line_loss_db_per_100m`` is a matched-loss approximation applied to the
    realized gain; the primary SWR remains the lossless network input and
    mismatch-dependent line loss plus the splitter's internal isolation/return
    loss are not modeled. ``splitter_loss_db`` is the excess loss beyond the
    ideal N-way division and is applied to the realized gain. In Wilkinson
    mode the splitter and feed lines are solved by the N-port circuit solver at
    ``splitter_design_frequency_hz`` instead of the NEC TL co-simulation.
    ``level_matching_networks`` holds one optional L/Pi/T network per level.
    ``level_transformer_ratios`` holds one optional ideal impedance ratio per
    level in Wilkinson mode; an empty tuple means 1:1 everywhere. The two
    ``*_tolerance_pct`` values bound the divider component corner analysis.
    """

    mode: StackedYagiFeedMode = StackedYagiFeedMode.IDEAL
    reference_length_m: float = 0.0
    line_increment_m: float = 0.0
    velocity_factor: float = 1.0
    characteristic_impedance_ohm: float = 50.0
    splitter_loss_db: float = 0.0
    line_loss_db_per_100m: float = 0.0
    splitter_design_frequency_hz: float = 0.0
    level_matching_networks: tuple[MatchingNetwork | None, ...] = ()
    level_transformer_ratios: tuple[float, ...] = ()
    branch_impedance_tolerance_pct: float = 0.0
    isolation_resistor_tolerance_pct: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "mode", StackedYagiFeedMode(self.mode))
        ensure_non_negative(self.reference_length_m, name="reference_length_m")
        ensure_non_negative(self.line_increment_m, name="line_increment_m")
        ensure_positive(self.velocity_factor, name="velocity_factor")
        if self.velocity_factor > 1.0:
            raise ValueError("velocity_factor must not exceed 1")
        ensure_positive(
            self.characteristic_impedance_ohm,
            name="characteristic_impedance_ohm",
        )
        ensure_non_negative(self.splitter_loss_db, name="splitter_loss_db")
        ensure_non_negative(self.line_loss_db_per_100m, name="line_loss_db_per_100m")
        ensure_non_negative(
            self.splitter_design_frequency_hz,
            name="splitter_design_frequency_hz",
        )
        if not math.isfinite(self.splitter_design_frequency_hz):
            raise ValueError("splitter_design_frequency_hz must be finite")
        if self.mode is StackedYagiFeedMode.NETWORK and self.line_increment_m <= 0.0:
            raise ValueError("network mode requires a positive line_increment_m")
        if self.mode is StackedYagiFeedMode.NETWORK and self.reference_length_m <= 0.0:
            raise ValueError("network mode requires a positive reference_length_m")
        if self.mode is StackedYagiFeedMode.WILKINSON and self.reference_length_m <= 0.0:
            raise ValueError("Wilkinson mode requires a positive reference_length_m")
        for network in self.level_matching_networks:
            if network is not None and not isinstance(network, (LNetwork, PiNetwork, TNetwork)):
                raise ValueError("per-level matching supports L, Pi, or T networks only")
        for ratio in self.level_transformer_ratios:
            ensure_positive(ratio, name="level_transformer_ratios")
            if not math.isfinite(ratio):
                raise ValueError("level_transformer_ratios must be finite")
        for name, value in (
            ("branch_impedance_tolerance_pct", self.branch_impedance_tolerance_pct),
            ("isolation_resistor_tolerance_pct", self.isolation_resistor_tolerance_pct),
        ):
            if not math.isfinite(value) or not 0.0 <= value < 100.0:
                raise ValueError(f"{name} must be finite and between 0 and 100")

    def line_length_for_level(self, level_index: int) -> float:
        return self.reference_length_m + level_index * self.line_increment_m

    def level_matching_network_for_level(self, level_index: int) -> MatchingNetwork | None:
        if 0 <= level_index < len(self.level_matching_networks):
            return self.level_matching_networks[level_index]
        return None

    def level_transformer_ratio_for_level(self, level_index: int) -> float:
        if 0 <= level_index < len(self.level_transformer_ratios):
            return self.level_transformer_ratios[level_index]
        return 1.0

    def line_loss_for_level(self, level_index: int) -> float:
        """Return the matched line loss for a zero-based level line."""

        return self.line_loss_db_per_100m * self.line_length_for_level(level_index) / 100.0

    def splitter_design_frequency_for(self, default_frequency_hz: float) -> float:
        """Return the declared Wilkinson design frequency or the default."""

        if self.splitter_design_frequency_hz > 0.0:
            return self.splitter_design_frequency_hz
        return default_frequency_hz


def stacked_yagi_parameters(
    *,
    frequency_hz: float = 145_000_000.0,
    count: int = 2,
    height_m: float = 12.0,
    spacing_m: float | None = None,
    phase_step_deg: float = 0.0,
    amplitude_ratio: float = 1.0,
    max_top_height_m: float = 0.0,
    azimuth_deg: float = 0.0,
    polarization: Polarization = Polarization.HORIZONTAL,
    material: ConductorMaterial = ALUMINUM,
    ground: GroundModel = FREE_SPACE,
    radius_m: float | None = None,
    feed: StackedYagiFeed | None = None,
) -> StackedYagiParameters:
    """Return an NBS five-element stack with a starting half-wave spacing.

    The spacing is a starting value, not a validated gain or feed-network
    recommendation. A vertical-polarized stack uses the longest element plus
    0.1 wavelength so adjacent levels cannot overlap.
    """

    yagi = nbs_five_element(
        frequency_hz=frequency_hz,
        height_m=height_m,
        azimuth_deg=azimuth_deg,
        polarization=polarization,
        material=material,
        ground=ground,
        radius_m=radius_m,
    )
    if spacing_m is None:
        spacing = 0.5 * wavelength_m(frequency_hz)
        if polarization is Polarization.VERTICAL:
            span = max(element.length_m for element in yagi.elements)
            spacing = span + 0.1 * wavelength_m(frequency_hz)
    else:
        spacing = spacing_m
    return StackedYagiParameters(
        yagi=yagi,
        count=count,
        spacing_m=spacing,
        phase_step_deg=phase_step_deg,
        amplitude_ratio=amplitude_ratio,
        max_top_height_m=max_top_height_m,
        feed=feed or StackedYagiFeed(),
    )


@dataclass(frozen=True, slots=True)
class StackedYagiParameters:
    """Two to four identical Yagis on a vertical stack.

    The base Yagi's optional mast and guy fields describe one shared support:
    the mast runs from ground to the top boom and the guys attach to its top.
    A folded driven element or a beta/hairpin match is copied to every level.
    The folded geometry has no ideal per-level transformer, so use the feed
    network or per-level matching to transform its impedance.
    """

    yagi: YagiParameters
    count: int = 2
    spacing_m: float = 0.0
    phase_step_deg: float = 0.0
    amplitude_ratio: float = 1.0
    max_top_height_m: float = 0.0
    feed: StackedYagiFeed = field(default_factory=StackedYagiFeed)

    def __post_init__(self) -> None:
        if self.count < 2 or self.count > 4:
            raise ValueError("a stacked Yagi requires 2 to 4 levels")
        if not math.isclose(self.yagi.transformer_ratio, 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(
                "a stacked Yagi takes per-level transformers in its feed specification; "
                "set the base Yagi transformer_ratio to 1.0"
            )
        ensure_positive(self.spacing_m, name="spacing_m")
        ensure_positive(self.amplitude_ratio, name="amplitude_ratio")
        ensure_non_negative(self.max_top_height_m, name="max_top_height_m")
        if (
            self.feed.level_matching_networks
            and len(self.feed.level_matching_networks) != self.count
        ):
            raise ValueError("level_matching_networks must have one entry per level")
        if (
            self.feed.level_transformer_ratios
            and len(self.feed.level_transformer_ratios) != self.count
        ):
            raise ValueError("level_transformer_ratios must have one entry per level")
        if not math.isfinite(self.phase_step_deg):
            raise ValueError("phase_step_deg must be finite")
        if (
            self.yagi.polarization is Polarization.VERTICAL
            and self.spacing_m <= self.element_span_m
        ):
            raise ValueError("vertical-polarized stack levels would overlap; increase spacing_m")
        if self.max_top_height_m > 0.0 and self.max_top_height_m < self.highest_tip_m:
            raise ValueError(
                "max_top_height_m must be at least the current highest conductor point"
            )

    @property
    def template_name(self) -> str:
        return "Stacked Yagi"

    @property
    def frequency_hz(self) -> float:
        return self.yagi.frequency_hz

    @property
    def height_m(self) -> float:
        return self.yagi.height_m

    @property
    def azimuth_deg(self) -> float:
        return self.yagi.azimuth_deg

    @property
    def material(self) -> ConductorMaterial:
        return self.yagi.material

    @property
    def ground(self) -> GroundModel:
        return self.yagi.ground

    @property
    def wire_radius_m(self) -> float:
        return self.yagi.elements[0].radius_m

    @property
    def effective_phase_step_deg(self) -> float:
        if self.feed.mode is StackedYagiFeedMode.IDEAL:
            return self.phase_step_deg
        return -360.0 * self.feed.line_increment_m / (self.feed.velocity_factor * self.wavelength_m)

    @property
    def source_phases(self) -> tuple[float, ...]:
        return tuple(level * self.effective_phase_step_deg for level in range(self.count))

    @property
    def source_amplitudes(self) -> tuple[float, ...]:
        return (1.0, *((self.amplitude_ratio,) * (self.count - 1)))

    @property
    def splitter_design_frequency_hz(self) -> float:
        """Resolved Wilkinson design frequency, defaulting to the Yagi frequency."""

        return self.feed.splitter_design_frequency_for(self.frequency_hz)

    @property
    def wavelength_m(self) -> float:
        return self.yagi.wavelength_m

    @property
    def element_span_m(self) -> float:
        """Longest element tip-to-tip length."""

        return max(element.length_m for element in self.yagi.elements)

    @property
    def boom_length_m(self) -> float:
        """Distance from the reflector to the last element."""

        return max(element.position_m for element in self.yagi.elements)

    @property
    def minimum_spacing_m(self) -> float:
        """Smallest spacing that keeps adjacent levels from overlapping."""

        if self.yagi.polarization is Polarization.VERTICAL:
            return self.element_span_m + 0.001
        return 0.001

    @property
    def maximum_spacing_m(self) -> float | None:
        """Largest spacing allowed by the mechanical top-height envelope."""

        if self.max_top_height_m <= 0.0:
            return None
        highest_offset = (
            self.element_span_m / 2.0 if self.yagi.polarization is Polarization.VERTICAL else 0.0
        )
        return (self.max_top_height_m - self.yagi.height_m - highest_offset) / (self.count - 1)

    @property
    def top_height_m(self) -> float:
        """Boom height of the highest level."""

        return self.yagi.height_m + (self.count - 1) * self.spacing_m

    @property
    def lowest_tip_m(self) -> float:
        """Lowest conductor point of the lowest level."""

        if self.yagi.polarization is Polarization.HORIZONTAL:
            return self.yagi.height_m
        return self.yagi.height_m - self.element_span_m / 2.0

    @property
    def highest_tip_m(self) -> float:
        """Highest conductor point of the highest level."""

        if self.yagi.polarization is Polarization.HORIZONTAL:
            return self.top_height_m
        return self.top_height_m + self.element_span_m / 2.0

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        base = self.yagi.to_antenna(include_support=False)
        wires: list[Wire] = []
        for level in range(self.count):
            z_offset = level * self.spacing_m
            for wire in base.wires:
                wires.append(
                    Wire(
                        id=f"{STACKED_YAGI_LEVEL_PREFIX}{level + 1}-{wire.id}",
                        start=Point3D(
                            wire.start.x_m,
                            wire.start.y_m,
                            wire.start.z_m + z_offset,
                        ),
                        end=Point3D(
                            wire.end.x_m,
                            wire.end.y_m,
                            wire.end.z_m + z_offset,
                        ),
                        radius_m=wire.radius_m,
                        material=wire.material,
                    )
                )
        wires.extend(self.yagi.support_wires(top_height_m=self.top_height_m))
        primary_wire = f"{STACKED_YAGI_LEVEL_PREFIX}1-{base.feed.wire_id}"
        if self.feed.mode is StackedYagiFeedMode.NETWORK:
            feed_wire = base.feed_wire
            node_x = (feed_wire.start.x_m + feed_wire.end.x_m) / 2.0
            node_y = (feed_wire.start.y_m + feed_wire.end.y_m) / 2.0
            node_z = self.highest_tip_m + 1.0
            node = Wire(
                id=STACKED_YAGI_SPLITTER_NODE_ID,
                start=Point3D(node_x, node_y, node_z),
                end=Point3D(node_x, node_y, node_z + SPLITTER_NODE_LENGTH_M),
                radius_m=SPLITTER_NODE_RADIUS_M,
                material=self.yagi.material,
            )
            wires.append(node)
            node_offset = SPLITTER_NODE_LENGTH_M / 2.0
            sources: tuple[Source, ...] = ()
            phase_lines = tuple(
                TransmissionLine(
                    id=f"{STACKED_YAGI_LEVEL_PREFIX}{level + 1}-phase-line",
                    start_wire_id=STACKED_YAGI_SPLITTER_NODE_ID,
                    start_offset_m=node_offset,
                    end_wire_id=f"{STACKED_YAGI_LEVEL_PREFIX}{level + 1}-{base.feed.wire_id}",
                    end_offset_m=base.feed.offset_m,
                    characteristic_impedance_ohm=self.feed.characteristic_impedance_ohm,
                    length_m=self.feed.reference_length_m + level * self.feed.line_increment_m,
                    velocity_factor=self.feed.velocity_factor,
                )
                for level in range(self.count)
            )
            primary_feed = FeedPoint(
                wire_id=STACKED_YAGI_SPLITTER_NODE_ID,
                offset_m=node_offset,
            )
        else:
            primary_feed = FeedPoint(wire_id=primary_wire, offset_m=base.feed.offset_m)
            phase_lines = ()
            sources = tuple(
                Source(
                    wire_id=f"{STACKED_YAGI_LEVEL_PREFIX}{level + 1}-{base.feed.wire_id}",
                    offset_m=base.feed.offset_m,
                    amplitude=self.amplitude_ratio,
                    phase_deg=level * self.effective_phase_step_deg,
                )
                for level in range(1, self.count)
            )
        return AntennaModel(
            name=name or self.template_name,
            design_frequency_hz=base.design_frequency_hz,
            wires=tuple(wires),
            feed=primary_feed,
            environment=base.environment,
            sources=sources,
            transmission_lines=base.transmission_lines + phase_lines,
        )
