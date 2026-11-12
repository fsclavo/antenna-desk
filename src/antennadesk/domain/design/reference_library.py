# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Curated reference designs with traceable published sources.

Each entry selects one concrete, source-backed starting design from an
existing family. The library does not add geometry rules, performance claims,
or a solver path; it reuses the family parameters and the evidence registry.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..antennas.design import AntennaDesignParameters, antenna_type_for
from ..antennas.dipole import DipoleParameters
from ..antennas.endfed import efhw_parameters, sloper_parameters
from ..antennas.g5rv import g5rv_parameters
from ..antennas.hexbeam import published_hexbeam_parameters
from ..antennas.inverted_v import InvertedVParameters
from ..antennas.moxon import moxon_20m_wire
from ..antennas.scv import ScvKind, scv_parameters
from ..antennas.trap_dipole import w3dzz_parameters
from ..antennas.yagi import nbs_five_element
from ..antennas.zs6bkw import zs6bkw_parameters
from ..environment.ground import GroundModel
from .evidence import EVIDENCE, EvidenceEntry
from .formulas import half_wave_length_m

ARRL_DIPOLE_FREQUENCY_HZ = 7_100_000.0
ARRL_INVERTED_V_FREQUENCY_HZ = 7_100_000.0
ARRL_INVERTED_V_TOTAL_LENGTH_M = 465.6 / 7.1 * 0.3048


@dataclass(frozen=True, slots=True)
class ReferenceDesign:
    """One concrete design with a published source and visible scope."""

    key: str
    title_key: str
    project_name_key: str
    summary_key: str
    published_key: str
    modeled_key: str
    evidence_template: str
    parameters: AntennaDesignParameters
    search_terms: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in (
            "key",
            "title_key",
            "project_name_key",
            "summary_key",
            "published_key",
            "modeled_key",
            "evidence_template",
        ):
            if not getattr(self, field_name).strip():
                raise ValueError(f"reference design {field_name} must not be empty")
        if self.evidence_template not in EVIDENCE:
            raise ValueError(
                f"reference design {self.key} uses an unknown evidence template "
                f"{self.evidence_template!r}"
            )
        if antenna_type_for(self.parameters) == "":
            raise ValueError("reference design antenna type must not be empty")
        object.__setattr__(
            self,
            "search_terms",
            tuple(term.strip().lower() for term in self.search_terms if term.strip()),
        )

    @property
    def evidence(self) -> EvidenceEntry:
        return EVIDENCE[self.evidence_template]

    @property
    def frequency_hz(self) -> float:
        return self.parameters.frequency_hz

    @property
    def antenna_type(self) -> str:
        return antenna_type_for(self.parameters)


def _arrl_dipole() -> ReferenceDesign:
    return ReferenceDesign(
        key="arrl_dipole_40m",
        title_key="reference.arrl_dipole_40m.title",
        project_name_key="reference.arrl_dipole_40m.project_name",
        summary_key="reference.arrl_dipole_40m.summary",
        published_key="reference.arrl_dipole_40m.published",
        modeled_key="reference.arrl_dipole_40m.modeled",
        evidence_template="wire_dipole",
        parameters=DipoleParameters(
            frequency_hz=ARRL_DIPOLE_FREQUENCY_HZ,
            total_length_m=half_wave_length_m(ARRL_DIPOLE_FREQUENCY_HZ),
            height_m=10.0,
            ground=GroundModel.free_space(),
        ),
        search_terms=("dipole", "wire", "40m", "hf", "half wave"),
    )


def _cebik_moxon() -> ReferenceDesign:
    return ReferenceDesign(
        key="cebik_moxon_20m",
        title_key="reference.cebik_moxon_20m.title",
        project_name_key="reference.cebik_moxon_20m.project_name",
        summary_key="reference.cebik_moxon_20m.summary",
        published_key="reference.cebik_moxon_20m.published",
        modeled_key="reference.cebik_moxon_20m.modeled",
        evidence_template="moxon",
        parameters=moxon_20m_wire(),
        search_terms=("moxon", "wire beam", "20m", "hf", "front to back"),
    )


def _nbs_yagi() -> ReferenceDesign:
    return ReferenceDesign(
        key="nbs_yagi_6m",
        title_key="reference.nbs_yagi_6m.title",
        project_name_key="reference.nbs_yagi_6m.project_name",
        summary_key="reference.nbs_yagi_6m.summary",
        published_key="reference.nbs_yagi_6m.published",
        modeled_key="reference.nbs_yagi_6m.modeled",
        evidence_template="yagi",
        parameters=nbs_five_element(
            frequency_hz=50_100_000.0,
            height_m=10.0,
            ground=GroundModel.free_space(),
        ),
        search_terms=("yagi", "beam", "6m", "vhf", "nbs", "5 element"),
    )


def _w3dzz() -> ReferenceDesign:
    return ReferenceDesign(
        key="w3dzz_trap_dipole",
        title_key="reference.w3dzz_trap_dipole.title",
        project_name_key="reference.w3dzz_trap_dipole.project_name",
        summary_key="reference.w3dzz_trap_dipole.summary",
        published_key="reference.w3dzz_trap_dipole.published",
        modeled_key="reference.w3dzz_trap_dipole.modeled",
        evidence_template="trap_dipole",
        parameters=w3dzz_parameters(),
        search_terms=("trap dipole", "w3dzz", "80m", "40m", "20m", "hf"),
    )


