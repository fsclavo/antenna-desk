# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validated multiband analysis plans and family defaults."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..antennas.beverage import BeverageParameters
from ..antennas.biquad import BiquadParameters
from ..antennas.custom import CustomAntennaParameters
from ..antennas.design import AntennaDesignParameters
from ..antennas.dipole import DipoleParameters
from ..antennas.discone import DisconeParameters
from ..antennas.endfed import EndFedParameters, EndFedPreset
from ..antennas.fan_dipole import FanDipoleParameters
from ..antennas.loaded_dipole import LoadedDipoleParameters
from ..antennas.ocfd import OCFDParameters
from ..antennas.phased_vertical import PhasedVerticalParameters
from ..antennas.quad_beam import QuadBeamParameters
from ..antennas.t2fd import T2FDParameters
from ..antennas.transmission_line_doublet import (
    DoubletPreset,
    TransmissionLineDoubletParameters,
)
from ..antennas.trap_dipole import TrapDipoleParameters
from ..antennas.zepp import ZeppParameters
from ..simulation.bands import (
    AMATEUR_BANDS,
    AmateurBand,
    amateur_band_by_id,
    amateur_band_for,
)
from ..simulation.frequency import FrequencyPlan
from . import formulas

DEFAULT_BAND_POINTS = 15
BROADBAND_BAND_POINTS = 21
MAX_BAND_POINTS = 1_000

G5RV_DEFAULT_BAND_IDS = ("80m", "40m", "20m", "15m", "10m")
ZS6BKW_DEFAULT_BAND_IDS = ("40m", "20m", "17m", "12m", "10m")
RANDOM_WIRE_BAND_IDS = ("80m", "40m", "30m", "20m", "17m", "15m", "12m", "10m")
HF_BAND_IDS = ("80m", "40m", "30m", "20m", "17m", "15m", "12m", "10m")


class BandEvidence(StrEnum):
    PUBLISHED = "published"
    HEURISTIC = "heuristic"
    TUNABLE = "tunable"
    BROADBAND = "broadband"
    CURRENT = "current"


@dataclass(frozen=True, slots=True)
class BandSelection:
    """One amateur band included in an analysis."""

    band: AmateurBand
    points: int = DEFAULT_BAND_POINTS

    def __post_init__(self) -> None:
        if self.band.start_hz <= 0.0 or self.band.stop_hz < self.band.start_hz:
            raise ValueError("band range must be positive and ordered")
        if self.points < 2 or self.points > MAX_BAND_POINTS:
            raise ValueError(f"band points must be between 2 and {MAX_BAND_POINTS}")

    @property
    def band_id(self) -> str:
        return self.band.name

    @property
    def center_hz(self) -> float:
        return self.band.center_hz

    @property
    def frequency_plan(self) -> FrequencyPlan:
        return FrequencyPlan.sweep(self.band.start_hz, self.band.stop_hz, self.points)


@dataclass(frozen=True, slots=True)
class BandPlan:
    """An ordered, duplicate-free set of bands to analyze."""

    selections: tuple[BandSelection, ...]

    def __post_init__(self) -> None:
        selections = tuple(sorted(self.selections, key=lambda item: item.band.start_hz))
        object.__setattr__(self, "selections", selections)
        ids = [selection.band_id for selection in selections]
        if len(ids) != len(set(ids)):
            raise ValueError("a band plan must not contain duplicate bands")

    def __bool__(self) -> bool:
        return bool(self.selections)

    def __len__(self) -> int:
        return len(self.selections)

    @property
    def band_ids(self) -> tuple[str, ...]:
        return tuple(selection.band_id for selection in self.selections)

    def with_points(self, points: int) -> BandPlan:
        return BandPlan(
            tuple(BandSelection(selection.band, points) for selection in self.selections)
        )


@dataclass(frozen=True, slots=True)
class BandDefault:
    """The recommended band plan for a design, with its evidence level."""

    plan: BandPlan
    evidence: BandEvidence
    note_key: str


