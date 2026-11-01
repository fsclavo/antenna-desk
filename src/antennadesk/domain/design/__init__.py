# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Frequency-first antenna dimension estimation."""

from .estimate import Confidence, DimensionEstimate, DimensionRow, DimensionUnit
from .estimators import (
    SUPPORTED_ESTIMATOR_TYPES,
    UnsupportedEstimateError,
    estimate_intent,
)
from .intent import DesignIntent, LoopShape, VerticalForm

__all__ = [
    "SUPPORTED_ESTIMATOR_TYPES",
    "Confidence",
    "DesignIntent",
    "DimensionEstimate",
    "DimensionRow",
    "DimensionUnit",
    "LoopShape",
    "UnsupportedEstimateError",
    "VerticalForm",
    "estimate_intent",
]
