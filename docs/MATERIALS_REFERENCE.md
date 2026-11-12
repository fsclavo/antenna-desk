# Materials reference

AntennaDesk includes a read-only, source-backed materials reference under
**Tools → Materials Reference...**. It is a construction selection aid, not a
solver model or a product catalog. Every row shows the value used, a note about
its limits, and a link to the source.

Values are nominal datasheet or standards data, not measurements of a specific
part. Verify the manufacturer datasheet for the exact product before buying or
building.

## Wire

| Material | Conductivity | Relative permeability | Source |
|---|---:|---:|---|
| Copper | 58.0 MS/m | 1.0 | ASTM B3 / IEC 60028, annealed copper (100% IACS) |
| Aluminum | 35.0 MS/m | 1.0 | ASTM B230/B231, 1350 aluminum (61% IACS) |

Copper is the default conductor for traps, coils, and general HF wire.
Aluminum is a lightweight alternative for elements and long spans. The solver
uses these homogeneous conductivity values; plating, stranding, insulation,
connections, and temperature are not modeled.

## Coax

The shared catalog contains 16 source-backed cables. The materials-reference
dialog and the feed-line editor both read this one catalog.

### 50 Ω cables

| Type | Velocity factor | Matched loss | Datasheet reference | Source and revision |
|---|---:|---:|---:|---|
| RG-58A/U | 0.73 | 14.76 dB/100 m | 100 MHz | Belden 8219, Rev 2 (2008-09-23) |
| RG-8X | 0.82 | 10.17 dB/100 m | 100 MHz | Belden 9258, Rev 0.344 (2022-04-08) |
| RG-8/U | 0.66 | 6.23 dB/100 m | 100 MHz | Belden 8237, Rev 0.342 (2020-11-09) |
| RG-213/U | 0.66 | 6.23 dB/100 m | 100 MHz | Belden 8267, Rev 0.336 (2020-09-30) |
| RG-214/U | 0.66 | 6.23 dB/100 m | 100 MHz | Belden 8268, Rev 0.290 (2019-08-22) |
| RG-174/U | 0.66 | 27.56 dB/100 m | 100 MHz | Belden 8216, Rev 2 (2009-09-30) |
| RG-316/U | 0.69 | 36.09 dB/100 m | 100 MHz | Fairview FMC03051, Rev 1.5 (2018) |
| RG-400/U | 0.70 | 29.53 dB/100 m | 400 MHz | Fairview RG400, Rev A (2024-07-24) |
| LMR-240 | 0.83 | 9.90 dB/100 m | 150 MHz | Times Microwave LMR-240, 2022-06 |
| LMR-400 | 0.84 | 5.00 dB/100 m | 150 MHz | Times Microwave LMR-400, 2022-06 |
| LMR-600 | 0.87 | 3.28 dB/100 m | 150 MHz | Times Microwave LMR-600, Fairview copy Rev B (2024-05-13) |
| Belden 9913 | 0.84 | 4.59 dB/100 m | 100 MHz | Belden 9913, Rev 0.367 (2022-04-08) |
| LDF4-50A | 0.88 | 2.169 dB/100 m | 100 MHz | Andrew/CommScope LDF4-50A, revised 2026-07-10 |
| Ultraflex 7 | 0.83 | 5.80 dB/100 m | 100 MHz | Messi & Paoloni Ultraflex 7, 2022 catalog |

### 75 Ω cables

| Type | Velocity factor | Matched loss | Datasheet reference | Source and revision |
|---|---:|---:|---:|---|
| RG-6/U | 0.82 | 6.04 dB/100 m | 100 MHz | Belden 1694A, Rev 1 (2003-12-04) |
| RG-11/U | 0.84 | 4.27 dB/100 m | 100 MHz | Belden 8213, Rev 0.342 (2022-04-08) |

The **Apply to feed line** action in the materials-reference dialog copies the
selected impedance, velocity factor, and matched loss into the project feed
line. The feed-line editor also has a **Catalog** selector that fills the same
three fields; the length stays editable, and manual edits to impedance, velocity
factor, or loss switch the selector back to **Custom**.

The selected catalog key is not persisted. When a project feed line has exactly
one matching catalog entry, reopening the dialog selects that entry. When
several cables share the same electrical values (for example RG-8/U, RG-213/U,
and RG-214/U), the selector shows **Custom** rather than claiming a specific
cable. The electrical values remain intact.

The simulation uses a **constant matched loss**, not a frequency-dependent
attenuation table. The datasheet point is shown with its reference frequency so
the choice is visible. Datasheet values assume a matched line (VSWR 1.0) and
typically 25 °C; connectors, aging, moisture, and the actual installation are
not included. The 75 Ω cables are receive/SDR/satellite choices; verify
connectors and matching before using them on a 50 Ω transmitter.

## Ferrite

| Mix | Type | Initial permeability µi | Suppression range | Source |
|---|---|---:|---:|---|
| Fair-Rite 31 | MnZn | 1500 | 1–500 MHz | Fair-Rite 31 Material data sheet |
| Fair-Rite 43 | NiZn | 800 | 20–250 MHz | Fair-Rite 43 Material data sheet |
| Fair-Rite 61 | NiZn | 125 | 200–2000 MHz | Fair-Rite 61 Material data sheet |

