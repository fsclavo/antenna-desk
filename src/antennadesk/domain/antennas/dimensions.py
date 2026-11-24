# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Managed length dimensions for the live-tuning preview."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace

from .beverage import BeverageParameters
from .biquad import BiquadParameters
from .design import (
    AntennaDesignParameters,
    primary_dimension_m,
    with_primary_dimension,
)
from .dipole import DipoleParameters
from .discone import DisconeParameters
from .endfed import EndFedParameters
from .folded_dipole import FoldedDipoleParameters
from .hexbeam import HexbeamParameters
from .inverted_v import InvertedVParameters
from .log_periodic import LogPeriodicParameters
from .loop import LoopParameters
from .ocfd import OCFDParameters
from .phased_vertical import PhasedVerticalParameters
from .scv import ScvParameters
from .t2fd import T2FDParameters
from .transmission_line_doublet import TransmissionLineDoubletParameters
from .trap_dipole import TrapDipoleParameters
from .trap_yagi import TrapYagiParameters
from .vertical import VerticalParameters
from .zepp import ZeppParameters


@dataclass(frozen=True, slots=True)
class ManagedDimension:
    """One editable length dimension with a display-safe range."""

    key: str
    label_key: str
    minimum_m: float
    maximum_m: float
    read: Callable[[AntennaDesignParameters], float]
    write: Callable[[AntennaDesignParameters, float], AntennaDesignParameters]


def _field_dimension(
    key: str,
    label_key: str,
    field: str,
    minimum_m: float,
    maximum_m: float,
) -> ManagedDimension:
    def read(parameters: AntennaDesignParameters) -> float:
        value = getattr(parameters, field, None)
        if not isinstance(value, (int, float)):
            raise TypeError(f"{type(parameters).__name__} has no length field {field!r}")
        return float(value)

    def write(
        parameters: AntennaDesignParameters,
        value: float,
    ) -> AntennaDesignParameters:
        return replace(parameters, **{field: value})  # type: ignore[arg-type]

    return ManagedDimension(
        key=key,
        label_key=label_key,
        minimum_m=minimum_m,
        maximum_m=maximum_m,
        read=read,
        write=write,
    )


_PRIMARY = ManagedDimension(
    key="primary",
    label_key="field.primary_dimension",
    minimum_m=0.01,
    maximum_m=2_000.0,
    read=primary_dimension_m,
    write=with_primary_dimension,
)


def _height(
    field: str = "height_m",
    *,
    key: str = "height",
    label_key: str = "field.height",
) -> ManagedDimension:
    return _field_dimension(key, label_key, field, 0.0, 1_000.0)


