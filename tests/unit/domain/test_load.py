# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.load import SeriesLoad


def test_series_load_accepts_rlc_values() -> None:
    load = SeriesLoad(
        id="load-1",
        wire_id="radiator",
        offset_m=2.5,
        resistance_ohm=10.0,
        inductance_h=12e-6,
        capacitance_f=30e-12,
    )

    assert load.offset_m == pytest.approx(2.5)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("offset_m", -1.0),
        ("resistance_ohm", -1.0),
        ("inductance_h", -1.0),
        ("capacitance_f", -1.0),
    ],
)
def test_series_load_rejects_negative_values(field: str, value: float) -> None:
    values = {
        "id": "load-1",
        "wire_id": "radiator",
        "offset_m": 1.0,
        "resistance_ohm": 1.0,
    }
    values[field] = value

    with pytest.raises(ValueError):
        SeriesLoad(**values)  # type: ignore[arg-type]


def test_series_load_requires_a_non_zero_element() -> None:
    with pytest.raises(ValueError, match="non-zero"):
        SeriesLoad(id="load-1", wire_id="radiator", offset_m=1.0)


def test_antenna_validates_load_references() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    model = parameters.to_antenna()

    with pytest.raises(ValueError, match="unknown wire"):
        AntennaModel(
            name=model.name,
            design_frequency_hz=model.design_frequency_hz,
            wires=model.wires,
            feed=model.feed,
            loads=(SeriesLoad("load-1", "missing", 1.0, resistance_ohm=1.0),),
        )

    with pytest.raises(ValueError, match="outside wire"):
        AntennaModel(
            name=model.name,
            design_frequency_hz=model.design_frequency_hz,
            wires=model.wires,
            feed=model.feed,
            loads=(SeriesLoad("load-1", "radiator", 21.0, resistance_ohm=1.0),),
        )


def test_with_loads_preserves_the_original_model() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    model = parameters.to_antenna()
    load = SeriesLoad("load-1", "radiator", 10.0, inductance_h=12e-6)

    loaded = model.with_loads((load,))

    assert loaded.loads == (load,)
    assert model.loads == ()
