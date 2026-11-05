# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Evidence level of every catalog template.

`docs/VALIDATION_PLAN.md` defines three evidence levels:

- **A, reference-backed:** compared with a traceable independent source using a
  metric-specific tolerance.
- **B, published/heuristic:** based on a published design rule or starting
  point; structural and scaling tests are still required.
- **C, experimental:** arbitrary or unverified geometry.  Structural tests and
  a visible limitation are required; no accuracy claim is made.

This module is the machine-readable form of that classification.  The catalog
cannot add a template without an entry, and the table in the validation plan is
generated from it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EvidenceLevel(StrEnum):
    REFERENCE = "A"
    PUBLISHED = "B"
    EXPERIMENTAL = "C"


@dataclass(frozen=True, slots=True)
class EvidenceEntry:
    template: str
    level: EvidenceLevel
    source: str
    tolerance: str
    limitation: str


EVIDENCE: dict[str, EvidenceEntry] = {
    "wire_dipole": EvidenceEntry(
        template="wire_dipole",
        level=EvidenceLevel.REFERENCE,
        source=("NEC-2 User's Guide examples 1 and 3; ARRL Antenna Book, 24th ed., Ch. 2, p. 2.12"),
        tolerance="0.05 Ω impedance; 0.15 dB gain",
        limitation="Free-space and the published ground cases only.",
    ),
    "folded_dipole": EvidenceEntry(
        template="folded_dipole",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "ARRL Antenna Book, 24th ed., Ch. 2, pp. 2.12-2.13: an equal-conductor "
            "folded dipole has the same gain and four times the resistance"
        ),
        tolerance="0.2 dB gain; 0.5 on the resistance ratio",
        limitation="No independent absolute impedance reference.",
    ),
    "loop": EvidenceEntry(
        template="loop",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "ARRL Antenna Book, 24th ed., Ch. 5, p. 5.4, for the quad case; "
            "the polygon correction is a calibrated starting rule"
        ),
        tolerance="15 Ω for the quad preset only",
        limitation="Delta and arbitrary polygon side counts are structural.",
    ),
    "quad_loop": EvidenceEntry(
        template="quad_loop",
        level=EvidenceLevel.REFERENCE,
        source="ARRL Antenna Book, 24th ed., Ch. 5, p. 5.4: about 120 Ω at resonance",
        tolerance="15 Ω",
        limitation="Published quad geometry only.",
    ),
    "delta_loop": EvidenceEntry(
        template="delta_loop",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "ON4UN, Low-Band DXing, Ch. 10: resonant delta-loop circumference "
            "is approximately 1.05-1.06 wavelengths"
        ),
        tolerance="1% on the resonant circumference",
        limitation=(
            "Circumference only; feedpoint impedance and polarization depend on "
            "the feed position and height."
        ),
    ),
    "vertical": EvidenceEntry(
        template="vertical",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "ARRL practical length rules 234/f for a quarter-wave vertical and "
            "585/f for a 5/8-wave vertical"
        ),
        tolerance="0.5% on radiator length",
        limitation=(
            "Gain and feedpoint impedance depend on radial count and ground; "
            "those are not independently validated."
        ),
    ),
    "loaded_vertical": EvidenceEntry(
        template="loaded_vertical",
        level=EvidenceLevel.EXPERIMENTAL,
        source="Quarter-wave starting rule plus a series loading-coil model",
        tolerance="Not applicable (structural)",
        limitation="Coil Q and the ground model are not independently validated.",
    ),
    "yagi": EvidenceEntry(
        template="yagi",
        level=EvidenceLevel.REFERENCE,
        source="NBS TN-688 5-element preset, 9.2 dBd (11.35 dBi)",
        tolerance="0.5 dB",
        limitation="Only the published preset; edited element geometry is experimental.",
    ),
    "moxon": EvidenceEntry(
        template="moxon",
        level=EvidenceLevel.REFERENCE,
        source="L. B. Cebik, W4RNL, 'The Moxon Rectangle: A Review', Table 1 and text",
        tolerance="1.5 Ω real; 5 Ω reactance; 0.3 dB gain; better than 30 dB F/B",
        limitation="Published 20 m dimensions only.",
    ),
    "ocfd": EvidenceEntry(
        template="ocfd",
        level=EvidenceLevel.PUBLISHED,
        source="R. Sanders, VK2WB, 'Analysis of the Off Centre Fed (OCF) dipole', Table 1",
        tolerance="Published 200-350 Ω range, not a strict numeric tolerance",
        limitation="The source does not fully specify its EZNEC ground model.",
    ),
    "inverted_v": EvidenceEntry(
        template="inverted_v",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "ARRL, 'Wire Antennas for the Beginner': 120-degree inverted-V total "
            "length is 465.6/f MHz feet"
        ),
        tolerance="1% on total length for the 120-degree case",
        limitation=(
            "The 90-degree case and ground detuning use separate empirical "
            "starting rules; gain and feedpoint impedance are not independently "
            "validated."
        ),
    ),
    "fan_dipole": EvidenceEntry(
        template="fan_dipole",
        level=EvidenceLevel.EXPERIMENTAL,
        source="Per-band half-wave starting rule; mutual coupling is not modeled",
        tolerance="Not applicable (structural)",
        limitation="A coupled fan is not a parallel combination of independent dipoles.",
    ),
    "trap_dipole": EvidenceEntry(
        template="trap_dipole",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "RSARS, 'W3DZZ Multi-band Antenna 80-40-20-15-10m': 33 ft inner and "
            "22 ft outer sections, 7.1 MHz traps, 5.024 µH and 100 pF"
        ),
        tolerance="1% on the 33/22 ft sections; 2% on the trap resonance",
        limitation=(
            "The feed line and tuner are not modeled; the trap is an ideal "
            "parallel LC, and the default starting dimensions are a full-size "
            "80/20 m trap dipole rather than W3DZZ."
        ),
    ),
    "t2fd": EvidenceEntry(
        template="t2fd",
        level=EvidenceLevel.PUBLISHED,
        source="Cebik wide-long broadband starting rule",
        tolerance="Not a strict numeric tolerance",
        limitation="Termination resistor and transformer are ideal.",
    ),
    "endfed": EvidenceEntry(
        template="endfed",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "ARRL End-Fed Half-Wave Antenna Kit: 66 ft on 40 m, 33 ft on 20 m, "
            "16 ft on 10 m, 49:1 transformer, about 2500 Ω; PA9X: counterpoise "
            "0.05λ of the longest wavelength"
        ),
        tolerance="5% on the half-wave wire length; 0.05λ counterpoise; 49:1 ratio",
        limitation=(
            "The 49:1 transformer is an ideal ratio; the counterpoise is a "
            "straight wire; height, ground, and the common-mode choke are not "
            "modeled."
        ),
    ),
    "sloper": EvidenceEntry(
        template="sloper",
        level=EvidenceLevel.EXPERIMENTAL,
        source="End-fed preset with a sloped radiator",
        tolerance="Not applicable (structural)",
        limitation="No independent numerical reference.",
    ),
    "random_wire": EvidenceEntry(
        template="random_wire",
        level=EvidenceLevel.EXPERIMENTAL,
        source="Random-wire geometry with a tuner-assisted band plan",
        tolerance="Not applicable (structural)",
        limitation="No accuracy claim.",
    ),
    "g5rv": EvidenceEntry(
        template="g5rv",
        level=EvidenceLevel.PUBLISHED,
        source="Published G5RV dimensions; lossless transmission-line model",
        tolerance="Not a strict numeric tolerance",
        limitation="Line loss is not modeled; matching depends on the installation.",
    ),
    "zs6bkw": EvidenceEntry(
        template="zs6bkw",
        level=EvidenceLevel.REFERENCE,
        source=(
            "Cebik/W4RNL SWR values 1.15, 1.47, and 1.56 at 40/20/10 m; commercial 27.5 m variant"
        ),
        tolerance="0.3 SWR",
        limitation="Lossless line model.",
    ),
    "zepp": EvidenceEntry(
        template="zepp",
        level=EvidenceLevel.EXPERIMENTAL,
        source="Classic Zepp starting geometry; simplified lossless line",
        tolerance="Not applicable (structural)",
        limitation="Experimental; no independent numerical reference.",
    ),
    "j_pole": EvidenceEntry(
        template="j_pole",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "M0UKD, 'Slim Jim and J Pole calculator': a J pole is 0.75λ tall, "
            "with a 0.5λ radiator and a 0.25λ matching stub; ARRL QST, Feb 2003, "
            "conventional 2 m J-pole dimensions"
        ),
        tolerance=(
            "1% on the half-wave and quarter-wave sections; 10% on the overall "
            "height against the ARRL 2 m construction"
        ),
        limitation=(
            "Starting dimensions only; the 50 Ω feed offset, ground, mast, and "
            "feed-line coupling are not independently validated."
        ),
    ),
    "slim_jim": EvidenceEntry(
        template="slim_jim",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "F. Judd, G2BCX, 'Slim Jim - 2 metre aerial', Practical Wireless, "
            "1978: about 60 in overall at 145 MHz; M0UKD calculator: 0.5λ "
            "radiator above a 0.25λ stub with a small gap"
        ),
        tolerance="1% on the half-wave and quarter-wave sections; 5% on the overall length at 2 m",
        limitation=(
            "Starting dimensions only; the feed point, fold spacing, and the "
            "effect of the feed line are not independently validated."
        ),
    ),
    "ringo": EvidenceEntry(
        template="ringo",
        level=EvidenceLevel.EXPERIMENTAL,
        source="Ringo radiator and ring starting geometry",
        tolerance="Not applicable (structural)",
        limitation="No independent numerical reference.",
    ),
    "doublet": EvidenceEntry(
        template="doublet",
        level=EvidenceLevel.EXPERIMENTAL,
        source="Doublet geometry with a feed line",
        tolerance="Not applicable (structural)",
        limitation="No independent numerical reference.",
    ),
    "custom": EvidenceEntry(
        template="custom",
        level=EvidenceLevel.EXPERIMENTAL,
        source="User-defined wire geometry",
        tolerance="Not applicable",
        limitation="No accuracy claim; imports and diagnostics only.",
    ),
}


def evidence_for(template: str) -> EvidenceEntry:
    return EVIDENCE[template]


def render_markdown_table() -> str:
    lines = [
        "| Template | Level | Source | Tolerance | Limitation |",
        "|---|---|---|---|---|",
    ]
    for entry in EVIDENCE.values():
        lines.append(
            f"| `{entry.template}` | {entry.level.value} | {entry.source} "
            f"| {entry.tolerance} | {entry.limitation} |"
        )
    return "\n".join(lines)
