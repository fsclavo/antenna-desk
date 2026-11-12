# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Source-backed materials reference for construction decisions.

The tables are reference data, not solver models.  Coax presets can initialize
the project feed line; wire, ferrite, and insulator entries are informational.
Every value carries a bibliographic source and a visible limitation.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..antennas.feed_line import FeedLine
from ..antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ..common.units import ensure_positive


@dataclass(frozen=True, slots=True)
class ReferenceSource:
    """A traceable citation for one materials table row."""

    label: str
    url: str = ""
    revision: str = ""

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("source label must not be empty")


@dataclass(frozen=True, slots=True)
class WireReference:
    key: str
    material: ConductorMaterial
    source: ReferenceSource

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("wire reference key must not be empty")
        if not self.material.name.strip():
            raise ValueError("wire reference material name must not be empty")

    @property
    def conductivity_ms_per_m(self) -> float:
        return self.material.conductivity_s_per_m / 1_000_000.0


@dataclass(frozen=True, slots=True)
class CoaxReference:
    key: str
    characteristic_impedance_ohm: float
    velocity_factor: float
    matched_loss_db_per_100m: float
    reference_frequency_hz: float
    source: ReferenceSource

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("coax reference key must not be empty")
        ensure_positive(
            self.characteristic_impedance_ohm,
            name="characteristic_impedance_ohm",
        )
        ensure_positive(self.velocity_factor, name="velocity_factor")
        if self.velocity_factor > 1.0:
            raise ValueError("velocity_factor must not exceed 1")
        ensure_positive(
            self.matched_loss_db_per_100m,
            name="matched_loss_db_per_100m",
        )
        ensure_positive(self.reference_frequency_hz, name="reference_frequency_hz")

    def feed_line(self, length_m: float) -> FeedLine:
        """Return a feed line initialized from this datasheet point."""

        return FeedLine(
            characteristic_impedance_ohm=self.characteristic_impedance_ohm,
            length_m=length_m,
            velocity_factor=self.velocity_factor,
            matched_loss_db_per_100m=self.matched_loss_db_per_100m,
        )


@dataclass(frozen=True, slots=True)
class FerriteReference:
    key: str
    material_type: str
    initial_permeability: float
    frequency_min_mhz: float
    frequency_max_mhz: float
    source: ReferenceSource

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("ferrite reference key must not be empty")
        if not self.material_type.strip():
            raise ValueError("ferrite material type must not be empty")
        ensure_positive(self.initial_permeability, name="initial_permeability")
        ensure_positive(self.frequency_min_mhz, name="frequency_min_mhz")
        ensure_positive(self.frequency_max_mhz, name="frequency_max_mhz")
        if self.frequency_max_mhz <= self.frequency_min_mhz:
            raise ValueError("ferrite frequency range must be increasing")


@dataclass(frozen=True, slots=True)
class InsulatorReference:
    key: str
    dielectric_strength: str
    weather_key: str
    source: ReferenceSource

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("insulator reference key must not be empty")
        if not self.dielectric_strength.strip():
            raise ValueError("insulator dielectric strength must not be empty")
        if self.weather_key not in {"excellent", "good", "limited"}:
            raise ValueError("insulator weather key must be excellent, good, or limited")


