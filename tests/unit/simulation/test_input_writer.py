# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.nec2.input_writer import write_nec2_input


def _manual_model() -> AntennaModel:
    return DipoleParameters(
        frequency_hz=299_800_000.0,
        total_length_m=0.5,
        height_m=0.0,
        wire_radius_m=0.001,
    ).to_antenna(name="Manual example")


def _spec(
    *,
    segments: int = 7,
    frequency_plan: FrequencyPlan | None = None,
    extended_thin_wire_kernel: bool = False,
    include_conductor_losses: bool = False,
    far_field: FarFieldRequest | None = None,
) -> SimulationSpec:
    return SimulationSpec(
        frequency_plan=frequency_plan or FrequencyPlan.single(299_800_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=segments),
        extended_thin_wire_kernel=extended_thin_wire_kernel,
        include_conductor_losses=include_conductor_losses,
        far_field=far_field or FarFieldRequest(enabled=False),
    )


def test_free_space_single_frequency_deck() -> None:
    deck = write_nec2_input(_manual_model(), _spec())

    assert "CM AntennaDesk generated NEC-2 input" in deck.text
    assert "GW 1 7 -0.250000000 0.000000000 0.000000000 " in deck.text
    assert "GE 0" in deck.text
    assert "FR 0 1 0 0 299.800000000 0.000000000" in deck.text
    assert "EX 0 1 4 0 1.0" in deck.text
    assert "XQ" in deck.text
    assert "RP " not in deck.text
    assert deck.text.endswith("\n")
    assert deck.feed_tag == 1
    assert deck.feed_segment == 4


def test_perfect_ground_deck() -> None:
    model = DipoleParameters(
        frequency_hz=299_800_000.0,
        total_length_m=0.5,
        height_m=0.0,
        wire_radius_m=0.001,
        ground=GroundModel.perfect(),
    ).to_antenna()
    deck = write_nec2_input(model, _spec())

    assert "GE 1" in deck.text
    assert "GN 1" in deck.text


def test_finite_ground_deck() -> None:
    model = DipoleParameters(
        frequency_hz=30_000_000.0,
        total_length_m=5.0,
        height_m=2.0,
        wire_radius_m=0.3,
        ground=GroundModel.finite(
            relative_permittivity=6.0,
            conductivity_s_per_m=0.001,
        ),
    ).to_antenna()
    deck = write_nec2_input(model, _spec(frequency_plan=FrequencyPlan.single(30_000_000.0)))

    assert "GE 1" in deck.text
    assert "GN 0 0 0 0 6.000000000 0.001000000" in deck.text


def test_extended_kernel_and_frequency_sweep() -> None:
    deck = write_nec2_input(
        _manual_model(),
        _spec(
            frequency_plan=FrequencyPlan.sweep(6_900_000.0, 7_300_000.0, 21),
            extended_thin_wire_kernel=True,
        ),
    )

    assert "EK" in deck.text
    assert "FR 0 21 0 0 6.900000000 0.020000000" in deck.text


def test_far_field_request_replaces_xq() -> None:
    deck = write_nec2_input(
        _manual_model(),
        _spec(far_field=FarFieldRequest(enabled=True)),
    )

    assert "RP 0 19 1 1000 0.000000 0.000000 10.000000 0.000000" in deck.text
    assert "XQ" not in deck.text


def test_multi_wire_tags_and_feed_mapping() -> None:
    first = Wire(
        id="first",
        start=Point3D(-1.0, 0.0, 0.0),
        end=Point3D(0.0, 0.0, 0.0),
        radius_m=0.001,
        material=COPPER,
    )
    second = Wire(
        id="second",
        start=Point3D(0.0, 0.0, 0.0),
        end=Point3D(1.0, 0.0, 0.0),
        radius_m=0.001,
        material=COPPER,
    )
    model = AntennaModel(
        name="two wires",
        design_frequency_hz=7_100_000.0,
        wires=(first, second),
        feed=FeedPoint("second", 0.5),
    )
    deck = write_nec2_input(model, _spec(segments=10))

    assert "GW 1 10 " in deck.text
    assert "GW 2 10 " in deck.text
    assert "EX 0 2 6 0 1.0" in deck.text
    assert deck.layout.wires[0].first_segment == 1
    assert deck.layout.wires[1].first_segment == 11


