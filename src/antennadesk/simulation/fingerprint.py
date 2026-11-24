# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic model/spec fingerprints."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from ..domain.antennas.antenna import AntennaModel
from ..domain.simulation.spec import SimulationSpec

FINGERPRINT_FORMAT = "antennadesk-simulation-v1"


def model_fingerprint(model: AntennaModel, spec: SimulationSpec) -> str:
    spec_payload = asdict(spec)
    # Runtime-only diagnostic context; adding it must not invalidate stored
    # fingerprints or make a completed result look stale.
    spec_payload.pop("matching_network_origin", None)
    if spec_payload.get("site_ground") is None:
        spec_payload.pop("site_ground", None)
    payload = {
        "format": FINGERPRINT_FORMAT,
        "model": asdict(model),
        "spec": spec_payload,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
