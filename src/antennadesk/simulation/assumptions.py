# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pure validation of the assumptions made by the NEC-2 adapter."""

from __future__ import annotations

import math

from ..domain.antennas.antenna import AntennaModel
from ..domain.antennas.wire import Wire
from ..domain.common.validation import Diagnostic, Severity
from ..domain.environment.ground import GroundKind
from ..domain.simulation.spec import SimulationSpec

# NEC-2 requires wires to be separated from a ground plane. Ground-mounted
# radials and dipoles are raised by this small physical clearance when the
# canonical model sits exactly on the ground.
GROUND_CLEARANCE_M = 0.01


def _wire_lies_near_ground(wire: Wire) -> bool:
    low = min(wire.start.z_m, wire.end.z_m)
    high = max(wire.start.z_m, wire.end.z_m)
    if not 0.0 <= low < GROUND_CLEARANCE_M:
        return False
    if high < GROUND_CLEARANCE_M:
        return True
    # A non-vertical wire that starts near the ground can be a sloped radial or
    # another intentional ground-level run. Raise the model instead of letting
    # its low endpoint bypass the clearance. Vertical stubs keep their
    # deliberate wire-to-ground connection.
    horizontal = math.hypot(
        wire.end.x_m - wire.start.x_m,
        wire.end.y_m - wire.start.y_m,
    )
    return horizontal > 1e-9


def ground_clearance_offset_m(model: AntennaModel) -> float:
    """Return the NEC ground clearance applied to the whole model.

    Only models that contain a wire lying in or near the ground plane are
    raised. A vertical wire that ends on the ground plane is an intentional
    wire-to-ground connection (for example, a Beverage feed or termination
    stub), not a buried radial, so it must keep its endpoint at z = 0.
    """

    if model.environment.ground.kind is GroundKind.FREE_SPACE:
        return 0.0
    min_z = min(point.z_m for wire in model.wires for point in (wire.start, wire.end))
    if not 0.0 <= min_z < GROUND_CLEARANCE_M:
        return 0.0
    if not any(_wire_lies_near_ground(wire) for wire in model.wires):
        return 0.0
    return GROUND_CLEARANCE_M - min_z


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
        else:
            offset_m = ground_clearance_offset_m(model)
            if offset_m > 0.0:
                diagnostics.append(
                    Diagnostic(
                        code="geometry.ground_clearance",
                        severity=Severity.INFO,
                        message=(
                            f"the model is raised by {offset_m:.3f} m "
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
                                "conductors lying at or near ground level (for example, "
                                "ground-mounted radials) are approximated by a "
                                f"{offset_m:.3f} m NEC clearance. NEC-2 does not "
                                "model buried or soil-contact wires, so impedance "
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