def managed_dimensions(
    parameters: AntennaDesignParameters,
) -> tuple[ManagedDimension, ...]:
    """Return the managed length dimensions for a family.

    The primary dimension is always first when the family has one. Secondary
    dimensions are included only when they are meaningful for the current
    design (for example, a radial length only when radials are enabled).
    """

    try:
        primary_dimension_m(parameters)
    except TypeError:
        return ()
    dimensions = [_PRIMARY]

    if isinstance(parameters, DipoleParameters):
        dimensions.append(_height())
    elif isinstance(parameters, FoldedDipoleParameters):
        dimensions.extend(
            (
                _height(),
                _field_dimension("spacing", "field.spacing", "spacing_m", 0.001, 100.0),
            )
        )
    elif isinstance(parameters, LoopParameters):
        dimensions.append(_height())
    elif isinstance(parameters, VerticalParameters):
        dimensions.extend(
            (
                _field_dimension(
                    "base_height",
                    "field.base_height",
                    "base_height_m",
                    0.0,
                    100.0,
                ),
                *(
                    (
                        _field_dimension(
                            "radial_length",
                            "field.radial_length",
                            "radial_length_m",
                            0.0,
                            1_000.0,
                        ),
                    )
                    if parameters.radial_count > 0
                    else ()
                ),
                *(
                    (
                        _field_dimension(
                            "top_hat_radius",
                            "field.top_hat_radius",
                            "top_hat_radius_m",
                            0.0,
                            100.0,
                        ),
                    )
                    if parameters.top_hat_enabled
                    else ()
                ),
                *(
                    (
                        _field_dimension(
                            "loading_coil_offset",
                            "field.loading_coil_offset",
                            "loading_coil_offset_m",
                            0.0,
                            100.0,
                        ),
                    )
                    if parameters.loading_coil_enabled
                    else ()
                ),
            )
        )
    elif isinstance(parameters, InvertedVParameters):
        dimensions.append(
            _field_dimension(
                "apex_height",
                "field.apex_height",
                "apex_height_m",
                0.0,
                1_000.0,
            )
        )
    elif isinstance(parameters, OCFDParameters):
        dimensions.append(_height())
    elif isinstance(parameters, EndFedParameters):
        dimensions.extend(
            (
                _field_dimension(
                    "feed_height",
                    "field.feed_height",
                    "feed_height_m",
                    0.0,
                    1_000.0,
                ),
                _field_dimension(
                    "end_height",
                    "field.end_height",
                    "end_height_m",
                    0.0,
                    1_000.0,
                ),
            )
        )
    elif isinstance(parameters, T2FDParameters):
        dimensions.extend(
            (
                _height(),
                _field_dimension("spacing", "field.spacing", "spacing_m", 0.001, 100.0),
            )
        )
    elif isinstance(parameters, (BeverageParameters, HexbeamParameters, LogPeriodicParameters)):
        dimensions.append(_height())
    elif isinstance(parameters, ScvParameters):
        dimensions.extend(
            (
                _field_dimension(
                    "vertical_height",
                    "field.vertical_height",
                    "vertical_height_m",
                    0.0,
                    1_000.0,
                ),
                _field_dimension(
                    "base_height",
                    "field.base_height",
                    "base_height_m",
                    0.0,
                    100.0,
                ),
            )
        )
    elif isinstance(parameters, BiquadParameters):
        dimensions.append(
            _field_dimension(
                "base_height",
                "field.base_height",
                "base_height_m",
                0.0,
                100.0,
            )
        )
        if parameters.reflector_enabled:
            dimensions.append(
                _field_dimension(
                    "reflector_spacing",
                    "field.reflector_spacing",
                    "reflector_spacing_m",
                    0.001,
                    100.0,
                )
            )
    elif isinstance(parameters, TrapDipoleParameters):
        dimensions.append(_height())
    elif isinstance(parameters, PhasedVerticalParameters):
        dimensions.extend(
            (
                _field_dimension("spacing", "field.spacing", "spacing_m", 0.001, 100.0),
                _field_dimension(
                    "base_height",
                    "field.base_height",
                    "base_height_m",
                    0.0,
                    100.0,
                ),
                *(
                    (
                        _field_dimension(
                            "radial_length",
                            "field.radial_length",
                            "radial_length_m",
                            0.0,
                            1_000.0,
                        ),
                    )
                    if parameters.radial_count > 0
                    else ()
                ),
            )
        )
    elif isinstance(parameters, DisconeParameters):
        dimensions.append(
            _field_dimension(
                "base_height",
                "field.base_height",
                "base_height_m",
                0.0,
                100.0,
            )
        )
    elif isinstance(parameters, TrapYagiParameters):
        dimensions.append(_height())
        dimensions.append(
            _field_dimension(
                "reflector_spacing",
                "field.reflector_spacing",
                "reflector_spacing_m",
                0.001,
                100.0,
            )
        )
        if parameters.element_count > 2:
            dimensions.append(
                _field_dimension(
                    "director_spacing",
                    "field.director_spacing",
                    "director_spacing_m",
                    0.001,
                    100.0,
                )
            )
    elif isinstance(parameters, TransmissionLineDoubletParameters):
        dimensions.extend(
            (
                _height(),
                _field_dimension(
                    "feed_height",
                    "field.feed_height",
                    "feed_height_m",
                    0.0,
                    100.0,
                ),
            )
        )
    elif isinstance(parameters, ZeppParameters):
        dimensions.extend(
            (
                _field_dimension("spacing", "field.spacing", "spacing_m", 0.001, 100.0),
                _field_dimension(
                    "base_height",
                    "field.base_height",
                    "base_height_m",
                    0.0,
                    100.0,
                ),
            )
        )
    return tuple(dimensions)