# Wire conductivity is the nominal homogeneous value already used by the
# solver.  ASTM/IEC standards define the 100% IACS copper and 1350 aluminum
# references; plating, stranding, and temperature are outside the model.
ASTM_COPPER = ReferenceSource(
    label="ASTM B3 / IEC 60028, annealed copper (100% IACS)",
    url="https://www.astm.org/b0003-13r22.html",
    revision="ASTM B3-13 (2022)",
)
ASTM_ALUMINUM = ReferenceSource(
    label="ASTM B230/B231, 1350 aluminum (61% IACS)",
    url="https://www.astm.org/b0230-07r18.html",
    revision="ASTM B230-07 (2018)",
)
BELDEN_RG58A = ReferenceSource(
    label="Belden 8219 RG-58A/U technical data sheet",
    url="https://objects.eanixter.com/PD319399.PDF",
    revision="Rev 2 (2008-09-23)",
)
BELDEN_RG8X = ReferenceSource(
    label="Belden 9258 RG-8X technical data sheet",
    url="https://www.rigpix.com/otherusefulinfo/coax/belden_rg8x.pdf",
    revision="Rev 0.344 (2022-04-08)",
)
BELDEN_RG8 = ReferenceSource(
    label="Belden 8237 RG-8/U technical data sheet",
    url="https://belden-cable.ru/upload/iblock/33b/33beead6f24b16cb0b9e4155cf65d96e.pdf",
    revision="Rev 0.342 (2020-11-09)",
)
BELDEN_RG213 = ReferenceSource(
    label="Belden 8267 RG-213/U technical data sheet",
    url="https://www.belden-cable.ru/upload/iblock/688/688ddc9aaec82bfaa742ae04c74872a5.pdf",
    revision="Rev 0.336 (2020-09-30)",
)
BELDEN_RG214 = ReferenceSource(
    label="Belden 8268 RG-214/U technical data sheet",
    url="https://mra-raycom.com/wp-content/uploads/simple-file-list/Specifications/Belden-RG214-Coax-8268-Techdata.pdf",
    revision="Rev 0.290 (2019-08-22)",
)
BELDEN_RG174 = ReferenceSource(
    label="Belden 8216 RG-174/U technical data sheet",
    url="https://objects.eanixter.com/PD319397.PDF",
    revision="Rev 2 (2009-09-30)",
)
FAIRVIEW_RG316 = ReferenceSource(
    label="Fairview RG316/U data sheet (FMC03051)",
    url="https://www.fairviewmicrowave.com/content/dam/infinite-electronics/product-assets/fairview-microwave/olcc-datasheets/FMC03051.pdf",
    revision="REV 1.5 (2018)",
)
FAIRVIEW_RG400 = ReferenceSource(
    label="Fairview RG400/U data sheet",
    url="https://www.fairviewmicrowave.com/content/dam/infinite-electronics/product-assets/fairview-microwave/product-datasheets/RG400-U-BULK.pdf",
    revision="Rev A (2024-07-24)",
)
BELDEN_RG6 = ReferenceSource(
    label="Belden 1694A RG-6/U technical data sheet",
    url="https://docs.rs-online.com/94d8/0900766b80027eb3.pdf",
    revision="Rev 1 (2003-12-04)",
)
BELDEN_RG11 = ReferenceSource(
    label="Belden 8213 RG-11/U technical data sheet",
    url="https://www.gca.co.uk/document/1820/RG11DATASHEET.pdf",
    revision="Rev 0.342 (2022-04-08)",
)
TIMES_LMR240 = ReferenceSource(
    label="Times Microwave LMR-240 data sheet",
    url="https://timesmicrowave.com/wp-content/uploads/2022/06/lmr-240-datasheet.pdf",
    revision="2022-06",
)
TIMES_LMR400 = ReferenceSource(
    label="Times Microwave LMR-400 data sheet",
    url="https://timesmicrowave.com/wp-content/uploads/2022/06/lmr-400-datasheet-1.pdf",
    revision="2022-06",
)
FAIRVIEW_LMR600 = ReferenceSource(
    label="Times Microwave LMR-600 data sheet (Fairview copy)",
    url="https://www.fairviewmicrowave.com/content/dam/infinite-electronics/product-assets/fairview-microwave/product-datasheets/LMR-600.pdf",
    revision="Rev B (2024-05-13)",
)
BELDEN_9913 = ReferenceSource(
    label="Belden 9913 technical data sheet",
    url="https://docs.rs-online.com/2c0b/A700000008749587.pdf",
    revision="Rev 0.367 (2022-04-08)",
)
ANDREW_LDF4 = ReferenceSource(
    label="Andrew/CommScope LDF4-50A data sheet",
    url="https://www.andrew.com/globalassets/digizuite/115611-p360-ldf4-50a-external.pdf",
    revision="Revised 2026-07-10",
)
MESSI_ULTRAFLEX7 = ReferenceSource(
    label="Messi & Paoloni Ultraflex 7 full data sheet",
    url="https://www.freebytes.com/catalog/files/Ultraflex%207%20-%20Full%20Datasheet%20ENG.pdf",
    revision="2022 catalog",
)
FAIR_RITE_31 = ReferenceSource(
    label="Fair-Rite 31 Material data sheet",
    url="https://fair-rite.com/31-material-data-sheet/",
)
FAIR_RITE_43 = ReferenceSource(
    label="Fair-Rite 43 Material data sheet",
    url="https://fair-rite.com/43-material-data-sheet/",
)
FAIR_RITE_61 = ReferenceSource(
    label="Fair-Rite 61 Material data sheet",
    url="https://fair-rite.com/61-material-data-sheet/",
)
CHEMOURS_PTFE = ReferenceSource(
    label="Chemours Teflon PTFE handbook, table 3 (ASTM D149, 2.03 mm; RJ Chase copy)",
    url="http://www.rjchase.com/ptfe_handbook.pdf",
)
DUPONT_DELRIN = ReferenceSource(
    label="DuPont Delrin product and properties guide (ASTM D149, 3.2 mm)",
    url="https://www.emcoplastics.com/assets/pdf/delrin/Delrin%20Product%20and%20Properties%20Guide%20Dupont.pdf",
)
ALUMINA_96 = ReferenceSource(
    label="96% alumina typical properties (Stanford Advanced Materials)",
    url="https://www.samaterials.com/content/alumina-ceramic-common-types-and-specifications.html",
)


WIRE_REFERENCES: tuple[WireReference, ...] = (
    WireReference(key="copper", material=COPPER, source=ASTM_COPPER),
    WireReference(key="aluminum", material=ALUMINUM, source=ASTM_ALUMINUM),
)