def _g3txq_hexbeam() -> ReferenceDesign:
    return ReferenceDesign(
        key="g3txq_hexbeam_20m",
        title_key="reference.g3txq_hexbeam_20m.title",
        project_name_key="reference.g3txq_hexbeam_20m.project_name",
        summary_key="reference.g3txq_hexbeam_20m.summary",
        published_key="reference.g3txq_hexbeam_20m.published",
        modeled_key="reference.g3txq_hexbeam_20m.modeled",
        evidence_template="hexbeam",
        parameters=published_hexbeam_parameters(),
        search_terms=("hexbeam", "wire beam", "20m", "hf", "g3txq"),
    )


def _g5rv() -> ReferenceDesign:
    return ReferenceDesign(
        key="g5rv",
        title_key="reference.g5rv.title",
        project_name_key="reference.g5rv.project_name",
        summary_key="reference.g5rv.summary",
        published_key="reference.g5rv.published",
        modeled_key="reference.g5rv.modeled",
        evidence_template="g5rv",
        parameters=g5rv_parameters(frequency_hz=3_500_000.0),
        search_terms=("g5rv", "doublet", "multiband", "80m", "hf", "ladder line"),
    )


def _zs6bkw() -> ReferenceDesign:
    return ReferenceDesign(
        key="zs6bkw",
        title_key="reference.zs6bkw.title",
        project_name_key="reference.zs6bkw.project_name",
        summary_key="reference.zs6bkw.summary",
        published_key="reference.zs6bkw.published",
        modeled_key="reference.zs6bkw.modeled",
        evidence_template="zs6bkw",
        parameters=zs6bkw_parameters(),
        search_terms=("zs6bkw", "doublet", "multiband", "80m", "hf", "ladder line"),
    )


def _half_square() -> ReferenceDesign:
    return ReferenceDesign(
        key="cebik_half_square",
        title_key="reference.cebik_half_square.title",
        project_name_key="reference.cebik_half_square.project_name",
        summary_key="reference.cebik_half_square.summary",
        published_key="reference.cebik_half_square.published",
        modeled_key="reference.cebik_half_square.modeled",
        evidence_template="half_square",
        parameters=scv_parameters(ScvKind.HALF_SQUARE, 7_150_000.0),
        search_terms=("half square", "vertical array", "40m", "hf", "cebik"),
    )


def _bobtail_curtain() -> ReferenceDesign:
    return ReferenceDesign(
        key="cebik_bobtail_curtain",
        title_key="reference.cebik_bobtail_curtain.title",
        project_name_key="reference.cebik_bobtail_curtain.project_name",
        summary_key="reference.cebik_bobtail_curtain.summary",
        published_key="reference.cebik_bobtail_curtain.published",
        modeled_key="reference.cebik_bobtail_curtain.modeled",
        evidence_template="bobtail_curtain",
        parameters=scv_parameters(ScvKind.BOBTAIL_CURTAIN, 7_150_000.0),
        search_terms=("bobtail curtain", "vertical array", "40m", "hf", "cebik"),
    )


def _arrl_efhw() -> ReferenceDesign:
    return ReferenceDesign(
        key="arrl_efhw_40m",
        title_key="reference.arrl_efhw_40m.title",
        project_name_key="reference.arrl_efhw_40m.project_name",
        summary_key="reference.arrl_efhw_40m.summary",
        published_key="reference.arrl_efhw_40m.published",
        modeled_key="reference.arrl_efhw_40m.modeled",
        evidence_template="endfed",
        parameters=efhw_parameters("40m"),
        search_terms=("efhw", "end fed", "49:1", "40m", "hf", "wire"),
    )


def _chameleon_sloper() -> ReferenceDesign:
    return ReferenceDesign(
        key="chameleon_sloper",
        title_key="reference.chameleon_sloper.title",
        project_name_key="reference.chameleon_sloper.project_name",
        summary_key="reference.chameleon_sloper.summary",
        published_key="reference.chameleon_sloper.published",
        modeled_key="reference.chameleon_sloper.modeled",
        evidence_template="sloper",
        parameters=sloper_parameters(),
        search_terms=("sloper", "efhw", "40m", "hf", "chameleon", "portable"),
    )


def _arrl_inverted_v() -> ReferenceDesign:
    return ReferenceDesign(
        key="arrl_inverted_v",
        title_key="reference.arrl_inverted_v.title",
        project_name_key="reference.arrl_inverted_v.project_name",
        summary_key="reference.arrl_inverted_v.summary",
        published_key="reference.arrl_inverted_v.published",
        modeled_key="reference.arrl_inverted_v.modeled",
        evidence_template="inverted_v",
        parameters=InvertedVParameters(
            frequency_hz=ARRL_INVERTED_V_FREQUENCY_HZ,
            leg_length_m=ARRL_INVERTED_V_TOTAL_LENGTH_M / 2.0,
            apex_height_m=10.0,
            included_angle_deg=120.0,
            ground=GroundModel.free_space(),
        ),
        search_terms=("inverted v", "dipole", "40m", "hf", "wire"),
    )


REFERENCE_DESIGNS: tuple[ReferenceDesign, ...] = (
    _arrl_dipole(),
    _cebik_moxon(),
    _nbs_yagi(),
    _w3dzz(),
    _g3txq_hexbeam(),
    _g5rv(),
    _zs6bkw(),
    _half_square(),
    _bobtail_curtain(),
    _arrl_efhw(),
    _chameleon_sloper(),
    _arrl_inverted_v(),
)


def reference_design_by_key(key: str) -> ReferenceDesign:
    for design in REFERENCE_DESIGNS:
        if design.key == key:
            return design
    raise KeyError(f"unknown reference design: {key}")
