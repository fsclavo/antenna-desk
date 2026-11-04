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
        level=EvidenceLevel.EXPERIMENTAL,
        source="Polygon-corrected circumference starting rule; no independent delta-loop reference",
        tolerance="Not applicable (structural)",
        limitation="Starting dimensions; verify with a simulation or a measurement.",
    ),
    "vertical": EvidenceEntry(
        template="vertical",
        level=EvidenceLevel.EXPERIMENTAL,
        source="Quarter-wave starting rule; no independent gain reference",
        tolerance="Not applicable (structural)",
        limitation="Radial count and the ground model dominate the result.",
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
        level=EvidenceLevel.EXPERIMENTAL,
        source="Half-wave dipole starting rule with an included-angle heuristic",
        tolerance="Not applicable (structural)",
        limitation="No independent numerical reference.",
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
        level=EvidenceLevel.EXPERIMENTAL,
        source="Trap-loaded dipole starting geometry",
        tolerance="Not applicable (structural)",
        limitation="Traps are ideal; no independent numerical reference.",
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
        level=EvidenceLevel.EXPERIMENTAL,
        source="Half-wave end-fed starting rule",
        tolerance="Not applicable (structural)",
        limitation="Transformer is an ideal impedance ratio; the counterpoise is wire geometry.",
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
        level=EvidenceLevel.EXPERIMENTAL,
        source="Quarter-wave radiator and quarter-wave stub starting rule",
        tolerance="Not applicable (structural)",
        limitation="No independent numerical reference.",
    ),
    "slim_jim": EvidenceEntry(
        template="slim_jim",
        level=EvidenceLevel.EXPERIMENTAL,
        source="Folded J-pole starting geometry",
        tolerance="Not applicable (structural)",
        limitation="No independent numerical reference.",
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
