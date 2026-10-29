"""Deterministic model/spec fingerprints."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from ..domain.antennas.antenna import AntennaModel
from ..domain.simulation.spec import SimulationSpec

FINGERPRINT_FORMAT = "antennadesk-simulation-v1"


def model_fingerprint(model: AntennaModel, spec: SimulationSpec) -> str:
    payload = {
        "format": FINGERPRINT_FORMAT,
        "model": asdict(model),
        "spec": asdict(spec),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
