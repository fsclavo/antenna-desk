# Historical backlog — UX queue notes

> **Historical design notes, captured 2026-11-20.** Not current
> guidance. Current status: [`../../STATUS.md`](../../STATUS.md); active
> queue: [`../../AUTONOMOUS_BACKLOG.md`](../../AUTONOMOUS_BACKLOG.md).

## Product experience queue (2026-11-11)

UX1–UX17 are complete. The 0.5 **Decide**, 0.6 **Build**, 0.7 **Measure**, and
0.8 **Explore** releases are closed. UX18–UX20 and UX21–UX24 were implemented on
2026-11-12; the 0.9 **Sustain** slice is complete. UX32–UX38, the
frequency-first starting-dimensions, semantics, pristine-recalculation,
quad-beam-estimator, scale-to-frequency, and creation-tab work, were completed
on 2026-11-17. The adaptive length display-units track (U0–U6) is implemented;
only the manual desktop light/dark and font-scaling checklist remains before
the release decision.
UX21–UX24 were added from direct user feedback and completed the
same day. UX25 and UX26 were queued on 2026-11-13 and completed the same day.
UX27 and UX28 were added the same day from terminology feedback; UX27 and UX28
were completed on 2026-11-13.
UX29 was added and completed the same day from feed-connection feedback.
UX30 was queued on 2026-11-17 from per-template material-default feedback and
was completed the same day. UX31 was queued on 2026-11-17 from feed-schematic
feedback and was completed the same day.
UX32–UX37 were queued on 2026-11-17 from frequency-first starting-dimension
feedback. UX32–UX37 are complete. UX38 was queued on 2026-11-17 from
new-antenna tab feedback and is also complete. UX39 was queued on 2026-11-18
from impedance/SWR point-density feedback, UX40 was queued the same day from the
3D-report request, and UX41 was queued from optimizer operating-mode feedback
and completed on 2026-11-19. UX39 and UX40 were completed on 2026-11-19; the
UX queue is clear. The product trust and station track started on 2026-11-19;
wave 0 (TS1–TS7, DL9) and DL1/DL2 are done; DL5 is the remaining wave-1 item.
See §Product trust and station wave above.
EF1–EF9 were queued on 2026-11-13 from the shortened-EFHW optimizer review;
EF1–EF6, EF7a, EF7b, EF8a, the bounded EF8 feedpoint choke model, and EF9
L/Pi/T matching are implemented, including automatic L/Pi/T synthesis with a
visible design Q.

The first slice accepts these constraints:

- The advisor is deterministic and evidence-backed. It does not call a language
  model and does not simulate every candidate.
- The comparison basis is explicit and recalculated. Stored results from
  different conditions are never presented as directly comparable.
- The installation profile is metadata. It does not claim terrain, obstacle, or
  support-structure modeling.
- Guided mode is progressive disclosure, not a reduced feature set. Every
  advanced action remains available in Standard or Advanced.
- The feed-chain topology work starts with an ADR. The current project network is
  a feedpoint network evaluated before the feed line; a shack tuner and a
  transmitter-side balun are not the same topology and must not be presented as
  if they were.

## UX23 — Common coax catalog (research note, 2026-11-12)

**Implemented on 2026-11-12.** The final 16-entry catalog, values, revisions,
and limitations live in
[`MATERIALS_REFERENCE.md`](../../MATERIALS_REFERENCE.md). The candidate table below is
kept as the research starting point; several final entries use a different
datasheet from the candidate list where that source had clearer values.

The initial materials-reference work has three source-backed entries: Belden
8219 RG-58A/U, Belden 8267 RG-213/U, and Times Microwave LMR-400. UX23 expands
that same catalog instead of creating a second list. The candidate set below covers
the common amateur 50 Ω families plus 75 Ω cables used for receive, SDR, and
legacy installations. It is a research starting point, not a list of values to
copy blindly: every entry still needs its datasheet values verified.