Ferrite data is reference only. AntennaDesk does not model a ferrite core,
complex permeability, core geometry, winding, or common-mode impedance
`Zcm(f)`. The table is not counted as feed-line loss. Use the manufacturer's
`Zcm(f)` data or a measurement for a common-mode choke.

Fair-Rite also lists 61 material for inductive applications up to 25 MHz; the
range in the table is the suppression range.

## Insulators

| Material | Dielectric strength | Weather | Source |
|---|---|---|---|
| PTFE (Teflon) | 24 kV/mm (2.03 mm) | Excellent | Chemours Teflon PTFE handbook, table 3 (ASTM D149) |
| Delrin (acetal) | 16.5 kV/mm (3.2 mm) | Good (UV-stabilized grades) | DuPont Delrin product and properties guide (ASTM D149) |
| 96% alumina ceramic | 12–15 kV/mm | Excellent | 96% alumina typical properties (Stanford Advanced Materials) |

Dielectric strength depends on thickness, porosity, temperature, and the test
method. The values are selection aids, not a guarantee for a finished part.
Creepage and clearance, UV aging, water absorption, mechanical loads, and
mounting are not designed by this table.

## Evidence and limitations

- The materials reference is evidence level **B**: source-backed starting
  values, not measured or independently validated for a specific product.
- It does not change the antenna model, SWR, gain, or the solver path.
- The coax action initializes the existing feed-line model; it does not add a
  frequency-dependent coax attenuation model.
- Ferrite and insulator rows are informational and are not part of the
  simulation.
- No project schema change is required; the reference is static application
  data.

## Sources

- ASTM B3 / IEC 60028, annealed copper (100% IACS):
  <https://www.astm.org/b0003-13r22.html>
- ASTM B230/B231, 1350 aluminum (61% IACS):
  <https://www.astm.org/b0230-07r18.html>
- Belden 8219 RG-58A/U technical data sheet:
  <https://objects.eanixter.com/PD319399.PDF>
- Belden 9258 RG-8X technical data sheet:
  <https://www.rigpix.com/otherusefulinfo/coax/belden_rg8x.pdf>
- Belden 8237 RG-8/U technical data sheet:
  <https://belden-cable.ru/upload/iblock/33b/33beead6f24b16cb0b9e4155cf65d96e.pdf>
- Belden 8267 RG-213/U technical data sheet:
  <https://www.belden-cable.ru/upload/iblock/688/688ddc9aaec82bfaa742ae04c74872a5.pdf>
- Belden 8268 RG-214/U technical data sheet:
  <https://mra-raycom.com/wp-content/uploads/simple-file-list/Specifications/Belden-RG214-Coax-8268-Techdata.pdf>
- Belden 8216 RG-174/U technical data sheet:
  <https://objects.eanixter.com/PD319397.PDF>
- Fairview RG316/U data sheet (FMC03051):
  <https://www.fairviewmicrowave.com/content/dam/infinite-electronics/product-assets/fairview-microwave/olcc-datasheets/FMC03051.pdf>
- Fairview RG400/U data sheet:
  <https://www.fairviewmicrowave.com/content/dam/infinite-electronics/product-assets/fairview-microwave/product-datasheets/RG400-U-BULK.pdf>
- Belden 1694A RG-6/U technical data sheet:
  <https://docs.rs-online.com/94d8/0900766b80027eb3.pdf>
- Belden 8213 RG-11/U technical data sheet:
  <https://www.gca.co.uk/document/1820/RG11DATASHEET.pdf>
- Times Microwave LMR-240 data sheet:
  <https://timesmicrowave.com/wp-content/uploads/2022/06/lmr-240-datasheet.pdf>
- Times Microwave LMR-400 data sheet:
  <https://timesmicrowave.com/wp-content/uploads/2022/06/lmr-400-datasheet-1.pdf>
- Times Microwave LMR-600 data sheet (Fairview copy):
  <https://www.fairviewmicrowave.com/content/dam/infinite-electronics/product-assets/fairview-microwave/product-datasheets/LMR-600.pdf>
- Belden 9913 technical data sheet:
  <https://docs.rs-online.com/2c0b/A700000008749587.pdf>
- Andrew/CommScope LDF4-50A data sheet:
  <https://www.andrew.com/globalassets/digizuite/115611-p360-ldf4-50a-external.pdf>
- Messi & Paoloni Ultraflex 7 full data sheet:
  <https://www.freebytes.com/catalog/files/Ultraflex%207%20-%20Full%20Datasheet%20ENG.pdf>
- Fair-Rite 31 Material data sheet: <https://fair-rite.com/31-material-data-sheet/>
- Fair-Rite 43 Material data sheet: <https://fair-rite.com/43-material-data-sheet/>
- Fair-Rite 61 Material data sheet: <https://fair-rite.com/61-material-data-sheet/>
- Chemours Teflon PTFE handbook (table 3; RJ Chase copy):
  <http://www.rjchase.com/ptfe_handbook.pdf>
- DuPont Delrin product and properties guide:
  <https://www.emcoplastics.com/assets/pdf/delrin/Delrin%20Product%20and%20Properties%20Guide%20Dupont.pdf>
- 96% alumina typical properties (Stanford Advanced Materials):
  <https://www.samaterials.com/content/alumina-ceramic-common-types-and-specifications.html>