COAX_REFERENCES: tuple[CoaxReference, ...] = (
    CoaxReference(
        key="rg58a",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.73,
        matched_loss_db_per_100m=14.76,
        reference_frequency_hz=100_000_000.0,
        source=BELDEN_RG58A,
    ),
    CoaxReference(
        key="rg8x",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.82,
        matched_loss_db_per_100m=10.17,
        reference_frequency_hz=100_000_000.0,
        source=BELDEN_RG8X,
    ),
    CoaxReference(
        key="rg8",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.66,
        matched_loss_db_per_100m=6.23,
        reference_frequency_hz=100_000_000.0,
        source=BELDEN_RG8,
    ),
    CoaxReference(
        key="rg213",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.66,
        matched_loss_db_per_100m=6.23,
        reference_frequency_hz=100_000_000.0,
        source=BELDEN_RG213,
    ),
    CoaxReference(
        key="rg214",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.66,
        matched_loss_db_per_100m=6.23,
        reference_frequency_hz=100_000_000.0,
        source=BELDEN_RG214,
    ),
    CoaxReference(
        key="rg174",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.66,
        matched_loss_db_per_100m=27.56,
        reference_frequency_hz=100_000_000.0,
        source=BELDEN_RG174,
    ),
    CoaxReference(
        key="rg316",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.69,
        matched_loss_db_per_100m=36.09,
        reference_frequency_hz=100_000_000.0,
        source=FAIRVIEW_RG316,
    ),
    CoaxReference(
        key="rg400",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.70,
        matched_loss_db_per_100m=29.53,
        reference_frequency_hz=400_000_000.0,
        source=FAIRVIEW_RG400,
    ),
    CoaxReference(
        key="rg6",
        characteristic_impedance_ohm=75.0,
        velocity_factor=0.82,
        matched_loss_db_per_100m=6.04,
        reference_frequency_hz=100_000_000.0,
        source=BELDEN_RG6,
    ),
    CoaxReference(
        key="rg11",
        characteristic_impedance_ohm=75.0,
        velocity_factor=0.84,
        matched_loss_db_per_100m=4.27,
        reference_frequency_hz=100_000_000.0,
        source=BELDEN_RG11,
    ),
    CoaxReference(
        key="lmr240",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.83,
        matched_loss_db_per_100m=9.9,
        reference_frequency_hz=150_000_000.0,
        source=TIMES_LMR240,
    ),
    CoaxReference(
        key="lmr400",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.84,
        matched_loss_db_per_100m=5.0,
        reference_frequency_hz=150_000_000.0,
        source=TIMES_LMR400,
    ),
    CoaxReference(
        key="lmr600",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.87,
        matched_loss_db_per_100m=3.28,
        reference_frequency_hz=150_000_000.0,
        source=FAIRVIEW_LMR600,
    ),
    CoaxReference(
        key="belden9913",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.84,
        matched_loss_db_per_100m=4.59,
        reference_frequency_hz=100_000_000.0,
        source=BELDEN_9913,
    ),
    CoaxReference(
        key="ldf4",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.88,
        matched_loss_db_per_100m=2.169,
        reference_frequency_hz=100_000_000.0,
        source=ANDREW_LDF4,
    ),
    CoaxReference(
        key="ultraflex7",
        characteristic_impedance_ohm=50.0,
        velocity_factor=0.83,
        matched_loss_db_per_100m=5.8,
        reference_frequency_hz=100_000_000.0,
        source=MESSI_ULTRAFLEX7,
    ),
)


FERRITE_REFERENCES: tuple[FerriteReference, ...] = (
    FerriteReference(
        key="fairrite_31",
        material_type="MnZn",
        initial_permeability=1500.0,
        frequency_min_mhz=1.0,
        frequency_max_mhz=500.0,
        source=FAIR_RITE_31,
    ),
    FerriteReference(
        key="fairrite_43",
        material_type="NiZn",
        initial_permeability=800.0,
        frequency_min_mhz=20.0,
        frequency_max_mhz=250.0,
        source=FAIR_RITE_43,
    ),
    FerriteReference(
        key="fairrite_61",
        material_type="NiZn",
        initial_permeability=125.0,
        frequency_min_mhz=200.0,
        frequency_max_mhz=2000.0,
        source=FAIR_RITE_61,
    ),
)


INSULATOR_REFERENCES: tuple[InsulatorReference, ...] = (
    InsulatorReference(
        key="ptfe",
        dielectric_strength="24 kV/mm (2.03 mm)",
        weather_key="excellent",
        source=CHEMOURS_PTFE,
    ),
    InsulatorReference(
        key="delrin",
        dielectric_strength="16.5 kV/mm (3.2 mm)",
        weather_key="good",
        source=DUPONT_DELRIN,
    ),
    InsulatorReference(
        key="alumina_96",
        dielectric_strength="12-15 kV/mm",
        weather_key="excellent",
        source=ALUMINA_96,
    ),
)


MATERIALS_REFERENCE = {
    "wire": WIRE_REFERENCES,
    "coax": COAX_REFERENCES,
    "ferrite": FERRITE_REFERENCES,
    "insulator": INSULATOR_REFERENCES,
}
