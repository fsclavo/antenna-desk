from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.common.validation import DomainValidationError, Severity
from antennadesk.domain.environment.environment import Environment


def _wire(
    wire_id: str = "radiator",
    start: Point3D | None = None,
    end: Point3D | None = None,
) -> Wire:
    return Wire(
        id=wire_id,
        start=start if start is not None else Point3D(-10.0, 0.0, 8.0),
        end=end if end is not None else Point3D(10.0, 0.0, 8.0),
        radius_m=0.001,
        material=COPPER,
    )


def _antenna(
    *,
    name: str = "Dipole",
    frequency_hz: float = 7_100_000.0,
    wires: tuple[Wire, ...] | None = None,
    feed: FeedPoint | None = None,
) -> AntennaModel:
    return AntennaModel(
        name=name,
        design_frequency_hz=frequency_hz,
        wires=wires if wires is not None else (_wire(),),
        feed=feed if feed is not None else FeedPoint("radiator", 10.0),
        environment=Environment(),
    )


def test_valid_antenna_has_no_diagnostics() -> None:
    antenna = _antenna()
    assert antenna.validate() == ()
    assert antenna.feed_wire.id == "radiator"
    assert antenna.wire_by_id("radiator") == antenna.wires[0]


def test_empty_name_is_rejected() -> None:
    with pytest.raises(DomainValidationError) as error:
        _antenna(name=" ")
    assert any(d.code == "antenna.name.empty" for d in error.value.diagnostics)


@pytest.mark.parametrize("frequency", [0.0, -1.0, math.nan])
def test_invalid_frequency_is_rejected(frequency: float) -> None:
    with pytest.raises(DomainValidationError) as error:
        _antenna(frequency_hz=frequency)
    assert any(d.code == "antenna.frequency.invalid" for d in error.value.diagnostics)


def test_empty_wire_list_is_rejected() -> None:
    with pytest.raises(DomainValidationError) as error:
        _antenna(wires=(), feed=FeedPoint("radiator", 0.0))
    assert any(d.code == "antenna.wires.empty" for d in error.value.diagnostics)


def test_duplicate_wire_ids_are_rejected() -> None:
    first = _wire()
    second = _wire(start=Point3D(0.0, 0.0, 8.0), end=Point3D(1.0, 0.0, 8.0))
    with pytest.raises(DomainValidationError) as error:
        _antenna(wires=(first, second))
    assert any(d.code == "antenna.wire.duplicate_id" for d in error.value.diagnostics)


def test_unknown_feed_wire_is_rejected() -> None:
    with pytest.raises(DomainValidationError) as error:
        _antenna(feed=FeedPoint("missing", 0.0))
    assert any(d.code == "antenna.feed.unknown_wire" for d in error.value.diagnostics)


def test_out_of_range_feed_is_rejected() -> None:
    with pytest.raises(DomainValidationError) as error:
        _antenna(feed=FeedPoint("radiator", 25.0))
    assert any(d.code == "antenna.feed.out_of_range" for d in error.value.diagnostics)


def test_feed_at_wire_end_is_a_warning() -> None:
    antenna = _antenna(feed=FeedPoint("radiator", 20.0))
    diagnostics = antenna.validate()
    assert any(
        diagnostic.code == "antenna.feed.at_wire_end" and diagnostic.severity is Severity.WARNING
        for diagnostic in diagnostics
    )


def test_unknown_wire_lookup_raises_key_error() -> None:
    with pytest.raises(KeyError):
        _antenna().wire_by_id("missing")
