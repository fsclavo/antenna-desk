# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Common comparison basis for design variants.

The basis makes the conditions explicit before two or more designs are
compared: a shared frequency plan, ground, reference frequency, and an optional
reference height. Height mapping is deliberately conservative: families with a
directly comparable height field are moved to the reference height, vertical
families are shifted by their base height, and ambiguous families keep their
native height with a visible warning.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from ..antennas.beverage import BeverageParameters
from ..antennas.dipole import DipoleParameters
from ..antennas.endfed import EndFedParameters
from ..antennas.fan_dipole import FanDipoleParameters
from ..antennas.folded_dipole import FoldedDipoleParameters
from ..antennas.hexbeam import HexbeamParameters
from ..antennas.inverted_l import InvertedLParameters
from ..antennas.inverted_v import InvertedVParameters
from ..antennas.loaded_dipole import LoadedDipoleParameters
from ..antennas.loop import LoopParameters
from ..antennas.magnetic_loop import MagneticLoopParameters
from ..antennas.moxon import MoxonParameters
from ..antennas.ocfd import OCFDParameters
from ..antennas.phased_vertical import PhasedVerticalParameters
from ..antennas.quad_beam import QuadBeamParameters
from ..antennas.t2fd import T2FDParameters
from ..antennas.transmission_line_doublet import TransmissionLineDoubletParameters
from ..antennas.trap_dipole import TrapDipoleParameters
from ..antennas.trap_yagi import TrapYagiParameters
from ..antennas.vertical import VerticalParameters
from ..antennas.yagi import YagiParameters
from ..common.units import ensure_positive
from ..environment.ground import GroundModel
from ..projects.project import DesignVariant
from ..simulation.frequency import FrequencyPlan


@dataclass(frozen=True, slots=True)
class ComparisonBasis:
    """The conditions applied to every design before comparison."""

    frequency_plan: FrequencyPlan
    ground: GroundModel
    reference_height_m: float | None
    reference_frequency_hz: float

    def __post_init__(self) -> None:
        ensure_positive(self.reference_frequency_hz, name="reference_frequency_hz")
        if self.reference_height_m is not None:
            ensure_positive(self.reference_height_m, name="reference_height_m")
        plan = self.frequency_plan
        if not (plan.start_hz - 1e-6 <= self.reference_frequency_hz <= plan.stop_hz + 1e-6):
            raise ValueError("reference_frequency_hz must be inside the frequency plan")


@dataclass(frozen=True, slots=True)
class BasisApplication:
    """One design after the basis was applied."""

    design: DesignVariant
    height_mapped: bool
    warnings: tuple[str, ...] = ()


_DIRECT_HEIGHT_TYPES = (
    DipoleParameters,
    FoldedDipoleParameters,
    LoopParameters,
    MagneticLoopParameters,
    OCFDParameters,
    TrapDipoleParameters,
    YagiParameters,
    MoxonParameters,
    HexbeamParameters,
    TrapYagiParameters,
    QuadBeamParameters,
    TransmissionLineDoubletParameters,
    T2FDParameters,
    LoadedDipoleParameters,
    BeverageParameters,
)


def native_height_m(parameters: object) -> float | None:
    """Return a practical native height for a design, when one exists."""

    if isinstance(parameters, _DIRECT_HEIGHT_TYPES):
        value = getattr(parameters, "height_m", None)
        if isinstance(value, (int, float)):
            return float(value)
    if isinstance(parameters, InvertedVParameters):
        return parameters.apex_height_m
    if isinstance(parameters, FanDipoleParameters):
        return parameters.apex_height_m
    if isinstance(parameters, VerticalParameters):
        return parameters.base_height_m + parameters.height_m
    if isinstance(parameters, PhasedVerticalParameters):
        return parameters.base_height_m + parameters.height_m
    if isinstance(parameters, EndFedParameters):
        return parameters.feed_height_m
    if isinstance(parameters, InvertedLParameters):
        return parameters.base_height_m + parameters.vertical_height_m
    return None


def apply_comparison_basis(
    design: DesignVariant,
    basis: ComparisonBasis,
) -> BasisApplication:
    """Return ``design`` with the common ground and height applied."""

    parameters = replace(design.parameters, ground=basis.ground)
    warnings: list[str] = []
    height_mapped = False

    if basis.reference_height_m is None:
        warnings.append("native_height")
    elif isinstance(parameters, _DIRECT_HEIGHT_TYPES):
        parameters = replace(parameters, height_m=basis.reference_height_m)
        height_mapped = True
    elif isinstance(parameters, (InvertedVParameters, FanDipoleParameters)):
        try:
            parameters = replace(
                parameters,
                apex_height_m=basis.reference_height_m,
            )
            height_mapped = True
        except ValueError:
            warnings.append("height_too_low")
    elif isinstance(parameters, (VerticalParameters, PhasedVerticalParameters)):
        if basis.reference_height_m >= parameters.height_m:
            parameters = replace(
                parameters,
                base_height_m=basis.reference_height_m - parameters.height_m,
            )
            height_mapped = True
        else:
            warnings.append("height_too_low")
    else:
        warnings.append("height_mapping_unavailable")

    return BasisApplication(
        design=design.with_parameters(parameters),
        height_mapped=height_mapped,
        warnings=tuple(warnings),
    )
