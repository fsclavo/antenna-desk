# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Normalized DL6WU Yagi reference dimensions for 2 to 15 elements.

Source: L. B. Cebik, W4RNL, "Appreciating DL6WU Wide-Band Long-Boom Yagi
Design", 32-element DL6WU table derived from RSGB, The VHF/UHF DX Book,
chapter 7 (DL6WU) and chapter 10. Element diameter in the source is 4 mm at
432 MHz. Dimensions are stored as factors of wavelength.
"""

from __future__ import annotations

# (length_factor, cumulative_spacing_from_reflector_factor)
DL6WU_ELEMENTS: tuple[tuple[float, float], ...] = (
    (0.491, 0.000),  # reflector
    (0.476, 0.200),  # driven element
    (0.435, 0.275),  # director 1
    (0.431, 0.455),
    (0.426, 0.670),
    (0.421, 0.920),
    (0.417, 1.200),
    (0.413, 1.500),
    (0.410, 1.815),
    (0.407, 2.145),
    (0.404, 2.490),
    (0.402, 2.850),
    (0.400, 3.225),
    (0.398, 3.615),
    (0.396, 4.015),
)

MIN_YAGI_ELEMENTS = 2
MAX_YAGI_ELEMENTS = len(DL6WU_ELEMENTS)


def dl6wu_elements(count: int) -> tuple[tuple[float, float], ...]:
    """Return the first ``count`` elements of the DL6WU trimming reference."""

    if not MIN_YAGI_ELEMENTS <= count <= MAX_YAGI_ELEMENTS:
        raise ValueError(
            f"Yagi element count must be between {MIN_YAGI_ELEMENTS} and {MAX_YAGI_ELEMENTS}"
        )
    return DL6WU_ELEMENTS[:count]
