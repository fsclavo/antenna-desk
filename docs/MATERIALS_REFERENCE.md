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

| Type | Z₀ | Velocity factor | Matched loss | Datasheet reference | Source |
|---|---:|---:|---:|---:|---|
| RG-58A/U | 50 Ω | 0.73 | 14.76 dB/100 m | 100 MHz | Belden 8219 technical data sheet |
| RG-213/U | 50 Ω | 0.66 | 6.23 dB/100 m | 100 MHz | Belden 8267 technical data sheet |
| LMR-400 | 50 Ω | 0.84 | 5.00 dB/100 m | 150 MHz | Times Microwave LMR-400 data sheet |

The **Apply to feed line** action copies the selected impedance, velocity
factor, and matched loss into the project feed line. The current feed-line
length is preserved; a new line starts at 10 m. The feed-line dialog remains
the place to edit the length, impedance, velocity factor, and loss directly.

The simulation uses a **constant matched loss**, not a frequency-dependent
attenuation table. The datasheet point is shown with its reference frequency so
the choice is visible. Datasheet values assume a matched line (VSWR 1.0) and
typically 25 °C; connectors, aging, moisture, and the actual installation are
not included.

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
- Belden 8267 RG-213/U technical data sheet:
  <https://www.belden.com/products/Cable/Coax-Triax-Cable/50-Ohm-Coax-Cable/8267>
- Times Microwave LMR-400 data sheet:
  <https://timesmicrowave.com/wp-content/uploads/2022/06/lmr-400-datasheet-1.pdf>
- Fair-Rite 31 Material data sheet: <https://fair-rite.com/31-material-data-sheet/>
- Fair-Rite 43 Material data sheet: <https://fair-rite.com/43-material-data-sheet/>
- Fair-Rite 61 Material data sheet: <https://fair-rite.com/61-material-data-sheet/>
- Chemours Teflon PTFE handbook (table 3; RJ Chase copy):
  <http://www.rjchase.com/ptfe_handbook.pdf>
- DuPont Delrin product and properties guide:
  <https://www.emcoplastics.com/assets/pdf/delrin/Delrin%20Product%20and%20Properties%20Guide%20Dupont.pdf>
- 96% alumina typical properties (Stanford Advanced Materials):
  <https://www.samaterials.com/content/alumina-ceramic-common-types-and-specifications.html>
