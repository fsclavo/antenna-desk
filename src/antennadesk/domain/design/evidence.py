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
        limitation=(
            "Free-space and the published ground cases only. Optional wire sag "
            "uses a nine-segment parabolic approximation and is not part of the "
            "published reference comparison."
        ),
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
            "feed impedance and have no independent impedance reference. "
            "Tapered tips are geometric only; boom-mounting correction is not "
            "modeled. Gamma matches are not modeled by NEC-2 here."
        ),
    ),
    "moxon": EvidenceEntry(
        template="moxon",
        level=EvidenceLevel.REFERENCE,
        source="L. B. Cebik, W4RNL, 'The Moxon Rectangle: A Review', Table 1 and text",
        tolerance="1.5 Ω real; 5 Ω reactance; 0.3 dB gain; better than 30 dB F/B",
        limitation=(
            "Reference-backed at 14.17 MHz only; dimensions scaled to another "
            "frequency or edited are a heuristic starting point."
        ),
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
    "shortened_endfed_80_10": EvidenceEntry(
        template="shortened_endfed_80_10",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "Steve Nichols G0KYA, 'A shortened multi-band End-Fed Half Wave "
            "(EFHW) antenna for 80-10m'; EA7EER, 'Antena End Fed para 10-15-20-40 "
            "y 80 m'; G4WIF, 'End Fed Half Wave Antenna' (20.35 m + 110 µH + "
            "2.39 m, 49:1, 100 pF)"
        ),
        tolerance=(
            "Starting dimensions: 20.35 m lower section, 110 µH coil, 2.39 m "
            "top section; published SWR 1.2-3.0 on 80 m and 1.0-1.2 on 40 m"
        ),
        limitation=(
            "Starting dimensions only; the published inverted-L installation is "
            "modeled as a straight wire. The transformer, 100 pF matching "
            "capacitor, common-mode choke, ground, and matching losses are not "
            "modeled. The cited comparison is 8-12 dB below a dipole on 80 m. "
            "Scaled or edited geometry is experimental."
        ),
    ),
    "shortened_endfed_40_10": EvidenceEntry(
        template="shortened_endfed_40_10",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "radioaficion.com, PA0EJH design, kx4o schematic: 40-20-10 m "
            "shortened EFHW with 10.01 m lower section, 23 µH coil, 1.85 m top "
            "section, 49:1 transformer, and 100 pF matching capacitor"
        ),
        tolerance="Starting dimensions only; no independent R/X or pattern tolerance is published",
        limitation=(
            "The matching unit, 100 pF capacitor, choke, ground, and installation "
            "are not modeled, and the model uses a straight wire. CA4EMT "
            "documents a different 40-20-10 variant (34 µH, 1.6 m top, 1:8, "
            "150 pF); this preset follows the 23 µH/100 pF schematic. Scaled or "
            "edited geometry is experimental."
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
        level=EvidenceLevel.PUBLISHED,
        source=(
            "Martybugs, 'Biquad Antenna Construction' (after Trevor Marshall), "
            "2.44 GHz: two square loops with quarter-wave sides (about 31 mm), "
            "15 mm reflector spacing, and a 123 mm square solid reflector; "
            "measured 11-12 dBi"
        ),
        tolerance="2% on loop side; 10% on reflector spacing",
        limitation=(
            "Only the starting loop side and spacing are reference-backed. The "
            "model uses a wire-rectangle reflector and shared rails, not the "
            "published solid reflector, so gain, feedpoint impedance, bandwidth, "
            "and ground effects are not reproduced. Tune or measure the "
            "installed antenna."
        ),
    ),
    "double_biquad": EvidenceEntry(
        template="double_biquad",
        level=EvidenceLevel.EXPERIMENTAL,
        source=(
            "Martybugs, 'Double Biquad Antenna', 2.4 GHz: two biquads side by "
            "side on a 110 x 220 mm solid reflector, about 13-14 dBi; the "
            "template is a four-loop vertical stack with a wire reflector"
        ),
        tolerance="Not applicable (structural mismatch)",
        limitation=(
            "The published double biquad is a side-by-side pair on a solid "
            "reflector, while the template stacks four loops vertically around "
            "shared rails with a wire reflector. The different topology changes "
            "the current distribution and feed impedance, so the published gain "
            "and dimensions are not a direct reference. Keep experimental."
        ),
    ),
    "beverage": EvidenceEntry(
        template="beverage",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "W. Silver, N0AX, and F. Donovan, W3LPL, 'The Beverage Antenna, 100 "
            "Years Later', QST, November 2021, pp. 55-57: a one-wavelength "
            "starting length, 500 ohm termination, and 6-10 ft typical height"
        ),
        tolerance="1% on the one-wavelength starting length; 500 ohm nominal termination",
        limitation=(
            "Only the starting length, termination, and height rule are "
            "reference-backed. The termination is a short vertical wire with a "
            "series resistor, not a complete ground system. Gain, pattern, "
            "termination efficiency, ground conductivity, and feed line are not "
            "independently validated."
        ),
    ),
    "loaded_dipole": EvidenceEntry(
        template="loaded_dipole",
        level=EvidenceLevel.EXPERIMENTAL,
        source=(
            "R. Hiller, W5RH, 'Designing a Coil-Loaded (short) Dipole', BVARC, "
            "3.91 MHz: 62 ft total, coils about 50% out each side, 38.6 uH "
            "each; EZNEC feed resistance 8/21/25 ohm at 25/35/50 ft"
        ),
        tolerance="Not applicable (ground model unspecified)",
        limitation=(
            "The published example is a specific 3.91 MHz, 62 ft portable "
            "dipole; its EZNEC ground model is not stated, so the feed "
            "resistance could not be reproduced reliably. The template's "
            "generic defaults use a different coil position. Coil Q, core loss, "
            "self-capacitance, link contact resistance, and the portable "
            "installation are not modeled. Keep experimental."
        ),
    ),
    "phased_vertical": EvidenceEntry(
        template="phased_vertical",
        level=EvidenceLevel.EXPERIMENTAL,
        source=(
            "Quarter-wave-spaced vertical radiators with an ideal linear phase "
            "and amplitude progression; no independent numerical reference for "
            "the generated array"
        ),
        tolerance="Not applicable (structural)",
        limitation=(
            "Mutual coupling is included by the wire solver, but the combining "
            "network, per-element matching, feed-line loss, radial screen "
            "efficiency, and the installation are not modeled. The reported "
            "impedance and SWR refer only to the primary feed. Verify the pattern "
            "and match with the solver or a measurement."
        ),
    ),
    "quad_beam": EvidenceEntry(
        template="quad_beam",
        level=EvidenceLevel.EXPERIMENTAL,
        source=(
            "Quarter-wave-side square loops with a scaled reflector and optional "
            "director, fifth-wave spacing, and a center-side feed; no independent "
            "numerical reference for the generated beam"
        ),
        tolerance="Not applicable (structural)",
        limitation=(
            "The square loops are ideal thin-wire polygons. Spreaders, boom and "
            "mast effects, feed-line routing, and the matching network are not "
            "modeled. The quarter-wave side and fifth-wave spacing are starting "
            "heuristics; gain, front-to-back ratio, and feedpoint impedance are "
            "not independently validated."
        ),
    ),
    "discone": EvidenceEntry(
        template="discone",
        level=EvidenceLevel.EXPERIMENTAL,
        source=(
            "Quarter-wave-slant radial-wire cone with a 0.7x top disc and a small "
            "feed gap; no independent numerical reference for the generated "
            "discone"
        ),
        tolerance="Not applicable (structural)",
        limitation=(
            "The cone and disc are radial wire approximations, not solid "
            "surfaces. The coax, mast, and feed transition are not modeled. "
            "Impedance, bandwidth, and radiation pattern are not independently "
            "validated; the shape is a starting point for simulation."
        ),
    ),
    "trap_yagi": EvidenceEntry(
        template="trap_yagi",
        level=EvidenceLevel.EXPERIMENTAL,
        source=(
            "Two-band Yagi with one ideal parallel LC trap pair per element; no "
            "independent numerical reference for the generated trapped array"
        ),
        tolerance="Not applicable (structural)",
        limitation=(
            "The traps are ideal parallel LC loads with no core or dielectric "
            "loss. Boom mounting, trap hardware, feed line, and matching network "
            "are not modeled. Gain, front-to-back ratio, and impedance on either "
            "band are not independently validated."
        ),
    ),
    "hexbeam": EvidenceEntry(
        template="hexbeam",
        level=EvidenceLevel.PUBLISHED,
        source=(
            "Steve Hunt, G3TXQ, 'A Broadband Hexbeam', antenneX no. 128, "
            "December 2007: 20 m reference at 14.184 MHz with a 219 in driver "
            "half, 207 in reflector half, 24 in tip gap, and 130 in turning radius"
        ),
        tolerance=(
            "1% on the published driver/reflector half-lengths, tip gap, and turning radius"
        ),
        limitation=(
            "The model reconstructs the bent W/U wire path from the published "
            "lengths; it does not reproduce the exact commercial frame, spreader "
            "sag, feed balun, or multi-band nesting. Gain, front-to-back ratio, "
            "and impedance are not independently validated."
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
