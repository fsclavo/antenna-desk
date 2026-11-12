# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure validation of the assumptions made by the NEC-2 adapter."""

from __future__ import annotations

import math

from ..domain.antennas.antenna import AntennaModel
from ..domain.common.validation import Diagnostic, Severity
from ..domain.environment.ground import GroundKind
from ..domain.simulation.spec import SimulationSpec

# NEC-2 requires wires to be separated from a ground plane. Ground-mounted
# radials and dipoles are raised by this small physical clearance when the
# canonical model sits exactly on the ground.
GROUND_CLEARANCE_M = 0.01


def validate_nec2_assumptions(
    model: AntennaModel,
    spec: SimulationSpec,
) -> tuple[Diagnostic, ...]:
    """Return diagnostics for assumptions the NEC-2 adapter cannot represent."""

    diagnostics: list[Diagnostic] = []

    if spec.include_conductor_losses:
        for wire in model.wires:
            if not math.isclose(
                wire.material.relative_permeability,
                1.0,
                rel_tol=1e-9,
                abs_tol=1e-9,
            ):
                diagnostics.append(
                    Diagnostic(
                        code="solver.permeability_unsupported",
                        severity=Severity.WARNING,
                        message=(
                            "relative permeability is not emitted to NEC; "
                            "the adapter models conductor conductivity only"
                        ),
                        field="material.relative_permeability",
                    )
                )

    ground = model.environment.ground
    if ground.kind is not GroundKind.FREE_SPACE:
        min_z = min(point.z_m for wire in model.wires for point in (wire.start, wire.end))
        if min_z < -1e-9:
            diagnostics.append(
                Diagnostic(
                    code="geometry.below_ground",
                    severity=Severity.ERROR,
                    message=(
                        "the model has wires below the ground plane; raise the geometry above z = 0"
                    ),
                    field="geometry",
                )
            )
        elif min_z < GROUND_CLEARANCE_M:
            diagnostics.append(
                Diagnostic(
                    code="geometry.ground_clearance",
                    severity=Severity.INFO,
                    message=(
                        f"the model is raised by {GROUND_CLEARANCE_M - min_z:.3f} m "
                        "above the ground plane for NEC"
                    ),
                    field="geometry",
                )
            )
            if ground.kind is GroundKind.FINITE:
                diagnostics.append(
                    Diagnostic(
                        code="geometry.ground_mounted_wires",
                        severity=Severity.WARNING,
                        message=(
                            "conductors at or near ground level (for example, "
                            "ground-mounted radials) are approximated by a "
                            f"{GROUND_CLEARANCE_M:.3f} m NEC clearance. NEC-2 does "
                            "not model buried or soil-contact wires, so impedance "
                            "and gain may be numerically unreliable. Use a "
                            "sensitivity study and measurement, or raise the "
                            "radial plane."
                        ),
                        field="geometry",
                    )
                )

    if (
        model.environment.ground.kind is not GroundKind.FREE_SPACE
        and spec.far_field.enabled
        and spec.far_field.theta_stop_deg > 90.0
    ):
        diagnostics.append(
            Diagnostic(
                code="far_field.below_ground",
                severity=Severity.WARNING,
                message=(
                    "far-field points below the ground plane were requested; "
                    "use theta <= 90 degrees for ground models"
                ),
                field="far_field",
            )
        )

    return tuple(diagnostics)
