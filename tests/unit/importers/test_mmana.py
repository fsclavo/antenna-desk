# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.importers.mmana import parse_mmana_file


def _maa() -> str:
    return """Two wires
*
7.1
***Wires***
2
-5, 0, 8, 5, 0, 8, 0.001, -1
5, 0, 8, 5, 5, 8, 0.001, -1
*** Source ***
1, 1
w1c, 0.0, 1.0
*** Load ***
0, 1
*** Segmentation ***
400, 40, 2.0, 1
*** G/H/M/R/AzEl/X ***
0, 10.0, 0, 50.0, 0, 0, 0
"""


def test_imports_mmana_wires_and_source() -> None:
    result = parse_mmana_file(_maa())
    parameters = result.parameters

    assert parameters.frequency_hz == pytest.approx(7_100_000.0)
    assert [wire.id for wire in parameters.wires] == ["w1", "w2"]
    assert parameters.feed.wire_id == "w1"
    assert parameters.feed.offset_m == pytest.approx(5.0)
    assert any("ground" in warning.lower() for warning in result.warnings)


def test_rejects_an_maa_file_without_a_source() -> None:
    with pytest.raises(ValueError, match="source"):
        parse_mmana_file("Test\n*\n7.1\n***Wires***\n1\n-5,0,8,5,0,8,0.001,-1\n")