def default_band_plan(
    parameters: AntennaDesignParameters,
    *,
    high_impedance_feed_line: bool = False,
) -> BandDefault:
    """Return candidate analysis bands for a design family.

    These are starting points, not claims that the antenna is resonant on every
    selected band. Narrowband families receive only their current band. A
    center-fed dipole with a high-impedance feed line is treated as a doublet,
    because the project feed line is the only persisted identity the preset has.
    """

    if isinstance(parameters, DipoleParameters) and high_impedance_feed_line:
        return BandDefault(
            _plan_from_ids(HF_BAND_IDS),
            BandEvidence.TUNABLE,
            "band.note.doublet",
        )
    if isinstance(parameters, TransmissionLineDoubletParameters):
        if parameters.preset is DoubletPreset.G5RV:
            return BandDefault(
                _plan_from_ids(G5RV_DEFAULT_BAND_IDS),
                BandEvidence.PUBLISHED,
                "band.note.g5rv",
            )
        return BandDefault(
            _plan_from_ids(ZS6BKW_DEFAULT_BAND_IDS),
            BandEvidence.PUBLISHED,
            "band.note.zs6bkw",
        )
    if isinstance(parameters, ZeppParameters):
        return BandDefault(
            _harmonic_plan(parameters.frequency_hz, harmonics=(1, 3, 5)),
            BandEvidence.HEURISTIC,
            "band.note.zepp",
        )
    if isinstance(parameters, BiquadParameters):
        return BandDefault(
            _current_band_plan(parameters.frequency_hz),
            BandEvidence.CURRENT,
            "band.note.biquad",
        )
    if isinstance(parameters, BeverageParameters):
        return BandDefault(
            _current_band_plan(parameters.frequency_hz),
            BandEvidence.CURRENT,
            "band.note.beverage",
        )
    if isinstance(parameters, LoadedDipoleParameters):
        return BandDefault(
            _current_band_plan(parameters.frequency_hz),
            BandEvidence.CURRENT,
            "band.note.loaded_dipole",
        )
    if isinstance(parameters, DisconeParameters):
        return BandDefault(
            _current_band_plan(parameters.frequency_hz),
            BandEvidence.CURRENT,
            "band.note.discone",
        )
    if isinstance(parameters, PhasedVerticalParameters):
        return BandDefault(
            _current_band_plan(parameters.frequency_hz),
            BandEvidence.CURRENT,
            "band.note.phased_vertical",
        )
    if isinstance(parameters, QuadBeamParameters):
        return BandDefault(
            _current_band_plan(parameters.frequency_hz),
            BandEvidence.CURRENT,
            "band.note.quad_beam",
        )
    if isinstance(parameters, CustomAntennaParameters) and parameters.generator_id == "g5rv":
        return BandDefault(
            _plan_from_ids(G5RV_DEFAULT_BAND_IDS),
            BandEvidence.PUBLISHED,
            "band.note.g5rv",
        )
    if isinstance(parameters, CustomAntennaParameters) and parameters.generator_id == "zs6bkw":
        return BandDefault(
            _plan_from_ids(ZS6BKW_DEFAULT_BAND_IDS),
            BandEvidence.PUBLISHED,
            "band.note.zs6bkw",
        )
    if isinstance(parameters, CustomAntennaParameters) and parameters.generator_id == "zepp":
        return BandDefault(
            _harmonic_plan(parameters.frequency_hz, harmonics=(1, 3, 5)),
            BandEvidence.HEURISTIC,
            "band.note.zepp",
        )
    if isinstance(parameters, OCFDParameters):
        return BandDefault(
            _harmonic_plan(parameters.frequency_hz),
            BandEvidence.HEURISTIC,
            "band.note.ocfd",
        )
    if isinstance(parameters, EndFedParameters):
        if parameters.preset is EndFedPreset.RANDOM_WIRE:
            return BandDefault(
                _plan_from_ids(RANDOM_WIRE_BAND_IDS),
                BandEvidence.TUNABLE,
                "band.note.random_wire",
            )
        return BandDefault(
            _harmonic_plan(
                parameters.frequency_hz,
                harmonics=(1, 2, 4) if parameters.preset is EndFedPreset.SLOPER else (1, 2, 4, 8),
            ),
            BandEvidence.TUNABLE,
            "band.note.sloper" if parameters.preset is EndFedPreset.SLOPER else "band.note.endfed",
        )
    if isinstance(parameters, FanDipoleParameters):
        return BandDefault(
            _fan_plan(parameters),
            BandEvidence.HEURISTIC,
            "band.note.fan",
        )
    if isinstance(parameters, TrapDipoleParameters):
        return BandDefault(
            _two_band_plan(parameters.frequency_hz, parameters.high_band_frequency_hz),
            BandEvidence.HEURISTIC,
            "band.note.trap",
        )
    if isinstance(parameters, T2FDParameters):
        return BandDefault(
            _bands_between(
                parameters.frequency_hz,
                parameters.highest_frequency_hz,
                points=BROADBAND_BAND_POINTS,
            ),
            BandEvidence.BROADBAND,
            "band.note.t2fd",
        )
    return BandDefault(
        _current_band_plan(parameters.frequency_hz),
        BandEvidence.CURRENT,
        "band.note.current",
    )