def test_conductor_loss_card_is_emitted() -> None:
    deck = write_nec2_input(
        _manual_model(),
        _spec(include_conductor_losses=True),
    )

    assert "LD 5 1 0 0 58000000.000000000" in deck.text


def test_series_load_card_is_emitted_on_the_mapped_segment() -> None:
    from antennadesk.domain.antennas.load import SeriesLoad

    load = SeriesLoad(
        id="load-1",
        wire_id="radiator",
        offset_m=0.25,
        resistance_ohm=25.0,
        inductance_h=12e-6,
        capacitance_f=30e-12,
    )
    model = _manual_model().with_loads((load,))
    deck = write_nec2_input(model, _spec(segments=7))

    assert "LD 0 1 4 4 25.000000000 0.000012000 0.000000000030" in deck.text


def test_parallel_load_card_is_emitted_as_ld1() -> None:
    from antennadesk.domain.antennas.load import ParallelLoad

    load = ParallelLoad(
        id="load-1",
        wire_id="radiator",
        offset_m=0.25,
        inductance_h=12e-6,
        capacitance_f=30e-12,
    )
    deck = write_nec2_input(_manual_model().with_loads((load,)), _spec(segments=7))

    assert "LD 1 1 4 4 0.000000000 0.000012000 0.000000000030" in deck.text


def test_loaded_vertical_emits_its_loading_coil_on_the_radiator() -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=2.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=1.0,
        loading_coil_inductance_h=12e-6,
        loading_coil_resistance_ohm=0.5,
    )
    deck = write_nec2_input(parameters.to_antenna(name="Loaded vertical"), _spec(segments=7))

    assert "LD 0 1 4 4 0.500000000 0.000012000 0.000000000000" in deck.text


def test_trap_dipole_emits_parallel_traps_on_both_sides() -> None:
    from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters

    parameters = TrapDipoleParameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=14_100_000.0,
        inner_length_m=10.0,
        outer_length_m=5.0,
        trap_frequency_hz=14_100_000.0,
        trap_inductance_h=10e-6,
        height_m=12.0,
    )
    deck = write_nec2_input(parameters.to_antenna(name="Trap dipole"), _spec(segments=7))

    assert "LD 1 1 2 2 0.000000000 0.000010000 0.000000000013" in deck.text
    assert "LD 1 1 6 6 0.000000000 0.000010000 0.000000000013" in deck.text


def test_transmission_line_card_uses_electrical_length() -> None:
    from antennadesk.domain.antennas.transmission_line import TransmissionLine

    line = TransmissionLine(
        id="line-1",
        start_wire_id="radiator",
        start_offset_m=0.1,
        end_wire_id="radiator",
        end_offset_m=0.4,
        characteristic_impedance_ohm=50.0,
        length_m=1.0,
        velocity_factor=0.5,
    )
    model = _manual_model().with_transmission_lines((line,))
    deck = write_nec2_input(model, _spec(segments=7))

    assert (
        "TL 1 2 1 6 50.000000000 2.000000000 0.000000000 0.000000000 0.000000000 0.000000000"
    ) in deck.text


def test_load_card_uses_local_segment_number_for_later_wires() -> None:
    from antennadesk.domain.antennas.load import SeriesLoad
    from antennadesk.domain.antennas.materials import COPPER

    second = Wire(
        id="second",
        start=Point3D(0.0, 0.0, 10.0),
        end=Point3D(0.0, 0.0, 10.5),
        radius_m=0.001,
        material=COPPER,
    )
    model = _manual_model().with_transmission_lines(())  # keep the first wire
    model = AntennaModel(
        name="Two wires",
        design_frequency_hz=299_800_000.0,
        wires=(*model.wires, second),
        feed=model.feed,
        environment=model.environment,
        loads=(SeriesLoad("load-1", "second", 0.25, resistance_ohm=50.0),),
    )

    deck = write_nec2_input(model, _spec(segments=7))

    assert "LD 0 2 4 4 50.000000000" in deck.text