| Cable | Z₀ | Typical role | Primary source |
|---|---:|---|---|
| RG-58A/U | 50 Ω | Short HF/VHF runs, mobile, jumpers | [Belden 8219](https://www.belden.com/products/Cable/Coax-Triax-Cable/50-Ohm-Coax-Cable/8219) |
| RG-8X | 50 Ω | Medium HF/VHF runs, portable | [Belden 9258](https://www.belden.com/products/Cable/Coax-Triax-Cable/50-Ohm-Coax-Cable/9258) |
| RG-8/U | 50 Ω | Legacy HF/VHF, medium runs | [Belden 8237](https://www.belden.com/products/Cable/Coax-Triax-Cable/50-Ohm-Coax-Cable/8237) |
| RG-213/U | 50 Ω | Rugged HF/VHF, longer runs | [Belden 8267](https://www.belden.com/products/Cable/Coax-Triax-Cable/50-Ohm-Coax-Cable/8267) |
| RG-214/U | 50 Ω | Double-shielded RG-213 | [Belden 8268](https://www.belden.com/products/Cable/Coax-Triax-Cable/50-Ohm-Coax-Cable/8268) |
| RG-174/U | 50 Ω | Very short jumpers, portable | [Belden 8216](https://www.belden.com/products/Cable/Coax-Triax-Cable/50-Ohm-Coax-Cable/8216) |
| RG-316/U | 50 Ω | PTFE jumpers, SDR and portable use | [RG 316 U datasheet](https://www.tme.eu/Document/f95eb7ec6601001fd1c465534b0403a1/RG316.pdf) |
| RG-400/U | 50 Ω | PTFE double-shielded jumpers | [Fairview RG400](https://www.fairviewmicrowave.com/content/dam/infinite-electronics/product-assets/fairview-microwave/product-datasheets/RG400-U-BULK.pdf) |
| RG-6/U | 75 Ω | Receive, SDR, satellite and TV | [Belden 1694A](https://www.belden.com/products/cable/video-cable/coaxial-video-cable/1694a) |
| RG-11/U | 75 Ω | Low-loss 75 Ω runs | [Belden 8213](https://www.belden.com/products/Cable/Video-Cable/Coaxial-Video-Cable/8213) |
| LMR-240 | 50 Ω | Smaller low-loss HF/VHF/UHF | [Times LMR-240](https://timesmicrowave.com/wp-content/uploads/2022/06/lmr-240-datasheet.pdf) |
| LMR-400 | 50 Ω | Common low-loss HF/VHF/UHF | [Times LMR-400](https://timesmicrowave.com/wp-content/uploads/2022/06/lmr-400-datasheet-1.pdf) |
| LMR-600 | 50 Ω | Long low-loss VHF/UHF runs | [Times LMR-600](https://timesmicrowave.com/wp-content/uploads/2022/03/lmr-600-coax-cables-datasheet.pdf) |
| Belden 9913 | 50 Ω | Low-loss HF/VHF | [Belden 9913](https://www.belden.com/products/cable/coax-triax-cable/50-ohm-coax-cable/9913) |
| CommScope LDF4-50A | 50 Ω | 1/2-inch hardline, long runs | [Andrew LDF4-50A](https://www.andrew.com/globalassets/digizuite/115611-p360-ldf4-50a-external.pdf) |
| Messi & Paoloni Ultraflex 7 | 50 Ω | Flexible low-loss, European market | [Ultraflex 7](https://messi.it/en/catalogue/50-ohm-cables/ultraflex-7.htm) |

Optional legacy or regional variants: RG-59/U 75 Ω
([Belden 8241F](https://www.belden.com/products/Cable/Video-Cable/Coaxial-Video-Cable/8241f)),
RG-58C/U if a manufacturer datasheet is available, and regional low-loss
equivalents such as DXE-400MAX or Davis BuryFlex only when their own datasheet
is traceable. Do not substitute one manufacturer's values for another. The
table's 50 Ω/75 Ω values are class labels; store the datasheet's exact nominal
impedance, because some RG-8/U and RG-58 variants are slightly off 50 Ω.

Data rules for every entry:

- Store `key`, display name, characteristic impedance, velocity factor, matched
  loss, reference frequency, source label/URL, and a visible limitation.
- Transcribe velocity factor and attenuation from the cited manufacturer
  datasheet at a documented frequency. Do not copy values from a generic RG
  table, a distributor summary, or another cable family.
- Keep variants separate: RG-58A/U and RG-58C/U are not interchangeable;
  standard, foam, and double-shielded constructions can differ.
- Show the reference frequency in the UI. A single datasheet point remains a
  constant-loss initialization; frequency-dependent attenuation is a separate
  optional table (ADR-0039).
- Multi-point attenuation tables interpolate only inside the documented
  frequency range. Outside it, endpoint values are used and preflight warns; do
  not claim accuracy outside the source range.

## UX25 — Stainless steel 304 conductor (design note, 2026-11-13)

**Implemented on 2026-11-13.** This note is retained as the implementation
record. Do not substitute a generic "steel" preset, carbon steel, galvanized
steel, 316, or a different permeability model.

### Decision

Add **only** austenitic stainless steel 304 as a selectable conductor material.
Do not add carbon steel, galvanized steel, 316, or a custom-material editor in
this item. In amateur practice, carbon steel is marginal for radiating
elements; 304 is the useful corrosion-resistant option for whips, portable and
marine elements, and mechanical conductors.

### Material data

- Nominal annealed 304: resistivity **7.2×10⁻⁵ Ω·cm** (7.2×10⁻⁷ Ω·m), therefore
  conductivity **1.389×10⁶ S/m**.
- Primary source: **ASM Material Data Sheet, AISI Type 304 stainless steel**,
  <https://asm.matweb.com/search/specificmaterial.asp?bassnum=mq304a>. Record
  the exact label and URL in `WIRE_REFERENCES`; do not copy a generic steel
  table or a distributor summary.
- Published values for annealed 304 give a relative permeability of
  approximately **1.003–1.02**. Cold work can raise it slightly and also raises
  resistivity.
- Store **μr = 1.0** in `ConductorMaterial` and explain the approximation in
  the reference note. Do not store 1.008 and do not change the
  `solver.permeability_unsupported` threshold in this item. The solver models
  conductivity only; the error from this rounding is about 1 % or less for
  this grade.
- The visible note must state: higher RF loss than copper (about **6.5×** the
  RF resistance of copper for the same diameter at 7.1 MHz and 2 mm), suitable
  for whips, portable/marine elements, and mechanical conductors; not for
  coils, traps, or small loops. Cold-worked 304 can be slightly magnetic.
- Evidence level **B**: nominal source-backed data, not a measurement of a
  specific wire. Verify the actual product datasheet before buying or building.

### Implementation constraints

- `domain/antennas/materials.py`: add `STAINLESS_STEEL_304`; keep `COPPER` and
  `ALUMINUM` unchanged. Add one ordered `CONDUCTOR_MATERIALS` tuple
  `(COPPER, ALUMINUM, STAINLESS_STEEL_304)` and use it everywhere. Do not keep
  duplicating per-form material lists.
- UI: replace every local `MATERIALS = (COPPER, ALUMINUM)` definition (currently
  30 modules) with the shared tuple. The order must remain copper, aluminum,
  304; append 304 last so existing defaults and tests do not shift.
- Add a shared helper to populate and retranslate the material combo from
  `material.name` (`material.<name>`). Remove fixed `setItemText(0/1)` calls and
  per-form key tuples. This is required so a future material does not repeat the
  same edit in 30 files.
- `ui/dialogs/component_calculator_dialog.py`: use the same presets. The
  calculator already uses μr in its skin-depth and RF-resistance formulas, so
  μr = 1.0 keeps it consistent with the solver.
- `ui/i18n.py`: add `material.stainless_steel_304`,
  `materials.wire.stainless_steel_304.name`,
  `materials.wire.stainless_steel_304.note`, and
  `component_calculator.stainless_steel_304`. Keep English and Spanish in sync.
- `ui/report_i18n.py`: add **"Stainless steel 304"** and
  **"stainless_steel_304"** so construction sheets, HTML/PDF reports, and BOM
  values translate correctly.
- `domain/design/materials_reference.py`: add one `WireReference` with key
  `stainless_steel_304`, the source above, and a note containing the
  limitations. It must reference the same `STAINLESS_STEEL_304` object used by
  the selectors, so the reference table and solver cannot diverge.
  `MATERIALS_REFERENCE.md` gets the matching row and source link. Do not add a
  generic "steel" row.
- `help.field.material`: mention that the solver uses conductivity only and
  that 304 is a higher-loss conductor. Keep the existing 240-character help
  limit and both languages.
- Keep **copper** as the default material in every editor and in the
  frequency-first designer. The designer-from-frequency dialog keeps its
  current behavior: it preserves an existing material and otherwise starts at
  copper; do not add a material selector there in this item.
  **Superseded on 2026-11-17 by UX30** for new-design template defaults only.
  The material presets, combo order, frequency-first preservation behavior, and
  every existing project material remain unchanged.

### Do not

- Do not add carbon steel, galvanized steel, 316, or a generic "steel".
- Do not use 316, generic stainless, or carbon-steel values as substitutes for
  the 304 source.
- Do not change `ConductorMaterial`, `MaterialPayload`, the project schema, or
  add a migration.
- Do not change `write_nec2_input`, `validate_nec2_assumptions`, or the
  permeability warning threshold.
- Do not emit relative permeability to NEC and do not use the `σ/μr` effective
  conductivity workaround. That is a separate solver item.
- Do not add a material capability flag, per-family exclusion, structural
  material field, or custom-material editor.
- Do not make 304 the default, reorder copper/aluminum, or change existing
  project materials. **UX30 exception:** 304 is the default only for the
  `loaded_vertical` template; the other 40 templates use the copper or aluminum
  mapping in UX30.
- Do not change the NEC importer. Imported decks still become copper and
  `LD 5` is still ignored; document that pre-existing limitation if it becomes
  relevant.
- Do not claim mechanical strength, corrosion validation, temperature
  behavior, weld/connection quality, or structural modeling.

### Tests and documentation

- Update the preset test in `tests/unit/domain/test_geometry.py`.
- Update the exact wire-reference tuple in
  `tests/unit/domain/design/test_materials_reference.py` to
  `("copper", "aluminum", "stainless_steel_304")`, and assert the source URL and
  conductivity.
- The existing materials-reference i18n test must pass with the new EN/ES name
  and note.
- Extend the form retranslation test for the 304 label; cover at least one form
  per UI pattern and rely on the shared helper for the rest.
- Add persistence round-trip coverage for a design using 304; there is no
  migration.
- Add BOM, conductor-cost key, and report-text coverage:
  `conductor:stainless_steel_304:<diameter>` and localized "Stainless steel
  304".
- Add component-calculator coverage for 304 skin depth and RF resistance.
- Add a deck test asserting `LD 5` uses **1.389×10⁶ S/m** and that 304 does
  **not** produce `solver.permeability_unsupported`; copper and aluminum decks
  must remain unchanged.
- Update `MATERIALS_REFERENCE.md`, `DOMAIN_MODEL.md`, `SOLVER_ADAPTER.md`,
  `USER_GUIDE.md`, and `CHANGELOG.md`.
- No ADR is required because this item changes neither solver behavior nor
  schema. The μr = 1.0 approximation and the conductivity-only model must be
  visible in the materials reference and user guide.

### Acceptance

- 304 is selectable in every family editor and in the component calculator.
- Copper remains the default for this item's scope; existing copper/aluminum
  projects and tests are unchanged. **Superseded by UX30** for new-design
  template defaults only.
- The Materials Reference wire tab shows 304 with its source and limitation.
- Reports and the UI show the localized "Stainless steel 304"; machine-readable
  CSV and cost keys keep the stable internal name `stainless_steel_304`.
- The NEC deck uses 1.389×10⁶ S/m and emits no permeability warning.
- The full gate in the Rules section passes; no schema or migration change.

### Out of scope

- Carbon steel or galvanized steel: require a separate solver decision
  (`σ/μr` mapping or a loss correction) and must not be smuggled in as another
  preset.
- 316: a separate source-backed preset if requested.
- Structural steel, towers, masts, booms, and mechanical design: a separate
  feature, not a conductor material.
- Temperature, cold-work, plating, and connection resistance: visible
  limitations only; do not model them in this item.

## UX26 — Geometry and pattern in exported reports (design note, 2026-11-13)

**Implemented on 2026-11-13.** This note is retained as the implementation
record.

### Problem

The HTML simulation report currently contains impedance, SWR, and an
elevation-only power-gain chart; it has no antenna geometry. The native PDF
report contains impedance and SWR charts only. Geometry and pattern already
exist as separate exports, but those exports capture live widgets, so they
depend on window size, zoom, theme, and DPI and are not reproducible from the
immutable result snapshot.

### Decision

- Add to both reports:
  - one canonical antenna geometry figure, using the same principal-projection
    policy as the construction sheet (ADR-0027) and the existing scene contract;
  - azimuth and elevation pattern cuts at the report frequency, following the
    UX21 cut semantics and showing the selected metric consistently.
- Keep the construction sheet as the dimensioned artifact. The simulation
  report geometry figure identifies the antenna and its orientation; do not
  duplicate dimension-placement logic in this item.
- Use total gain as the default report metric. A report-specific metric
  selector remains deferred product work and is not part of UX26.
- Do not add the 3D pattern view to reports. Keep figures 2D and vector.
- Handle band analysis explicitly: one geometry figure for the design plus a
  pattern section per band, consistent with the existing band-pattern section.
- When far-field data is disabled or unavailable, show a localized explanation
  instead of an empty chart or a silent omission.

### Rendering constraints

- Figures must be deterministic and headless. Prefer pure SVG builders in
  `reporting/`; the HTML report must stay Qt-free.
- Do not call `QWidget.grab()` or `save_pattern_image()`/`save_image()` from
  the reporting path. If the existing construction renderer requires Qt,
  render it offscreen at a fixed size, theme, and DPI, and keep that adapter in
  the UI layer.
- HTML inlines SVG so the file stays self-contained. The native PDF draws the
  same SVG as vector content. Do not embed PNG screenshots or the 3D view.
- Reuse the canonical scene/model and wires; do not synthesize a replacement
  shape or infer the family from wire counts.
- Keep output size bounded: no image per frequency, and no duplicated geometry
  per band.

### Tests and documentation

- HTML and PDF tests for single-band and band-analysis output, including
  geometry presence, both pattern cuts, and vector content.
- Tests for far-field disabled, missing pattern points, and multiple bands.
- Determinism test: identical snapshot and language produce identical report
  figures.
- EN/ES report headings and help, with the coverage manifest passing.
- Update `USER_GUIDE.md`, `ARCHITECTURE.md` (report contents), and
  `CHANGELOG.md`.
- No schema, solver, or domain changes.

### Out of scope

- 3D pattern rendering in reports.
- A report-specific gain/directivity/realized-gain selector.
- Interactive or animated HTML output.
- Replacing the construction sheet or duplicating its dimension layout.

## UX27 — Spanish ROE terminology (design note, 2026-11-13)

**Implemented on 2026-11-13.** This note is retained as the implementation
record.

### Decision

- Spanish UI and Spanish report text must use **ROE** (*relación de ondas
  estacionarias*), not **SWR**.
- English remains **SWR**.
- The first explanatory use should expand the acronym as **“ROE (relación de
  ondas estacionarias)”**; later uses stay “ROE”.
- This is a presentation-only change. Do not rename `SweepMetric.SWR`,
  `OptimizationMetric.SWR`, report keys such as `table.swr`, CSV columns, solver
  messages, or any domain identifier.

### Spanish grammar

- ROE is feminine: “la ROE”, “una ROE alta”, “ROE absoluta”, “ROE residual”.
- Replace “el SWR” with “la ROE”; “del SWR” with “de la ROE”; “SWR alto” with
  “ROE alta”; “SWR absoluto” with “ROE absoluta”.
- Do not leave hybrid text such as “la SWR” or “ROE (SWR)” unless it is an
  explicit bilingual equipment note. Prefer no parenthetical SWR in Spanish.

### Translation gaps to close

The following 18 keys in `src/antennadesk/ui/i18n.py` still contain “SWR” in
their Spanish value:

- `feed_line.hint`
- `matching_network.hint`
- `endfed.installation_return_hint`
- `endfed.convergence_converged`
- `endfed.convergence_unresolved`
- `endfed.convergence_result`
- `endfed.convergence_result_impedance`
- `endfed.convergence_matching_note`
- `optimize.min_swr_objective`
- `optimize.min_swr_edges_objective`
- `optimize.min_swr_operating_objective`
- `optimize.max_bandwidth_objective`
- `optimize.balanced_objective`
- `optimize.swr_tolerance`
- `optimize.swr_limit`
- `optimize.swr_weight`
- `optimize.max_swr_constraint`
- `element_optimize.objective.min_swr`

Also inspect the Spanish values in `src/antennadesk/ui/evidence_i18n.py` and
`src/antennadesk/ui/report_i18n.py`; they already use ROE, but add a guard so
they cannot regress.

### Hardcoded labels

Replace the literal “SWR” with a translated short label in:

- `ui/dialogs/endfed_dialog.py:226` (cursor/readout)
- `ui/dialogs/measurement_comparison_dialog.py:130,317` (axis labels)
- `ui/dialogs/parameter_sweep_dialog.py:721,726,764` (axis, series name, table
  header)
- `ui/dialogs/robustness_dialog.py:443,478` (axis and table header)

Use the existing `table.swr` key (`SWR`/`ROE`) for the short label, or add one
shared `chart.swr` key and use it everywhere. Do not create per-dialog
duplicates.

### Reports

- `src/antennadesk/reporting/construction_sheet.py:1460` hardcodes
  `SWR ≤ 2 bandwidth`; route it through `tr(...)` and add the Spanish mapping
  “Ancho de banda ROE ≤ 2” to `report_i18n.py`.
- Check all report paths for raw `SWR` literals. `html_report.py`,
  `report_pdf.py`, and the localized design-summary rows already use
  `Translator.report`.
- The acronym definition belongs in the user-facing help/glossary, for example
  `confidence.explain.swr` or the SWR chart help. Keep it short and within the
  240-character help limit.

### Tests and documentation

- Add a regression test that scans every Spanish value in `ui/i18n.py`,
  `ui/report_i18n.py`, and `ui/evidence_i18n.py` for `\bSWR\b` and fails on a
  match. If a deliberate exception is ever needed, require an explicit allowlist
  with a reason.
- Add Spanish-locale tests for the four dialogs above and for the
  construction-sheet bandwidth row.
- Keep English assertions unchanged; English still says SWR.
- Review the existing Spanish strings for article/agreement by hand; a regex
  cannot validate grammar.
- Update `CHANGELOG.md` under the Spanish UI/localization change. No ADR,
  schema, migration, solver, or domain change.

### Acceptance

- No Spanish UI or report string contains “SWR”.
- Spanish uses “ROE” with feminine articles and agreement.
- English remains “SWR”; internal keys, enums, and CSV columns are unchanged.
- The first explanatory use expands “ROE”.
- EN/ES tests, the help coverage manifest, and the full gate pass.

### Out of scope

- Renaming `SWR` identifiers, report keys, CSV columns, or solver output.
- Translating equipment displays or third-party VNA terminology.
- Changing English text to ROE.

## UX28 — Vertical radiator length terminology (design note, 2026-11-13)

**Implemented on 2026-11-13.** This note is retained as the implementation
record.

### Decision

- In English, use **length** for the physical vertical radiating element:
  “Radiator length”, “Vertical length”, “Element length”.
- In Spanish, use **largo** as requested: “Largo del radiador”, “Largo
  vertical”, “Largo del elemento”. Do not change existing “Longitud horizontal”
  or “Longitud del stub” in this item; the mixed style is deliberate and
  documented.
- Keep **height** for installation/position dimensions: base height, feed
  height, height above ground, top height, ring height, coil height above base,
  apex height, stack height, boom centerline height, available height.
- Keep internal field names (`height_m`, `radiator_height_m`,
  `vertical_height_m`), optimizer variable names, project schema, and CSV/JSON
  keys unchanged. No migration.

### Label mapping

| Key | English now | English after | Spanish after |
|---|---|---|---|
| `vertical.height` | Radiator height | Radiator length | Largo del radiador |
| `j_pole.radiator_height` | Radiator height | Radiator length | Largo del radiador |
| `ringo.radiator_height` | Radiator height | Radiator length | Largo del radiador |
| `inverted_l.vertical_height` | Vertical height | Vertical length | Largo vertical |
| `scv.vertical_height` | Vertical height | Vertical length | Largo vertical |
| new `phased_vertical.height` | `field.height` = Height | Element length | Largo del elemento |

- `phased_vertical` currently uses the generic `field.height`; give it a family
  key so Yagi/dipole installation heights are unaffected.
- Change summary text in `ringo.geometry`, `j_pole.geometry`, and
  `phased_vertical.geometry` (“height” → “length”; “altura” → “largo”).
- Change `ringo.ar6_example_hint` “3.1 m overall height” → “3.1 m overall
  length” and “3,1 m de altura total” → “3,1 m de largo total”. The follow-up
  “el radiador mide 3.05 m” stays.
- `vertical.geometry` (“Top height”) remains a height because it is base height +
  radiator length, i.e. the installation top.

### Reports

- `reporting/design_summary.py`:
  - Vertical, Ringo, J-Pole: “Radiator height” → “Radiator length”.
  - Inverted-L, SCV: “Vertical height” → “Vertical length”.
  - Zepp: keep “Radiator height”. That row is
    `base_height_m + matching_section_length_m`, the radiator’s top above
    ground, not its length. Optionally rename it “Radiator top height” for
    clarity, but do not call it “length”.
- `reporting/construction_sheet.py`: same mapping for SCV, Ringo, J-Pole, and
  Vertical. Keep the Zepp rows at lines 1357 and 1403 as heights.
- `ui/report_i18n.py`: add “Radiator length” → “Largo del radiador” and
  “Vertical length” → “Largo vertical”; keep “Radiator height” → “Altura del
  radiador” for Zepp.

### Help

Add or update family help for each renamed label. The help must say that this
is the physical vertical extent of the radiating element, not the total
conductor length when a loading coil or top hat is fitted, and not the
installation height. Keep EN/ES in sync and within the 240-character limit.

- `help.vertical.height`
- `help.j_pole.radiator_height`
- `help.ringo.radiator_height`
- `help.inverted_l.vertical_height`
- `help.scv.vertical_height`
- `help.phased_vertical.height` (replace the stale
  `help.phased_vertical.field.height`)

### Do not

- Do not rename `height_m`, `radiator_height_m`, `vertical_height_m`, optimizer
  variables, schema fields, or CSV/JSON columns.
- Do not change `field.height` globally; it is also the installation height for
  horizontal antennas.
- Do not rename base, feed, top, ring, coil, apex, stack, or boom heights.
- Do not rename `discone.cone_height`. The cone height is the vertical distance
  from the apex to the base plane, not the slant wire length.
- Do not rename the Zepp “Radiator height” report row.
- Do not change any numerical value, geometry, solver behavior, or default.
- Do not add a migration or bump the schema.

### Tests and documentation

- Update `tests/ui/geometry/test_scene.py:298` and
  `tests/ui/geometry/test_contract.py:269,477` for the new summary wording.
- Update `tests/unit/reporting/test_design_summary.py:496`.
- Update `tests/ui/test_form_retranslate.py` for the new phased-vertical key and
  keep the other label keys.
- Update `tests/ui/test_help.py` if help keys are added or renamed.
- Add assertions that the English and Spanish labels are correct in every
  affected editor, that the report rows use the new labels, and that
  installation-height labels did not change.
- Add a regression test that the Zepp report row stays “Radiator height” and
  that the discone cone label stays “Cone height”.
- Update `USER_GUIDE.md` where it names the vertical dimension, plus
  `CHANGELOG.md`. No ADR is required because there is no numerical, solver, or
  schema change.
- Full gate: `ruff check`, `ruff format --check`, both `mypy` passes, and
  `pytest`.

### Acceptance

- Vertical, J-Pole, Ringo, inverted-L, SCV, and phased-vertical editors use
  “length”/“largo” for the radiating element.
- Base, feed, top, ring, coil, apex, stack, boom, and available heights still
  use “height”/“altura”.
- Zepp “Radiator height” and discone “Cone height” are unchanged and documented
  as exceptions.
- Reports, construction sheet, EN/ES help, and tests are consistent.
- No schema, domain, solver, or numerical change.

### Out of scope

- Renaming the Spanish “radiador” to “irradiante”.
- Changing “Longitud horizontal” or “Longitud del stub” to “Largo”.
- Renaming discone cone height, Zepp radiator height, or any installation
  height.
- Adding new geometry or changing any simulated dimension.

## UX29 — Constructive feed connection detail (design note, 2026-11-13)

**Implemented on 2026-11-13.** This note is retained as the implementation
record.

### Context

`AntennaModel.feed` is a single `FeedPoint(wire_id, offset_m)`. The NEC deck
applies an ideal source across the segment at that point. The model has no
two-terminal port, no center/shield assignment, no balun topology, and no
common-mode current. The construction sheet can therefore describe dimensions
and give prose notes, but it cannot show the physical connection.

The Yagi is the clearest example:

- A straight driven element without a balun is a center-fed dipole: one half
  goes to the coax center and the other to the shield. That is a direct but
  unbalanced feed of a balanced antenna; the shield carries common-mode current
  unless a current balun/choke is installed.
- A folded driven element is not a simple dipole. It has two parallel
  conductors joined at both ends. The feed is a gap in one conductor; the other
  conductor is continuous and carries current. It is not a parasitic element.
  A 4:1 current balun/transformer is a common starting point, but the actual
  ratio depends on the element.
- A beta/hairpin is a shorted matching stub across the driven-element gap. It
  changes the feed impedance; it is not a balun and does not replace the
  balanced-to-unbalanced transition.
- A gamma match is not modeled because NEC-2 is unreliable for close-spaced
  gamma assemblies. The app already points the user to an equivalent matching
  network.

Today the UI shows a **Feed** marker on the sketch, a Feed & matching summary
with the feed line, balun/unun loss, balance note, and current-balun checkbox,
and prose construction notes. The Yagi note says "Feed the center of element
N"; the folded note says "the second conductor remains passive", which is
ambiguous and can be read as "parasitic". There is no connection table, no
center/shield assignment, and no schematic.

Two existing inconsistencies should be fixed in this item:

1. The hardware BOM `Balun / unun` quantity uses `project.balun_loss` and the
   ideal transformer ratio, but ignores `project.current_balun`.
2. A balanced design without a recorded current balun is visible in the Feed &
   matching summary and the construction sheet, but not in pre-flight.

### Decision

1. Add a **read-only, derived** `FeedConnectionDetail` per design. It describes
   the physical connection at the feedpoint. It is not a solver input and does
   not change the canonical model.
2. Resolve it from `AntennaDesignParameters`, the generated `AntennaModel`, and
   existing project feed state (`current_balun`, `transformer_ratio`,
   `balun_loss`, `feed_line`, matching network). No new schema in phase 1.
3. Keep four states separate and visible:
   - **Modeled:** what the solver actually uses.
   - **Recorded:** what the user says is installed.
   - **Recommended:** what the topology normally needs.
   - **Not modeled:** what the app cannot predict.
4. Expose it in three places:
   - a compact connection row and **View feed connection...** button in the
     existing Feed & matching summary;
   - a `FeedConnectionDialog` with a schematic, connection table, state matrix,
     parts, steps, and limitations;
   - a **Feedpoint assembly** section in the HTML construction sheet, native
     PDF, and ZIP package.
5. Add one family-owned descriptor for every `AntennaDesignParameters` type. A
   central registry only dispatches. If a family cannot state the physical
   mapping reliably, return `UNKNOWN` with an explicit reason; never guess.
6. Add a deterministic, renderer-neutral schematic. The UI paints it with
   QPainter; reporting exports SVG. It is marked **not to scale** and is
   separate from the canonical geometry scene.
7. Do not change `FeedPoint`, the NEC deck, the solver, or simulation results in
   phase 1.
8. No schema change in phase 1. Phase 2 may add a per-design
   `FeedInstallation` record; that requires a separate ADR and migration.

### File plan

- `domain/antennas/feed_connection.py`: enums, terminal/connection/detail
  dataclasses, and validation helpers.
- `domain/antennas/feed_balance.py`: neutral `FeedBalance` enum; re-export from
  `domain/design/feed_balance.py`.
- `domain/design/feed_connection_registry.py`: type-to-descriptor registry and
  coverage guard.
- Each family module: one `*_feed_connection(...)` function; wire IDs stay in
  the family module.
- `reporting/feed_schematic.py`: renderer-neutral schematic and SVG.
- `ui/widgets/feed_matching_summary.py`: summary row and button.
- `ui/dialogs/feed_connection_dialog.py`: schematic, table, state matrix,
  steps, and limits.
- `ui/main_window.py`: action, state, and retranslation.
- `reporting/construction_sheet.py`: feedpoint assembly section.
- `reporting/design_summary.py`: feed connection rows.
- `reporting/construction_package.py`: BOM fix.
- `ui/construction_pdf.py`: vector feed schematic and section.
- `ui/construction_package.py`: pass the schematic to HTML and PDF.
- `domain/design/preflight.py`: feed-connection warnings.
- `ui/i18n.py`: English/Spanish labels and help keys.
- Tests under `tests/unit/domain/`, `tests/unit/reporting/`, and `tests/ui/`.
- Docs: new ADR, `DOMAIN_MODEL.md`, `USER_GUIDE.md`, and `CHANGELOG.md`.

### Data model

Proposed types live in `domain/antennas/feed_connection.py`; the registry lives
in `domain/design/feed_connection_registry.py`. Names may change during
implementation, but the information must remain.

```python
class FeedTopology(StrEnum):
    CENTER_FED_DIPOLE = "center_fed_dipole"
    OFF_CENTER_FED_DIPOLE = "off_center_fed_dipole"
    FOLDED_DIPOLE = "folded_dipole"
    BETA_HAIRPIN = "beta_hairpin"
    LOOP_GAP = "loop_gap"
    BASE_FED_VERTICAL = "base_fed_vertical"
    TOP_JUNCTION_FEED = "top_junction_feed"
    END_FED = "end_fed"
    END_FED_STUB = "end_fed_stub"
    APEX_GAP = "apex_gap"
    MULTI_PORT = "multi_port"
    UNKNOWN = "unknown"


class FeedInterface(StrEnum):
    DIRECT_COAX = "direct_coax"
    CURRENT_BALUN = "current_balun"
    TRANSFORMER = "transformer"
    BALANCED_LINE = "balanced_line"
    MULTI_PORT = "multi_port"
    UNKNOWN = "unknown"


class BalunRequirement(StrEnum):
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    NOT_REQUIRED = "not_required"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class FeedTerminal:
    role_key: str
    wire_id: str | None
    offset_m: float | None
    side: str | None  # "start", "end", "before", "after", "ground", ...


@dataclass(frozen=True)
class FeedConnection:
    source_key: str
    target_key: str
    note_key: str | None = None


@dataclass(frozen=True)
class FeedConnectionDetail:
    topology: FeedTopology
    terminals: tuple[FeedTerminal, FeedTerminal]
    balance: FeedBalance  # enum moved to a neutral antennas module
    balun_requirement: BalunRequirement
    interface: FeedInterface
    transformer_ratio: float | None
    match_hardware_key: str | None
    connections: tuple[FeedConnection, ...]
    gap_m: float | None
    gap_source_key: str | None
    steps: tuple[str, ...]  # i18n keys, not localized text
    limitations: tuple[str, ...]  # i18n keys, not localized text
```

`connections` is the ordered connection table. Use stable node keys such as
`terminal.a`, `terminal.b`, `coax.center`, `coax.shield`,
`balun.unbalanced.center`, `balun.balanced.a`,
`transformer.primary.center`, `transformer.secondary.a`, `ground`, `radials`,
and `counterpoise`. This represents a balun or transformer as an explicit node
instead of pretending the coax reaches the antenna terminals directly.

`FeedBalance` currently lives in `domain/design/feed_balance.py`, which imports
every family module. Do not import that module from
`domain/antennas/feed_connection.py`: it would create a cycle once family
modules import the detail types. Move the enum to a neutral module such as
`domain/antennas/feed_balance.py` and re-export it from
`domain/design/feed_balance.py`; keep the classifier functions in the design
layer.

The state matrix should be built by a separate pure function, for example
`feed_connection_facts(detail, parameters, project)`, returning ordered
`(state, key, value)` facts. This keeps the descriptor independent from the
project record and makes the modeled/recorded/recommended/not-modeled boundary
testable.

### Topology inventory

The first implementation must cover every type in `AntennaDesignParameters`.
The following table is the starting inventory; phase 0 confirms each family's
actual feed geometry and marks `UNKNOWN` where the canonical model does not
encode it.

| Group | Families | Topology | Balance | Notes |
|---|---|---|---|---|
| Center-fed dipole | dipole, fan dipole, loaded dipole, trap dipole, inverted V, Moxon, straight Yagi, trap Yagi, hexbeam | `CENTER_FED_DIPOLE` | balanced | Current balun/choke normally required; hexbeam has `feed_gap_m` |
| Folded/loop | folded dipole, folded Yagi, full-wave loop, T2FD, quad beam, biquad | `FOLDED_DIPOLE` or `LOOP_GAP` | balanced | Transformer or current balun; loop feed at a gap |
| Off-center | OCFD | `OFF_CENTER_FED_DIPOLE` | balanced | Typical 4:1 current balun; verify the actual ratio |
| Base-fed vertical | vertical, inverted L, Ringo | `BASE_FED_VERTICAL` | unbalanced | Center to radiator; shield to radials/ground/counterpoise |
| Top-junction array | SCV half-square/bobtail | `TOP_JUNCTION_FEED` | unbalanced | Feed on the vertical below the top junction; matching and ground return are not modeled |
| End-fed | end-fed, Beverage | `END_FED` | unbalanced | Transformer/unun at the feed; counterpoise/ground return |
| End-fed stub | Zepp, J-pole | `END_FED_STUB` | balanced/unbalanced | Stub is a matching section, not a balun |
| Apex/loop gap | discone, magnetic loop | `APEX_GAP` or `LOOP_GAP` | unknown | Coax/mast/coupling transition is not modeled |
| Multi-port | phased vertical | `MULTI_PORT` | unbalanced | Primary port plus sources; combining network is ideal |
| Transmission line | G5RV, ZS6BKW, doublet | `CENTER_FED_DIPOLE` | balanced | Feed line may be balanced; do not assume coax |
| Custom/imported | custom wires, imported decks | `UNKNOWN` | unknown | Show the feed point; do not guess center/shield |

Do not infer the topology from the wire count. Use the parameter type and the
family-owned descriptor, as required by the geometry presentation contract.

### Family descriptor rules

Each family module exposes a small pure function, for example
`yagi_feed_connection(parameters, model) -> FeedConnectionDetail`. The registry
maps each parameter type to that function.

The descriptor must:

- identify both terminals with `wire_id`, `offset_m`, and `side`, and validate
  them against `to_antenna()`;
- state the balance and the balun requirement;
- state the interface (`DIRECT_COAX`, `CURRENT_BALUN`, `TRANSFORMER`,
  `BALANCED_LINE`, `MULTI_PORT`, or `UNKNOWN`);
- include the ideal transformer ratio only when the family models one;
- include matching hardware only when the family models it;
- return i18n keys, never localized text;
- list explicit limitations for every unmodeled physical item;
- return `UNKNOWN` with a reason rather than a plausible guess.

A coverage test iterates every `AntennaDesignParameters` type and fails if a
descriptor is missing, returns an invalid terminal, or uses a wire/offset that
does not exist in the generated model. A second test compares `balance` with
`feed_balance()` and `balun_requirement` with `requires_current_balun()`;
documented refinements need an explicit reason and a test.

### Yagi contract

This is the acceptance-defining case.

| Case | Terminals | Interface | Balance / balun | Modeled scope | Limitations |
|---|---|---|---|---|---|
| Straight, no match | `element-N` at center, `side="before"` and `side="after"`; tapered uses `element-N-center` | `DIRECT_COAX` when no balun is recorded, otherwise `CURRENT_BALUN` | balanced; current balun required | Ideal source at the center segment; no gap parameter | Common-mode current, shield radiation, balun balance, coax loss |
| Folded | `element-N-a` at center, `side="before"` and `side="after"`; `element-N-b` is continuous and joined at both ends | `TRANSFORMER` | balanced; current balun/transformer required | Ideal ratio from `transformer_ratio`; two conductors plus end connectors | Ideal transformer; balun frequency response, power handling, common-mode |
| Beta/hairpin | `element-N-feed` `start` and `end`; hairpin length/spacing from parameters | `CURRENT_BALUN` | balanced; current balun required | Hairpin in NEC; ratio forced to 1.0 | Hairpin tune, common-mode, no gamma |
| Gamma | none | `UNKNOWN` | unknown | Not modeled | NEC-2 close-spaced gamma unreliability; use an equivalent network |

Required Yagi wording:

- Straight: "One half to the coax center and the other to the shield is the
  direct connection, but the shield then carries common-mode current. A 1:1
  current balun/choke is normally required."
- Folded: "The second conductor is not cut; it is continuous, connected at both
  ends, and carries part of the current. It is not a parasitic element."
- Beta/hairpin: "The hairpin is a matching stub, not a balun."
- Gamma: "Not modeled; use an equivalent matching network."
- Polarity: "On a balanced load, A and B are interchangeable in the ideal model.
  With a balun, follow its marked output terminals. Without a balun, the choice
  changes the shield reference and common-mode behavior, not the ideal pattern."

For a straight Yagi the model has no `feed_gap_m`. Do not invent one. The
schematic may show a gap as a physical connection detail, but it must be marked
**not to scale** and must not be added to the canonical geometry. If the user
records a gap, store it as an as-built dimension, not as a solver parameter.

### UI contract

`FeedMatchingSummary` (`ui/widgets/feed_matching_summary.py`) adds:

- a **Connection** row with a one-line summary from the descriptor;
- a **View feed connection...** button;
- a compact state line when the recommended and recorded states differ.

`FeedConnectionDialog` (`ui/dialogs/feed_connection_dialog.py`) shows:

- the schematic at the top, marked **not to scale**;
- the ordered connection table (`source_key` → `target_key`) with notes;
- an interface summary (direct coax, current balun, transformer, balanced line,
  or multi-port);
- the four-state matrix (modeled, recorded, recommended, not modeled);
- parts, assembly steps, and a safety/weatherproofing note;
- limitations and the explicit "not a solver result" statement.

Add `Design → Feed Connection Detail...` and the summary button. The action is
enabled only with a design and disabled with an explicit reason otherwise. No
editing in phase 1.

Help keys must be added to `HELP_MANIFEST` and kept within the 240-character
limit, for example:

- `help.section.feed_connection`
- `help.action.feed_connection`
- `help.feed_connection.summary`
- `help.feed_connection.schematic`
- `help.feed_connection.table`
- `help.feed_connection.states`
- `help.feed_connection.limitations`

Every label, step, and limitation needs English and Spanish. The schematic must
not rely on color alone; use text labels and line styles. Visual light/dark and
scaling QA remains manual.

### Reporting contract

- `reporting/construction_sheet.py`: add a **Feedpoint assembly** section
  before **Construction notes**, with the schematic, connection table, state
  matrix, steps, and limitations. Use `tr(...)` for every heading and label.
- `ui/construction_pdf.py`: accept an optional `feed_schematic_svg` (and a
  raster fallback if needed), draw it as a vector figure, and repeat the table,
  steps, and limitations with page-break safety.
- `ui/construction_package.py`: pass the feed schematic to the HTML and PDF.
  Keep the ZIP contents to the existing HTML, PDF, CSVs, build notes, and
  optional pre-flight; a separate feed CSV is optional.
- `reporting/design_summary.py`: add `feed_connection_rows(detail)` so the
  HTML report and PDF can show the physical connection separately from
  `feed_matching_rows`, which remains the electrical chain.
- `reporting/construction_package.py`: fix the `Balun / unun` hardware row so
  `project.current_balun` contributes to the quantity and the note; do not
  double-count the loss model. Add generic feed hardware rows only where they
  are real parts, not as invented ratings.
- `domain/design/preflight.py`: add warnings for a balanced antenna without a
  recorded current balun, a folded Yagi with ratio 1.0, and a beta/hairpin with
  a ratio other than 1.0. Add an information finding when the feed gap is not
  modeled. These are warnings/information, not errors.

### Schematic contract

- Renderer-neutral and deterministic; no Qt imports in domain or reporting.
- Fixed layout per topology; no automatic graph layout.
- Nodes, edges, and symbols with text labels: A, B, center, shield, balun
  ratio, match hardware, ground/radials/counterpoise, feed line.
- Marked **not to scale**; never used as a dimension source.
- UI uses the theme palette; reporting uses black/white-friendly strokes.
- SVG for HTML and PDF; QPainter for the dialog; raster fallback only when SVG
  is unavailable.
- Do not export the schematic to DXF; the construction DXF remains geometry.
- Snapshot tests assert structure and labels, not pixels.
- **Refined by UX31 (2026-11-17):** the drawing is now per interface, coax is
  drawn as a cable with a cross-section, and terminal labels come from
  `FeedTerminal.side`. The QPainter path was not added; the same SVG is used by
  the dialog, sheet, PDF, and ZIP.

### Wording rules

- Never say the app simulates the balun, the choke, or common-mode current.
- Use **modeled**, **recorded**, **recommended**, and **not modeled** exactly.
- A balun is not a tuner; a 1:1 balun does not fix SWR.
- An unun is not a balun; a 49:1 end-fed transformer still needs a
  counterpoise/return and normally a choke on the coax.
- A beta/hairpin is not a balun; a gamma is not modeled.
- A folded element's second conductor is not a parasitic.
- Do not claim a unique polarity for a balanced load.
- Do not invent a feed gap, power rating, or choke impedance. Use family
  parameters or report the limitation.

### Tests

- Domain: Yagi straight, folded, beta/hairpin, gamma, and tapered; every family
  descriptor; coverage manifest; terminal validation; consistency with
  `feed_balance`; no localized text in the domain.
- Reporting: construction sheet section, connection table, state matrix,
  limitations, deterministic SVG, PDF section, ZIP contents, BOM balun quantity,
  pre-flight warnings.
- UI: summary row and button, dialog content, Yagi cases, no-design state,
  retranslation, help manifest, enabled/disabled action, accessibility labels.
- Regression: simulation fingerprint and a sample result are unchanged; schema
  stays 45 in phase 1.
- Full gate: `ruff check`, `ruff format --check`, both `mypy` passes, and
  `pytest` with `NEC2C` where available.

### Acceptance

- A user can see, for a Yagi, whether the connection is direct coax, a current
  balun, a folded transformer, or a beta/hairpin, and which conductor goes to
  which terminal.
- Every family has a descriptor or an explicit `UNKNOWN` with a reason.
- The construction sheet, PDF, and ZIP contain a feedpoint assembly with the
  schematic, connection table, steps, and limitations.
- The UI keeps modeled, recorded, recommended, and not-modeled states separate.
- No solver, schema, or numerical change.
- EN/ES, help coverage, and the full gate pass.

### Out of scope

- Modeling common-mode current, balun balance, frequency response, power
  handling, or coax shield radiation.
- Real connector loss, weatherproofing physics, or mechanical drawings.
- Gamma/delta match modeling.
- Replacing `FeedPoint` with a two-terminal `FeedPort`.
- A per-design `FeedInstallation` record (phase 2, separate ADR and migration).
- Drawing a synthetic gap in the canonical geometry or exporting the schematic
  to DXF.
- Auto-selecting a balun or changing the design.

### Phases

- **Phase 0, taxonomy and family inventory:** 0.5–1 day. Confirm the table above
  against the family builders and mark unknown cases.
- **Phase 1, read-only detail:** 5–8 days. Types, descriptors, registry, UI,
  sheet/PDF/ZIP, tests, docs. This is the shippable slice.
- **Phase 2, installation record:** 3–5 days, only if users need structured
  connector/balun/weatherproofing metadata. Requires an ADR and a later schema
  (47 or higher).
- **Phase 3, real electrical models:** blocked by G27 and traceable data.

### Risks

- A schematic can be read as a solver result. Mitigate with the four-state
  matrix and the "not to scale / not a solver result" label.
- Family coverage can drift. Mitigate with a coverage test that fails on every
  missing descriptor.
- The i18n/help surface is large. Mitigate with keys, the help manifest, and
  EN/ES tests.
- `current_balun` is project-global. Document the limitation and do not change
  it in phase 1; a per-design record is a phase 2 decision.
- Balanced feed lines and multi-port arrays do not fit a single coax schematic.
  Use `BALANCED_LINE`/`MULTI_PORT` and explicit limitations; do not guess.

## UX30 — Per-template default conductor material (design note, 2026-11-17)

**Status:** implemented on 2026-11-17. This note is retained as the execution
record. The resolver, domain defaults, form selectors, reference-library
materials, tests, and documentation are in place.

### Problem

`ConductorMaterial` is stored per wire, but every editor starts its material
selector at the first preset, **Copper**. Only `LogPeriodicParameters` and
`LogPeriodicForm` start at **Aluminum**. As a result, a new Yagi, vertical,
J Pole, Slim Jim, discone, Ringo, or beam starts with copper even when the
common amateur construction uses aluminum or stainless steel. The user asked
for the material normally used to build each antenna to be preselected, while
keeping the selector editable.

This is a defaults change. It does not add a material, change the solver code,
change the schema, or rewrite existing projects. New designs can produce a
slightly different conductor loss because they start with a different material;
that is the intended effect, not a solver change.

### Decision

- Add one pure **template → default material** resolver. Suggested location:
  `src/antennadesk/domain/antennas/material_defaults.py`. Key it by the catalog
  or template identifier, not by `AntennaFamily`.
- The resolver belongs to the domain layer and must not import `ui/` or
  PySide6. Keep the key strings stable in the resolver or move the catalog key
  constants to a shared domain module; do not import the catalog dialog.
- Suggested API: `default_material_for_template(template_id: str) ->
  ConductorMaterial`. It owns the complete mapping and falls back to `COPPER`
  only for an unknown/custom key; a coverage test must fail if a catalog key is
  missing or an extra key is present.
- Do not derive the default from `AntennaFamily`. `moxon`, `hexbeam`,
  `quad_beam`, `biquad`, `double_biquad`, and `half_square` are wire models but
  are explicitly assigned aluminum by this decision; `bobtail_curtain` and
  `inverted_l` stay copper despite their catalog family.
- Use the resolver in every new-design editor and in any new-design factory
  wrapper that initializes a fresh template. Do not use it inside the published
  reference factories, and do not scatter `ALUMINUM` or `STAINLESS_STEEL_304`
  literals across forms.
- Keep `CONDUCTOR_MATERIALS` in the order
  `(COPPER, ALUMINUM, STAINLESS_STEEL_304)` and keep the shared combo helper.
  Select by `findData(...)`, not by index.
- The selector remains editable. The default is only the initial selection.
- Existing designs keep their stored material when opened or edited; only a new
  design gets the template default.
- Material remains a conductor-loss input (`conductivity_s_per_m`,
  `relative_permeability`), not a structural or tubing model.
- Confirmed choices from the project owner on 2026-11-17: Moxon, Hexbeam, Quad
  beam, Biquad (both variants), and Half square are aluminum; Bobtail curtain
  and Inverted L remain copper; J Pole and Slim Jim are aluminum; Loaded
  vertical is stainless steel 304.

### Target mapping

Use these exact catalog keys. The labels are the existing catalog labels.

**Aluminum — 15 templates**

| Key | Label |
|---|---|
| `yagi` | Yagi |
| `trap_yagi` | Trapped Yagi |
| `log_periodic` | Log-periodic (LPDA); already aluminum |
| `vertical` | Vertical + radials |
| `ringo` | Ringo |
| `j_pole` | J Pole |
| `slim_jim` | Slim Jim |
| `discone` | Discone |
| `phased_vertical` | Phased vertical array |
| `moxon` | Moxon rectangle |
| `hexbeam` | Hexbeam |
| `quad_beam` | Quad beam |
| `biquad` | Biquad |
| `double_biquad` | Double biquad |
| `half_square` | Half square |

**Stainless steel 304 — 1 template**

| Key | Label |
|---|---|
| `loaded_vertical` | Loaded vertical / mobile whip |

**Copper — 25 templates**

| Key | Label |
|---|---|
| `wire_dipole` | Wire dipole |
| `folded_dipole` | Folded dipole |
| `bobtail_curtain` | Bobtail curtain |
| `beverage` | Beverage |
| `loaded_dipole` | Loaded / linked dipole |
| `endfed` | End-fed wire / EFHW |
| `sloper` | Sloper |
| `random_wire` | Random wire |
| `shortened_endfed_80_10` | Shortened EFHW 80-10 m |
| `shortened_endfed_40_10` | Shortened EFHW 40-20-10 m |
| `g5rv` | G5RV |
| `zs6bkw` | ZS6BKW |
| `zepp` | Zepp |
| `doublet` | Doublet |
| `fan_dipole` | Fan dipole |
| `trap_dipole` | Trap dipole |
| `t2fd` | T2FD |
| `inverted_v` | Inverted-V |
| `inverted_l` | Inverted L |
| `ocfd` | Off-center-fed dipole |
| `loop` | Loop |
| `delta_loop` | Delta loop |
| `quad_loop` | Quad loop |
| `magnetic_loop` | Magnetic loop |
| `custom` | Custom wires |

Counts: **15 aluminum + 1 stainless 304 + 25 copper = 41 catalog templates**.
The 15 aluminum entries include the already-aluminum `log_periodic`; therefore
**14 templates change from copper to aluminum** and **1 changes from copper to
stainless 304**.

### Current audit

- `src/antennadesk/domain/antennas/materials.py` defines
  `CONDUCTOR_MATERIALS = (COPPER, ALUMINUM, STAINLESS_STEEL_304)`.
- `src/antennadesk/ui/material_combo.py` adds the presets in that order and does
  not select a default.
- `src/antennadesk/ui/widgets/log_periodic_form.py:137` is the only form that
  explicitly selects aluminum; its `set_parameters` fallback also selects
  aluminum when the material is unknown.
- Every other family `*Parameters` with a material field defaults to `COPPER`,
  except `LogPeriodicParameters`, which defaults to `ALUMINUM`.
  `CustomAntennaParameters` has no single material field; its editor starts
  each new wire at copper.
- `src/antennadesk/ui/main_window.py` routes New Antenna through the `new_*`
  dialog methods and Change Template through `_parameters_from_catalog`; both
  use the same family dialogs. Do not add a second material map.
- `src/antennadesk/ui/dialogs/design_from_frequency_dialog.py` preserves the
  current design material. Do not add a material selector there.
- `tests/ui/test_yagi_dialog.py:44` and
  `tests/ui/test_vertical_dialog.py:22` assert `"Copper"` and must change.
- `tests/ui/test_custom_dialog.py:25` and
  `tests/ui/test_inverted_v_dialog.py:23` stay `"Copper"`.
- `tests/ui/test_log_periodic_dialog.py` and
  `tests/unit/domain/test_log_periodic.py:46` stay aluminum.
- `docs/MATERIALS_REFERENCE.md:20` currently says copper is the default
  conductor for general HF wire; update it to describe the per-template
  defaults without changing the material data.
- The UX25 note in this file says “Keep copper as the default material in every
  editor” and “Do not make 304 the default.” The superseded note added there
  makes UX30 authoritative for new-design template defaults only.

### Domain and factory constraints

- Set the dataclass default `material=ALUMINUM` for:
  `YagiParameters`, `TrapYagiParameters`, `VerticalParameters`,
  `RingoParameters`, `JPoleParameters`, `DisconeParameters`,
  `PhasedVerticalParameters`, `MoxonParameters`, `HexbeamParameters`,
  `QuadBeamParameters`, and `BiquadParameters`.
- Keep `LogPeriodicParameters` at `ALUMINUM`.
- Keep the published source-factory defaults `moxon_20m_wire(...,
  material=COPPER)` and `published_hexbeam_parameters(..., material=COPPER)`.
  They describe source-backed wire references, not the generic template
  default. The new Moxon/Hexbeam editors select aluminum through the resolver.
  If an implementation changes either factory default, every reference-library
  call must pass explicit copper.
- `ScvParameters` covers both variants. Keep the dataclass default `COPPER`, but
  make `scv_parameters(kind, ..., material: ConductorMaterial | None = None)`
  choose `ALUMINUM` for `HALF_SQUARE` and `COPPER` for `BOBTAIL_CURTAIN` when
  the caller does not pass an explicit material. Preserve every explicit
  material override, including the reference-library copper override. The form
  must produce the same result. Add tests for both kinds.
- `VerticalParameters` is shared by **Vertical + radials** and **Loaded
  vertical / mobile whip**. Default it to `ALUMINUM`. The loaded-vertical dialog
  path (`VerticalDialog(mobile=True)`) must pass or select
  `STAINLESS_STEEL_304`. Do not infer 304 from `loading_coil_enabled` alone,
  because a normal vertical can enable a loading coil.
- Copper families keep their `COPPER` defaults:
  `DipoleParameters`, `FoldedDipoleParameters`, `LoopParameters`,
  `MagneticLoopParameters`, `OCFDParameters`, `InvertedVParameters`,
  `InvertedLParameters`, `FanDipoleParameters`, `EndFedParameters`,
  `LoadedDipoleParameters`, `TrapDipoleParameters`, `T2FDParameters`,
  `BeverageParameters`, `ZeppParameters`,
  `TransmissionLineDoubletParameters`, and `CustomAntennaParameters`.
  The `g5rv_parameters`, `zs6bkw_parameters`, and `doublet_parameters`
  factories also keep `material=COPPER`; G5RV and ZS6BKW return
  `CustomAntennaParameters`, and the doublet returns `DipoleParameters`.
- `DesignIntent.material` stays `COPPER`. The current UI paths that need a
  template default must pass it explicitly; `DesignFromFrequencyDialog`
  preserves the design material. Add a regression test. Do not add a hidden
  sentinel or make `DesignIntent` guess from `antenna_type` in this item.
- `moxon_20m_wire`, `published_hexbeam_parameters`, and `scv_parameters` are
  also used by the source-backed reference library. Keep the published
  reference material explicit (see below); do not let a template default
  silently rewrite a published design.

### UI constraints

Affected forms:

- `src/antennadesk/ui/widgets/yagi_form.py`
- `src/antennadesk/ui/widgets/trap_yagi_form.py`
- `src/antennadesk/ui/widgets/vertical_form.py`
- `src/antennadesk/ui/widgets/ringo_form.py`
- `src/antennadesk/ui/widgets/j_pole_form.py`
- `src/antennadesk/ui/widgets/discone_form.py`
- `src/antennadesk/ui/widgets/phased_vertical_form.py`
- `src/antennadesk/ui/widgets/moxon_form.py`
- `src/antennadesk/ui/widgets/hexbeam_form.py`
- `src/antennadesk/ui/widgets/quad_beam_form.py`
- `src/antennadesk/ui/widgets/biquad_form.py`
- `src/antennadesk/ui/widgets/scv_form.py`

Rules:

- A **new** design selects the resolver material. An editor opened with
  `parameters` must preserve `parameters.material`; never replace an existing
  design's material with the template default.
- Forms that load a starting factory in `__init__` (`HexbeamForm`, `ScvForm`,
  and any similar pattern) must ensure the factory call uses the template
  default or select the default after `set_parameters`, but only on the
  no-existing-parameters path. Do not break the `parameters` path.
- Dialogs delegate to their forms. Keep
  `YagiDialog`, `TrapYagiDialog`, `VerticalDialog`, `RingoDialog`,
  `JPoleDialog`, `DisconeDialog`, `PhasedVerticalDialog`, `MoxonDialog`,
  `HexbeamDialog`, `QuadBeamDialog`, `BiquadDialog`, and `ScvDialog`
  consistent. `JPoleDialog` must produce aluminum for both J Pole and Slim Jim.
  `ScvDialog`/`ScvForm` must produce aluminum for Half square and copper for
  Bobtail.
- `Loaded vertical` is the existing `VerticalDialog(mobile=True)` path. It must
  preselect 304; `VerticalDialog(mobile=False)` preselects aluminum.
  `VerticalForm.load_mobile_example()` must not reset the material selector to
  copper.
- `log_periodic_form.py` keeps aluminum. The copper forms and
  `custom_antenna_dialog.py` keep copper; do not add overrides to them.
- Keep the material combo order and the shared `populate_material_combo` /
  `retranslate_material_combo` behavior. Do not add a second material list.
  Prefer one small helper to select the resolver default with `findData(...)`
  instead of repeating the same three lines in twelve forms.
- Do not add a new i18n key for this change; “Aluminum” and “Stainless steel
  304” already exist. Optionally review `help.field.material` and add one short
  sentence that the initial preset follows the template, if it fits the
  240-character EN/ES limit.

### Catalog routes

- New Antenna uses `AntennaCatalogDialog` plus the `new_*` dialog methods;
  Change Template uses the same catalog and `_parameters_from_catalog`. Both
  must reach the same family dialogs. Do not add a separate material map in
  `main_window.py`.
- Change Template from an existing design to a different template gets the new
  template default. Opening and editing an existing design keeps its stored
  material. If Change Template resolves to the same catalog key as the current
  design, preserve the current material instead of resetting it; add a
  regression test for a copper Yagi re-accepting the Yagi template.
- Doublet Change Template uses `DoubletDialog`; it stays copper.
- `Design from frequency` preserves the current material; it does not reset it
  to the template default.
- Reports, the wire schedule, and the BOM already read the wire material; no
  reporting/BOM code change is required. Update a report test only if it
  asserts a default material for a changed template.

### Reference library

`src/antennadesk/domain/design/reference_library.py` must keep the material
documented by each source, even when the new template default differs:

- `_cebik_moxon()`: pass `material=COPPER` explicitly to `moxon_20m_wire`; the
  Cebik 20 m reference is a #14 copper-wire Moxon.
- `_g3txq_hexbeam()`: pass `material=COPPER` explicitly to
  `published_hexbeam_parameters`; the reference is a wire-element hexbeam.
- `_cebik_half_square()`: pass `material=COPPER` explicitly to
  `scv_parameters`; the Cebik reference uses #12 copper wire.
- `_cebik_bobtail_curtain()`: copper; explicit is fine.
- `_nbs_yagi()`: audit the source. If the source does not state a conductor
  material, keep the existing reference material and document the limitation.
  Do not silently change a published reference.
- Other reference designs keep their current material.

Add tests that assert these source-backed reference materials. A template
default must never mutate a `ReferenceDesign` constructor.

### Tests

Add `tests/ui/test_material_defaults.py` or extend the existing dialog tests.
At minimum cover:

- New Yagi: Aluminum.
- New Trapped Yagi: Aluminum.
- New Vertical: Aluminum.
- New Loaded vertical: Stainless steel 304.
- New Ringo: Aluminum.
- New J Pole: Aluminum.
- New Slim Jim: Aluminum.
- New Discone: Aluminum.
- New Phased vertical: Aluminum.
- New Moxon: Aluminum.
- New Hexbeam: Aluminum.
- New Quad beam: Aluminum.
- New Biquad: Aluminum.
- New Double biquad: Aluminum.
- New Half square: Aluminum.
- New Bobtail curtain: Copper.
- New Inverted L: Copper.
- New Custom: Copper.
- New Log-periodic: Aluminum (regression; already).
- New wire dipole, folded dipole, loop/delta/quad loop, OCFD, all end-fed
  presets, G5RV, ZS6BKW, Zepp, doublet, fan dipole, trap dipole, T2FD,
  inverted V, Beverage, loaded dipole, and magnetic loop: Copper (regression).

Additional coverage:

- Resolver coverage: iterate `antenna_catalog_dialog.ENTRIES` and assert every
  catalog key has exactly one mapped material; fail on missing or extra keys.
- Existing-design preservation: open an affected dialog with `parameters`
  whose material is `COPPER` or `STAINLESS_STEEL_304` and assert the dialog
  keeps it.
- Persistence regression: save/reopen a project with a copper Yagi or an
  aluminum vertical and assert the wire materials are unchanged; no migration
  is involved.
- `Change Template`: at least one aluminum template and the loaded-vertical
  304 path; assert the created design material. Also assert that a copper Yagi
  re-accepting the same Yagi template keeps copper.
- `Design from frequency`: assert it preserves the current design material.
- `ScvKind`: `scv_parameters(HALF_SQUARE)` is aluminum and
  `scv_parameters(BOBTAIL_CURTAIN)` is copper, with an explicit override still
  respected.
- `VerticalDialog(mobile=False)` is aluminum and `mobile=True` is 304.
- Reference library: Cebik Moxon, G3TXQ Hexbeam, and Cebik half square remain
  copper; Cebik bobtail remains copper; NBS Yagi matches its documented value.
- Domain defaults for every changed `*Parameters` constructor.
- `moxon_20m_wire`, `published_hexbeam_parameters`, and `scv_parameters`
  source-factory behavior remains source-faithful.

Update existing tests:

- `tests/ui/test_yagi_dialog.py:44`: Copper → Aluminum.
- `tests/ui/test_vertical_dialog.py:22`: Copper → Aluminum; add the mobile 304
  assertion.
- Keep `tests/ui/test_custom_dialog.py:25` and
  `tests/ui/test_inverted_v_dialog.py:23` at Copper.
- Keep `tests/ui/test_log_periodic_dialog.py` and
  `tests/unit/domain/test_log_periodic.py:46` at Aluminum.
- Keep `tests/ui/test_form_retranslate.py` material-order assertions.
- Full gate: `uv run ruff check .`, `uv run ruff format --check .`,
  `uv run mypy`, `uv run mypy --config-file mypy_ui.ini`, and
  `uv run pytest` with `NEC2C` when available.

### Documentation

- `docs/MATERIALS_REFERENCE.md`: replace the sentence that copper is the
  default for general HF wire with a short per-template default table or a
  pointer to the resolver. Keep the material conductivity, source, and
  limitation tables unchanged.
- `docs/DOMAIN_MODEL.md`: add a short “Default material by template”
  subsection or a pointer to the resolver. State that material is a conductor
  preset, not a structural/tubing model. Keep the existing per-family text.
- `docs/USER_GUIDE.md`: state that new designs preselect the common material,
  the selector remains editable, and existing projects keep their material.
- `CHANGELOG.md`: add the new defaults under the unreleased section.
- Update the UX25 note and this item when implementation is complete. Do not
  mark UX30 done before the full gate passes.
- No ADR is required: no solver, schema, persistence, or architecture change.
  If a formal product decision record is desired, add one line to
  `docs/archive/founding-decisions.md`; do not create an ADR for a default selector.

### Acceptance

- Every new-design editor preselects the exact material in the mapping; the
  selector remains editable.
- Existing designs and reference designs keep their stored/source material.
- 15 templates default to aluminum (including the already-aluminum
  log-periodic), 1 to stainless 304, and 25 to copper.
- J Pole and Slim Jim are aluminum; Half square is aluminum; Bobtail is copper;
  Vertical is aluminum; Loaded vertical is 304.
- `CONDUCTOR_MATERIALS` order and the shared combo helper are unchanged.
- No schema or migration, no solver-code change, no importer change, and no
  radius/geometry change.
- Tests, documentation, and the full gate pass; EN/ES labels remain unchanged.

### Do not

- Do not derive the default from `AntennaFamily`.
- Do not reorder `CONDUCTOR_MATERIALS` or add a new material.
- Do not change existing project materials or add a migration.
- Do not change wire radii or model aluminum tubing in this item. The wire
  models stay wire models.
- Do not add per-wire material mixing (for example aluminum radiator plus
  copper radials); a family editor still applies one material to all generated
  wires.
- Do not change `DesignIntent.material` with a hidden sentinel or geometry
  inference.
- Do not change the NEC importer, `write_nec2_input`, `validate_nec2_assumptions`,
  `LD 5`, the solver code, or the conductor-loss formulas.
- Do not silently change a source-backed reference design.
- Do not add a universal 304 default; 304 applies only to `loaded_vertical`.

### Out of scope

- Aluminum-tube geometry, radius presets, or structural modeling.
- Per-wire material mixing and defaults for radials vs radiator.
- Changing imported NEC/MMANA deck materials.
- A custom-material editor or a new conductor preset.
- Changing the material selector’s labels, order, or solver semantics.
- Changing any existing project file, schema version, or migration.

### Implementation order

1. Add the resolver and the domain defaults; add unit tests.
2. Apply the resolver to the affected forms and dialogs; keep the
   existing-parameters path untouched.
3. Update the reference library with explicit source materials and tests.
4. Update existing tests and add per-template default coverage.
5. Update documentation and `CHANGELOG.md`; run the full gate.

### Risks

- Split families (`ScvKind`, `VerticalDialog(mobile=...)`) can take the wrong
  default; test both branches.
- Forms that load a preset factory in `__init__` can overwrite the combo;
  apply the default only for a new design.
- Reference-library drift is the main correctness risk; explicit source
  materials and tests are mandatory.
- Changing a default material changes conductor loss. Audit tests and fixtures
  that build a design without an explicit material; make unrelated fixtures
  explicit instead of rewriting expected physics. Do not change source-backed
  reference values to absorb a default change.
- `Change Template` and `Design from frequency` are separate paths; test both.
- The old UX25 “Copper remains the default” wording can confuse a reviewer;
  the superseded note must remain visible.

## UX31 — Draw coax as coax in the feed-connection schematic (design note, 2026-11-17)

**Status:** implemented on 2026-11-17. This note is retained as the execution
record. The direct-coax drawing, cross-section, per-interface layouts, terminal
labels, and EN/ES coverage are in place.

### Problem

`reporting/feed_schematic.py::feed_schematic_svg()` always renders one generic
four-terminal block diagram, regardless of `FeedInterface`:

- two left lines with hardcoded `Antenna terminal A` and `Antenna terminal B`;
- a rounded box in the middle labeled with the interface (`Direct coax`,
  `1:1 current balun`, ...);
- two right lines labeled `Coax center` and `Coax shield` for every coax-side
  interface.

The user reported that this looks like a box with two conductors entering and
two leaving, not like a coaxial cable where one conductor is the center and the
shield surrounds it. The concern is valid: the drawing is a block diagram, not
a construction drawing, and for direct coax the block misrepresents the
physical connection.

For `DIRECT_COAX` this is physically wrong and contradicts the text:

1. There is no device between the antenna and the coax; the box invents an
   adapter or balun.
2. Two parallel right-hand lines are the usual symbol for a balanced two-wire
   line, not coaxial cable.
3. The shield is not drawn around the center conductor, so the coaxial
   construction and the shield's exterior/common-mode path are invisible.
4. The four-terminal box looks like a balun in the one case where the text says
   there is no balun.
5. `Antenna terminal B` is hardcoded even when the terminal is `ground`
   (vertical) or `counterpoise` (end-fed).
6. `CURRENT_BALUN`, `TRANSFORMER`, `BALANCED_LINE`, `MULTI_PORT`, and `UNKNOWN`
   reuse the same layout; only the center label changes.

The summary and connection table are correct. A construction aid must not
contradict them. A user can miswire the shield or add an unnecessary device
based on the drawing.

### Decision

1. Keep the deterministic, renderer-neutral SVG builder in
   `reporting/feed_schematic.py`; do not use AI-generated images, raster
   assets, or ASCII in the app.
2. Use a per-interface drawing. Keep a device block only where a real device
   exists (`CURRENT_BALUN`, `TRANSFORMER`, `MULTI_PORT`). For `DIRECT_COAX`,
   draw only the cable and the two connections. For `BALANCED_LINE`, draw a
   two-conductor line with no coax. For `UNKNOWN`, use a dashed
   “verify wiring” block.
3. Draw coax as coax: center conductor inside an outer shield, a
   cutaway/termination at the antenna end, and a small cross-section inset.
   Never draw coax as two parallel lines.
4. Derive the drawing from `FeedConnectionDetail` (`interface`, `topology`,
   `terminals`, `connections`, `transformer_ratio`, `match_hardware`). Do not
   add a second hardcoded mapping that can drift from the table.
5. Derive left-side labels from `FeedTerminal.side`:
   - `before`, `after`, or `start`/`end` on a wire: `Antenna terminal {role}`;
   - `ground`: `Ground / radials`;
   - `counterpoise`: `Counterpoise`;
   - no wire / unknown: `Return`.
6. Keep the four states visible: solid for the modeled/recorded path, dashed
   for unknown or “recommended but not recorded”.
7. Keep `Schematic · not to scale` and `Construction aid, not a solver result.`
8. No domain, solver, schema, persistence, or numerical change.
   `FeedConnectionDetail` already carries the needed information.

UX29's schematic contract is refined, not replaced. The implemented path is one
renderer-neutral SVG used by the dialog (`QSvgWidget`), the HTML construction
sheet, the native PDF, and the ZIP. Do not add the QPainter path described in
the original UX29 note. The theme-palette bullet is still unimplemented; UX31
keeps the existing white background and fixes only the topology and coax
depiction.

### Visual contract

The ASCII below is the topology specification, not the final rendering. The
final output is SVG; do not put ASCII in a `QLabel`/`QTextEdit`.

#### Direct coax

```text
DIRECT COAX - wiring view (not to scale)

   antenna side                          coax side
   A o--------------+
                    |  center conductor
                    +------------------>  @  center

   B o--------------+
                    |  shield braid
                    +------------------>  O  shield
                                             (surrounds the center)

COAX CROSS-SECTION

        +-----------------+
        |    +-------+    |
        |    |   @   |    |    @ = center conductor
        |    +-------+    |    O = shield / braid
        +-----------------+
```

Rules:

- One cable, not two. The two right-hand arrows are the two conductors of the
  same coax; in the SVG, draw a single cable body with a cutaway at the top
  and a cross-section inset.
- The shield is the outer conductor and also the outside of the cable. Draw it
  as a tube/ring, not as a second wire beside the center.
- In the balanced center-fed case, do not add a third wire or a separate ground
  symbol for the shield; it is both the return conductor and the cable
  exterior. In the base-fed/end-fed case, the shield/return connects to
  ground/radials or the counterpoise and may use the corresponding symbol.
- A → center, B → shield for a balanced center-fed load. Keep the order from
  `detail.connections`.
- Do not draw a middle box. A caption `Direct coax` is allowed above or below
  the drawing; it must not look like a device.
- If the recommended choke is shown, draw it dashed and label it
  `Recommended, not recorded`; never solid, never on the modeled path.

#### Current balun

```text
1:1 CURRENT BALUN / CHOKE (recorded)

   A o--------------+     +----------------+
                    |     | 1:1 current    |
                    +-----+ balun / choke  |
   B o--------------+     +----------------+
                              |        |
                           center    shield
                              +----+---+
                                   |
                              +----+----+
                              |  COAX   |
                              |  @   O  |
                              +----+----+
                                   |
                                to rig
```

- The block is legitimate here; label it `recorded` only when
  `current_balun` is true.
- Left side: balanced A/B. Right side: coax center/shield with the coax symbol.
- Do not invent winding topology or a specific choke impedance.

#### Transformer / balun

- Draw a generic two-port transformer/balun block or an ideal transformer
  symbol.
- Show `{ratio}:1` from `detail.transformer_ratio` (for example `4:1`).
- Label the antenna side `secondary A/B` and the coax side
  `primary center/shield`.
- Label the model `ideal`; do not imply a real core, winding, or power rating.
- For a folded Yagi, the secondary is across A/B; the text still says conductor
  B is continuous and not a parasitic.

#### Balanced line

- Two parallel conductors, no coax symbol.
- Left A/B; right `Balanced line A/B`.
- Note: `The balun location depends on the tuner; it is not modeled.`

#### Multi-port

- Keep a combining block; label `Primary port` and `Return`/`Additional
  sources`.
- State `Combining network not modeled.`

#### Unknown

- Dashed block with `?`; label `Verify the wiring`.
- Do not guess center/shield or draw a coax.

#### General

- Draw an un-dimensioned feed gap only where the topology has one; never add a
  numeric gap unless `detail.gap_m` is present and sourced.
- Keep the existing labels `Direct coax`, `Coax center`, and `Coax shield` in
  the SVG where they remain accurate; do not rename the canonical
  connection-table targets in this item.
- Do not show a balun, choke, or transformer as installed unless the project
  record says so.

### Terminal-label rules

| `FeedTerminal.side` | Left label |
|---|---|
| `before`, `after` | `Antenna terminal {role}` |
| `start`, `end` with `wire_id` | `Antenna terminal {role}` |
| `ground` | `Ground / radials` |
| `counterpoise` | `Counterpoise` |
| `wire_id is None` or unknown | `Return` |

For `wire_id is None` and a side other than `ground`/`counterpoise`, use
`Return`; never label it `Antenna terminal B`.

Right-side labels:

| Interface | Right labels |
|---|---|
| `DIRECT_COAX`, `CURRENT_BALUN`, `TRANSFORMER` | `Coax center`, `Coax shield`, with coax symbol and cross-section |
| `BALANCED_LINE` | `Balanced line A`, `Balanced line B` |
| `MULTI_PORT` | `Primary port`, `Additional sources`/`Return` |
| `UNKNOWN` | `Verify the wiring` |

### File plan

- `src/antennadesk/reporting/feed_schematic.py`: rewrite the renderer. Add
  helpers such as `_terminal_label`, `_coax_cable`, `_coax_cross_section`,
  `_device_block`, `_balanced_line`, and `_unknown_block`. Add semantic
  `id` groups (`antenna-side`, `coax`, `coax-cross-section`,
  `interface-device`, `balanced-line`, `unknown`) for tests.
- `src/antennadesk/ui/report_i18n.py`: add the English/Spanish labels listed
  below. Keep existing canonical table labels unchanged.
- `src/antennadesk/ui/i18n.py`: update `help.feed_connection.schematic`
  (EN/ES) to mention the physical wiring and coax cross-section; keep the help
  coverage manifest green.
- `src/antennadesk/ui/dialogs/feed_connection_dialog.py`: verify the
  `QSvgWidget` size and minimum height accommodate the new drawing; no logic
  change expected.
- `src/antennadesk/ui/construction_pdf.py`: verify `_figure_size`/`draw_figure`
  and page breaks with the new SVG height; no logic change expected.
- `tests/unit/reporting/test_feed_schematic.py`: replace the two string-only
  tests with semantic structure and mapping tests.
- `tests/unit/reporting/test_construction_sheet.py`: update the feed section
  assertions if the drawing changes; keep the section embedded.
- `tests/ui/test_feed_connection_dialog.py`: update only if an assertion
  depends on a removed drawing label; the connection-table expectations stay.
- `docs/USER_GUIDE.md`: update the **Feed connection detail** section with the
  new visual language and state meanings.
- `CHANGELOG.md`: add a Fixed/Changed entry under Unreleased.
- `docs/AUTONOMOUS_BACKLOG.md`: mark UX31 done and add a pointer from UX29
  when implemented.
- No domain, solver, persistence, schema, or migration files.

### Data and architecture constraints

- Do not change `domain/antennas/feed_connection.py`,
  `domain/design/feed_connection.py`, `FeedPoint`, `AntennaModel`,
  `write_nec2_input`, the solver, or the schema.
- `feed_schematic_svg(detail, labeler)` stays pure and deterministic; no Qt
  imports in `reporting` or `domain`.
- Do not localize inside reporting; use the labeler. New labels must be in
  `ui/report_i18n.py`, not in the domain.
- `detail.connections` remains the authoritative connection table; the drawing
  must not add or omit connections. If a connection is not drawable, show it
  as text or an explicit unknown, not silently.
- Keep the existing SVG width (720 px) if possible; height may grow for the
  cross-section. Verify `construction_pdf.py` `_figure_size`/`draw_figure` and
  page breaks.
- Use standard SVG primitives (`rect`, `line`, `circle`, `path`, `text`); no
  external fonts, images, markers, or CSS variables. `QSvgRenderer` must
  render it.
- No new dependency; use the existing SVG path (`QSvgWidget`/`QSvgRenderer`)
  and the existing translation/reporting helpers.
- Use unique `id` values if more than one schematic can appear in one HTML
  document; currently one per sheet. Prefix if needed.
- Keep the white background for print/HTML; theme-aware dark SVG is out of
  scope. If the dialog's dark theme makes the white card jarring, record it as
  a separate cosmetic item.

### Labels and help

Add English/Spanish pairs; keep the wording consistent with the existing
`Coax center`/`Coax shield` table labels:

- `Center conductor` / `Conductor central`
- `Shield (braid)` / `Malla (trenza)`
- `Coax cross-section` / `Sección del coaxil`
- `Coax cable` / `Cable coaxil`
- `Ground / radials` / `Tierra / radiales`
- `Counterpoise` / `Contrapeso`
- `Return` / `Retorno`
- `Driven element` / `Elemento excitado` (only if the element is drawn)
- `Recommended, not recorded` / `Recomendado, no registrado`
- `Modeled as ideal` / `Modelado como ideal`
- `Combining network not modeled` / `Red combinadora no modelada`
- `Primary` / `Primario` and `Secondary` / `Secundario`
- `Balanced output` / `Salida balanceada` and `Coax input` / `Entrada de
  coaxil` where applicable

Reuse existing translations where the string already exists (`Balanced
output`, `Unbalanced input`, `Transformer secondary A/B`, etc.). Do not
duplicate a key with different Spanish copy. Run the Spanish translator over
the SVG in tests so no new English string leaks.

### Tests

- Direct coax:
  - no `id="interface-device"` group;
  - `id="coax"` and `id="coax-cross-section"` present;
  - cross-section has an outer shield and an inner center (two concentric
    circles or equivalent);
  - `A` maps to center and `B` maps to shield, matching
    `detail.connections`;
  - no two-parallel-line coax on the right.
- Vertical/base-fed: `Ground / radials` present; `Antenna terminal B` absent.
- End-fed: `Counterpoise` present.
- Current balun: `interface-device` present; balanced A/B on the left; coax
  center/shield on the right; `recorded` only when the project flag is set.
- Transformer: `4:1` and `ideal` present; primary/secondary sides distinct.
- Balanced line: no `id="coax"`; `Balanced line A/B` present.
- Multi-port: combining block present; explicit not-modeled text.
- Unknown: dashed `unknown` group; `Verify the wiring` present; no coax.
- Determinism: same detail and labeler produce identical SVG.
- EN/ES: every new label translates; no raw keys.
- Construction sheet/PDF/ZIP: the feed section still embeds the schematic and
  the connection table; page breaks remain valid.
- Regression: schema version, solver fingerprint, and a sample simulation
  result are unchanged (no code path touched).
- Full gate: `uv run ruff check .`, `uv run ruff format --check .`,
  `uv run mypy`, `uv run mypy --config-file mypy_ui.ini`, `uv run pytest`.
- Manual QA: dialog in light/dark, 100 %/150 % scaling, Spanish, HTML report,
  native PDF, and ZIP.

### Documentation

- `docs/USER_GUIDE.md`: explain that direct coax is drawn as a cable with a
  center conductor and shield, that a dashed choke means recommended but not
  recorded, and that the schematic is not a solver result.
- `CHANGELOG.md`: describe the corrected drawing under Unreleased.
- `docs/AUTONOMOUS_BACKLOG.md`: mark UX31 done and update the UX29 note to
  point to this item for the refined visual contract.
- No new ADR: this keeps ADR-0036's renderer-neutral SVG decision and changes
  only the drawing. If the implementation adds a new state or a data field,
  stop and write an ADR instead.

### Acceptance

- A straight Yagi with direct coax shows a real coaxial cable and a
  cross-section, with no middle “Direct coax” device box.
- A/B map to center/shield exactly as the connection table says; the drawing
  and table cannot disagree.
- Every interface has a distinct, physically honest drawing: direct coax,
  current balun, transformer, balanced line, multi-port, unknown.
- Terminal labels honor `ground`, `counterpoise`, and `return`; no false
  “Antenna terminal B”.
- A recommended choke is dashed or textual, never drawn as installed.
- The dialog, HTML construction sheet, native PDF, and ZIP show the same
  schematic.
- EN/ES labels, help coverage, and the full gate pass.
- No domain, solver, schema, or numerical change.

### Do not

- Do not use AI-generated or raster images; no ASCII in the app.
- Do not change `FeedPoint`, `FeedConnectionDetail`, the domain descriptors,
  the solver, the schema, persistence, or migrations.
- Do not infer the interface from wire count or geometry.
- Do not draw a box for direct coax.
- Do not draw coax as two parallel wires.
- Do not draw a recommended choke as installed.
- Do not invent balun windings, impedance, power rating, or connector type.
- Do not rename the canonical table labels (`Coax center`, `Coax shield`)
  without updating the domain, `report_i18n.py`, and tests together.
- Do not add a synthetic gap to the canonical geometry scene.
- Do not make `reporting` depend on Qt, the theme palette, or runtime fonts.
- Do not use SVG markers or external CSS if `QSvgRenderer` support is
  uncertain; use simple shapes.

### Out of scope

- 3D cable routing, connector drawings, weatherproofing, strain relief, and
  drip-loop graphics.
- Common-mode current prediction, shield radiation, and transfer impedance.
- Real balun/choke electrical models or frequency response.
- Topology-specific insets for OCFD, folded elements, loops, and hairpins
  (possible second phase).
- Dark-mode theme-aware SVG background.
- ASCII rendering in the application.
- Changing UX29's domain model or adding a per-design `FeedInstallation`
  record.

### Implementation order

1. Add semantic `id` groups and helpers; keep the current labels where they
   remain accurate.
2. Implement direct coax and terminal labels; add the first semantic tests.
3. Implement current balun, transformer, balanced line, multi-port, and
   unknown; add their tests.
4. Add EN/ES labels and update the schematic help text.
5. Verify the dialog, construction sheet, native PDF, and ZIP; manual QA.
6. Update the user guide, changelog, and this backlog note; run the full gate.

### Risks

- The drawing can still be read as a solver result; keep the four-state
  wording and the “not a solver result” label.
- A generic balun block can imply an invented topology; label it
  `recorded`/`ideal` and keep the limitations visible.
- Spanish labels are longer; use multi-line labels and test at the minimum
  dialog width and 150 % scaling.
- SVG test assertions can become brittle; assert semantic groups and labels,
  not pixel snapshots.
- `QSvgRenderer` compatibility is the main rendering risk; use standard
  primitives and inspect the native PDF manually.
- Duplicate `id` values if multiple schematics are embedded; prefix IDs if
  that path is added.
- The white SVG card in dark mode remains a cosmetic mismatch; do not hide it
  by changing the drawing unless the theme work is explicitly in scope.

## UX32–UX37 — Frequency-first starting dimensions (queue note, 2026-11-17)

### Context

`quad_beam_parameters()` already derives the starting geometry from the design
frequency:

- loop side = `0.25 λ × 0.95`;
- reflector/director spacing = `0.2 λ`;
- height = `0.25 λ` (constructor default only; the editor should preserve
  the installation height).

At 144 MHz that is a side of about **0.494 m** and a spacing of about
**0.416 m**. The problem is not the formula; it is the UI path:

- `QuadBeamDialog` creates the form with the 14.1 MHz seed and then calls only
  `set_frequency_hz()`, which changes the spinbox but not the geometry;
- `QuadBeamForm.load_starting_dimensions()` exists but is neither invoked nor
  exposed;
- `quad_beam` is absent from `ESTIMATORS`, so **Estimate Dimensions...** is
  disabled.

The same gap exists in the hexbeam, discone, trap-Yagi, and phased-vertical
generators: their forms already have `load_starting_dimensions()`, but their
dialogs only set the frequency. Biquad and Beverage already call the helper
after setting a requested frequency; Yagi already rescales the element table
when the frequency changes. The goal of this queue is to make the starting
dimensions consistent without silently resizing tuned designs.

Do not solve this with a universal “multiply every length by
`f_old / f_new`” operation. Height, base height, conductor radius, feed line,
matching network, loading coils, traps, and multiband element sets are not
simple wavelength-scaled dimensions. The family constructor or estimator knows
the correct starting law; use it.

### UX32 — First slice: quad beam (S)

**Status:** implemented on 2026-11-17. The action, frequency seeding, field
preservation, EN/ES help, and tests are in place. UX33–UX37 are complete.

**Goal:** a new or changed-template quad beam opens with geometry for the
requested frequency, and the user can explicitly reload the starting dimensions
after editing the frequency.

Implementation:

1. When `QuadBeamDialog` receives `frequency_hz` and no explicit `parameters`,
   set the frequency and call `load_starting_dimensions()`, following the
   Biquad/Beverage pattern.
2. Change `QuadBeamForm.load_starting_dimensions()` to preserve
   `current.height_m`. Do not reset height to `wavelength * 0.25`; at 144 MHz
   that would put the antenna at 0.52 m.
3. Preserve `wire_radius_m`, `material`, `ground`, `azimuth_deg`,
   `element_count`, `reflector_scale`, `director_scale`, and
   `transformer_ratio`.
4. Expose the action as **Load starting dimensions** in the form/dialog, with
   EN/ES text and help. Because the form is shared, the action is also
   available in the inline editor.
5. Pass the active design frequency from `new_quad_beam_antenna()` when a
   project/design exists. `_parameters_from_catalog()` already passes the
   frequency on the Change Template path.
6. Keep `quad_beam_parameters()` domain defaults unchanged in this slice.

Acceptance:

- `QuadBeamDialog(frequency_hz=144_000_000.0)` returns loop side
  `pytest.approx(0.494, abs=0.002)` and reflector spacing
  `pytest.approx(0.416, abs=0.002)`, not the 14.1 MHz geometry.
- A height of 3.2 m set by the user remains 3.2 m after changing frequency and
  reloading; a custom 6:1 transformer and a 1.1 reflector scale also remain.
- The 2-element default keeps 4:1; a 3-element design keeps 2:1 unless the user
  edited the ratio.
- The Change Template path at 144 MHz produces 144 MHz geometry.
- The button retranslates in English and Spanish and is covered by a UI test.
- No domain formula, schema, solver, or migration change.
- Update the user guide and `CHANGELOG.md`; run the full gate.

Do not in UX32:

- register the quad-beam estimator;
- auto-resize on every frequency keystroke;
- change the constructor’s λ/4 height default;
- touch Yagi, Moxon, fan, trap, loaded, or multiband scaling.

### UX33 — Generalize the existing helper (S–M)

**Status:** implemented on 2026-11-17. The four generators now seed at the
requested frequency and expose the shared action. UX34–UX37 are complete.

Apply the UX32 pattern to the generators whose forms already implement
`load_starting_dimensions()`:

- hexbeam;
- discone;
- trap Yagi;
- phased vertical.

Each dialog must set the requested frequency before loading the starting
dimensions. Each form must preserve its installation and matching fields:
height/base height, azimuth, conductor radius, material, ground, element count,
and any family-specific transformer or phase/amplitude values. Trap Yagi must
keep the low/high/trap frequency relationship consistent. Expose the action
with translated labels and help.

Acceptance: one test per generator for the requested-frequency path, one test
per generator for the action, preservation tests for the family-specific
fields, and no formula or schema change. Biquad and Beverage are the reference
implementations; do not copy their labels blindly because the families have
different installation fields.

### UX34 — Frequency semantics decision (S)

**Status:** implemented on 2026-11-17 as
[ADR-0043](../../ADR/0043-design-versus-analysis-frequency.md). No code or behavior
change; UX35 remains the implementation slice.

Write a short ADR/decision note before adding automatic recalculation. The
recommended policy is:

- **Design frequency** describes the intended antenna. Changing it may
  regenerate starting dimensions only while the geometry is pristine, with
  visible feedback.
- **Analysis frequency** is the frequency at which an existing geometry is
  evaluated. It must not resize the antenna. The existing sweeps, band
  analysis, and measurement comparison remain the analysis paths.
- Edited or solver-tuned geometry is never resized silently. The user must
  choose **Load starting dimensions** or the explicit **Scale geometry to
  frequency** action.
- If the product does not add a separate analysis-frequency field, the guide
  and help must say so explicitly.

The ADR must define the pristine test, the undo behavior, the wording of the
feedback, and which families are eligible. No code change in this item; update
the ADR, user guide, and help plan.

### UX35 — Pristine-geometry recalculation (M)

**Status:** implemented on 2026-11-17. The five generators now use the shared
`StartingDimensionsState`, preserve installation fields, and stop automatic
resizing after a managed edit. UX36–UX37 are complete.

Implement the policy chosen in UX34 for the families covered by UX32 and UX33:

- track whether the electrical geometry still matches the last generated
  starting point;
- when the design frequency changes and the geometry is pristine, regenerate
  the starting dimensions and show a short, non-modal note;
- after any electrical edit, never resize silently; show that the frequency
  changed and offer the explicit action;
- make **Load starting dimensions** available in the same place in every
  covered editor;
- preserve installation and matching fields exactly as in UX32/UX33;
- recompute from the family formula on each frequency change; do not
  accumulate a scale factor, so intermediate values cannot drift through
  rounding.

Acceptance: pristine and edited paths, undo/redo, EN/ES retranslation, help,
and no silent changes to a tuned design. No schema or solver change. Do not
include loaded, trapped, multiband, Yagi/Moxon, fan, or transmission-line
families without a family-specific starting rule.

### UX36 — Quad beam estimator (M)

**Status:** implemented on 2026-11-17. The estimator, dialog element-count
field, registry entry, preservation path, and tests are in place. UX37 remains
queued.

Register `quad_beam` in `domain/design/estimators.py` so **Estimate
Dimensions...** works after project creation.

Implementation requirements:

- add `quad_beam_elements` (2–3, default 2) to `DesignIntent` and validate it;
- add the field to `DesignFromFrequencyDialog` and pass it through
  `_build_intent()`;
- implement `estimate_quad_beam()` with the documented quarter-wave-side /
  fifth-wave-spacing heuristic, `height_m=intent.height_m`, the current
  material/ground/radius/azimuth, and the family transformer default;
- return `Confidence.HEURISTIC`, the application-preset source, assumptions
  about height/ground, warnings about the starting geometry and reactive feed,
  a documented tolerance, and display rows for side, spacing, height, and
  element count;
- add a `QuadBeamParameters` branch to `_preserve_estimate_context()` that
  keeps reflector/director scales and transformer ratio; the element count and
  height come from the dialog, and the generic context preserves radius,
  material, ground, and azimuth;
- remove `quad_beam` from `ESTIMATORLESS_CATALOG_KEYS` and cover the registry,
  parameterized NEC smoke test, domain, dialog, and Apply path;
- update `ANTENNA_DESIGN_ESTIMATORS.md`, EN/ES help, user guide, and changelog.

At 144 MHz the estimate must produce the same 0.494 m side and 0.416 m spacing
as UX32. Do not claim validated gain or feedpoint impedance. No schema change;
estimator provenance already exists.

### UX37 — Explicit scale-to-frequency action (M–L)

**Status:** implemented on 2026-11-17. The domain allowlist, target-frequency
dialog, menu action, preservation rules, disabled reasons, undo path, and tests
are in place. UX32–UX37 are complete.

Add an explicit action for a design that is already tuned or edited. This is
not automatic and must not reuse a universal “scale every length” rule.

Recommended first allowlist, limited to families with a clean primary-dimension
path:

- wire dipole;
- folded dipole;
- loop;
- quad beam;
- biquad;
- discone;
- hexbeam.

Use `primary_dimension_m()` and `with_primary_dimension()` for the allowlisted
families, or a small family-specific rule where the primary dimension does not
cover a derived dimension. Compute the target from the current primary
dimension and `f_old / f_new`, preserve installation and matching fields, and
show old/new frequency plus an explicit approximation warning. The action must
enter undo history. Families with loads, traps, multiband elements, Yagi/Moxon
tapering, fan elements, transmission lines, or no single primary dimension must
be disabled with a reason.

Acceptance: domain tests for the ratio and preservation, unsupported-family
tests, UI confirmation/cancel tests, undo/redo, EN/ES help, and no schema or
solver change. Do not include height, radius, feed line, matching network,
coils, or traps in the scaled set.

### Shared constraints

- UX32 is the first slice and must ship alone; do not bundle UX33–UX37.
- Use the documented family heuristic or constructor. Do not invent a new
  numerical reference.
- Do not change the project schema, solver, or persisted project format.
- Keep the user guide, help manifest, translation catalog, and changelog in
  sync with each item.
- Run the full gate before declaring any item complete.

## UX38 — Select the Design tab after antenna creation (queue note, 2026-11-17)

**Status:** implemented on 2026-11-17. The creation funnel now selects the
Design tab after success, with cancellation and failure covered by tests.

### Problem

The sidebar keeps its current tab when a project is created. In Advanced mode
`_apply_workflow_mode()` deliberately opens the Simulation tab, and a user who
manually selected Simulation keeps that tab after generating an antenna. The
creation path `_create_project_from_parameters()` calls `_set_project()` and
`_select_design()` but never changes `_sidebar_tabs`.

The requested behavior is limited to creation: after generating a new antenna,
the Design tab must be selected. This is not a change to the workflow-mode
semantics.

### Implementation contract

- In `_create_project_from_parameters()`, after the successful `_set_project()`
  call, select `_design_tab` with `_sidebar_tabs.setCurrentWidget()`.
- Do not switch the tab before creation succeeds: a cancelled name dialog, an
  invalid design, or a failed repository operation must leave the current tab
  unchanged.
- The creation funnel covers every New Antenna catalog template, the basic
  templates, Antenna Advisor, and Reference Design Library.
- Keep Advanced mode unchanged: selecting Advanced still opens Simulation, and
  the user can return to Design manually. The new rule only overrides the tab
  after a successful creation.
- Out of scope: Change Template, Open Project, NEC/MMANA import, New Variant,
  persisted preferences, and every schema, domain, or solver change.

### Acceptance

- UI regression test: enable Advanced mode, create an antenna, and assert that
  `_sidebar_tabs.currentWidget()` is `_design_tab`; keep the existing
  Advanced-mode test that asserts Simulation is selected immediately after the
  mode change.
- Verify cancellation and creation failure do not change the current tab.
- Update `docs/USER_GUIDE.md` and `CHANGELOG.md`.
- Run the full gate; no new translation or help keys are required.

## UX39 — At least 100 computed points in generated single-design impedance/SWR charts (queue note, 2026-11-18)

**Status:** implemented 2026-11-19. The generated defaults are 100 points, the
marker layer is bounded, and the tests and docs listed below are updated.

### Problem

Generated single-design templates default to 31 points
(`DEFAULT_GENERATED_SWEEP_POINTS` in
`src/antennadesk/ui/main_window.py`); most use a ±5% span, while some use wider
spans. The shared two-band plan defaults to 61
(`DEFAULT_TWO_BAND_SWEEP_POINTS`). The reported case was a ~145 MHz design with
31 points across ~15 MHz, about a 0.48 MHz step. Basic/custom sweep controls
already default to 100 when a sweep is enabled, the magnetic loop uses 101, and
band analysis exposes 3–201 points per band (default 15).

The impedance and SWR charts plot one point per solver frequency. They do not
interpolate, smooth, or synthesize intermediate values: the line between
points is only a visual join. Requiring 100 chart points therefore means 100
NEC solves at 100 frequencies. That is a frequency-sampling increase, not a
claim of higher electromagnetic accuracy; the accuracy at each point is still
set by segmentation, ground, conductor losses, and the thin-wire model.

### Decision

- Raise the generated single-design default to **100 points**. Keep the span
  unchanged; only the count changes. `100` means 99 intervals; use `101` if a
  future product decision requires 100 intervals.
- Raise the two-band shared default from 61 to 100.
- Preserve explicit plans that already have at least 100 points (for example
  the magnetic loop's 101) and every user override.
- Do not interpolate, smooth, average, or fabricate intermediate points.
- Do not silently cap below 100 or reduce the sweep to fit the pattern budget.
  If a model is too slow, the user can lower **Points** or raise the timeout.
- Keep the current 180 s default timeout, cancellation, and indeterminate
  progress. True per-frequency progress remains P7/D4 and is out of scope.
- Keep ADR-0019's pattern-snapshot policy: the impedance sweep keeps all
  points, while far-field patterns remain limited to snapshots and the storage
  budget.
- Band analysis keeps its per-band 3–201 control and its current default. A
  global band-analysis default of 100 is a separate product decision; the
  existing control already supports it.
- In the impedance and SWR charts, keep every computed point in the line and
  in the table. Apply a density-aware marker policy so 100 points do not
  become an unreadable band of 5 px symbols: symbols may be shrunk, decimated,
  or suppressed above a threshold, but the line data, cursor series, table,
  CSV, and reports retain every point. Prefer a testable pure helper over
  layout-dependent guessing.

### Feasibility evidence (2026-11-18)

Local check with one nec2c process, one deck containing `FR 0 N`, and patterns
disabled. Timings are a feasibility check, not a target-hardware guarantee.

| Model | Segments | 31 points | 100 points |
|---|---:|---:|---:|
| 40 m dipole | 21 | 0.013 s | 0.030 s |
| G5RV | 66 | 0.08 s | 0.24 s |
| 7 MHz vertical, 32 radials, 3.5–30 MHz | 725 | 12.6 s | 41.3 s |

The cost is approximately linear in the frequency count and is about 3× from
31 to 100. The 725-segment 100-point case fits the 180 s default. At 890
segments the backlog's 31-point runtime note is 25.3 s including five pattern
snapshots; a 100-point run is expected to remain within the default on the same
class of machine, but it must be re-measured. The existing timeout and cancel
path remain the guard for larger models or slower hardware.

Storage is not a blocker: `estimate_project_bytes` gives about 26 MB of JSON
(≈4.4 MB compressed) for 100 points at 725 segments and about 32 MB (≈5.3 MB
compressed) at 890 segments. Both are below the 32 MB warning and the 64 MB
hard limit. The 24 MB pattern budget is compressed and only stressed by much
larger models; the pattern step may still be coarsened, and that reduction is
already reported. ADR-0042 already benchmarked 101 points per band across
eight bands: 1.18 s with four workers and 7.05 MB compressed for the G5RV
case.

### Implementation contract

- `src/antennadesk/ui/main_window.py`: set `DEFAULT_GENERATED_SWEEP_POINTS` to
  100 and `DEFAULT_TWO_BAND_SWEEP_POINTS` to 100; the custom sweep spin box
  inherits the first constant. Audit every `FrequencyPlan.sweep(...)` call in
  the generated spec builders and replace only the 31/61 defaults. Keep
  explicit counts at or above 100.
- `src/antennadesk/ui/widgets/dipole_form.py`: verify the basic form remains
  at 100; no change is expected.
- `src/antennadesk/ui/widgets/results_view.py`: add the marker-density policy
  to the impedance and SWR plots only. Keep the full `x`/`y` arrays in the
  line, the table rows, the cursor series, and exports. Do not apply the policy
  to the pattern, current, or measurement charts in this item.
- Do not touch `FrequencyPlan`, `SimulationSpec`, the NEC input writer, the
  parser, normalization, or the project schema.
- Do not change band-analysis defaults, the comparison dialog's point count,
  or optimizer/synthesis target plans.
- No new ADR is required for a constant/default change. If the implementation
  adds an adaptive points-by-model-size policy or a user-facing resolution
  control, record the policy in an ADR first.

### Tests and acceptance

- [x] A table-driven UI test over the generated templates asserts
      `frequency_plan.count >= 100` for every enabled sweep. Cover at least the
      T2FD, vertical, Yagi, end-fed, beverage, loaded-dipole, and two-band
      builders; exclude single-frequency custom mode by design.
- [x] The Auto (template) view and the Points spin box show 100 for generated
      templates; **Custom** still overrides, and a single-frequency custom plan
      remains count 1.
- [x] Impedance and SWR charts contain one plotted point per computed
      frequency, the table has one row per frequency, and no interpolation is
      introduced.
- [x] At 100 points the chart line uses all points; the marker layer is
      bounded and the plot is legible at the minimum supported window width.
      The cursor still snaps to each computed point.
- [x] A 100-point NEC2C smoke run of a representative generated design
      completes within the 180 s default and returns 100 results; record the
      wall time and keep the test solver-marked.
- [x] Project save/load round-trips a 100-point result; record the estimated
      compressed size and confirm it stays below the warning threshold for the
      tested models.
- [x] Update the tests that currently assert 31:
      `tests/ui/test_main_window_presets.py` (T2FD) and
      `tests/ui/test_main_window_simulation.py` (vertical and generated-spec
      fixtures). Rename the "performance-safe defaults" test if the wording no
      longer describes the policy.
- [x] Update `docs/USER_GUIDE.md`, `docs/VALIDATION_PLAN.md`,
      `docs/archive/plans/MULTIBAND_ANALYSIS_PLAN.md`, and `CHANGELOG.md`. Add a new
      changelog entry; do not rewrite historical release entries.
- [x] Run the full gate: `ruff check`, `ruff format --check`, both `mypy`
      passes, and `NEC2C=... uv run pytest`.

### Out of scope

- Interpolated or synthetic points, smoothing, or curve fitting.
- Changing segmentation, ground, conductor, or solver accuracy claims.
- Changing band-analysis defaults or its 3–201 range.
- Reopening P7/D4 per-frequency progress or the single-deck multi-band plan.
- Changing optimizer, synthesis, robustness, tuning, or comparison plans.
- Schema migration or project-format changes.
- Rewriting historical ADR-0019 or old changelog entries.

Follow-up not included here: if band analysis should also default to 100 points
per band, raise its 15-point default in a separate item. ADR-0042 already
benchmarks 101 points per band, but runtime and storage multiply by the number
of selected bands.

### Risks

- Large radial models at 100 points are about 3× slower. On a slower target
  machine or a much larger model, the 180 s default may be exceeded; the user
  must lower Points or raise the timeout. Do not add silent capping.
- Dense markers can obscure the curve. The marker policy must be independent
  of the data series so the user never loses computed points.
- Tests and docs that repeat "31-point sweep" are spread across the UI tests,
  user guide, validation plan, and multiband plan; update them together.
- The pattern budget may coarsen the pattern at high point counts. Keep the
  existing diagnostic visible; do not trade away the impedance sweep.

### Implementation note

`DEFAULT_GENERATED_SWEEP_POINTS` and `DEFAULT_TWO_BAND_SWEEP_POINTS` are 100.
The G5RV, ZS6BKW, and Zepp custom sweep presets also use 100; explicit custom
overrides and band-analysis defaults are unchanged. No spec builder uses a
literal count below 100 except the magnetic loop's explicit 101.

`results_view.marker_indices` returns at most 20 evenly spaced symbol indices,
always including the endpoints. The impedance and SWR lines keep the full
`x`/`y` arrays; separate marker layers are decimated, and the table, cursor,
CSV, and reports keep every computed point. The pattern, current, and
measurement charts are unchanged.

Tests cover the generated spec builders, Auto/Custom point counts, dense chart
data and marker bounds, a real NEC2C 100-point run, and a 100-point project
round trip. The NEC2C smoke run was about 0.02 s for the 21-segment dipole on
2026-11-19; the persistence estimate is about 4.4 MB compressed at 725
segments, below the 32 MB warning.

## UX40 — Static 3D far-field lobe in the HTML/PDF reports (queue note, 2026-11-18)

**Status:** implemented 2026-11-19. The report builder, HTML/PDF integration,
localized labels, tests, and documentation are in place.

### Request and problem

The HTML and native PDF reports show azimuth and elevation cuts at the
maximum-gain direction. When the result contains the sampled theta/phi grid
(the normal UI path does), a third, holistic view is possible without another
solver run. A static 3D wireframe helps directional antennas (Yagi, Moxon, quad,
hexbeam, phased arrays) show sidelobes and nulls that can fall between two
orthogonal cuts.

UX26 deliberately kept reports 2D and vector and listed 3D report rendering as
out of scope. This item reverses that presentation-only exclusion for one
static vector figure. It does not reopen the interactive 3D strategy or add a
3D engine.

### Feasibility evidence

- `FrequencyResult.far_field` stores `theta_deg`, `phi_deg`, and
  `gain_total_db` for every sampled direction. The normal UI request is a 5°
  grid: 37×73 points in free space and 19×73 with ground; the user may choose a
  finer step, and the pattern budget may coarsen it to 30° (7×13 in free space,
  4×13 with ground), which is still enough for a wireframe.
- `ui/widgets/radiation_pattern_3d_view.py` already defines the useful
  visual language: gain normalization, green/yellow/red bins, orthographic
  projection at yaw 38° and pitch 26°, a ground grid/ring, a maximum-gain
  marker, and X/Y/Z axes. It is a QWidget and must not be imported into
  `reporting/`, which is Qt-free.
- The report pipeline already builds dependency-free SVG (`svg_chart.py`) and
  the native PDF renders SVG through `QSvgRenderer` as vector content
  (`report_pdf.py`). No new dependency is needed.
- A decimated 19×37 mesh with one path per gain bin is tens of kilobytes, not
  megabytes. One figure per report is well below the existing report size.
- The main risk is data availability, not rendering. `FarFieldRequest` allows
  `phi_count=1` for a single cut, and older or imported results may not contain
  a 2D grid. The figure must say so explicitly; it must never interpolate a
  surface from two cuts.

### Recommendation

**Viable and recommended with a bounded scope.** Add exactly one static 3D
wireframe to the primary far-field section of both reports. Treat it as a visual
complement to the quantitative cuts, not a replacement. Do not add a figure per
band and do not make it interactive. The value is highest for directional
antennas; for a simple dipole or vertical the existing cuts still carry the
quantitative story, but one small figure is consistent and harmless.

### Decision

- Add one 3D figure at the same pattern frequency as the existing cuts, after
  the azimuth and elevation charts, in HTML and native PDF.
- Build a pure, deterministic SVG in `reporting/pattern_lobe.py`. The HTML
  report stays Qt-free and the PDF keeps vector content. Do not call
  `QWidget.grab()`, `save_pattern_image()`, or any live-widget capture.
- Use a fixed light palette and fixed orientation matching the Pattern tab
  default, so the same immutable snapshot and language produce identical
  output.
- Draw only valid grid points. Do not interpolate a surface, synthesize a shape
  from the cuts, or fill missing angles. Filter non-finite values and use the
  same low-gain display floor as the Pattern tab so a deep null does not
  collapse the lobe. When the model uses ground, ignore theta samples below the
  ground plane, matching the Pattern tab.
- Decimate the displayed mesh to at most 19 theta × 37 phi positions, including
  both endpoints, and group segments by gain bin. Keep the stored pattern, the
  2D cuts, and the pattern export at full resolution.
- Use the same `gain_total_db` field as the cuts. Label the legend and caption
  as total gain in dBi, matching the cut series label; do not imply directivity
  or realized gain.
- Add a numeric min/max legend, a maximum-gain marker with direction, X/Y/Z
  orientation cues, and a ground ring when the model uses ground. State in the
  caption that the geometry figure carries the antenna orientation. Color is
  decorative; the legend and caption carry the values.
- Add `role="img"` and SVG `<title>`/`<desc>`, plus a visible caption with
  frequency, angular sampling, and maximum gain/direction.
- Explicit unavailable states:
  - no far-field data: keep the existing "No far-field pattern available.";
  - fewer than two theta samples, fewer than two phi samples, or fewer than
    four valid points: "3D pattern unavailable: the far-field data does not
    contain a 2D angular grid.";
  - all gains unavailable: use the same explicit unavailable message.
- Band sections keep their existing 2D cuts only. The report contains at most
  one 3D figure.
- No report option or preferences dialog in this item. Include the figure
  whenever a usable grid exists; a user toggle is a separate UI decision.

### Implementation contract

- New `src/antennadesk/reporting/pattern_lobe.py`: pure builder that accepts a
  `FrequencyResult`, a labeler, and a ground flag, and returns either an SVG
  string or an explicit unavailable reason. No PySide6 import.
- `src/antennadesk/reporting/html_report.py`: add a sibling to
  `_pattern_cut_charts` for the 3D figure in the primary "Far field" section;
  pass ground from
  `design.antenna.environment.ground.kind is not GroundKind.FREE_SPACE`.
- `src/antennadesk/ui/report_pdf.py`: call the same builder and render the SVG
  with the existing chart helper in the primary pattern section. Keep the band
  sections unchanged.
- `src/antennadesk/ui/report_i18n.py`: add the new English source labels and
  their Spanish translations.
- Do not change the Pattern tab, `RadiationPattern3DView`, the solver, the
  stored result, the model fingerprint, or the project schema.

### Tests and acceptance

- [x] A new `tests/unit/reporting/test_pattern_lobe.py` uses a regular synthetic
      grid and asserts that the SVG contains the wireframe paths, legend,
      maximum-gain marker, title/description, and ground ring as applicable.
- [x] Repeated rendering of the same snapshot and language is byte-identical.
- [x] Free-space and ground patterns both render; the ground ring is absent in
      free space.
- [x] Missing or non-finite gains do not produce NaN coordinates; a single-cut
      pattern returns the explicit unavailable reason and no SVG.
- [x] The displayed mesh respects the 19×37 vertex cap and a documented
      segment/path-size bound; stored points are not mutated.
- [x] HTML tests assert exactly one 3D figure in the primary section, none per
      band, and the localized reason for far-field-disabled and single-cut
      results.
- [x] The native PDF test confirms the figure is included and adds no new
      `/Subtype /Image` object; the existing vector assertion still passes.
- [x] Every new static report label is in `REPORT_SPANISH`; the placeholder
      parity and static-label coverage tests pass.
- [x] A manual A4 light-theme/grayscale check confirms that the figure, legend,
      caption, and marker remain legible and do not overwhelm the two cuts.
- [x] Update `docs/USER_GUIDE.md` (report contents), `docs/ARCHITECTURE.md`
      (report contents), `docs/VALIDATION_PLAN.md` (report checks), and
      `CHANGELOG.md`. Do not rewrite historical UX26 text; add the new
      decision and link this note.
- [x] Run the full gate: `ruff check`, `ruff format --check`, both `mypy`
      passes, and `NEC2C=... uv run pytest`.

### Out of scope

- Interactive rotation or zoom, animation, WebGL/three.js, or any new runtime
  dependency.
- One 3D figure per band, per pattern snapshot, or per frequency.
- A report-specific power/directivity/realized-gain selector; that remains
  deferred from UX26.
- Changing the Pattern tab or the existing 3D view.
- Adding the pattern figure to the construction sheet; that sheet remains the
  build artifact with its geometry views.
- Replacing the 2D cuts or presenting the static 3D wireframe as a
  quantitative measurement.
- Domain, solver, persistence, schema, or fingerprint changes.

### Risks

- Single-cut and legacy results have no 2D grid. The unavailable message must
  be visible and must not be replaced by a synthesized surface.
- A fixed viewpoint can hide lobes behind the wireframe. Keep the familiar
  default orientation, pair the figure with both cuts, and do not imply that
  the reader can rotate it.
- Print and grayscale legibility is weaker than on screen. Use darker
  report-specific colors, a numeric legend, and a visible caption.
- Report size and length can grow if the figure is repeated. Cap it at one
  figure and one decimated mesh, and record the generated size in the tests or
  manual check.
- The color mapping can drift from the Pattern tab. Preserve the green/yellow/
  red gain order and test the semantic mapping; exact RGB parity is not
  required for print.

### Implementation note

`reporting/pattern_lobe.py` is a pure builder. It filters non-finite gains and
the lower hemisphere for grounded models, requires a 2×2 angular grid with at
least four valid points, and returns either an SVG or an explicit localized
reason. The displayed mesh is decimated to at most 19×37 positions; the stored
pattern is never mutated. The figure uses a fixed yaw/pitch, dark green/yellow/
red gain bins, a six-step numeric legend, a maximum marker, X/Y/Z cues, and a
ground ring. The SVG includes `role="img"`, `<title>`/`<desc>`, and a visible
two-line caption.

HTML adds the figure only to the primary far-field section; band sections keep
their 2D cuts. The native PDF renders the same SVG through the existing vector
chart helper, so no image object is added. EN/ES labels are in
`REPORT_SPANISH`. Tests cover determinism, ground filtering, missing and
non-finite gains, single-cut and all-missing unavailable states, the 19×37 cap,
one HTML figure and none per band, and vector PDF output.

### Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Render the live widget or capture a PNG | Depends on theme, DPI, size, and zoom; not reproducible; bloats HTML and violates the vector/Qt-free report contract |
| Import `RadiationPattern3DView` into `reporting/` | Adds Qt to the HTML reporting path and reuses an interactive widget as a document renderer |
| Offscreen widget adapter in the UI layer | Reuses interactive hints/legend and palette; harder to make byte-deterministic across platforms and to strip the "drag to rotate" chrome; a report-specific pure builder is simpler |
| Interactive WebGL/three.js in HTML | New dependency, not printable, not self-contained, and outside the static report contract |
| Derive a 3D surface from the azimuth/elevation cuts | Invents data and misrepresents the sampled pattern |
| Add a figure for every band | Multiplies pages and size with little new information; the band table and 2D cuts already compare bands |

### Decision record

UX26's exclusion was a presentation decision, not a domain or solver decision.
This item reverses it for one static vector figure. No new ADR is required
unless the renderer is promoted to a shared 3D visualization strategy; in that
case, write the ADR before sharing it beyond reports.

## UX41 — Optimizer operating-mode scope and capability flags (queue note, 2026-11-18)

**Status:** implemented 2026-11-19. The mode names, scope line, plan-source
reporting, help, and generic-mode policy are in place. The unused
`supports_band_aware`/`supports_robust` descriptor fields were removed.

### Problem

The family optimizer dialog always offers **Single frequency**, **Band-aware**,
and **Robust (tolerance)**; the widget adds all three unconditionally in
`src/antennadesk/ui/dialogs/family_optimization_dialog.py`. For a monoband
antenna such as an Inverted-V, this reads as if the user had declared a
multiband model. The actual behavior is narrower:

- **Band-aware** evaluates every scoring frequency in the current band plan.
  `MainWindow._optimizer_band_edges()` turns each selected band into its start,
  center, and stop frequency. For an Inverted-V the default plan is one band, so
  the mode evaluates three points inside that band. It is a worst-case
  band-edge sweep, not multiband optimization.
- **Robust** perturbs dimensional variables by ± tolerance at the same scoring
  frequencies. It is independent of the number of bands and is useful for a
  monoband design.
- **Analyze Bands** is not a declaration step. It is a simulation/report action
  that also stores a `BandPlan`. The plan already has a per-family default; the
  analysis only replaces it with the user's selected set.
- `AntennaOptimizerDescriptor` exposes `supports_band_aware` and
  `supports_robust`, but no descriptor sets them and no code reads them. They are
  a dead contract left from Phase A.
- The English label **Band-aware** and the Spanish **Consciente de banda** are
  ambiguous, and the dialog shows an editable MHz field without saying how many
  bands or frequencies it resolved.
- The Phase C plan says that with no plan the fallback is the design frequency
  ±5 %. In the normal UI path, the plan fallback is the current band's
  start/center/stop; the ±5 % fallback appears only when the dialog receives no
  band edges. The documentation and implementation should agree.

### Decision

1. **Do not require Analyze Bands.** Band-aware remains available for a
   monoband design because evaluating the band edges is a legitimate worst-case
   objective. Analyze Bands is optional and only changes the plan source.
2. **Do not gate Robust behind band analysis.** It is a tolerance mode, not a
   multiband mode.
3. **Make the scope visible.** Add a read-only scope line in the dialog that
   states the resolved plan source and the evaluation size, for example
   `Current band plan · 1 band · 3 frequencies` or
   `Current band plan · 3 bands · 9 frequencies`. Update it when the mode
   changes, the plan changes, or the editable edges become invalid. A manual
   edit must show `Manual edges · N frequencies`, not pretend to come from the
   plan.
4. **Rename the user-facing strings, not the domain.** Use an explicit
   band-edge label in English and Spanish (for example **Band-edge sweep** /
   **Barrido de bordes de banda**) and keep `OptimizationMode.BAND_AWARE` and the
   persisted `"band_aware"` value unchanged. Keep single-frequency and robust
   labels explicit about their scope.
5. **Close the capability flags.** Prefer removing the unused
   `supports_band_aware`/`supports_robust` fields and documenting that both
   modes are generic over any descriptor with a positive evaluation frequency
   and at least two distinct scoring frequencies. If a future family cannot
   support one mode, add a capability flag with a translated unavailable reason
   in that family's ADR; do not leave unused fields as an implied policy.
6. **Reconcile the fallback contract.** Centralize the resolved-edge logic so
   the dialog, the budget estimate, and the summary use the same frequencies.
   Document the plan default, the manual override, and the ±5 % fallback in one
   place. Do not silently substitute the design frequency when a usable plan
   exists.

### Implementation contract

- `src/antennadesk/ui/dialogs/family_optimization_dialog.py`: add the scope
  label near the mode/band-edge controls; compute the band count and frequency
  count from the resolved plan, not from the raw text; disable or hide the
  label consistently while a run is active; keep the existing editable field
  and validation.
- `src/antennadesk/ui/main_window.py`: keep `_optimizer_band_edges()` as the
  plan-to-edge source; expose the plan source (current plan, manual, fallback)
  to the dialog instead of only the raw tuple. Do not change when Apply Best
  starts a band analysis.
- `src/antennadesk/domain/optimization/descriptor.py`: remove the two unused
  fields, or add one explicit capability policy with tests. If removed, update
  ADR-0026's descriptor sketch and any coverage tests that mention them.
- `src/antennadesk/ui/i18n.py`: rename the mode strings and add EN/ES help for
  the scope line, the plan source, the manual-edge state, and the fact that
  Robust perturbs dimensions rather than bands. Update the help coverage
  manifest.
- Keep `OptimizationMode`, `OptimizationSummary.mode`, the persisted
  `"band_aware"`/`"robust"` strings, scoring, aggregation, band-edge
  validation, and Apply Best behavior unchanged.
- Update `docs/USER_GUIDE.md`, `docs/archive/plans/OPTIMIZER_PHASE_C_PLAN.md` (or add an
  implementation note), `docs/ADR/0026-family-optimizer-architecture.md` if the
  flags are removed, and `CHANGELOG.md`. Do not rewrite historical release
  notes.

### Tests and acceptance

- [x] A monoband Inverted-V opens the optimizer with Band-aware available and
      the scope line showing one band and three frequencies, without any prior
      Analyze Bands run.
- [x] After a multiband Analyze Bands plan, the same dialog shows the band
      count and `3 × bands` scoring frequencies, and the edges match the stored
      plan.
- [x] Manual edge edits change the frequency count and label the source as
      manual; invalid text keeps the previous valid scope or shows the existing
      validation error without claiming a plan source.
- [x] Robust remains selectable for the monoband design, shows its tolerance
      control, and the scope line explains that the frequency plan is unchanged
      and the geometry is perturbed.
- [x] Switching modes updates the budget hint and scope line consistently; the
      estimate still counts frequencies × scenarios × candidates × seeds.
- [x] Descriptor coverage fails if a family is optimizable but its capability
      state is undefined; if the flags are removed, no test or doc references a
      dead field.
- [x] EN/ES tests cover the new mode labels, scope line, plan-source states, and
      retranslation; the help manifest passes. Persisted summaries still parse
      and render their mode values under the new labels.
- [x] No schema, migration, solver, scoring, or default-band-plan change.
- [x] Run the full gate: `ruff check`, `ruff format --check`, both `mypy`
      passes, and `NEC2C=... uv run pytest`.

### Out of scope

- Making Analyze Bands a prerequisite for any optimizer mode.
- A new multiband optimizer or changing the per-band edge policy.
- Changing `OptimizationMode`, the persisted summary schema, scoring, or the
  number of frequencies per band.
- Changing the default band plan for any family.
- Adding per-band amplitude/phase weighting or inter-band coupling.
- Solver, segmentation, or numerical changes.

### Risks

- The scope line can become a second source of truth. Derive both the label and
  the command from one resolved-edge function.
- A rename can break tests and docs that use the old display string; keep the
  internal enum stable and update every EN/ES surface together.
- Removing the unused flags may look like a loss of future flexibility. Document
  the generic-mode policy and require a new ADR for a family-specific opt-out.
- A monoband user may still read **Band-edge sweep** as multiband. Keep the
  explicit `1 band · 3 frequencies` text and the current-plan source visible.

### Implementation note

`FamilyOptimizationDialog` accepts `BandPlanSource` (`current_plan`, `manual`,
`fallback`) and the current plan's band count from `MainWindow`. The new
**Evaluation scope** line derives its frequency count from the same parsed
edges as the budget hint. Editing the edge field switches the source to
`manual`; invalid text reports an invalid manual scope without claiming a plan
source. The design-frequency ±5 % path remains the fallback when the dialog
receives no edges, including the selected-HexBeam-band optimizer. The internal
`OptimizationMode` values and persisted strings are unchanged. The descriptor
capability flags were removed; ADR-0026 documents both modes as generic.

Tests cover a monoband current plan, a three-band plan, manual and invalid
edges, operating-frequency scoring, both languages, mode switching, budget
hints, descriptor flag removal, and the main-window plan-source handoff.

## UX42 — Band-analysis 100-point default and storage guard (2026-11-19)

**Status:** implemented 2026-11-19.

`DEFAULT_BAND_POINTS` and `BROADBAND_BAND_POINTS` are 100. `BandSelection`
defaults, `_two_band_plan`, harmonic plans, and the band dialog therefore start
at 100 points per band. The dialog fallback imports the domain constant instead
of carrying a second number.

After `_fit_band_specs_to_budget`, `_start_band_analysis` reads the fitted
`PatternBudget.estimated_project_bytes`. `project_size_action()` classifies it
as `ok` (≤32 MB), `warn` (32–64 MB), or `block` (>64 MB). A warning asks for
confirmation; a block calls `_show_error` and returns before creating the
worker. This covers the case where 100-point sweeps for large radial models
exceed the project limit even after far-field patterns are coarsened or
disabled. Tests cover the domain defaults, dialog default, size thresholds,
blocked run, warning cancellation, and the sweep-only size estimates for a
compact dipole and a 725-segment model.

## UX43 — Optional 3D report figure preference (2026-11-19)

**Status:** implemented 2026-11-19.

`UiPreferences.report_include_3d` defaults to true and is stored under
`ui/report_3d`. The Preferences dialog exposes **Include static 3D far-field
figure**; the MainWindow passes the value as `include_pattern_lobe` to
`write_html_report` and `write_report_pdf`. Both writers default to including
the figure for direct callers. Disabling it removes only the primary 3D
wireframe; the 2D cuts, band sections, and Pattern tab are unchanged. Tests
cover the QSettings round trip, the dialog, accepted preferences, both report
writers with the option off, and the EN/ES help manifest.

## UX44 — Opt-in 3D far-field figure per analyzed band (2026-11-19)

**Status:** implemented 2026-11-19.

`UiPreferences.report_include_band_3d` defaults to false and is stored under
`ui/report_band_3d`. The Preferences dialog adds **Include 3D figure in each
analyzed band**, enabled only while the primary 3D option is checked. Both
report writers accept `include_band_pattern_lobes`; band figures are emitted
only when it and `include_pattern_lobe` are true. HTML adds one figure to each
band section after its 2D cuts; the PDF does the same in its band loop. The
standard report stays at one primary figure unless the user opts in. Tests
cover the preference round trip, the dialog dependency, HTML and PDF figure
counts, and the vector PDF path.
