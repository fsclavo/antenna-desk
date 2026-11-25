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
from dataclasses import dataclass

from ..common.units import ensure_positive, wavelength_m
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .feed import FeedPoint, Source
from .geometry import Point3D
from .materials import ALUMINUM, ConductorMaterial
from .polarization import Polarization
from .wire import Wire
from .yagi import YagiMatchType, YagiParameters, nbs_five_element

ANTENNA_TYPE_STACKED_YAGI = "stacked_yagi"
STACKED_YAGI_LEVEL_PREFIX = "level-"


def stacked_yagi_parameters(
    *,
    frequency_hz: float = 145_000_000.0,
    count: int = 2,
    height_m: float = 12.0,
    spacing_m: float | None = None,
    phase_step_deg: float = 0.0,
    amplitude_ratio: float = 1.0,
    azimuth_deg: float = 0.0,
    polarization: Polarization = Polarization.HORIZONTAL,
    material: ConductorMaterial = ALUMINUM,
    ground: GroundModel = FREE_SPACE,
    radius_m: float | None = None,
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
    )


@dataclass(frozen=True, slots=True)
class StackedYagiParameters:
    """Two to four identical Yagis on a vertical stack."""

    yagi: YagiParameters
    count: int = 2
    spacing_m: float = 0.0
    phase_step_deg: float = 0.0
    amplitude_ratio: float = 1.0

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
        if not math.isfinite(self.phase_step_deg):
            raise ValueError("phase_step_deg must be finite")
        if (
            self.yagi.polarization is Polarization.VERTICAL
            and self.spacing_m <= self.element_span_m
        ):
            raise ValueError("vertical-polarized stack levels would overlap; increase spacing_m")

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
    def source_phases(self) -> tuple[float, ...]:
        return tuple(level * self.phase_step_deg for level in range(self.count))

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
        sources = tuple(
            Source(
                wire_id=f"{STACKED_YAGI_LEVEL_PREFIX}{level + 1}-{base.feed.wire_id}",
                offset_m=base.feed.offset_m,
                amplitude=self.amplitude_ratio,
                phase_deg=level * self.phase_step_deg,
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
        )
