# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Frequency-dependent balun or unun insertion-loss model."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common.units import ensure_non_negative, ensure_positive


@dataclass(frozen=True, slots=True)
class BalunLoss:
    """A matched balun/unun insertion loss with a power-law frequency fit.

    The loss is ``reference_loss_db * (f / reference_frequency_hz) ** exponent``.
    It is a project-level post-processing model: it reduces realized gain but
    does not change the antenna geometry or the impedance transformation ratio.
    """

    enabled: bool = True
    reference_frequency_hz: float = 7_000_000.0
    reference_loss_db: float = 0.5
    exponent: float = 0.5

    def __post_init__(self) -> None:
        ensure_positive(self.reference_frequency_hz, name="reference_frequency_hz")
        ensure_non_negative(self.reference_loss_db, name="reference_loss_db")
        ensure_non_negative(self.exponent, name="exponent")

    @property
    def is_active(self) -> bool:
        return self.enabled and self.reference_loss_db > 0.0

    def loss_db(self, frequency_hz: float) -> float:
        """Return the matched insertion loss at ``frequency_hz``."""

        ensure_positive(frequency_hz, name="frequency_hz")
        if not self.is_active:
            return 0.0
        return float(
            self.reference_loss_db
            * math.pow(frequency_hz / self.reference_frequency_hz, self.exponent)
        )