def _plan_from_ids(band_ids: tuple[str, ...], *, points: int = DEFAULT_BAND_POINTS) -> BandPlan:
    selections = []
    for band_id in band_ids:
        band = amateur_band_by_id(band_id)
        if band is not None:
            selections.append(BandSelection(band, points))
    return BandPlan(tuple(selections))


def _current_band_plan(frequency_hz: float, *, points: int = DEFAULT_BAND_POINTS) -> BandPlan:
    band = amateur_band_for(frequency_hz, tolerance_fraction=0.0)
    if band is None:
        return BandPlan(())
    return BandPlan((BandSelection(band, points),))


def _harmonic_plan(
    frequency_hz: float,
    *,
    harmonics: tuple[int, ...] = (1, 2, 4, 8),
    points: int = DEFAULT_BAND_POINTS,
) -> BandPlan:
    bands: dict[str, AmateurBand] = {}
    for multiplier in harmonics:
        band = amateur_band_for(frequency_hz * multiplier, tolerance_fraction=0.05)
        if band is not None:
            bands[band.name] = band
    if not bands:
        return _current_band_plan(frequency_hz, points=points)
    return BandPlan(tuple(BandSelection(band, points) for band in bands.values()))


def _two_band_plan(low_hz: float, high_hz: float) -> BandPlan:
    bands: dict[str, AmateurBand] = {}
    for frequency_hz in (low_hz, high_hz):
        band = amateur_band_for(frequency_hz, tolerance_fraction=0.0)
        if band is not None:
            bands[band.name] = band
    if not bands:
        return _current_band_plan(low_hz)
    return BandPlan(tuple(BandSelection(band) for band in bands.values()))


def _fan_plan(parameters: FanDipoleParameters) -> BandPlan:
    bands: dict[str, AmateurBand] = {}
    for element in parameters.elements:
        frequency_hz = formulas.frequency_for_half_wave_length(element.length_m)
        band = amateur_band_for(frequency_hz, tolerance_fraction=0.01)
        if band is not None:
            bands[band.name] = band
    if not bands:
        return _current_band_plan(parameters.frequency_hz)
    return BandPlan(tuple(BandSelection(band) for band in bands.values()))


def _bands_between(start_hz: float, stop_hz: float, *, points: int) -> BandPlan:
    bands = [
        band for band in AMATEUR_BANDS if band.stop_hz >= start_hz and band.start_hz <= stop_hz
    ]
    if not bands:
        return _current_band_plan(start_hz, points=points)
    return BandPlan(tuple(BandSelection(band, points) for band in bands))
