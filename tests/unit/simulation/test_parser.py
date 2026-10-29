from __future__ import annotations

import pytest

from antennadesk.simulation.nec2.parser import Nec2ParseError, parse_nec2_output

COMPLETE_OUTPUT = """\
                               --------- FREQUENCY --------
                                FREQUENCY : 2.9980E+02 MHz
                                WAVELENGTH: 1.0000E+00 Mtr

                        --------- ANTENNA INPUT PARAMETERS ---------
  TAG   SEG       VOLTAGE (VOLTS)         CURRENT (AMPS)         IMPEDANCE (OHMS)        ADMITTANCE (MHOS)     POWER
  No:   No:     REAL      IMAGINARY     REAL      IMAGINARY     REAL      IMAGINARY    REAL       IMAGINARY   (WATTS)
    1     4  1.0000E+00  0.0000E+00  9.2058E-03 -5.1547E-03  8.2698E+01  4.6306E+01  9.2058E-03 -5.1547E-03  4.6029E-03

                           -------- CURRENTS AND LOCATION --------
                                  DISTANCES IN WAVELENGTHS

   SEG  TAG    COORDINATES OF SEGM CENTER     SEGM    ------------- CURRENT (AMPS) -------------
   No:  No:       X         Y         Z      LENGTH     REAL      IMAGINARY    MAGN        PHASE
     1    1   -0.2143    0.0000    0.0000   0.07143  2.3592E-03 -1.6881E-03  2.9010E-03  -35.584
     2    1   -0.1429    0.0000    0.0000   0.07143  5.9998E-03 -4.0463E-03  7.2367E-03  -33.996

                               ---------- POWER BUDGET ---------
                               INPUT POWER   =  4.6029E-03 Watts
                               RADIATED POWER=  4.6029E-03 Watts
                               STRUCTURE LOSS=  0.0000E+00 Watts
                               NETWORK LOSS  =  0.0000E+00 Watts
                               EFFICIENCY    =  100.00 Percent

                             ---------- RADIATION PATTERNS -----------

 ---- ANGLES -----     ----- POWER GAINS -----       ---- POLARIZATION ----   ---- E(THETA) ----    ----- E(PHI) ------
  THETA      PHI       VERTC    HORIZ    TOTAL       AXIAL      TILT  SENSE   MAGNITUDE    PHASE    MAGNITUDE     PHASE
 DEGREES   DEGREES        DB       DB       DB       RATIO   DEGREES            VOLTS/M   DEGREES     VOLTS/M   DEGREES
    0.00      0.00      2.14  -999.99     2.14      0.0000     -0.00 LINEAR  6.7245E-01   -122.28  0.0000E+00      0.00
   90.00      0.00   -999.99  -999.99  -999.99      0.0000      0.00         2.6497E-12     58.27  0.0000E+00      0.00
  180.00      0.00      2.14  -999.99     2.14      0.0000      0.00 LINEAR  6.7245E-01     57.72  0.0000E+00      0.00
"""


def test_parse_complete_output() -> None:
    parsed = parse_nec2_output(COMPLETE_OUTPUT)

    assert len(parsed.frequencies) == 1
    frequency = parsed.frequencies[0]
    assert frequency.frequency_hz == pytest.approx(299_800_000.0)
    assert len(frequency.input_parameters) == 1

    input_parameters = frequency.input_parameters[0]
    assert input_parameters.tag == 1
    assert input_parameters.segment == 4
    assert input_parameters.impedance_ohm == pytest.approx(complex(82.698, 46.306))
    assert input_parameters.power_w == pytest.approx(4.6029e-03)

    assert len(frequency.currents) == 2
    assert frequency.currents[0].segment == 1
    assert frequency.currents[0].current_a == pytest.approx(complex(2.3592e-03, -1.6881e-03))

    assert frequency.power_budget is not None
    assert frequency.power_budget.input_w == pytest.approx(4.6029e-03)
    assert frequency.power_budget.efficiency_percent == pytest.approx(100.0)

    assert len(frequency.far_field) == 3
    maximum = frequency.far_field[0]
    assert maximum.theta_deg == pytest.approx(0.0)
    assert maximum.gain_total_db == pytest.approx(2.14)
    assert maximum.polarization == "LINEAR"
    assert maximum.e_theta_magnitude_v_per_m == pytest.approx(0.67245)

    null = frequency.far_field[1]
    assert null.gain_total_db is None
    assert null.polarization is None


def test_manual_style_frequency_separator() -> None:
    text = COMPLETE_OUTPUT.replace(
        "FREQUENCY : 2.9980E+02 MHz",
        "FREQUENCY = 2.9980E+02 MHZ",
    )
    parsed = parse_nec2_output(text)
    assert parsed.frequencies[0].frequency_hz == pytest.approx(299_800_000.0)


def test_multiple_frequencies_are_associated_with_their_blocks() -> None:
    second = COMPLETE_OUTPUT.replace("2.9980E+02", "3.0000E+02").replace("8.2698E+01", "8.0000E+01")
    parsed = parse_nec2_output(COMPLETE_OUTPUT + second)

    assert len(parsed.frequencies) == 2
    assert parsed.frequencies[0].frequency_hz == pytest.approx(299_800_000.0)
    assert parsed.frequencies[1].frequency_hz == pytest.approx(300_000_000.0)
    assert parsed.frequencies[0].input_parameters[0].impedance_ohm.real == pytest.approx(82.698)
    assert parsed.frequencies[1].input_parameters[0].impedance_ohm.real == pytest.approx(80.0)


def test_missing_frequency_is_rejected() -> None:
    with pytest.raises(Nec2ParseError, match="before a frequency"):
        parse_nec2_output(
            "ANTENNA INPUT PARAMETERS\n"
            "  No:   No:     REAL      IMAGINARY\n"
            "    1     1  1.0  0.0  0.1  0.0  50.0  0.0  0.1  0.0  0.01\n"
        )


def test_empty_output_is_rejected() -> None:
    with pytest.raises(Nec2ParseError, match="no frequency"):
        parse_nec2_output("")
