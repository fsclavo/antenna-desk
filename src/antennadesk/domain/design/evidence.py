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
    "magnetic_loop": EvidenceEntry(
        template="magnetic_loop",
        level=EvidenceLevel.EXPERIMENTAL,
        source=(
            "Small-loop geometry with an ideal series tuning capacitor; no "
            "independent numerical reference for the generated design"
        ),
        tolerance="Not applicable (structural)",
        limitation=(
            "The capacitor is an ideal series RLC element with optional ESR; the "
            "coupling loop, capacitor voltage, and detailed loss mechanisms are "
            "not modeled. Tune the capacitance with the solver or a measurement."
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
            "Gain and feedpoint impedance depend on radial count, ground, and any "
            "capacitive top hat; those are not independently validated."
        ),
    ),
    "loaded_vertical": EvidenceEntry(
        template="loaded_vertical",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "K7MEM, 'Short Loaded Vertical', citing ARRL Antenna Book, 17th ed., "
            "pp. 16-5 to 16-11: a 102 in whip at 14.1 MHz needs a 4.511 µH base "
            "loading coil"
        ),
        tolerance="5% on the 102 in whip length and the 4.511 µH coil inductance",
        limitation=(
            "Only the published 14.1 MHz mobile example is reference-backed. The "
            "coil is an ideal series load; coil Q, ground, and the mobile "
            "installation are not modeled. Other loaded verticals remain "
            "experimental."
        ),
    ),
    "yagi": EvidenceEntry(
        template="yagi",
        level=EvidenceLevel.REFERENCE,
        source="NBS TN-688 5-element preset, 9.2 dBd (11.35 dBi)",
        tolerance="0.5 dB",
        limitation=(
            "Only the published preset; edited element geometry is experimental. "
            "The optional folded driven element and beta/hairpin match change "
            "feed impedance and have no independent impedance reference. Gamma "
            "matches are not modeled by NEC-2 here."
        ),
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
    "inverted_l": EvidenceEntry(
        template="inverted_l",
        level=EvidenceLevel.EXPERIMENTAL,
        source="Bent end-fed wire starting geometry; no independent numerical reference",
        tolerance="Not applicable (structural)",
        limitation=(
            "Vertical height, horizontal run, ground, and matching determine the "
            "result; tune them with the solver or a measurement."
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
        level=EvidenceLevel.PUBLISHED,
        source=(
            "Chameleon Antenna CHA LEFS Feather operator's manual: 66.5 ft "
            "EFHW radiator, 49:1 transformer, far end about 25 ft, feed "
            "transformer about 3 ft; tested 40/20/15/10 m sloper patterns"
        ),
        tolerance="5% on the radiator length and deployment heights",
        limitation=(
            "The transformer, feed line, choke, and site coupling are not "
            "modeled; the editor's default sloper is 10 m to 0.5 m, so the "
            "published geometry is a starting point, not the default."
        ),
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
        level=EvidenceLevel.PUBLISHED,
        source=(
            "ARRL Antenna Book, 24th ed., Ch. 20: a true Zepp is an end-fed "
            "half-wave radiator matched by a quarter-wave open-wire line; "
            "W8JI, 'End-fed vertical J-pole and horizontal Zepp': a 1/4λ stub "
            "feeding a 1/2λ element with a 1:1 current balun at the tuner"
        ),
        tolerance=(
            "5% on the half-wave and quarter-wave starting lengths; the "
            "conductor spacing and radius set the stub impedance"
        ),
        limitation=(
            "Starting dimensions only. The 1:1 common-mode choke, coaxial feed "
            "line, common-mode current, and installation are not modeled; the "
            "stub balance degrades on even harmonics and the match requires "
            "tuning."
        ),
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
    "half_square": EvidenceEntry(
        template="half_square",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "L. B. Cebik, W4RNL, 'SCVs: A Family Album', Table 1 (7.15 MHz): "
            "62.4 ft horizontal by 39 ft vertical, about 4.6 dBi and 65 ohm"
        ),
        tolerance="5% on the frequency-scaled horizontal and vertical dimensions",
        limitation=(
            "Published free-space, maximum-gain starting geometry only. Pattern, "
            "feedpoint impedance, ground, support height, feed line, and the "
            "matching network are not independently validated."
        ),
    ),
    "bobtail_curtain": EvidenceEntry(
        template="bobtail_curtain",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "L. B. Cebik, W4RNL, 'SCVs: A Family Album', Table 1 (7.15 MHz): "
            "125 ft horizontal by 38 ft vertical, about 6.3 dBi and 40 ohm at "
            "the center-wire/top-horizontal junction"
        ),
        tolerance="5% on the frequency-scaled horizontal and vertical dimensions",
        limitation=(
            "Published free-space, maximum-gain starting geometry only. Pattern, "
            "feedpoint impedance versus feed height, ground, support height, and "
            "the feed line are not independently validated."
        ),
    ),
    "biquad": EvidenceEntry(
        template="biquad",
        level=EvidenceLevel.EXPERIMENTAL,
        source=(
            "Quarter-wave loop side and eighth-wave reflector spacing are "
            "starting heuristics; no independent numerical reference for the "
            "generated geometry"
        ),
        tolerance="Not applicable (structural)",
        limitation=(
            "The model is a wire approximation with shared horizontal rails and "
            "a rectangular wire reflector. Gain, feedpoint impedance, bandwidth, "
            "reflector construction, and ground effects are not independently "
            "validated. Tune or measure the installed antenna."
        ),
    ),
    "double_biquad": EvidenceEntry(
        template="double_biquad",
        level=EvidenceLevel.EXPERIMENTAL,
        source=(
            "Four-loop extension of the same quarter-wave starting heuristic; no "
            "independent numerical reference"
        ),
        tolerance="Not applicable (structural)",
        limitation=(
            "The extra loop pair changes the current distribution and feed "
            "impedance; neither is independently validated. Use it as a "
            "starting point and verify with simulation or measurement."
        ),
    ),
    "beverage": EvidenceEntry(
        template="beverage",
        level=EvidenceLevel.EXPERIMENTAL,
        source=(
            "One-wavelength horizontal wire with a resistive termination to "
            "ground; the starting length and 500 ohm termination are heuristics, "
            "not an independent receiving-performance reference"
        ),
        tolerance="Not applicable (structural)",
        limitation=(
            "The termination is a short vertical wire with a series resistor, not "
            "a complete ground system. Gain is low and the pattern, termination "
            "efficiency, ground, and feed line are not independently validated. "
            "Use relative simulations and a measurement."
        ),
    ),
    "loaded_dipole": EvidenceEntry(
        template="loaded_dipole",
        level=EvidenceLevel.EXPERIMENTAL,
        source=(
            "Symmetric series R-L loading coils or open links on a center-fed "
            "dipole; no independent numerical reference for the generated "
            "portable geometry"
        ),
        tolerance="Not applicable (structural)",
        limitation=(
            "The coil is an ideal series R-L load. Core loss, self-capacitance, "
            "link contact resistance, and the portable installation are not "
            "modeled. The linked state only removes the outer sections; it does "
            "not model the physical link hardware."
        ),
    ),
    "doublet": EvidenceEntry(
        template="doublet",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "VU3DXR, '94-Foot Multi Band Doublet Antenna': 94 ft total, 41 ft "
            "of 450 Ω ladder line, 1:1 current balun, and a tuner"
        ),
        tolerance="5% on the radiator and feed-line lengths; 450 Ω line",
        limitation=(
            "The tuner and balun are not modeled; feed-line length, impedance, "
            "and installation dominate the match. The editor default is a "
            "half-wave dipole, so the 94 ft design is a starting point."
        ),
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
