# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Static capabilities of the nec2c adapter."""

from __future__ import annotations

from ...domain.simulation.solver import SolverCapabilities

NEC2C_CAPABILITIES = SolverCapabilities(
    name="nec2c",
    supports_frequency_sweep=True,
    supports_currents=True,
    supports_far_field=True,
    supports_perfect_ground=True,
    supports_finite_ground=True,
    supports_extended_thin_wire_kernel=True,
    supports_loads=False,
    supports_networks=False,
)
