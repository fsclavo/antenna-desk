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
from .materials import ALUMINUM, ConductorMaterial
from .polarization import Polarization
from .transmission_line import TransmissionLine
from .wire import Wire
from .yagi import YagiMatchType, YagiParameters, nbs_five_element

ANTENNA_TYPE_STACKED_YAGI = "stacked_yagi"
STACKED_YAGI_LEVEL_PREFIX = "level-"


class StackedYagiFeedMode(StrEnum):
    IDEAL = "ideal"
    PHASE_LINES = "phase_lines"
    NETWORK = "network"


@dataclass(frozen=True, slots=True)
class StackedYagiFeed:
    """Ideal splitter and phase-line specification for one stack.

    ``reference_length_m`` is the splitter-to-level-1 line. Every later level
    adds ``line_increment_m`` of the same line. The solver still receives ideal
    voltage sources: in phase-line mode the line lengths set the source phase
    at the design frequency and that phase is held fixed across a frequency
    sweep; in network mode NEC's lossless TL cards use the physical length at
    every solver frequency. Line loss and the reference-line impedance
    transformation are not modeled. ``splitter_loss_db`` is the excess loss
    beyond the ideal N-way division and is applied to the realized gain.
    """

    mode: StackedYagiFeedMode = StackedYagiFeedMode.IDEAL
    reference_length_m: float = 0.0
    line_increment_m: float = 0.0
    velocity_factor: float = 1.0
    characteristic_impedance_ohm: float = 50.0
    splitter_loss_db: float = 0.0

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
        if self.mode is StackedYagiFeedMode.NETWORK and self.line_increment_m <= 0.0:
            raise ValueError("network mode requires a positive line_increment_m")

    def line_length_for_level(self, level_index: int) -> float:
        return self.reference_length_m + level_index * self.line_increment_m


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
    """Two to four identical Yagis on a vertical stack."""

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
        if self.yagi.mast_diameter_m > 0.0 or self.yagi.guy_count > 0:
            raise ValueError("a stacked Yagi does not support mast or guy wires yet")
        if self.yagi.driven_folded or self.yagi.match_type is not YagiMatchType.NONE:
            raise ValueError(
                "a stacked Yagi does not support folded or matched driven elements yet"
            )
        if not math.isclose(self.yagi.transformer_ratio, 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("a stacked Yagi does not support a per-level feed transformer yet")
        ensure_positive(self.spacing_m, name="spacing_m")
        ensure_positive(self.amplitude_ratio, name="amplitude_ratio")
        ensure_non_negative(self.max_top_height_m, name="max_top_height_m")
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
        base = self.yagi.to_antenna()
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
        primary_wire = f"{STACKED_YAGI_LEVEL_PREFIX}1-{base.feed.wire_id}"
        if self.feed.mode is StackedYagiFeedMode.NETWORK:
            sources: tuple[Source, ...] = ()
            phase_lines = tuple(
                TransmissionLine(
                    id=f"{STACKED_YAGI_LEVEL_PREFIX}{level + 1}-phase-line",
                    start_wire_id=primary_wire,
                    start_offset_m=base.feed.offset_m,
                    end_wire_id=f"{STACKED_YAGI_LEVEL_PREFIX}{level + 1}-{base.feed.wire_id}",
                    end_offset_m=base.feed.offset_m,
                    characteristic_impedance_ohm=self.feed.characteristic_impedance_ohm,
                    length_m=level * self.feed.line_increment_m,
                    velocity_factor=self.feed.velocity_factor,
                )
                for level in range(1, self.count)
            )
        else:
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
            feed=FeedPoint(wire_id=primary_wire, offset_m=base.feed.offset_m),
            environment=base.environment,
            sources=sources,
            transmission_lines=base.transmission_lines + phase_lines,
        )
