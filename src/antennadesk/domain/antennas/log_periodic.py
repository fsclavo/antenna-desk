# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Log-periodic dipole array with a transposed phase line."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive
from ..environment.environment import Environment
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .feed import FeedPoint
from .geometry import Point3D
from .materials import ALUMINUM, ConductorMaterial
from .transmission_line import TransmissionLine
from .wire import Wire

ANTENNA_TYPE_LOG_PERIODIC = "log_periodic"
LOG_PERIODIC_ELEMENT_ID_PREFIX = "log-periodic-element-"
LOG_PERIODIC_PHASE_LINE_ID_PREFIX = "log-periodic-phase-line-"

MIN_ELEMENTS = 3
MAX_ELEMENTS = 12
MIN_TAU = 0.50
MAX_TAU = 0.98
MIN_SIGMA = 0.02
MAX_SIGMA = 0.20

# Cebik, "A 10-Meter LPDA", Phase 3. The published 28-30 MHz LPCAD
# geometry uses four elements and a 75 ohm phase line. These constants
# reproduce the published dimensions exactly after unit conversion.
CEBIK_10M_FREQUENCY_HZ = 28_000_000.0
CEBIK_10M_LONGEST_ELEMENT_M = 5.4628796
CEBIK_10M_TAU = 0.8954287724561619
CEBIK_10M_SIGMA = 0.08274361382593898
CEBIK_10M_ELEMENT_COUNT = 4
CEBIK_10M_WIRE_RADIUS_M = 0.0127  # 1.0 in diameter
CEBIK_10M_PHASE_LINE_Z0_OHM = 75.0


def log_periodic_parameters(
    *,
    frequency_hz: float = CEBIK_10M_FREQUENCY_HZ,
    frequency_high_hz: float | None = None,
    longest_element_length_m: float | None = None,
    tau: float = CEBIK_10M_TAU,
    sigma: float = CEBIK_10M_SIGMA,
    element_count: int = CEBIK_10M_ELEMENT_COUNT,
    wire_radius_m: float = CEBIK_10M_WIRE_RADIUS_M,
    phase_line_impedance_ohm: float = CEBIK_10M_PHASE_LINE_Z0_OHM,
    phase_line_velocity_factor: float = 1.0,
    feed_transformer_ratio: float = 1.0,
    height_m: float = 10.0,
    azimuth_deg: float = 0.0,
    material: ConductorMaterial = ALUMINUM,
    ground: GroundModel = FREE_SPACE,
) -> LogPeriodicParameters:
    """Return a log-periodic starting design scaled from the Cebik 10 m array.

    The reference geometry is the published 28-30 MHz LPCAD design. Scaling
    the longest element by ``28 MHz / frequency_hz`` preserves its electrical
    dimensions. The default 75 ohm phase line and 1:1 feed are the reference
    values; the model does not include a balun, feed-line loss, or a rear stub.
    """

    ensure_positive(frequency_hz, name="frequency_hz")
    if frequency_high_hz is None:
        frequency_high_hz = frequency_hz * 30.0 / 28.0
    if longest_element_length_m is None:
        longest_element_length_m = CEBIK_10M_LONGEST_ELEMENT_M * (
            CEBIK_10M_FREQUENCY_HZ / frequency_hz
        )
    return LogPeriodicParameters(
        frequency_low_hz=frequency_hz,
        frequency_high_hz=frequency_high_hz,
        longest_element_length_m=longest_element_length_m,
        tau=tau,
        sigma=sigma,
        element_count=element_count,
        wire_radius_m=wire_radius_m,
        phase_line_impedance_ohm=phase_line_impedance_ohm,
        phase_line_velocity_factor=phase_line_velocity_factor,
        feed_transformer_ratio=feed_transformer_ratio,
        height_m=height_m,
        azimuth_deg=azimuth_deg,
        material=material,
        ground=ground,
    )


