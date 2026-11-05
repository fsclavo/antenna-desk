# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Report-only performance benchmarks for the hot data paths.

Run with::

    uv run pytest benchmarks --benchmark-only -p no:pytest-qt --benchmark-json=benchmark.json

The CI job uploads the JSON artifact but does not enforce a threshold yet, so
machine-to-machine noise cannot fail a build. The pytest-qt plugin is disabled
because these benchmarks use only domain and persistence code.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.projects.project import Project
from antennadesk.domain.simulation.pattern import front_to_back_db, max_power_gain_db
from antennadesk.domain.simulation.result import FarFieldPoint
from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.simulation.nec2.parser import parse_nec2_output

_NEC2_BLOCK = """\
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

NEC2_OUTPUT = "".join(
    _NEC2_BLOCK.replace("2.9980E+02", f"{299.8 + index:.4E}") for index in range(10)
)
PATTERN = tuple(
    FarFieldPoint(
        theta_deg=float(index % 181),
        phi_deg=float((index * 7) % 360),
        gain_vertical_db=2.0 + math.sin(index / 10.0),
        gain_horizontal_db=1.0,
        gain_total_db=2.0 + math.sin(index / 10.0),
        axial_ratio=0.0,
        tilt_deg=0.0,
        polarization="LINEAR",
        e_theta_magnitude_v_per_m=1.0,
        e_theta_phase_deg=0.0,
        e_phi_magnitude_v_per_m=0.0,
        e_phi_phase_deg=0.0,
    )
    for index in range(10_000)
)


@pytest.mark.benchmark
def test_parse_nec2_output(benchmark) -> None:
    parsed = benchmark(parse_nec2_output, NEC2_OUTPUT)

    assert len(parsed.frequencies) == 10


@pytest.mark.benchmark
def test_pattern_metrics_on_a_large_pattern(benchmark) -> None:
    def metrics() -> tuple[float | None, float | None]:
        return max_power_gain_db(PATTERN), front_to_back_db(PATTERN)

    gains = benchmark(metrics)

    assert gains[0] is not None
    assert gains[1] is not None


@pytest.fixture
def project() -> Project:
    return CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="benchmark",
            variant_name="Initial",
            parameters=DipoleParameters(
                frequency_hz=7_100_000.0,
                total_length_m=20.0,
                height_m=10.0,
            ),
        )
    )


@pytest.mark.benchmark
def test_project_save_and_load(
    benchmark,
    project: Project,
    tmp_path: Path,
) -> None:
    repository = JsonProjectRepository()
    path = tmp_path / "benchmark.antennadesk"

    def save_load() -> None:
        repository.save(project, path)
        repository.load(path)

    benchmark(save_load)