def cebik_10m_log_periodic_parameters() -> LogPeriodicParameters:
    """Return the exact published Cebik 10 m reference geometry."""

    return LogPeriodicParameters(
        frequency_low_hz=CEBIK_10M_FREQUENCY_HZ,
        frequency_high_hz=30_000_000.0,
        longest_element_length_m=CEBIK_10M_LONGEST_ELEMENT_M,
        tau=CEBIK_10M_TAU,
        sigma=CEBIK_10M_SIGMA,
        element_count=CEBIK_10M_ELEMENT_COUNT,
        wire_radius_m=CEBIK_10M_WIRE_RADIUS_M,
        phase_line_impedance_ohm=CEBIK_10M_PHASE_LINE_Z0_OHM,
        phase_line_velocity_factor=1.0,
        feed_transformer_ratio=1.0,
        height_m=0.0,
        material=ALUMINUM,
    )


@dataclass(frozen=True, slots=True)
class LogPeriodicParameters:
    """A straight-element log-periodic dipole array on a common boom.

    Element 1 is the rear (longest) element and element ``N`` is the front
    (shortest) element. The transposed phase line connects adjacent element
    centers with reversed polarity; the rear element center terminates the
    line. The front element center is the feed point. The model is a normal
    ``AntennaModel`` with ``TransmissionLine`` two-ports, not a separate solver
    or model type.

    The supported reference is the published Cebik 10 m design. The generic
    tau/sigma geometry, scaled or edited designs, and non-free-space
    installations are starting points; the family evidence level is B.
    """

    frequency_low_hz: float
    frequency_high_hz: float
    longest_element_length_m: float
    tau: float
    sigma: float
    element_count: int = CEBIK_10M_ELEMENT_COUNT
    wire_radius_m: float = CEBIK_10M_WIRE_RADIUS_M
    phase_line_impedance_ohm: float = CEBIK_10M_PHASE_LINE_Z0_OHM
    phase_line_velocity_factor: float = 1.0
    feed_transformer_ratio: float = 1.0
    height_m: float = 10.0
    azimuth_deg: float = 0.0
    material: ConductorMaterial = ALUMINUM
    ground: GroundModel = FREE_SPACE

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_low_hz, name="frequency_low_hz")
        ensure_positive(self.frequency_high_hz, name="frequency_high_hz")
        if self.frequency_high_hz <= self.frequency_low_hz:
            raise ValueError("frequency_high_hz must exceed frequency_low_hz")
        ensure_positive(self.longest_element_length_m, name="longest_element_length_m")
        if not MIN_TAU <= self.tau <= MAX_TAU:
            raise ValueError(f"tau must be between {MIN_TAU} and {MAX_TAU}")
        if not MIN_SIGMA <= self.sigma <= MAX_SIGMA:
            raise ValueError(f"sigma must be between {MIN_SIGMA} and {MAX_SIGMA}")
        if not MIN_ELEMENTS <= self.element_count <= MAX_ELEMENTS:
            raise ValueError(f"element_count must be between {MIN_ELEMENTS} and {MAX_ELEMENTS}")
        ensure_positive(self.wire_radius_m, name="wire_radius_m")
        ensure_positive(
            self.phase_line_impedance_ohm,
            name="phase_line_impedance_ohm",
        )
        ensure_positive(
            self.phase_line_velocity_factor,
            name="phase_line_velocity_factor",
        )
        if self.phase_line_velocity_factor > 1.0:
            raise ValueError("phase_line_velocity_factor must not exceed 1")
        ensure_positive(self.feed_transformer_ratio, name="feed_transformer_ratio")
        ensure_non_negative(self.height_m, name="height_m")
        if self.shortest_element_length_m <= 2.0 * self.wire_radius_m:
            raise ValueError("the shortest element must exceed the conductor diameter")
        if self.longest_element_length_m <= 2.0 * self.wire_radius_m:
            raise ValueError("the longest element must exceed the conductor diameter")
        object.__setattr__(
            self,
            "azimuth_deg",
            units.normalize_azimuth_degrees(self.azimuth_deg),
        )

    @property
    def template_name(self) -> str:
        return "Log-periodic dipole array"

    @property
    def frequency_hz(self) -> float:
        """Geometric center frequency used by generic editor paths."""

        return self.center_frequency_hz

    @property
    def center_frequency_hz(self) -> float:
        return math.sqrt(self.frequency_low_hz * self.frequency_high_hz)

    @property
    def bandwidth_ratio(self) -> float:
        return self.frequency_high_hz / self.frequency_low_hz

    @property
    def element_lengths_m(self) -> tuple[float, ...]:
        return tuple(
            self.longest_element_length_m * self.tau**index for index in range(self.element_count)
        )

    @property
    def shortest_element_length_m(self) -> float:
        return self.element_lengths_m[-1]

    @property
    def first_spacing_m(self) -> float:
        return 2.0 * self.sigma * self.longest_element_length_m

    @property
    def element_spacings_m(self) -> tuple[float, ...]:
        return tuple(
            self.first_spacing_m * self.tau**index for index in range(self.element_count - 1)
        )

    @property
    def element_positions_m(self) -> tuple[float, ...]:
        positions = [0.0]
        for spacing in self.element_spacings_m:
            positions.append(positions[-1] + spacing)
        return tuple(positions)

    @property
    def boom_length_m(self) -> float:
        return self.element_positions_m[-1]

    @property
    def feed_element_number(self) -> int:
        return self.element_count

    @property
    def feed_wire_id(self) -> str:
        return self.element_wire_id(self.feed_element_number)

    @property
    def total_conductor_length_m(self) -> float:
        return sum(self.element_lengths_m)

    def element_wire_id(self, element_number: int) -> str:
        return f"{LOG_PERIODIC_ELEMENT_ID_PREFIX}{element_number}"

    def element_position_m(self, element_number: int) -> float:
        return self.element_positions_m[element_number - 1]

    def element_length_m(self, element_number: int) -> float:
        return self.element_lengths_m[element_number - 1]

    def to_antenna(self, *, name: str | None = None) -> AntennaModel:
        angle = units.degrees_to_radians(self.azimuth_deg)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        def point(local_x_m: float, local_y_m: float) -> Point3D:
            return Point3D(
                x_m=local_x_m * cos_angle - local_y_m * sin_angle,
                y_m=local_x_m * sin_angle + local_y_m * cos_angle,
                z_m=self.height_m,
            )

        wires: list[Wire] = []
        for index, (position, length) in enumerate(
            zip(self.element_positions_m, self.element_lengths_m, strict=True),
            start=1,
        ):
            half = length / 2.0
            wires.append(
                Wire(
                    id=self.element_wire_id(index),
                    start=point(position, -half),
                    end=point(position, half),
                    radius_m=self.wire_radius_m,
                    material=self.material,
                )
            )

        transmission_lines: list[TransmissionLine] = []
        for index, spacing in enumerate(self.element_spacings_m, start=1):
            transmission_lines.append(
                TransmissionLine(
                    id=f"{LOG_PERIODIC_PHASE_LINE_ID_PREFIX}{index}",
                    start_wire_id=self.element_wire_id(index),
                    start_offset_m=self.element_length_m(index) / 2.0,
                    end_wire_id=self.element_wire_id(index + 1),
                    end_offset_m=self.element_length_m(index + 1) / 2.0,
                    characteristic_impedance_ohm=self.phase_line_impedance_ohm,
                    length_m=spacing,
                    velocity_factor=self.phase_line_velocity_factor,
                    phase_reversal=True,
                )
            )

        return AntennaModel(
            name=name or self.template_name,
            design_frequency_hz=self.center_frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(
                wire_id=self.feed_wire_id,
                offset_m=self.shortest_element_length_m / 2.0,
            ),
            environment=Environment(ground=self.ground),
            transmission_lines=tuple(transmission_lines),
        )

    def with_frequency_low(self, frequency_hz: float) -> LogPeriodicParameters:
        """Scale the reference geometry and band ratio to a new low edge."""

        ensure_positive(frequency_hz, name="frequency_hz")
        ratio = frequency_hz / self.frequency_low_hz
        return LogPeriodicParameters(
            frequency_low_hz=frequency_hz,
            frequency_high_hz=self.frequency_high_hz * ratio,
            longest_element_length_m=self.longest_element_length_m / ratio,
            tau=self.tau,
            sigma=self.sigma,
            element_count=self.element_count,
            wire_radius_m=self.wire_radius_m,
            phase_line_impedance_ohm=self.phase_line_impedance_ohm,
            phase_line_velocity_factor=self.phase_line_velocity_factor,
            feed_transformer_ratio=self.feed_transformer_ratio,
            height_m=self.height_m,
            azimuth_deg=self.azimuth_deg,
            material=self.material,
            ground=self.ground,
        )
