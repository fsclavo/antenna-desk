# Autonomous execution backlog

**Date:** 2026-11-18
**Status:** active execution queue.

This is the only active execution queue. It contains shippable items,
dependencies, blockers, acceptance criteria, and the current test baseline.
Product scope and the antenna expansion order live in
[`ROADMAP.md`](ROADMAP.md); evidence status lives in
[`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md); architecture decisions live in
[`ADR/`](ADR/). Do not create a second backlog: add product scope to the
roadmap and active work here.

This is the ordered queue for continuing without waiting for new product
decisions. Each item is independently shippable and must leave the full gate
green. Items marked **blocked** require a measurement, a traceable source, or an
external service and must not be invented or simulated into existence.

## Rules

- One coherent milestone per change set.
- Run `ruff check`, `ruff format --check`, both `mypy` passes, and the full
  `NEC2C=... uv run pytest` before declaring an item complete.
- Add domain, persistence, UI, scene, reporting, optimizer, migration, and
  documentation coverage proportional to the item.
- No new numerical reference without a traceable source.
- Do not commit or push unless explicitly requested.

## Queue

| ID | Task | Size | Depends on | Acceptance |
|---|---|---|---|---|
| ~~A1~~ | ~~Decide the boom-correction policy~~ | S | traceable source | **Done 2026-11-08:** the Yagi dialog, evidence registry, and user guide state that boom mounting is not modeled |
| ~~A2~~ | ~~Export optimization evaluation/Pareto data~~ | S–M | none | **Done 2026-11-08:** UTF-8 CSV export with a stable schema, Pareto flags, and tests |
| ~~A3~~ | ~~Per-source input results for multi-source antennas~~ | M | multi-source model | **Done 2026-11-08:** every frequency stores ideal voltage, current, impedance, amplitude, phase, and power per driven source; the **Sources** tab exposes them; schema 29. |
| ~~B1~~ | ~~Promote `inverted_l` evidence if a source exists~~ | M | independent source | **Done 2026-11-08:** no source matches the current no-radial bent-wire template; Cebik uses 32 radials, K9LA uses a slanted top plus one radial, and K2AV uses a folded counterpoise. The audit keeps it C and records the sources considered. |
| ~~B2~~ | ~~Improve the Ringo matching-ring model~~ | M | manufacturer data or measurement | **Reviewed 2026-11-08:** the AR-6 manual confirms the 3.1 m height and 33 cm ring but the real antenna uses a split tuning ring, adjustable tuning rod, and 75 Ω coaxial stub that the template does not model. No published feedpoint R/X table was found; remains C. |
| ~~B3~~ | ~~Add independent checks for biquad/double biquad/Beverage/loaded dipole~~ | M–L | source or measurement | **Reviewed 2026-11-08:** `biquad` and `beverage` were promoted to B for published starting dimensions only; `double_biquad` and `loaded_dipole` remain C because their published topology or ground model differs. See `docs/EVIDENCE_AUDIT.md`. |
| B4 | Fan-dipole coupling calibration | M | measurement | A coupled-fan measurement is reproduced; no scalar correction is invented |
| ~~C1~~ | ~~**Phased verticals / arrays**~~ | XL | multi-source architecture | **Done 2026-11-08:** multi-source model and schema 24, then the 2–4 element phased vertical family with ideal phase/amplitude progression, radial screens, schema 25, editor, scene markers, reports, construction notes, and family optimizer. Evidence remains C pending a traceable reference. |
| ~~C2~~ | ~~Quad beam / hexbeam~~ | L | C1 lessons optional | **Done 2026-11-08:** quad beam with 2–3 loops plus a single-band hexbeam with published G3TXQ dimensions, schema 26/30, editors, scene contracts, reports, construction notes, and family optimizers. Evidence: quad beam C; hexbeam B on published starting dimensions, with the bent-wire reconstruction and frame limits visible. |
| ~~C3~~ | ~~**Log-periodic**~~ | L | transposed feed-line model | **Done 2026-11-16:** added a straight-element log-periodic dipole array as a normal family over `AntennaModel`, `Wire`, `FeedPoint`, and `TransmissionLine`. The only cross-cutting change is a generic `phase_reversal` flag on `TransmissionLine`, emitted as a negative NEC TL characteristic impedance. The Cebik 10 m 1.0 in, 75 Ω reference reproduces the published NEC-4 gain (7.37 vs 7.36 dBi), front-to-back ratio (22.01 dB), element-center phases (within 1.6°), and segmentation stability. Evidence is **B**: a published-model comparison, not a measurement. The ARRL/Cebik 7 MHz wire design is a swept-element V array and is not reproduced by this straight-element family; it remains a future variant. See `docs/ADR/0041-log-periodic-transposed-feed.md` and `docs/spikes/c3-log-periodic-spike.md`. |
| ~~C4~~ | ~~Discone~~ | L | none | **Done 2026-11-08:** radial-wire cone and disc with apex feed gap, schema 27, editor, scene, reports, construction notes, and optimizer. Evidence stays C because the wire approximation and feed transition are not validated. |
| ~~C5~~ | ~~Trapped / multiband Yagi~~ | L | trap model reuse | **Done 2026-11-08:** two-band trapped Yagi with ideal parallel LC trap pairs on each element, schema 28, editor, scene, reports, construction notes, and optimizer. Evidence stays C because trap loss and boom mounting are not modeled. |
| ~~C6~~ | ~~HexBeam geometry correctness~~ | M | published G3TXQ/K4KIO drawing | **Done 2026-11-18:** the single-band model now routes the M driver and rear U reflector on the six-spreader frame. Ten canonical wires, 6.604 m span, 0.6096 m tip gap, all wire points at or inside the 3.302 m turning radius, reflector midpoint at the rear, and a zero published fore-aft trim. Domain and optimizer share one frame helper; scene dimensions, golden scenes, reports, help, and docs are updated. Tests: 3,533 passed, 1 skipped; ruff/format/mypy pass; no schema or solver change. See `docs/spikes/c6-hexbeam-geometry.md`. |
| ~~C7~~ | ~~Multi-band HexBeam (1-5 bands)~~ | L | C6; feed-model decision; published 5-band table | **Done 2026-11-18 via C7a–C7c, with C7d–C7g follow-ups:** selectable band set and count (1-5) on a shared frame with nested G3TXQ 20/17/15/12/10 pairs, per-band tip gap and vertical offset, one driven band at a time, editable band editor/table, nested scene, per-band reports, editable custom band rows, selected-band optimization, and real NEC2C runs for 20/15/10 m. 6 m remains optional; multi-band performance is not validated. |
| ~~C7a~~ | ~~Multi-band HexBeam domain and schema~~ | M | C6; ADR-0045 | **Done 2026-11-18:** [ADR-0045](ADR/0045-multiband-hexbeam.md) accepted. `HexbeamBand`, optional `bands`, shared frame with linear per-band radius, one driven band at a time, schema 55 with no-value-rewrite migration, optimizer and frequency-scaling unavailable reasons. Domain, persistence, migration, and registry tests pass; full gate 3,542 passed, 1 skipped at C7a; no solver change. |
| ~~C7b~~ | ~~Multi-band HexBeam preset, editor, scene, and reports~~ | L | C7a | **Done 2026-11-18:** published 20/17/15/12/10 preset and 218/412 reconciliation; band checkboxes and read-only per-band table; nested scene rendering with the primary band emphasized and a band note; per-band summary/construction rows; EN/ES help; golden scenes updated. Multi-band optimization/scaling remain explicitly unavailable. |
| ~~C7c~~ | ~~Multi-band HexBeam validation and optimizer scope~~ | M | C7b | **Done 2026-11-18:** multi-band optimization remains explicitly unavailable with a translated reason; feed-harness, inter-band coupling, and balun limitations are visible in help/evidence/report rows; real NEC2C 20/15/10 m runs completed with one driven source per analysis and finite pattern results; validation/evidence docs updated; full gate 3,553 passed, 1 skipped. |
| ~~C7d~~ | ~~Selected-band HexBeam optimizer~~ | M–L | C7c; family-optimizer ADR | **Done 2026-11-18:** the family optimizer targets the active band from the editor. Its descriptor varies only that band's driver/reflector halves, tip gap, and height; the shared turning radius, conductor, and every other band stay fixed. Validation enforces the band's nested frame, conductor spacing, and a conductor-diameter clearance between adjacent band radii. The descriptor builds the model with the selected band excited and evaluates it at that band's frequency, and the dialog shows the target band. Full multi-band optimization remains explicitly unavailable. Covered by registry, use-case, UI-flow, and real NEC2C tests. |
| ~~C7e~~ | ~~Selectable HexBeam band dimensions and scene highlight~~ | M | C7c | **Done 2026-11-18:** transient active-band selector in the band group. The selected band's feed, halves, tip gap, turning radius, span, summary, and inset are dimensioned; its wires are emphasized and the other bands stay visible. The form emits a view-only signal, and the geometry view/export paths carry the active band. No schema change. |
| ~~C7f~~ | ~~Editable HexBeam band table and custom band sets~~ | M | C7c | **Done 2026-11-18:** the band table is editable (label, frequency, driver/reflector halves, tip gap, feed gap, vertical offset) and is the source of truth. Rows can be added or removed within 1–5; removing to one row returns to a single-band design. Labels and frequencies are editable, rows must stay ordered from lowest to highest frequency, and uncovered cells keep their exact canonical values. Custom sets are marked in the editor, design summary, and construction sheet; switching to a published preset asks before discarding them. EN/ES help and coverage tests added. |
| ~~C7g~~ | ~~HexBeam band-aware starting set and scaling policy~~ | S–M | C7c; source policy | **Done 2026-11-18:** in multi-band mode the primary-frequency field uniformly scales the selected published stack when the target stays inside the primary band. Band frequencies, lengths, gaps, offsets, and shared radius scale together; the form preserves the scaled bands, labels are nominal, and a reference-scaled warning is shown. Out-of-band targets are rejected. This is a starting-set scaler, not a general estimator or optimizer. |
| C7h | Optional 6 m HexBeam band | S | C7c; published 6 m row | Add the published 6 m driver/reflector/tip-spacer row and vertical offset, with the same frame-fit validation, editor option, reports, and evidence note. No performance claim. |
| C7i | HexBeam feed harness and inter-band coupling | L | traceable harness data or measurement | Model the parallel coax feed harness/jumper lengths and inter-band coupling, or keep it explicitly unavailable; no invented values. Blocked until a source or measurement exists. |
| ~~E1~~ | ~~Raise the simulation timeout default to 180 s and expose an override~~ | S | none | **Done 2026-11-08:** `SimulationSpec.timeout_s` defaults to 180 s; **Advanced simulation → Solver** exposes a 10–3600 s override applied to single runs, band analysis, and family optimizations; tests cover the default and override. |
| ~~E2~~ | ~~Parallelize independent optimizer evaluations with a bounded worker pool~~ | M–L | E1 | **Done 2026-11-08:** the engine accepts an optional batch evaluator and the command runs 1–8 bounded workers (dialog default `min(4, max(1, CPU − 1))`, sequential when 1). Candidate order and results are deterministic for a fixed configuration, cancellation reaches every in-flight solver process, and single-solve behavior is unchanged. |
| ~~E3~~ | ~~Parallelize band analysis with the same bounded pool~~ | M | E2 | **Done 2026-11-08:** bands run in bounded batches (dialog 1–4, command 1–8, sequential default) with results and progress in selection order; cancellation reaches running bands and keeps completed results. The real `nec2c` benchmark measured **1.3–1.8×** speedup with four workers, +14 MiB parent peak RSS, and 2.4–2.8 MiB per solver child; see `docs/MULTIBAND_PERFORMANCE.md`. Re-measured after E5 on 2026-11-10: the sequential path is 10–20 % faster and the four-worker speedup is **1.2–1.5×**. |
| ~~G1~~ | ~~Single construction view and wire schedule~~ | M | none | **Done 2026-11-09:** the geometry panel exposes **Construction** and **3D**; Construction resolves to the principal projection per family (front for vertical antennas, top for horizontal beams and loops, top for the cubical quad, front with a top inset for non-planar models). The construction sheet and native PDF include a wire schedule with every wire's endpoints, length, diameter, material, and feed point. Immediate dimension fixes cover Beverage length, hexbeam span/tip gap, magnetic-loop diameter, discone plan heights, J-Pole/Slim Jim feed/base/gap labels, and the hidden-dimension notice. See `docs/ADR/0027-construction-view-policy.md`. |
| ~~G2~~ | ~~Beam construction dimensions~~ | M | G1 | **Done 2026-11-09:** Yagi element labels and inter-element spacings; Moxon tip-detail inset; hexbeam spreader angle, turning radius, and half-detail segment lengths; trapped-Yagi element/spacing labels and symmetric trap inset; quad loop labels and director spacing. Detail insets are larger and the principal views now hide only low-priority overall dimensions. |
| ~~G3~~ | ~~Wire and vertical construction dimensions~~ | M | G1 | **Done 2026-11-09:** single-wire views dimension the feed offset and every load position; loaded-dipole links are measured from the feed; trap-dipole traps from the wire start; verticals dimension the loading-coil height and top-hat radius; half-square/bobtail dimension a nonzero feed offset below the top; fan dipoles label each leg, and the construction sheet lists included angles and end heights. |
| ~~G4~~ | ~~Embed the construction view in the sheet~~ | S–M | G1 | **Done 2026-11-09:** the construction sheet HTML and native PDF embed the rendered Construction view; the dialog preview loads the same image as a document resource. The sheet keeps the wire schedule below the figure. |
| ~~G5~~ | ~~Radial/array construction details~~ | S–M | G1 | **Done 2026-11-09:** discone cone angle plus half-angle/radial-step note; phased-vertical source labels with phase and amplitude; biquad loop-side stack dimension; quad-beam driven-loop front detail inset with the square side. |
| ~~G6~~ | ~~Installation auxiliary view in the sheet~~ | S | G4 | **Done 2026-11-09:** when Construction is a top view, the sheet renders a second front elevation with height, ground line, and feed height; the dialog preview and PDF include both figures. |
| ~~G7~~ | ~~Title block and bill of materials~~ | S | G4 | **Done 2026-11-09:** the HTML and PDF sheets have a project/design/antenna/frequency/units/date title block and a BOM with conductor totals grouped by material/diameter, plus load, line, and source counts. |
| ~~G8~~ | ~~Wire schedule CSV export~~ | S | G1 | **Done 2026-11-09:** the Export menu writes the per-wire schedule as CSV with the canonical header, coordinates, length, diameter, and material. |
| ~~G9~~ | ~~Evidence and limitations in the sheet~~ | S | G4 | **Done 2026-11-09:** the HTML and PDF sheets show the template's evidence level, source, tolerance, and limitation, including unmodeled frame/boom/balun/trap items. |
| ~~G10~~ | ~~Compact geometry layout at small pane sizes~~ | S | G1 | **Done 2026-11-09:** compact header/margins/offsets/label font, scaled angular radii, and small-size inset suppression; the hidden-dimension notice remains visible. The wire schedule carries the values that do not fit. |
| ~~G11~~ | ~~Dimension-anchor contract test~~ | S | G1 | **Done 2026-11-09:** every linear dimension is checked against its anchor distance in elevation and plan within 1% or 5 mm; sloped custom wires no longer label a 3D offset on a projected plan anchor. |
| ~~G12~~ | ~~Top auxiliary view for front-view families~~ | S | G6 | **Done 2026-11-09:** the sheet adds a Top layout figure for fan dipole, inverted V/L, end-fed wire, and Beverage, while top-view families keep the installation elevation. |
| ~~G13~~ | ~~Bill of materials CSV export~~ | S | G7 | **Done 2026-11-09:** the Export menu writes the grouped conductor BOM as CSV with material, diameter, wire count, and total length. |
| ~~G14~~ | ~~Hidden-dimension value strip~~ | S | G10 | **Done 2026-11-09:** a label below the sketch lists the dimension values that did not fit; it hides when everything is placed and retranslates with the UI language. |
| ~~G15~~ | ~~Reference-preset frequency policy~~ | S | none | **Done 2026-11-09:** Moxon and half-square/bobtail reference presets scale to the current frequency and preserve installation fields; Ringo and vertical-mobile examples show their fixed frequency. The evidence text distinguishes the published reference frequency from scaled geometry. |
| ~~G16~~ | ~~Localize the construction sheet and reports~~ | M | G1 | **Done 2026-11-09:** the HTML construction sheet, HTML simulation report, native construction PDF, and native report PDF follow the UI language. Reporting stays Qt-free and accepts an optional labeler; the UI passes `Translator.report`. Table headers, title blocks, headings, evidence rows, design-summary labels, construction notes, and chart titles are translated. Technical values, wire IDs, units, and user project names remain canonical. |
| ~~G17~~ | ~~Vector figures in native PDF exports~~ | S–M | G16 | **Done 2026-11-09:** the construction view and its auxiliary view render to in-memory SVG; the construction PDF draws them as vector figures and falls back to the raster preview when SVG is unavailable. The simulation report draws its SVG impedance and SWR charts directly, so both native PDFs avoid image XObjects for these figures. |
| ~~G18~~ | ~~Remove the basic-antenna wizard~~ | S–M | none | **Done 2026-11-09:** wire dipole, folded dipole, and loop (including delta and quad) now open a single `BasicAntennaDialog` with the full `DipoleForm`, frequency-aware starting dimensions, hidden Family/Template rows, and project-name confirmation after acceptance. The modal fits without a scrollbar at the default size. The old `DipoleWizard` and its translation keys were removed. |
| ~~G19~~ | ~~Show translated names in the antenna catalog~~ | S | none | **Done 2026-11-09:** catalog items use Qt user roles for the key, description, evidence, and family, so the description no longer overwrites the visible item text. The list shows the translated antenna name and the detail pane shows family, description, and evidence. |
| ~~G20~~ | ~~Localize report diagnostics and evidence text~~ | M | G16 | **Done 2026-11-09:** reports use the existing `diagnostic.<code>` translations with an English fallback for unknown codes, and the evidence source, tolerance, and limitation are translated per template and field. Tests enforce coverage of every diagnostic code and every evidence entry. |
| ~~G21~~ | ~~Multi-view construction sheet~~ | M | G17 | **Done 2026-11-09:** the sheet shows the dimensioned construction view, the complementary front/top view when available, and an isometric 3D view. HTML uses a responsive grid; the native PDF draws the additional views side by side with captions and keeps them vector. Families without a complementary view still get construction plus isometric. |
| ~~G22~~ | ~~Shortened loaded EFHW presets~~ | M | none | **Done 2026-11-09:** added 80-10 m (20.35 m + 110 µH + 2.39 m) and 40-20-10 m (10.01 m + 23 µH + 1.85 m) end-fed presets with a 49:1 transformer, editable series loading coil, schema 31, catalog routes, editor, band plans, evidence, construction notes, and optimizer variables. Matching unit, capacitor, choke, ground, and the inverted-L bend remain limitations. |
| ~~G23~~ | ~~EFHW feed-section and convergence model~~ | M | G22 | **Done 2026-11-10:** end-fed designs use a fixed 0.5 m feed section (three segments, part of the same wire) and, when no real counterpoise is enabled, a 0.10 m installation-return proxy for the coax/mast/earth path. The proxy is modeled but not drawn or included in the wire schedule/BOM; the shortened EFHW presets use it by default. The editor warns about legacy/no-return models and provides **Check convergence** over 10/21/51 radiator segments; the check keeps the normal three-segment minimum on auxiliary wires so the shortened presets complete instead of failing with negative resistance. Schema 32 migrates older projects with both fields at zero. |
| ~~G24~~ | ~~Fixed loading-coil node for the shortened EFHW~~ | M | G22, G23 | **Done 2026-11-10:** the radiator is split at the published coil offset into lower, coil, and top sections. The coil section is a fixed 0.10 m partition with three segments and the series load at its center, so changing the radiator segmentation no longer moves the coil. The convergence check distributes its 10/21/51 radiator counts between the lower and top sections while keeping the coil node fixed. The wire schedule and BOM merge the feed/coil/top partitions into one physical conductor, and the scene keeps a load marker at the coil. Tests cover the geometry, segmentation split, fallback when the coil is inside the feed section, wire schedule/BOM, persistence, scene contracts, and NEC2C convergence. |
| ~~G25~~ | ~~Model the 49:1 matching unit and primary 100 pF capacitor~~ | L | G24; traceable transformer data/measurement; 40-20-10 schematic | **Done 2026-11-10 with limitations:** the 100 pF capacitor is confirmed as a shunt across the transformer primary (G0KYA; K1RF; G4AON; PA0EJH/PA3HHO describe the input side) and is modeled through `PiNetwork` as an input shunt plus series leakage, never as a series load in the radiator. Schema 33 adds `matching_capacitance_f` and `transformer_leakage_inductance_h`; older projects migrate with both at zero, and new shortened presets start at 100 pF and 0.198 µH. The leakage value is a starting estimate from Squash Practice's measured 49:1 transformer, not the exact preset build; capacitor ESR, winding capacitance, the choke, ground, and the inverted-L bend remain unmodeled. Core loss is now available as an optional measured table in EF7b. UI hints, summaries, construction notes, evidence, and tests are updated; the published SWR remains a trend, not a hard reference. |
| ~~G26~~ | ~~Inverted-L option for the shortened EFHW~~ | M | G24 | **Done 2026-11-11:** added optional `bend_enabled`/`bend_vertical_length_m` fields with schema 35. The End-fed editor offers **Inverted-L bend**, a vertical section measured from the feed, and a derived horizontal run that preserves the total wire length; the straight horizontal installation remains the default. The G0KYA starting installation is about 8 m vertical and 15 m horizontal, and the model uses a sharp 90° corner. The scene, dimensions, wire schedule/BOM, design summary, construction sheet, optimizer variable/constraints, evidence, and validation notes are updated. Tests cover geometry, validation, persistence/migration, scene, schedule, reports, optimizer, and editor behavior. |
| G27 | Optional transformer, common-mode choke, and coaxial loss models | L | G25; measured transformer insertion loss/core data; common-mode current model or measurement; manufacturer coax attenuation data | **Partially delivered.** EF7b added the measured transformer-loss table (`BalunLoss`); EF8 added the bounded feedpoint common-mode choke; ADR-0039 adds frequency-dependent feed-line attenuation with source-backed RG-58A/RG-213 tables, log-frequency interpolation, endpoint clamping, and a preflight range warning. The loss-accounting audit is also done (ADR-0040): the feed-chain sum must match the transducer gain, and NEC conductor/load losses including the feedpoint choke stay in the antenna power budget. Still deferred: analytical ferrite core loss with complex permeability/core geometry/winding/load data; frequency-interpolated `Zcm(f)` and shack-end choke placement; the remaining coax/choke evidence audit. All loss fields stay optional and off/zero by default; no invented loss numbers. |
| ~~G28~~ | ~~Shortened EFHW convergence and optimizer policy~~ | M | G24, G25 | **Done 2026-11-10:** shortened presets use an impedance-only convergence verdict: absolute R spread up to 1 Ω and X spread up to 10 Ω; SWR is shown as informational because the matching unit is not fully modeled. With the current model the 80-10 preset is impedance-converged and the 40-20-10 preset remains R/X-sensitive. The matching capacitor and transformer leakage stay as optimizer context values; the optimizer dialog states that they are not optimized until a measured transformer model is available. Unit, UI, optimizer-registry, and NEC2C integration tests cover the policy; the published SWR remains a trend and the evidence level is unchanged. |
| ~~E4~~ | ~~Diagnose high-radial phased-array runtime and numerical validity~~ | S–M | C1 | **Done 2026-11-08:** 4×36 quarter-wave radial screens produced 267 wire crossings, 890 segments, 25.3 s, and negative primary resistance. Halving the radial length or using 2 m radials removed the crossings and completed. The editor now warns when `2 × radial length > element spacing`; ideal-source power absorption remains documented separately. |
| ~~E5~~ | ~~Diagnose low CPU during family optimization~~ | S | none | **Done 2026-11-10:** the nec2c adapter slept 50 ms per solver run even when `nec2c` finished in about 1 ms. It now uses `Popen.wait(timeout=...)`, which returns as soon as the child exits and keeps the interval only for cancellation checks. A 226-evaluation dipole optimization went from 11.8 s to 0.47 s on one worker and from 5.2 s to 0.30 s on four. Local-search batching was measured and reverted: it did not reduce wall time and changed evaluation counts. |
| ~~E6~~ | ~~Multi-seed verification for Thorough~~ | M | E2 | **Done 2026-11-10:** the optimizer runs 1–4 consecutive seeds (Thorough defaults to 3), selects the best-scoring result, and stores the winning seed and verification metrics. The dialog shows the score/parameter spread and warns when the designs diverge; integer and choice variables must match exactly. A real 40/20/10 m OCFD run with three seeds converged to 20.90311 m with score spread 0.0 and parameter spread 4.7e-8. |
| ~~H1~~ | ~~Tooltip/help infrastructure and UI help style guide~~ | S | none | **Done 2026-11-10:** added `Translator.optional()`; `ui/help.py` resolves explicit, family-specific, shared `help.<key>`, and `<key>_hint` fallbacks without returning raw keys. `FormLabels` sets and refreshes label plus paired-control tooltips, and `DipoleForm` applies help to its labels and form rows. The style guide is `docs/UI_HELP_STYLE.md`. Tests cover resolution order, missing-key clearing, form application, retranslation, and the dipole form. |
| ~~H2~~ | ~~Common field, section, tab, and action tooltips~~ | S–M | H1 | **Done 2026-11-10:** all 33 shared `field.*` keys have English/Spanish help; `FormLabels.bind_form` pairs labels with controls across 24 family forms, `DipoleForm` covers its form and sweep controls, and the main window applies section/action/geometry/result-tab help. Missing help stays silent. Tests cover field coverage, bind-form control pairing, disabled labels, the Yagi and dipole forms, window sections/actions/tabs, and English/Spanish retranslation. |
| ~~H3~~ | ~~Family-specific and dialog tooltips~~ | M–L | H1, H2 | **Done 2026-11-10:** added family-specific help for matching, traps, loading coils, radial systems, phased-array phase/amplitude, transmission-line stubs, magnetic-loop tuning, and related variants. Beam and dipole editors receive family context, with height/spacing overrides for Yagi, Moxon, hexbeam, trap Yagi, phased vertical, quad beam, and folded dipole. The feed-line, balun-loss, loads, matching-network, transmission-line, optimizer, synthesis, custom-antenna, and measurement dialogs apply row help via `apply_row_help()`. Tests cover overrides, representative family keys, and the nine parameter dialogs. |
| ~~H4~~ | ~~Results, tables, accessibility, and help coverage audit~~ | S–M | H3 | **Done 2026-11-10:** `apply_help()` now sets tooltip, What's This, and accessible description together; **Help → What's This?** (Shift+F1) enters Qt's help mode. Result tables and headers, charts, band/pattern/current controls, status indicators, and secondary export/cancel actions have help and accessible descriptions. A bilingual coverage manifest enforces section/action/tab/chart/table/dialog help and a 240-character limit, and rejects raw keys. Automated coverage includes Spanish retranslation and disabled-label help; visual light/dark and scaling QA remains manual. |
| ~~M1~~ | ~~Effective matching-network precedence for EFHW~~ | M | G25 | **Done 2026-11-10:** added the pure `resolve_matching_network()` resolver and routed single simulation, band analysis, family optimization, synthesis, and the EFHW convergence check through it. An active project network now replaces the internal EFHW matching capacitor/leakage; with no active project network the internal model remains effective. `override_active` is derived at runtime and carried only as the non-persisted `SimulationSpec.matching_network_override` flag. The solver reports `matching_network.override`, the ideal transformer ratio is unchanged, and cascading two networks remains explicitly unmodeled. Tests cover the four precedence cases, the UI spec path, and the diagnostic. |
| ~~M2~~ | ~~Matching-network visibility and override warnings~~ | M | M1 | **Done 2026-11-10:** the design panel now has a persistent **Feed & matching** summary with separate EFHW internal, project matching, feed-line, and balun rows. End-fed designs mark the internal matching values as retained and disable them while the project network overrides, with **Edit project network** and **Remove project network** actions; removal confirms and restores the internal network. The matching-network and optimizer dialogs show the override warning. Design summaries, construction sheets, HTML/PDF reports, and the EFHW construction note show the project chain and the retained/not-applied state. Tests cover visibility, hiding without an override, retranslation, removal, form state, dialog warnings, and report rows. |
| ~~M3~~ | ~~Persist the matching-network design target and preload the dialog~~ | S–M | M1 | **Done 2026-11-11:** added the project-level `MatchingNetworkDesign` record (frequency, load R/X, source impedance, optional origin) with schema 34 and a v33→v34 migration. Removing the project network clears the target. The matching-network dialog is split into **Design target** and **Components**, preloads stored values, records manual versus simulation origin, and adds **Use current simulation point** from the raw primary-side feed impedance. Topology-specific fields are shown only where they apply, the enable label no longer says L-only, and the hint covers L, Pi, and T. Tests cover the current-point conversion, apply/reopen, disabled-network clearing, schema round trip, migration, and undo/redo. |
| ~~M4~~ | ~~Create a project matching network from an impedance point~~ | S–M | M3 | **Done 2026-11-11:** the Impedance/SWR table now has a **Create Project Matching Network...** context-menu action. It uses the raw feed impedance from `source_results` divided by the ideal transformer ratio, not the post-chain `FrequencyResult.impedance_ohm`, and passes the frequency, load R/X, and real reference impedance into the preloaded matching-network dialog. The action is disabled with an explicit message when raw impedance is unavailable. Creating over an existing network asks for confirmation, and EFHW designs with active internal matching show the override warning before opening the dialog. Tests cover raw versus post-chain values with an active transformer, feed line, and matching network, action enable/disable, replacement confirmation and cancellation, EFHW warning cancellation, dialog cancellation, and preload. |
| ~~M5~~ | ~~Matching-network precedence ADR and user documentation~~ | S | M1 | **Done 2026-11-11:** added [ADR-0028](ADR/0028-matching-network-precedence.md), recording the Override policy for every `EndFedParameters` design with active internal matching, the four precedence cases, runtime derivation, project-global scope, the no-cascade limitation, the ideal transformer ratio, and how removing the project network restores the internal unit. The user guide now documents the project network, design target, **Use current simulation point**, Feed & matching summary, and restore procedure; the domain model and ADR-0014 cross-reference the new ADR, and `CHANGELOG.md` records the policy. |
| ~~P1~~ | ~~Shared task-progress widget and state model~~ | S | none | **Done 2026-11-10:** added `ui/widgets/task_progress.py` with explicit idle/running/cancelling/completed/cancelled/error states, indeterminate and determinate modes, an elapsed-time suffix, translated text keys, and reset/finish helpers. Tests cover state transitions, translation, and idle visibility. No domain, solver, or persistence changes. |
| ~~P2~~ | ~~Simulation progress feedback~~ | S | P1 | **Done 2026-11-10:** `MainWindow` shows an indeterminate status-bar bar with elapsed time and preparing/running/processing phases from `SimulationWorker.phase`; finish, failure, and cancellation reset it. Tests cover the lifecycle and elapsed text. |
| ~~P3~~ | ~~Band-analysis progress bar~~ | S | P1 | **Done 2026-11-10:** the existing `BandAnalysisWorker.progress(index, total, band)` signal drives a determinate bar and the `Band i/n: band` label; the status text now stays on "Analyzing bands..." while the analysis runs. Tests cover the shared start path, progress updates, and reset. |
| ~~P4~~ | ~~Family optimizer progress bar~~ | S–M | P1 | **Done 2026-11-10:** `FamilyOptimizationWorker` forwards the existing command progress callback as a Qt signal; the dialog shows a determinate bar with completed/estimated evaluations and the best score, throttles updates, caps running progress below 100%, and completes, cancels, or fails with the result. Tests cover forwarding, estimation text, cancellation, and terminal states. |
| ~~P5~~ | ~~Length optimizer progress bar~~ | S–M | P1 | **Done 2026-11-10:** `OptimizeDipoleLengthCommand` now reports evaluation progress; `OptimizationWorker` forwards it and the dialog shows a determinate bar using `max_evaluations + 2 * len(sensitivity_offsets_m)` as the estimated denominator. Finish, cancellation, and failure set terminal states; tests cover monotonic counts and the dialog progress lifecycle. |
| ~~P6~~ | ~~Element and synthesis optimizer progress bars~~ | M | P1, P4, P5 | **Done 2026-11-10:** `OptimizeElementsCommand` and `SynthesizeAntennaCommand` report evaluation progress; their workers forward it and both dialogs show the shared determinate bar with the maximum-evaluation budget as the estimated denominator. Finish, cancellation, and failure set terminal states; tests cover monotonic counts, worker forwarding, dialog completion, and cancellation. |
| ~~P7~~ | ~~True per-frequency simulation progress~~ | L | P2; ADR; benchmark; D4 decision | **Closed 2026-11-16:** ADR-0042 re-ran the multiband benchmark with a denser 101-point/band sweep and a solver-only single-deck comparison. The per-band path updates progress every 0.13–0.18 s at that density; the four-worker path is 2.7× faster than sequential and faster than a sequential single deck. True per-frequency progress would require incremental parsing for no demonstrated benefit. Keep per-band progress; revisit only under the ADR triggers. |
| ~~R1~~ | ~~Re-run the `v0.4.0` release workflow and replace manual assets~~ | S | GitHub Actions runner DNS/mirror; tag `v0.4.0` | **Superseded 2026-11-11:** the `v0.4.1` release workflow completed all jobs and published CI-built Linux, Windows installer/zip, and wheel/sdist artifacts. The manual `v0.4.0` assets remain as published; rerunning that older tag is no longer required. |
| ~~UX1~~ | ~~Guided mode and next-step coach~~ | S–M | none | **Done 2026-11-11:** added persistent Guided, Standard, and Advanced modes in **View → Workflow mode**, the toolbar **Mode** selector, and **Preferences**. Guided hides advanced actions and shows a state-derived next-step panel; Standard keeps the full editor with advanced simulation collapsed; Advanced expands it. The pure workflow state machine covers project, solver, simulation, diagnostics, high-SWR review, construction, measurement, comparison, and completion states; tests cover the transitions, action visibility, persistence, and EN/ES retranslation. |
| ~~UX2~~ | ~~Installation profile~~ | S–M | none | **Done 2026-11-11:** added project-level installation profiles with name, available height and horizontal space, orientation, support type, ground preset, notes, and optional local image reference. The dialog supports add, duplicate, remove, and active selection; the active profile appears in the design panel and in construction sheets and HTML/PDF reports. Schema 36 persists the profile list and active identifier, older projects migrate with no profiles, and the editor is covered by domain, persistence, reporting, dialog, main-window, undo/redo, and EN/ES retranslation tests. Profiles are metadata and do not apply their ground automatically. |
| ~~UX3~~ | ~~Antenna suitability profiles and guided advisor~~ | M | UX1, UX2 | **Done 2026-11-11:** added twelve HF suitability profiles with band coverage, footprint and height heuristics, feed/tuner requirement, construction effort, portability, operating intents, qualitative gain/takeoff/bandwidth classes, and evidence level. A deterministic advisor applies hard constraints (bands, space, height, portability, tuner, complexity, pattern) and returns up to three candidates with fit status, reasons, warnings, blockers, and stable ordering. Added the **Help me choose...** start-page and File-menu entry, prefilled from the active installation profile, with a result table and detail pane; **Open selected design** launches the existing family editor. No LLM or solver ranking. Tests cover the advisor engine, footprint scaling, blockers, dialog behavior, main-window integration, and EN/ES help. |
| ~~UX4~~ | ~~Comparison 2.0~~ | M–L | UX2; comparison-basis ADR | **Done 2026-11-11:** added [ADR-0029](ADR/0029-comparison-basis.md) and a `ComparisonBasis` with common frequency plan, ground, reference height, and reference frequency. The dialog compares two to four designs, shows the basis explicitly, and requires **Recompute comparison**, which runs each design through a new bounded comparison worker with progress and cancellation. Height mapping is conservative: direct/apex families move to the reference, verticals shift their base, and ambiguous families keep native height with visible warnings; **Native heights** disables mapping. The table has one column per design and adds footprint, maximum height, conductor length, wire/load/line counts, and build effort; band summaries and SWR/pattern overlays are dynamic. Tests cover the basis, mapping, batch use case, worker path, dialog behavior, and main-window run construction. |
| ~~UX5~~ | ~~Contextual explanations and confidence card~~ | M | none | **Done 2026-11-11:** the Diagnostics tab now starts with a result-confidence card that shows the template evidence level, source, tolerance, limitation, modeled scope, dominant uncertainties, and a verification reminder. A **What does this mean?** selector explains impedance, SWR, efficiency, gain/directivity/realized gain, takeoff, bandwidth, ground, and feed-line/matching losses. EN/ES, accessible help, and tests cover the card, topic switching, no-design state, retranslation, and the help manifest. |
| ~~UX6~~ | ~~Feed-chain topology and loss budget~~ | L | UX2; ADR-0030 | **Done 2026-11-11:** added `MatchingNetworkPosition` (`FEEDPOINT`, `SHACK`, `NONE`) to the project and simulation specs, with schema 37 and feedpoint migration. The matching-network dialog selects the position; `link_budget()` evaluates the selected chain and reports actual dissipative line and network losses from the two-port power balance. Added the **Feed-Chain Loss Budget...** dialog with path, transmitter power, per-frequency SWR, mismatch, line, network, balun, delivered/radiated power, and dominant stage. Reports and the feed/matching summary include the position. ADR-0030 documents the chain order, the conservative balun-position limitation, and the loss semantics. Tests cover two-port loss, shack/feedpoint line loss, persistence, dialogs, reports, and main-window configuration. |
| ~~UX7~~ | ~~Construction package 2.0~~ | M | UX6 | **Done 2026-11-11:** added a persistent `ConstructionRecord` with as-built notes, measured design/actual dimensions, and checklist state (schema 38). Added the **As-Built / Checklist...** editor, a hardware BOM, target coil/trap values, and a printable checklist in the construction sheet and native PDF. The construction sheet dialog exports a ZIP package with HTML, PDF, wire schedule CSV, conductor BOM CSV, and build notes. Tests cover domain validation, persistence/migration, reporting rows, HTML/PDF sections, the editor, undo/redo, the ZIP contents, and EN/ES text. |
| ~~UX8~~ | ~~Integrated coil/trap/loading calculators~~ | M | UX7 | **Done 2026-11-11:** added deterministic component calculators for Wheeler coil inductance/turns, ideal trap/LC resonance and reactance, ideal balun/unun turns and impedance ratios, copper/aluminum conductor resistance and skin depth, and common-mode choke reference notes. **Tools → Component Calculators...** hosts the set; the **Loads** editor opens the coil/trap tab seeded from the current load and applies the result back to the form. Tests cover formulas, invalid inputs, tabs, seed/apply behavior, and EN/ES help. No new schema. |
| ~~UX9~~ | ~~Construction pre-flight checks~~ | S–M | UX7 | **Done 2026-11-12:** added a read-only `PreflightReport` grouped by errors, warnings, and information. It checks canonical geometry, wire crossings/overlaps, short wires, feed/load/source/line positions, feed and line segment centering, segmentation, active installation height/width and ground, simulation status/staleness, and missing as-built/checklist data. **Design → Construction Pre-flight...** shows the grouped report and **Go to problem** opens the relevant editor; the status is never ready with an error. The sheet, native PDF, and ZIP package include the report and the package adds `preflight.txt`. The NEC-2 ground/permeability/far-field checks moved to a shared pure validator used by both the solver and pre-flight. Tests cover every new check, the dialog, main-window routing, report/PDF/package rendering, and EN/ES text. No new schema. |
| ~~UX10~~ | ~~Measurement sessions and timeline~~ | M | UX9 | **Done 2026-11-12:** added project-level `MeasurementSession` records with UTC date, optional design, location, conditions, and notes, plus an optional `Measurement.session_id`. The **Measurements** tab and **Tools → Measurement Sessions...** open a newest-first timeline; sessions can be created, edited, and deleted, with measurements preserved and detached on delete. **Edit measurement...** assigns a session, and legacy unassigned measurements remain accessible. **Compare measurements...** aligns two sweeps on their overlapping range, interpolates only there, and shows per-point R/X/SWR, `Δ|Z|`, `ΔSWR`, mean/max impedance change, mean SWR, and a resonance shift when unambiguous; differing calibration/reference plane/feed-line conditions are flagged. Schema 39 persists sessions and the measurement link; older projects migrate with no sessions and unassigned measurements. Tests cover validation, project invariants, deletion detach, migration/round-trip, comparison math, timeline dialogs, session editing, main-window undo, import assignment, and EN/ES text. |
| ~~UX11~~ | ~~Sensitivity-based tuning assistant~~ | M–L | UX10 | **Done 2026-11-12:** added a bounded tuning estimate from a measured reference and solver probes. It selects the nearest measured resonance (or minimum-SWR frequency), estimates the local `df/dD` slope with current/lower/higher probes, proposes `ΔD = (target - measured) / slope` clipped to the user's maximum adjustment, and verifies the proposed dimension with a fourth probe. **Measurements → Tune...** and **Tools → Tuning Assistant...** run the `TuneMeasurement` use case in a worker thread with progress and cancellation. Applying the proposal updates the design through the existing family adapter, enters undo history, and runs a normal simulation. The UI shows every probe, model resonance, SWR at target, bounds, clipping, and explicit local-model limitations. Families without an editable primary dimension are disabled with an explicit reason. Tests cover the domain estimate and clipping, solver probes, cancellation/errors, dialog proposal rendering and worker path, main-window apply/undo/availability, ResultsView routing, and EN/ES text. No schema change. |
| ~~UX12~~ | ~~Measurement uncertainty card~~ | S–M | UX10 | **Done 2026-11-12:** added a qualitative measurement uncertainty card to the **Measurements** tab. It reports calibration, reference plane, feed line/accessories, session conditions, point count, span, maximum spacing, reference impedance, resonance count, and simulated coverage/spacing; classifies documentation as documented, partially documented, or limited; and lists warnings for missing metadata, no/multiple resonances, and no/partial coverage. The assessment is a pure domain function and deliberately assigns no numeric ±Ω/±dB uncertainty. Tests cover documentation levels, missing/uncertain calibration, coverage warnings, resonance counts, sweep statistics, card rendering/retranslation/empty state, and EN/ES help. No schema change. |
| ~~UX13~~ | ~~Parameter sweeps (what-if)~~ | M | UX12 | **Done 2026-11-12:** added **Tools → Parameter Sweep...** with bounded 1D/2D sweeps over the family optimizer variables. The dialog validates ranges and a 400-point cap, warns above 100 solver runs, evaluates SWR/R/X/|Z| at one target frequency, and shows a 1D metric plot with R/X/|Z| overlays and a current-design marker or a selectable 2D color grid. Invalid points and solver errors stay visible. **Apply selected** and **Apply best SWR** use the normal family adapter, undo history, and a follow-up simulation. Sweeps are transient and do not interpolate or optimize between points. Tests cover axis generation, budget/plan validation, 1D/2D evaluation order, solver errors, cancellation, dialog budget/plotting/table/selection, main-window apply/undo/availability, and EN/ES help. No schema change. |
| ~~UX14~~ | ~~Tolerance and robustness analysis~~ | M–L | UX13 | **Done 2026-11-12:** added **Tools → Tolerance & Robustness...** with a bounded study over up to five continuous length/radius dimensions. It evaluates the nominal design, every selected tolerance-endpoint corner, and a seeded uniform Monte Carlo sample inside one fractional tolerance band. Results include nominal/worst-corner SWR, Monte Carlo median/P90/P95, pass fraction against an SWR limit, an SWR histogram, and a full scenario table; invalid points and solver errors stay visible. The analysis is read-only and transient, uses the same family descriptor as the optimizer, and runs in a worker thread with progress/cancellation. Tests cover spec limits, corner generation, deterministic Monte Carlo, statistics/histograms, solver scenarios, cancellation, dialog budget/run/retranslation, main-window availability, and EN/ES help. No schema change. |
| ~~UX15~~ | ~~Project journal~~ | M | UX14 | **Done 2026-11-12:** added **Tools → Project Journal...** with a newest-first timeline of manual dated entries. Entries store a UTC timestamp, title, kind (note, decision, as-built, measurement, tuning, photo, other), notes, an optional design link, and up to twelve local image references. Creating a linked entry can capture an immutable `JournalDesignSnapshot` with canonical summary rows and model wire/load/line/source counts. **Compare versions...** shows changed, added, removed, and unchanged fields between two stored snapshots or a snapshot and the current design, without judging quality. Editing text never recaptures a snapshot; deleting a design detaches the link but preserves the snapshot. Journal edits enter project undo. Schema 40 adds optional journal entries with a v39→v40 migration; tests cover domain validation, project CRUD/invariants, design-deletion detach, snapshot building/comparison, persistence round-trip and migration, editor/timeline/comparison dialogs, main-window undo, and EN/ES help. |
| ~~UX16~~ | ~~Guided experiments~~ | M–L | UX15 | **Done 2026-11-12:** added **Tools → Guided Experiments...** with three curated sweep presets: **Resonance and match** over the primary length dimension, **Height above ground** over a separate height dimension, and **Two dimensions at once** over length × height. The chooser explains the question, steps, range, metric, what to look for, and limits, and reports explicit reasons when a family lacks a required dimension. Starting one opens the existing **Parameter Sweep** dialog with axes preset and a guide banner; ranges, points, metric, validation, cancellation, and apply/undo behavior remain single-sourced. The experiments evaluate one target frequency and do not claim bandwidth, efficiency, pattern, or an optimum between points. Tests cover role resolution, unavailable reasons, 1D/2D plan counts, preset application in the sweep dialog, chooser details/retranslation, main-window apply/undo/availability, and EN/ES help. No schema change. |
| ~~UX17~~ | ~~Curated reference design library~~ | M + content | UX16 | **Done 2026-11-12:** added **File → Reference Design Library...** with twelve source-backed starting designs: ARRL 40 m dipole, Cebik 20 m Moxon, NBS 6 m Yagi, W3DZZ trap dipole, G3TXQ 20 m hexbeam, G5RV, ZS6BKW, Cebik half square, Cebik bobtail curtain, ARRL 40 m EFHW, Chameleon LEFS sloper, and ARRL 120° inverted V. Search filters by design, band, family, or source term; details show published reference, modeled scope, evidence level, source, tolerance, and limitations. **Open design** creates a normal project through the existing creation path and optionally runs the normal simulation. The library does not pre-run simulations or claim that published values were reproduced. Tests cover source-backed dimensions, unique keys, evidence levels, consistent design variants, filtering, details, retranslation, open/cancel behavior, and main-window project creation/simulation. No schema change. |
| ~~UX18~~ | ~~Minimal materials reference~~ | S–M | none | **Done 2026-11-12:** added **Tools → Materials Reference...** with four source-backed tabs. Wire lists copper and aluminum nominal conductivity/permeability; coax lists RG-58A/U, RG-213/U, and LMR-400 with impedance, velocity factor, matched loss, and reference frequency; ferrite lists Fair-Rite 31/43/61; insulators lists PTFE, Delrin, and 96% alumina. Each row shows its source, note, and limitations. The coax tab can apply the selected datasheet point to the project feed line while preserving its length; the simulation keeps a constant matched loss. Wire, ferrite, and insulator rows are reference only. Tests cover catalog invariants, sources, dialog tabs/selection, EN/ES labels/help, feed-line apply, main-window undo, and no-project behavior. No schema change. |
| ~~UX19~~ | ~~Portable project bundle~~ | S–M | none | **Done 2026-11-12:** added **File → Export Project Bundle...** and **Import Project Bundle...**. A bundle is a `.antennadesk-bundle` ZIP with `manifest.json`, the native `project.antennadesk` payload, and up to 100 referenced installation/journal images under `assets/`. Export rewrites only the bundled project's image references, records missing files, verifies asset sizes/hashes, and writes atomically in a worker thread. Import rejects traversal, absolute paths, symlinks, encrypted or duplicate entries, unknown entries, unlisted assets, size/hash mismatches, and invalid manifests; it extracts into a unique local folder, rewrites image references to local files, saves the project, and reports missing images. Tests cover round-trip, duplicate/missing assets, traversal, unlisted assets, corrupt hashes, unsupported manifests, oversized assets, unique destinations, main-window actions/errors, and EN/ES help. No schema change. |
| ~~UX20~~ | ~~Editable BOM costs~~ | S | none | **Done 2026-11-12:** added a project-level `BomCostRecord` (currency label plus stable `BomCostLine` keys) and **Design → BOM Costs...**. The dialog lists the current design's grouped conductor rows (per metre) and hardware rows (pieces, wires, or set), supports manual unit costs, shows line totals and a BOM total, and preserves cost lines for rows not present in the current design. Costs enter undo/redo and schema 45; older projects migrate with no costs. The construction sheet, native PDF, package notes, and conductor BOM CSV show cost columns/totals when present. The hardware `Antenna conductor` row is excluded from costs because the conductor BOM already carries it. No price catalog, currency conversion, tax, shipping, or labor. Tests cover domain validation, persistence/migration, entries/totals, CSV/HTML/PDF/package output, the dialog, main-window undo, and EN/ES help. |
| ~~UX21~~ | ~~Show azimuth and elevation pattern cuts side by side~~ | M | none | **Done 2026-11-12:** the **Cuts** tab shows four panes: azimuth line chart and polar lobes on the left, elevation line chart and polar lobes on the right. Frequency and metric stay shared; each plane has an independent cut selector (θ for azimuth, φ for elevation) defaulting to the maximum-gain direction and preserving selections across frequency and band changes. Each pane has its own title, axis labels, cursor readout, and a localized empty state when a cut is unavailable. The **3D lobe** tab is unchanged. The layout uses resizable splitters and remains usable at the minimum supported window size. Pattern PNG export saves the whole 2×2 Cuts view; the 3D tab saves the 3D view. No domain, solver, or persistence changes. Tests, EN/ES help, accessibility, user guide, and changelog updated. |
| ~~UX22~~ | ~~Make the pattern metric selector visibly meaningful~~ | S–M | none (coordinate with UX21) | **Done 2026-11-12:** the pattern chart titles and polar footers name the selected metric; the left axis, cursor readout, 3D label, and summary reflect the selection. A compact summary shows power gain, directivity, and realized gain for the selected frequency, with an explicit localized unavailable value instead of a silent omission. The metric definitions and lobe shape are unchanged. Tests cover titles, summary, cursor, unavailable values, retranslation, and independent cuts. EN/ES help, user guide, and changelog updated. No solver or schema changes. |
| ~~UX23~~ | ~~Expand the common coax catalog and add feed-line presets~~ | M | UX18; G27 only if frequency-dependent loss is included | **Done 2026-11-12:** expanded the shared source-backed coax catalog to 16 cables: RG-58A/U, RG-8X, RG-8/U, RG-213/U, RG-214/U, RG-174/U, RG-316/U, RG-400/U, RG-6/U, RG-11/U, LMR-240, LMR-400, LMR-600, Belden 9913, LDF4-50A, and Ultraflex 7. Each entry has impedance, velocity factor, matched loss at a documented reference frequency, source URL, revision, and visible limitations. The feed-line editor has a **Catalog** selector that fills the three electrical fields while keeping length editable; manual edits switch to **Custom**. The catalog key is not persisted; on reopen, a unique electrical match is preselected and ambiguous matches show **Custom**. The materials-reference dialog uses the same catalog. The simulation keeps the scalar matched-loss model; frequency interpolation remains G27. Tests cover catalog invariants, source/revision coverage, auto-fill, custom override, duplicate-value handling, dialog restoration, dialog behavior, and EN/ES labels/help. No schema change. |
| ~~UX24~~ | ~~Retune Moxon and Yagi catalog starting frequencies~~ | S | none | **Done 2026-11-12:** new Moxon editors start at 28.500 MHz with the Cebik 20 m wire reference scaled to that frequency, and new Yagi editors start at 145.000 MHz with the NBS five-element preset scaled from its published 50.1 MHz reference. The default field and starting geometry are generated together; a requested frequency passed to the Moxon dialog regenerates the scaled reference as well. Moxon and Yagi evidence/help state that the scaled defaults are heuristic starting points, while the exact Cebik 14.17 MHz and NBS 50.1 MHz references remain the source-backed cases. The Cebik and NBS reference actions still rescale to the current frequency. Ringo (50.100 MHz) and loaded vertical/mobile whip (7.100 MHz) keep their current defaults and are out of scope. Tests cover both defaults, the Moxon frequency-scaled dialog path, Yagi scaling/clearance behavior, EN/ES help, and the existing reference actions. No schema change. |
| ~~UX25~~ | ~~Add stainless steel 304 as a source-backed conductor material~~ | S–M | none | **Done 2026-11-13:** added `STAINLESS_STEEL_304` (1.389 MS/m, μr = 1.0), the ordered `CONDUCTOR_MATERIALS` tuple, and a shared material-combo helper used by all family editors and dialogs. The component calculator, materials reference, EN/ES labels, reports, BOM cost key, persistence round-trip, NEC `LD 5`, and no-permeability-warning tests are covered. Copper remains the default; no schema or solver-model change. |
| ~~UX26~~ | ~~Include canonical geometry and far-field pattern in exported antenna reports~~ | M–L | G17, UX21 | **Done 2026-11-13:** the HTML and native PDF simulation reports now include one canonical geometry figure rendered offscreen at a fixed size/light theme from the design snapshot, plus azimuth and elevation pattern cuts at the maximum-gain direction. Band analysis adds one pattern section per band using the band center; far-field-disabled or missing rows are explicit. New EN/ES headings and axes are translated. HTML/PDF/pattern tests are added; no schema or solver change. |
| ~~UX27~~ | ~~Use ROE consistently in the Spanish UI and reports~~ | S–M | none | **Done 2026-11-13:** all 18 Spanish UI keys that still said “SWR” now use “ROE” with feminine agreement; the first explanatory use expands “ROE (relación de ondas estacionarias)”. Hardcoded chart/table labels in the measurement comparison, parameter sweep, robustness, and end-fed dialogs use the shared localized label; the HTML report and construction-sheet bandwidth row are localized. A regression test scans every Spanish UI/report/evidence value for `\bSWR\b`; Spanish dialog and report tests cover the changed surfaces. English, internal identifiers, report keys, CSV columns, schema, and solver are unchanged. |
| ~~UX28~~ | ~~Call the vertical radiator dimension “length”, not “height”~~ | S–M | none | **Done 2026-11-13:** vertical, J-Pole, Ringo, inverted-L, SCV, and phased-vertical editors and report rows now use “length”/“largo” for the physical radiating element; base, feed, top, ring, coil, apex, stack, boom, and available heights remain “height”/“altura”. The Zepp “Radiator height” and discone “Cone height” exceptions are preserved. EN/ES help and tests cover the changed labels and installation heights. Internal field names, optimizer variables, schema, CSV/JSON keys, and solver behavior are unchanged. |
| ~~UX29~~ | ~~Show the constructive feed connection at the feedpoint~~ | M–L | UX6, UX7, UX9, ADR-0031, ADR-0033, ADR-0034 | **Done 2026-11-13:** added the read-only `FeedConnectionDetail` resolver, explicit Yagi straight/folded/beta/hairpin cases, a renderer-neutral SVG schematic, a **Connection** row and **View feed connection...** action, a read-only detail dialog, and a feedpoint assembly section in the construction sheet, native PDF, and ZIP. The four modeled/recorded/recommended/not-modeled states are separate; unclassified families return explicit unknown. ADR-0036, user guide, domain model, help, and tests are updated. No `FeedPoint`, solver, simulation, or schema change. |
| ~~UX30~~ | ~~Per-template default conductor material~~ | S–M | none | **Done 2026-11-17:** New Antenna and Change Template preselect the agreed material for every catalog template: aluminum for 15 templates, stainless 304 for the loaded vertical, and copper for the remaining 25; existing projects and reference designs keep their materials; no schema, solver-code, or migration change. |
| ~~UX31~~ | ~~Draw coax as coax in the feed-connection schematic~~ | S–M | UX29 | **Done 2026-11-17:** direct coax is drawn as a cable with a center conductor, outer shield, and cross-section; the middle device box is gone. Current balun, transformer, balanced line, multi-port, and unknown have distinct drawings; terminal labels honor ground/counterpoise/return; a recommended choke is dashed. EN/ES, dialog, HTML, PDF, ZIP, and tests pass; no domain, solver, or schema change. |
| ~~UX32~~ | ~~Quad beam frequency-first starting dimensions~~ | S | none | **Done 2026-11-17:** `QuadBeamDialog` now seeds the loop side and reflector/director spacing from the requested frequency, and `new_quad_beam_antenna()` reuses the active design frequency. **Load starting dimensions** is exposed in the shared form; it preserves the installation height, conductor, material, ground, azimuth, element count, reflector/director scales, and transformer. At 144 MHz the side is about 0.494 m and the spacing about 0.416 m. EN/ES, help, UI tests, user guide, and changelog are updated; no domain formula, schema, solver, or migration change. |
| ~~UX33~~ | ~~Generalize frequency-first generator seeding~~ | S–M | UX32 | **Done 2026-11-17:** hexbeam, discone, trapped Yagi, and phased-vertical generators now call their existing `load_starting_dimensions()` when a frequency is supplied and expose **Load starting dimensions** in the shared form. Each preserves its installation and matching fields; tests cover the frequency path, action, preservation, and EN/ES retranslation. Formulas, schema, and solver are unchanged. |
| ~~UX34~~ | ~~Decide design-frequency versus analysis-frequency semantics~~ | S | none | **Done 2026-11-17:** [ADR-0043](ADR/0043-design-versus-analysis-frequency.md) defines design versus analysis frequency, the pristine test, managed versus preserved fields per family, undo and modal-dialog behavior, user-facing wording, and the Yagi exception. No behavior change; UX35 implements the pristine-only automatic path. |
| ~~UX35~~ | ~~Pristine-geometry frequency recalculation~~ | M | UX33, UX34 | **Done 2026-11-17:** the five generators track their managed geometry; a design-frequency change regenerates only pristine geometry, shows an updated note, preserves installation fields, and stops auto-resizing after a managed edit. Edited geometry shows a stale message and offers **Load starting dimensions**. Modal generators update locally; project-editor changes remain normal unsaved form edits. Tests cover pristine/edited paths, preserved fields, loaded parameters, and new-project state. No schema or solver change. |
| ~~UX36~~ | ~~Quad beam frequency-first estimator~~ | M | UX32 | **Done 2026-11-17:** `quad_beam` is registered in the estimator registry; `DesignIntent` carries 2–3 elements; **Estimate Dimensions...** is enabled, preloads the current element count and height, and returns the documented quarter-wave-side/fifth-wave-spacing heuristic with confidence, source, assumptions, warnings, tolerance, and 144 MHz reference tests. Apply uses the dialog element count and height and preserves reflector/director scales, transformer, radius, material, ground, and azimuth. NEC smoke and UI/domain/registry tests pass; no schema change. |
| ~~UX37~~ | ~~Explicit scale-to-frequency action for tuned designs~~ | M–L | UX34, UX35 | **Done 2026-11-17:** **Design → Scale Geometry to Frequency...** scales the allowlisted wire dipole, folded dipole, loop, quad beam, biquad, discone, and hexbeam by the old/new frequency ratio, with a target-frequency dialog and approximation warning. Installation, conductor, ground, feed line, and matching values are preserved; loaded, trapped, multiband, Yagi/Moxon, and fan designs are disabled with a reason. It enters undo history and is covered by domain/UI tests. No schema or solver change. |
| ~~UX38~~ | ~~Select the Design tab after creating a new antenna~~ | S | none | **Done 2026-11-17:** after a successful New Antenna creation, `_create_project_from_parameters()` selects `_design_tab`; this covers catalog templates, Antenna Advisor, and Reference Design Library. Cancelled or failed creation leaves the current tab unchanged. Advanced mode still opens Simulation when the mode is selected; Change Template, Open Project, NEC/MMANA import, and New Variant are unchanged. Advanced-mode success, cancellation, and failure tests pass; user guide and changelog updated. No schema, solver, or i18n change. |
| UX39 | Raise generated single-design impedance/SWR sweeps to at least 100 computed points | S–M | none | Generated templates default to 100 points (including the two-band shared plan); every computed point remains in the chart, table, and exports; marker density is bounded without dropping data; tests and docs updated; no schema or solver change. |
| UX40 | Add a static 3D far-field lobe figure to the HTML and PDF simulation reports | S–M | UX26, UX21 | **Queued 2026-11-18:** add one deterministic, Qt-free isometric SVG wireframe of the full far-field grid to the primary far-field section, with a dBi legend, maximum-gain marker, ground ring when applicable, bounded decimation, and explicit single-cut/unavailable states. Band sections and the two 2D cuts remain unchanged. EN/ES labels, HTML/PDF vector tests, determinism and size-bound tests, user guide, architecture, validation plan, and changelog; no schema, solver, or domain change. |
| ~~U0~~ | ~~Close the adaptive length display-units spec~~ | S | none | **Done 2026-11-17:** [ADR-0044](ADR/0044-adaptive-length-display-units.md) and [`DISPLAY_UNITS_SPEC.md`](DISPLAY_UNITS_SPEC.md) accepted; backlog, roadmap, docs index, architecture, geometry contract, and project decisions linked. No code change. |
| ~~U1~~ | ~~Shared adaptive length formatter and Units preference~~ | S–M | U0 | **Done 2026-11-17:** added the Qt-free `DisplayUnits`/`LengthPolicy` formatter with metric auto (mm/cm/m), imperial auto (in/ft), fixed meters/feet, fixed per-unit precision, label trimming, zero/negative handling, scale hints, and table-unit selection. The four-option Units preference now stores the system and policy in QSettings, maps legacy metric/imperial values to automatic, and has EN/ES help. Boundary, negative, table, legacy-setting, and dialog tests pass. Scenes, forms, and reports remain unchanged until U2–U5; no schema change. |
| ~~U2~~ | ~~Adaptive units in geometry scenes~~ | M | U1 | **Done 2026-11-17:** `build_scene`/`_Factory`, dimension labels, summaries, detail insets, and the scale bar accept `DisplayUnits`. Auto scenes cover 28.5/435 MHz Moxon, 20 m dipole, and 435 MHz hexbeam; scale-bar steps are unit-aware; the small-dimension anchor tolerance is `max(0.5 mm, 1%)`. Legacy `unit_system=` callers keep fixed geometry strings and goldens. No form or report changes. |
| ~~U3~~ | ~~Adaptive units in antenna-family forms and tables~~ | M–L | U1 | **Done 2026-11-18:** all 26 family editors use `LengthFieldSpec`, including the discone, Moxon, hexbeam, quad beam, trapped Yagi, phased vertical, vertical, OCFD, beverage, fan dipole, dipoles/folded dipole/loop, inverted L/V, magnetic loop, biquad, Ringo, SCV, T2FD, Zepp, J-pole, transmission-line doublet, Yagi, log-periodic, and end-fed fields. The editable Yagi, log-periodic, and fan-dipole tables choose one unit per table and show it in the header; radius/diameter cells stay mm/in. The global length floor is 1 mm / 0.003 ft for small UHF features, and all forms are covered by fixed and automatic metric/imperial round-trip tests plus a frozen-suffix edit test. Acceptance met: physical values survive unit/policy switches, no silent clamping, table headers updated, and UI tests pass. |
| ~~U4~~ | ~~Adaptive units in optimization, synthesis, and auxiliary dialogs~~ | M | U1, U3 | **Done 2026-11-18:** the bounded length optimizer, family optimizer constraints, feed-line length, G5RV/ZS6BKW heights, synthesis bounds, design-from-frequency height/base/end fields, comparison reference height, transmission-line offsets/lengths, custom-wire coordinate table/radial length/feed offset, and robustness result formatting use `LengthFieldSpec`/`DisplayUnits`. Dialog-level `length_bounds` initialization was removed where per-field ranges replace it. Result formatting picks a unit per value without changing solver inputs. Acceptance met: auto/fixed and metric/imperial tests, no range regressions, EN/ES help unchanged, no solver change. |
| ~~U5~~ | ~~Adaptive units in construction sheets and human-readable reports~~ | M–L | U1, U2, U3 | **Done 2026-11-18:** construction-sheet and HTML/PDF report design-summary rows, installation profiles, feed/matching rows, loads, transmission lines, BOM totals, feed height, family dimension tables, construction-prose notes, wire schedules, and the custom report title/footer use `DisplayUnits`. The wire schedule picks one coordinate/length unit per table and shows it in the HTML header; the native PDF schedule uses the same unit. Construction notes choose one unit per note from their largest length. CSV stays canonical meters/mm and DXF keeps meter coordinates with `$INSUNITS=6`. Acceptance met: HTML/PDF/package tests, table-header units, CSV/DXF canonical assertions, no schema. Manual visual QA remains under U6. |
| U6 | Documentation, help audit, and visual QA | S–M | U2–U5 | **In progress 2026-11-18:** user guide, roadmap, units spec, README, changelog, help tests, and the automated font-scaling/geometry checks are updated. [`QA_PASS_2026-11-18.md`](QA_PASS_2026-11-18.md) records the automated gate and the remaining desktop light/dark/font-scaling checklist. The track closes after that manual QA. |
| ~~EF1~~ | ~~Preserve shortened-EFHW structural segmentation in optimizer candidates~~ | S–M | none | **Done 2026-11-13:** the optimizer descriptor can declare model-defined wire partitions. Only the shortened EFHW presets opt in, preserving the fixed three-segment feed and loading-coil sections while the radiator counts are recalculated. Unit tests cover 80-10 and 40-10; other families keep a `None` hook and the previous segmentation path. No solver, schema, or UI change. |
| ~~EF2~~ | ~~Diagnose input-shunt matching-network topology limits~~ | S | EF1 optional | **Done 2026-11-13:** added `MatchingNetworkOrigin` as runtime-only simulation context, a domain `input_shunt_l_network_swr_floor()` predicate, a `LinkBudget` floor field, and a `matching_network.topology_limit` warning. The warning appears only when the effective network is the internal EFHW input-shunt unit; project networks and other families stay unchanged. The origin is excluded from the model fingerprint and is not persisted. EN/ES diagnostic text, domain, link, fingerprint, resolution, and real NEC2C tests cover the path. |
| ~~EF3~~ | ~~Warn about the installation-return proxy and SWR confidence~~ | S | none | **Done 2026-11-13:** shortened EFHW editors now add an `endfed.warning.return_proxy` warning when the 0.1 m installation-return proxy is active. The results confidence card and exported reports add a **Model confidence** row that marks absolute SWR as informational and states that the installation return is a proxy, not a physical counterpoise. Standard end-fed, sloper, random wire, and every other family are unchanged. No solver or numerical change. |
| ~~EF4~~ | ~~Clarify the optimizer objective and expose best-SWR selection~~ | S–M | none | **Done 2026-11-13:** shortened EFHW descriptors now default to **Minimum SWR** while every other family keeps **Target impedance**. The dialog shows a hint when the selected candidate is worse than another feasible candidate's SWR, and adds **Apply Best SWR** independent of the objective. Objective help now states that target impedance minimizes `|Z−Z0|`, not SWR. No scoring, schema, or solver change; a `MIN_MISMATCH` objective remains a separate ADR. |
| ~~EF5~~ | ~~Recommend action when the optimizer optimum hits a search bound~~ | S | EF1 | **Done 2026-11-13:** added `variables_at_bounds()` in the optimizer variable module and a descriptor opt-in flag. The shortened EFHW descriptors set the flag; their summaries name the continuous unlocked variables within 1 % of a bound and recommend widening the range only when buildable. No automatic bound expansion; other families keep the previous recommendation set. |
| ~~EF6~~ | ~~Investigate 40-10 shortened-EFHW convergence~~ | M | EF1, EF3 | **Done 2026-11-13:** spike completed; no model change is justified without a traceable reference. Coil segment count 1–5 at the 0.10 m section does not remove the R/X sensitivity. A wider 0.20–0.50 m section makes 40-10 converge but makes 80-10 substantially worse, so there is no single section length that improves both. The preset keeps its R/X convergence check and gains an explicit editor warning that absolute SWR is informational. Thresholds were not relaxed. |
| ~~EF7a~~ | ~~Measured 49:1 transformer reactive preset~~ | M | EF6 | **Done 2026-11-13:** added an optional `EndFedTransformerModel` preset using Squash Practice's measured 2xFT114-43, 5T/30T build: 198 nH leakage, 2.7 pF secondary winding capacitance, and 25.8 µH magnetizing inductance. The model is selectable in the editor, persisted in schema 46, and used by the internal matching network only; core/frequency-dependent loss remains EF7b. No optimizer variables were added. |
| ~~EF7b~~ | ~~Measured transformer loss and frequency dependence~~ | L | EF7a; measured loss data | **Done 2026-11-13:** added the optional `EndFedTransformerLossModel` selector with the Squash Practice/AF7NX 2xFT114-43, 5T/30T table: 0.43/0.33/0.30/0.32 dB at the 80/40/20/10 m band centers. Values are interpolated linearly in log frequency between 3.75 and 28.5 MHz and clamped outside; the source measured one reference build at 50 W FT8, so this is not a universal loss model. The loss is off by default, requires a 49:1 ratio, and is reported as `transformer_loss_db`, separate from mismatch loss and the project `BalunLoss`. Schema 48 persists the selector and the per-frequency loss; CSV, feed-chain, results, construction sheet, and EN/ES help expose it. KN5L's ~0.3 dB core-loss data is cited as corroboration, not used to invent extra frequency points. |
| ~~EF8a~~ | ~~User-selectable end-fed return path~~ | M | EF3 | **Done 2026-11-13:** added `EndFedReturnPath` (`auto`, `installation_proxy`, `counterpoise`, `coax_shield`) and persisted it in schema 47. `auto` preserves the legacy counterpoise-or-proxy behavior; counterpoise and coax shield use the existing return length/height/azimuth fields, with the shield as a model-only straight-wire approximation. The optimizer searches the return length for counterpoise/coax and keeps the height variable only for a physical counterpoise. The editor, reports, construction sheet, scene note, and EN/ES help state that the shield is a wire approximation. EF8 later added an optional feedpoint choke; shack-end placement and shield transfer impedance remain unmodeled. No solver change for other families at EF8a. |
| ~~EF8~~ | ~~Common-mode return / coax-shield model for end-fed antennas~~ | L | measurement or validated common-mode model | **Done 2026-11-13 with explicit limits:** EF8a added the selectable return path and the coax-shield wire approximation. EF8 adds an optional **feedpoint** common-mode choke as a measured series R/X load on the shield, with a required source, a 49:1-compatible coax-shield return, a frequency-mismatch warning, and a predominantly-reactive warning. Positive X becomes a series L and negative X a series C; R is held constant. ADR-0037 records the model. Shack-end choke placement, frequency-interpolated `Zcm(f)`, shield transfer impedance, the real cable route, and absolute common-mode-current prediction remain unmodeled; no universal choke preset was invented. Do not optimize the installation proxy as a physical radial. |
| EF9 | Design-specific matching-network optimization | L | EF7b, EF8, ADR | **Done 2026-11-14; automatic Pi/T added 2026-11-16.** ADR-0038 implements an optional design-specific L/Pi/T network owned by `EndFedParameters`, with precedence **project network > design-specific network > internal fixed unit**, schema 50, bounded optimizer variables, UI, reports, and regression coverage. The project matching dialog and the design-specific end-fed action now synthesize L, Pi, or T from the current primary-side feed impedance, fill the editor, and wait for explicit user review. Pi/T use a visible total design Q (0 = auto above the minimum); a Q below the minimum returns no solution. The synthesis is lossless; component Q remains a separate loss model. Do not add loose C/L variables to the fixed input-shunt network. |
| ~~HF1~~ | ~~Frequency-aware optimizer-bound contract and ADR~~ | S | none | **Done 2026-11-18:** [ADR-0046](ADR/0046-frequency-aware-optimizer-bounds.md) accepted. It separates physical construction floors from per-run search bounds, requires λ/current-relative normalization, defines the initial-in-bounds and non-degenerate-span invariants, forbids silent initial clamping, records explicit-unavailable behavior, makes the Moxon gap a first-class contract, and forbids invented high-frequency reference values. No behavior change. |
| ~~HF2~~ | ~~Enforce descriptor bounds and remove silent initial clamping~~ | M | HF1 | **Done 2026-11-18:** descriptors validate every default-active initial value and reject outside bounds, non-finite values, degenerate spans, and unrepresentable integer/choice values. Availability returns a translated reason with family, variable, value, and bounds; unlocking a bad variable is blocked in the dialog before the solver starts; the engine returns `ERROR` instead of clamping. Locked variables stay context. Tests cover Moxon 2.4 GHz, vertical 2.4 GHz, Yagi 5.8 GHz, a valid Cebik 20 m Moxon, engine/use-case guards, and the UI message. |
| ~~HF3~~ | ~~Replace absolute length floors with frequency-aware bounds~~ | L | HF1, HF2 | **Done 2026-11-18:** `_length`/`around` now use relative bounds around the current frequency-scaled design; the old 0.1/0.5/0.05 m practical floors were removed. Remaining absolute floors are genuine: zero for heights/base planes, conductor clearance for gaps/spacings/tips, the end-fed feed-section structure, electrical component minima, and the biquad small-feature reference. Variable steps are span-normalized. A 1.8–5800 MHz matrix covers all supported optimizer families; a genuine conductor-floor violation still returns an explicit HF2 unavailable reason. No universal frequency cutoff was invented. |
| ~~HF4~~ | ~~Moxon geometry contract, gap variable, and constraints~~ | M–L | HF1–HF3 | **Done 2026-11-18:** added a shared `validate_moxon_geometry` used by the domain constructor, optimizer descriptor, and editor warning. The family optimizer exposes `gap_m` directly and derives the driven tip; the two redundant tip variables are gone. Gap/λ, gap/depth, gap/width, width/depth, tip/depth, and tip-sum envelopes are anchored to the Cebik 14.17 MHz reference and the exploratory 2.4 GHz control, with a hard conductor-clearance check. The 0.67λ failure is rejected. Tests cover 14.17/28.5/144/435/1500/2400 MHz, the exact reference, the optimizer rebuild, and the UI warning. No schema change. |
| ~~HF5~~ | ~~Yagi wavelength-relative bounds and high-element-count QA~~ | M | HF1–HF3 | **Done 2026-11-18:** the Yagi descriptor uses only relative bounds around the current normalized design; element, gap, height, fold-spacing, and hairpin bounds are radius-relative and steps are span-normalized. The 0.05 m element floor is gone. Tests cover 5/10/15/20/32 elements at 1.5/2.4/5.8 GHz, the DL6WU taper constraints, exact rebuild, and folded/beta-hairpin variables. Real NEC2C smoke runs complete for 2.4 GHz 15/32 elements and 5.8 GHz 5/15 elements with finite R/X; no gain claim. |
| ~~HF6~~ | ~~Moxon high-frequency estimator, radius, and confidence policy~~ | M | HF1, HF4 | **Done 2026-11-18:** the Cebik 20 m Moxon is reference-scaled only inside the 20 m band (14.0–14.35 MHz); outside it is explicitly heuristic with a high-frequency warning, an extrapolation assumption, and tolerance `max(5% width, gap)`. The starting gap must clear two conductor diameters or the estimate is unsupported. The 14.17 MHz reference stays exact; the 28.5 MHz default is heuristic; no 2.4 GHz published reference was invented. EN/ES warning and estimator-guide policy added. |
| HF7 | Thin-wire model-quality gate for high-frequency optimization | M–L | HF1, HF2 | **Queued 2026-11-18:** define segment/radius and Moxon-gap resolution policy; expose or select the extended thin-wire kernel; block candidates with errors or unacceptable warnings; test 1.5/2.4 GHz Moxon and 2.4/5.8 GHz Yagi with and without the extended kernel; document the chosen default. |
| HF8 | High-frequency optimizer diagnostics, defaults, and Apply Best guard | M | HF4–HF6 | **Queued 2026-11-18:** enable bound-hit diagnostics for all families; show initial versus clamped values, gap/λ, and gap/radius; review the Moxon default objective; block or confirm **Apply Best** on implausible geometry; use adaptive units in the optimizer table; EN/ES help and tests. |
| HF9 | High-frequency regression matrix, evidence, and documentation | M | HF2–HF8 | **Queued 2026-11-18:** add the frequency/family matrix, an old-behavior regression for the 2.4 GHz Moxon gap, invariant and solver-completion assertions, and a no-silent-clamp check; update the ADR, estimator guide, user guide, and `CHANGELOG.md`; make no accuracy claim without a traceable source. |
| HF10 | Design-frequency/geometry consistency for Moxon and Yagi | S–M | HF1, HF2; UX34/ADR-0043 | **Queued 2026-11-18:** reconcile the Moxon manual preset and the Yagi auto-scale exception with the pristine-geometry policy; warn or block optimization when geometry is grossly inconsistent with λ; test frequency changes, preset loads, and optimizer availability. |
| D1 | Live VNA/hardware control | L | hardware | Blocked/deferred; do not start without a device |
| D2 | Additional full-wave engines | L | engine choice | Deferred until a concrete engine is selected |
| D3 | GPG/Authenticode signing | M | release credentials | Deferred; requires signing keys and a release decision |
| ~~D4~~ | ~~Segmented frequency plan in one NEC deck~~ | M | solver benchmark | **Closed 2026-11-16 by ADR-0042:** the solver-only single deck saves about 0.95 s on 808 frequencies, while the four-worker per-band path is faster than a sequential single deck and preserves the existing result, pattern, project-size, and cancellation contracts. Keep per-band batching; revisit only under the ADR triggers. |

## High-frequency optimizer bounds and Moxon gap (design note, 2026-11-18)

**Status:** HF1–HF6 are implemented on 2026-11-18;
[ADR-0046](ADR/0046-frequency-aware-optimizer-bounds.md) is the accepted
contract. HF7–HF10 are queued; HF7–HF8 are the high-frequency fidelity slice,
and HF9 closes the track.

**Related:** [ADR-0026](ADR/0026-family-optimizer-architecture.md),
[ADR-0043](ADR/0043-design-versus-analysis-frequency.md),
[ADR-0044](ADR/0044-adaptive-length-display-units.md), and
[`ANTENNA_DESIGN_ESTIMATORS.md`](ANTENNA_DESIGN_ESTIMATORS.md).

**Trigger:** a user-visible inconsistency in the family optimizers at VHF/UHF.
The first confirmed case is a 2.4 GHz Moxon whose optimized tip gap is tens of
millimetres, far outside a plausible Moxon rectangle. The same bound pattern
exists in other families.

**Evidence:** reproduced with the real NEC2C adapter and the domain/application
optimizer. At 2.4 GHz the reference-scaled Moxon starts at width 44.99 mm,
depth 17.22 mm, tip gap 1.296 mm, but the optimizer bounds are
`width=[100, 101] mm` and `depth=[100, 101] mm`. The resulting gap is
76.1–93.0 mm (0.61–0.74 λ) for every feasible candidate. A production
`MULTI_OBJECTIVE` run returned gap 86.96 mm, SWR 15.50, 4.19 dBi, and 2.11 dB
front-to-back. An in-memory control that changed only the bounds to relative
values returned gap 4.86 mm, SWR 1.05, 6.06 dBi, and 25.06 dB front-to-back.
The control is exploratory and is **not** a numerical reference. The 1.5 GHz
case is the same: 2.07 mm reference gap versus a 61.8–88.3 mm optimizer range.

The root cause is the absolute length policy in the descriptors:

- `_length()` defaults to `minimum=0.1` m and `_length`/`around` treats that
  floor as the lower search bound, not as a physical constraint.
- When `value * (1 + fraction) <= minimum`, `around()` returns a degenerate
  interval above the current design (`high = low + 1 mm`).
- `OptimizationVariable.to_fraction()` silently clamps the current value into
  that interval; the engine evaluates the clamped design, not the editor
  design.
- The Moxon validator only checks `reflector_tip + driven_tip < depth`; a
  0.67 λ gap is feasible.
- Yagi element lengths have an absolute 0.05 m floor, which starts clamping
  15+ element arrays at 2.4 GHz and every element at 5.8 GHz.
- Many other families have absolute 0.1 m or 0.5 m floors and show the same
  behavior at 1.5/2.4 GHz.

### HF1 — Bound contract (accepted)

[ADR-0046](ADR/0046-frequency-aware-optimizer-bounds.md) is the accepted
contract. It defines:

- the difference between a **physical/construction floor** (a real minimum for
  a buildable design) and a **search bound** (the interval the optimizer may
  explore around the current design);
- how search bounds are derived from the current value and/or
  `wavelength_m(parameters.frequency_hz)`, including a minimum non-degenerate
  span;
- the invariant `variable.minimum <= initial_value <= variable.maximum` and a
  second invariant that rejects a degenerate span;
- whether an out-of-bounds or unsupported design produces an
  `OptimizerAvailability` reason with a translated key or a typed hard error,
  and the user-facing message;
- why the current design must never be silently clamped;
- the Moxon gap contract (direct `gap_m` variable versus derived gap, the
  allowed gap/λ, gap/radius, and gap/depth/width ranges, and how the Cebik
  14.17 MHz reference remains exact);
- the high-frequency validity policy for the Moxon linear scaling and the
  Yagi reference, including confidence and tolerance downgrades;
- the thin-wire kernel/segmentation policy and which warnings are hard;
- the no-invented-reference rule: high-frequency checks use invariants,
  published references, or measurements; they do not turn an exploratory
  control into a golden value.

ADR-0046 explicitly rejects a blanket `minimum=0` change. Removing every
construction floor would restore the search interval but could produce
unbuildable HF designs; the two concepts must stay separate.

### HF2 — Descriptor invariant and no silent clamp

**Implemented 2026-11-18.** `AntennaOptimizerDescriptor` validates its default
search scope in the constructor. `OptimizerAvailability` carries a translated
reason plus the family, variable, value, and bounds; the optimizer dialog checks
the selected variables again when the user unlocks a default-locked one. The
engine validates the active initial values and start points and returns
`OptimizationStatus.ERROR` without evaluating a clamped design. Locked
variables remain context and are exempt. The numerical span floor is 1 µm for
length/radius units and a smaller unit-relative floor for F, H, ratios, angles,
and counts. Tests cover Moxon 2.4 GHz, vertical 2.4 GHz, Yagi 5.8 GHz, the valid
Cebik 20 m Moxon, engine guards, the use case, and the UI message.

Implementation requirements:

- Add a shared descriptor validation helper or constructor check that rejects
  an initial value outside its variable bounds, a non-finite value, or a
  degenerate span.
- Surface the failure through the existing optimizer availability/error path
  with the family, variable, current value, and bounds. The UI must show it
  before starting a solver run.
- Change `optimize_design()` so the first candidate is the actual current
  design. If an active variable is outside bounds, do not clamp it; fail the
  run with a clear status/message.
- Preserve the existing behavior for intentionally locked variables: locked
  variables are context and must remain at their initial values.
- Add tests that would fail on the old code for Moxon 2.4 GHz, vertical
  2.4 GHz, and Yagi 5.8 GHz, plus a valid HF case that still converges.
- No solver or schema change.

### HF3 — Frequency-aware bounds across families

**Implemented 2026-11-18.** The shared `around()` keeps the interval relative to
the current value; `_length()` defaults to a 1 µm numerical floor and computes
its step from the search span. Practical 0.1/0.5/0.05 m floors were removed from
the descriptors. Gaps, spacings, tips, and discone dimensions use a
conductor-clearance floor; heights/base planes use zero; the end-fed
feed-section structure and the biquad small-feature minima remain. A matrix at
1.8/14/144/2400/5800 MHz covers every supported optimizer family and verifies
that initial values stay inside their bounds and that steps do not exceed the
span. Genuine physical-floor
violations still return the HF2 unavailable reason; no family-specific
frequency envelope was invented without evidence.

At minimum:

- `_length()` and `around()` gain an explicit, tested policy for a physical
  floor versus a search interval.
- Every `OptimizationVariable` length uses relative bounds or a λ-scaled
  floor; steps are also normalized where they are exposed in the UI.
- Families with a published normalized design (Yagi, Moxon, quad, hexbeam,
  discone, vertical, J-pole, Ringo) derive their search ranges from the
  design's normalized dimensions and the current frequency.
- Families that are not meaningful at a frequency return an explicit
  unavailable reason rather than a clamped search range. The decision is
  recorded in HF1; do not invent frequency envelopes without evidence.
- The biquad remains the reference for small-feature minima; do not regress
  its 0.01 m/0.001 m behavior.
- Cover all registry families in the matrix; a family is not exempt because
  it is usually HF-only. If it remains available at 2.4 GHz, it must either
  produce a sane bound set or explicitly say it is unsupported.
- No schema change.

### HF4 — Moxon geometry and optimizer contract

**Implemented 2026-11-18.** The shared validator is
`validate_moxon_geometry()` in `domain/antennas/moxon.py`. The optimizer now
uses `width_m`, `depth_m`, `gap_m`, `reflector_tip_m`, `height_m`, and the
conductor radius; the driven tip is derived. The geometry envelope is:

- gap/λ 0.004–0.10;
- gap/depth 0.03–0.40;
- gap/width 0.01–0.15;
- width/depth 1.5–4.5;
- reflector-tip/depth and driven-tip/depth 0.20–0.75;
- tip-sum/depth 0.50–0.97;
- gap greater than one conductor diameter.

These are construction-validity limits anchored to the Cebik 20 m reference
(gap/λ 0.0104, gap/depth 0.075, gap/width 0.029) and the exploratory 2.4 GHz
control (gap/λ 0.039, gap/depth 0.282, gap/width 0.108). They are not
performance values and do not encode the control's 4.86 mm gap. The domain
constructor, optimizer validation, and editor warning share the same function;
a 0.67λ gap is rejected before optimization. The estimator scales the Cebik gap
directly; HF6 adds a radius-aware two-diameter starting clearance and a
high-frequency confidence/tolerance policy, so an unbuildable thin-wire gap is
reported explicitly rather than silently changing the wire radius.

Requirements:

- Make the gap a first-class part of the Moxon optimizer contract. Either
  expose `gap_m` directly and derive the tips, or keep the current fields but
  enforce a documented relationship so the optimizer cannot independently
  move two redundant tip lengths into an implausible geometry.
- Add a shared Moxon geometry validator used by the domain, descriptor, and
  UI. It must check:
  - `gap_m > 0` (existing);
  - a documented minimum clearance relative to `wire_radius_m`;
  - a documented gap/λ range;
  - documented width/depth and tip/depth proportions;
  - the published 14.17 MHz reference dimensions still pass exactly.
- Do not hard-code the exploratory 4.86 mm or 7.27 mm values. The limits must
  be justified by the reference geometry, the thin-wire model, or a traceable
  source, and the ADR must state the evidence level.
- Ensure a 0.67 λ gap is rejected or reported as an invalid Moxon, not
  silently optimized.
- Add tests at 14.17 MHz (exact reference), 28.5 MHz, 144 MHz, 435 MHz,
  1.5 GHz, and 2.4 GHz. The high-frequency tests assert invariants and
  completion, not an invented performance target.
- No schema migration unless a new persisted field is unavoidable; prefer
  keeping the current `MoxonParameters` fields and changing only the
  optimizer variables/validation.

### HF5 — Yagi wavelength-relative bounds

**Implemented 2026-11-18.** The descriptor already used relative bounds after
HF3; HF5 removes the last absolute 0.05 m element floor and adds the missing
high-element-count QA. Element lengths, inter-element gaps, height, folded
spacing, and beta-hairpin dimensions are relative to the current scaled design;
conductor-spacing minima use the actual element radius. A 15-case matrix covers
5/10/15/20/32 elements at 1.5/2.4/5.8 GHz and asserts initial-in-bounds, the
DL6WU length/gap taper constraints, span-normalized steps, and exact rebuild.
Real NEC2C smoke runs cover 2.4 GHz 15/32 elements and 5.8 GHz 5/15 elements;
they assert completion, finite R/X, and no error, not a published gain.

Requirements:

- Remove the absolute 0.05 m element-length floor and the 0.01 m search
  steps from the Yagi descriptor; derive element/gap/height bounds from the
  current normalized design and λ.
- Keep the existing director length/gap taper constraints and the minimum
  conductor spacing; make the minimum spacing relative to the actual radius.
- Verify the DL6WU starting design for 5, 10, 15, 20, and 32 elements at
  1.5, 2.4, and 5.8 GHz: every initial value is inside its bounds, the taper
  constraints still pass, and the initial design rebuilds exactly.
- Add real NEC2C smoke coverage for 2.4 GHz 15/32 elements and 5.8 GHz 5/15
  elements. The test asserts completion, finite R/X, and no error; it does
  not claim a published gain.
- Check folded and beta/hairpin variables at high frequency; their minima
  remain tied to the conductor radius.
- No solver or schema change.

### HF6 — Moxon high-frequency estimator

**Implemented 2026-11-18.** The Cebik 20 m reference is reference-scaled only
inside the 20 m amateur band (14.0–14.35 MHz). Outside that band the estimate is
`Confidence.HEURISTIC`, carries `estimator.assumption.moxon_extrapolation`, and
emits `estimator.warning.moxon_high_frequency`. Its tolerance is
`max(5% width, gap)`, so it is never smaller than the gap. The wire radius is
not scaled; the starting gap must clear two conductor diameters or the estimate
is explicitly unsupported. The 14.17 MHz reference remains exact, the 28.5 MHz
editor default remains heuristic, and no high-frequency published reference was
invented.

Requirements:

- State the validated range of the Cebik 20 m linear scaling in
  `ANTENNA_DESIGN_ESTIMATORS.md` and the ADR. If no independent source exists
  for 1.5/2.4 GHz, the result is a heuristic, not a reference-scaled design.
- Make the starting geometry radius-aware. At minimum, detect when the scaled
  gap is smaller than a documented multiple of the wire diameter and either
  raise `UnsupportedEstimateError` or return a clearly labelled experimental
  estimate with a starting gap adjustment derived from a documented rule.
- Do not leave `REFERENCE_SCALED` confidence and a tolerance smaller than the
  gap for an extrapolation that is not validated. Downgrade confidence and
  make the tolerance meaningful.
- Add a strong EN/ES warning that the wire radius is not scaled and that the
  high-frequency Moxon needs independent verification; explain the
  construction implication when the gap is comparable to the conductor
  diameter.
- Keep 14.17 MHz exact and keep the 28.5 MHz editor default a documented
  heuristic.
- Do not invent a 2.4 GHz published reference. If a traceable source or
  measurement is added later, record it separately.

### HF7 — Thin-wire model-quality gate

Requirements:

- Define a shared quality policy for segment length versus wire radius,
  Moxon tip/gap resolution, and the extended thin-wire kernel.
- Expose the extended kernel in the simulation UI or select it
  automatically for families/frequencies where the default thin-wire kernel
  is outside its stated range. Record the chosen behavior and its effect.
- Make the optimizer treat model-quality failures as infeasible or as a
  blocking warning; do not silently optimize a model with
  `segmentation.radius_ratio_low` or `segment_too_short` when that invalidates
  the objective.
- Refine the Moxon tip/gap region or document why the current segmentation is
  sufficient. The 2.4 GHz Moxon tip segments are currently shorter than the
  gap and have a segment/radius ratio below 8.
- Test 1.5/2.4 GHz Moxon and 2.4/5.8 GHz Yagi with and without the extended
  kernel; assert deterministic completion and record the impedance change.
- No universal numerical accuracy claim; use convergence and invariant checks.

### HF8 — Diagnostics, defaults, and Apply Best

Requirements:

- Set `recommends_bound_hits=True` for Moxon, Yagi, and the other families
  where a bound hit is actionable, or make the recommendation universal.
  The current Moxon result sits at the width/depth bounds without a warning.
- Show the initial value, the optimizer value, and the bounds for every
  active variable; show the Moxon gap and gap/λ/gap-radius in the results and
  the optimizer table.
- Review the Moxon default objective. `MAX_GAIN` can select a poor match/F/B
  design even after the bounds are fixed. Record the decision; a
  multi-objective default or an F/B target with an SWR constraint are the
  candidate options. Do not change the Yagi default without the same review.
- Block or require confirmation for **Apply Best** when the selected design
  violates the Moxon geometry contract or has a critical model-quality
  warning.
- Do not present `converged` as a physical-validity claim. Pair the status
  with the geometry contract, bound-hit diagnostics, model-quality result, and
  high-SWR recommendation; a converged search can still be an unusable
  antenna.
- Use `DisplayUnits(AUTO)` in the family optimization dialog and pass it from
  `MainWindow`; the table must not hide sub-centimetre values in fixed meters.
- Add EN/ES help for every new warning/field and update the help coverage
  manifest.
- UI tests cover the warning, the bound table, the apply guard, and the
  adaptive units.

### HF9 — Regression matrix, evidence, and documentation

Required matrix:

- Frequencies: 1.8, 3.5, 7, 14, 28, 50, 144, 435, 1296, 2400, and 5800 MHz.
- Families: every optimizer registry type, with priority on Moxon, Yagi,
  vertical, dipole, folded dipole, inverted V, J-pole, Ringo, quad beam,
  discone, hexbeam, and biquad.
- Assertions:
  - every initial value is within its variable bounds;
  - no variable span is degenerate;
  - `build_parameters(initial_values)` reproduces the current parameters;
  - `validate(initial_values)` is empty for valid designs;
  - the optimizer does not silently change the initial design;
  - a real NEC2C run completes for the high-frequency priority cases;
  - Moxon gap/λ and gap/radius are inside the documented contract;
  - Yagi lengths/λ and gaps/radius are inside the documented contract.

Add an old-behavior regression that fails on the current code: at 2.4 GHz,
the Moxon initial width/depth must be inside their bounds and the optimizer
must not return a gap of 0.67 λ. The test must not depend on an invented
performance reference; it asserts the bound and geometry invariants.

Documentation:

- ADR-0046 and the estimator guide record the bound contract, the Moxon
  high-frequency validity, the thin-wire policy, and the confidence downgrade.
- The user guide explains why a high-frequency Moxon/Yagi may be marked
  experimental or unsupported, and how to rebuild a valid starting design.
- `CHANGELOG.md` records the behavior change when the implementation lands.
- Do not promote evidence levels or claim measured accuracy without a
  traceable source.

### HF10 — Design-frequency/geometry consistency

- Reconcile the Moxon manual **Load 20 m reference scaled to current
  frequency** action and the Yagi auto-scale exception with ADR-0043.
- If a design is grossly inconsistent with its design frequency (for example,
  a 20 m Moxon optimized at 2.4 GHz), show a warning and offer the explicit
  starting-dimension action; do not silently rescale tuned geometry.
- Consider an optimizer preflight check that compares the primary dimensions
  with λ and reports a clear “geometry and design frequency disagree”
  message.
- Test frequency changes, preset loads, pristine/edited states, and optimizer
  availability.

### File plan

- `src/antennadesk/domain/optimization/families/common.py`
- `src/antennadesk/domain/optimization/families/typed.py`
- `src/antennadesk/domain/optimization/families/yagi.py`
- `src/antennadesk/domain/optimization/families/dipole.py`
- `src/antennadesk/domain/optimization/families/vertical.py`
- `src/antennadesk/domain/optimization/families/scv.py`
- `src/antennadesk/domain/optimization/descriptor.py`
- `src/antennadesk/domain/optimization/registry.py`
- `src/antennadesk/domain/optimization/engine.py`
- `src/antennadesk/application/use_cases/optimize_antenna.py`
- `src/antennadesk/domain/antennas/moxon.py`
- `src/antennadesk/domain/design/estimators.py`
- `src/antennadesk/domain/simulation/segmentation.py`
- `src/antennadesk/simulation/discretization.py`
- `src/antennadesk/domain/simulation/spec.py`
- `src/antennadesk/ui/dialogs/family_optimization_dialog.py`
- `src/antennadesk/ui/main_window.py`
- `src/antennadesk/ui/i18n.py`
- `tests/unit/optimization/`, `tests/integration/simulation/`, `tests/ui/`
- `docs/ADR/0046-frequency-aware-optimizer-bounds.md`
- `docs/ANTENNA_DESIGN_ESTIMATORS.md`, `docs/USER_GUIDE.md`,
  `docs/VALIDATION_PLAN.md` (only if evidence changes), `CHANGELOG.md`

### Acceptance for the track

- HF1’s ADR is accepted and linked from the queue.
- Every descriptor passes the initial-in-bounds and non-degenerate-span
  invariants across the frequency matrix; no silent clamp remains.
- A 2.4 GHz Moxon no longer produces a 0.67 λ gap; its gap is inside the
  documented contract and the optimizer can explore a physically plausible
  design.
- Yagi 15/32 elements at 2.4 GHz and 5/32 elements at 5.8 GHz start inside
  bounds and complete a real NEC2C run.
- Other families either have sane bounds at 2.4 GHz or an explicit
  unsupported reason; no family silently evaluates a clamped design.
- Model-quality warnings are either resolved or block the optimizer.
- The optimizer UI shows bounds, gap ratios, and bound-hit diagnostics; Apply
  Best cannot silently accept a geometrically invalid design.
- The full gate passes: `ruff check`, `ruff format --check`, both `mypy`
  passes, and `NEC2C=... pytest`.

### Out of scope

- New antenna families or new solver engines.
- A universal frequency envelope without evidence.
- Inventing high-frequency Moxon/Yagi reference values.
- Automatic scaling of tuned geometry; ADR-0043 remains the policy.
- Multi-band Moxon/Yagi optimization.
- Matching-network optimization.
- Claiming measurement-grade accuracy for 1.5/2.4/5.8 GHz results.

### Risks and mitigations

- **Removing construction floors makes HF designs unbuildable.** Keep a
  separate physical floor and test HF construction values; do not equate
  “search bound” with “buildable minimum”.
- **Changing Moxon parameterization could break persistence.** Prefer the
  existing fields and change only optimizer variables/validation; if a new
  field is unavoidable, add schema migration and round-trip tests.
- **The extended kernel changes results.** Treat it as a modeling decision
  with regression and convergence evidence; do not enable it silently without
  documenting the effect.
- **Many families are affected.** Migrate incrementally, but do not close the
  track until every registry family passes the matrix or has an explicit
  unsupported reason.
- **The exploratory control is not a reference.** Do not turn 4.86 mm,
  7.27 mm, or 25 dB into golden values without a traceable source.

## HexBeam follow-ups (C6/C7 complete 2026-11-18)

C6 and C7 are complete. The former single-band model derived each tip from the
published wire half-length and placed it outside the 130 in frame, producing a
9.03 m span on a 3.30 m turning radius and a 0.67 m drawn tip gap against the
published 0.61 m. The corrected model has a 6.604 m span, a 0.6096 m tip gap,
and every wire point inside the 3.302 m turning radius. C7 adds the published
20/17/15/12/10 preset, editor, nested scene, reports, and NEC2C coverage.

### C6 acceptance (implemented 2026-11-18)

- Driver: two halves from the center feed to the front-side spreaders, then
  along the hexagon sides to the lateral tips; M shape.
- Reflector: one continuous wire around the rear three sides, with its
  midpoint at the rear; U shape.
- Ten canonical wires: feed, four driver segments, and five reflector segments
  (left/right tip, left/right inner, and the full rear side).
- Tip spacer: 24 in between the driver tip and reflector end, on the side.
- Every wire point is at or inside the turning radius; overall span is 2R
  (~6.60 m).
- `total_conductor_length_m` stays `2·(Ld + Lr) + feed_gap` and matches the sum
  of the canonical wire lengths within 1 mm; the invariant is tested.
- The published `element_separation_m` defaults to zero and is applied only as a
  reflector fore-aft trim; it is not a center-to-center spacing.
- Domain and optimizer feasibility checks share one frame helper; the old
  `driver_half > 1.5R` and reflector lower-bound rules are removed.
- Adaptive-unit tests cover both the legacy fixed-metric scene and
  `DisplayUnits` automatic; the 435 MHz drawn gap changes from 2.18 cm to
  1.99 cm.
- C6 keeps the current 219/207/24/130 constants; a parameterized test covers
  both that row and the G3TXQ 218/412/24/130 row. C7 reconciles the five-band
  20 m row.
- Plan dimensions, notes, construction sheet, design summary, and evidence
  agree with the geometry; no "published vs drawn gap" mismatch.
- Tests assert the frame-fit invariant, reflector rear midpoint, exact tip gap,
  and span; the golden scene is updated deliberately.
- Docs/help that describe the W/U or 60-degree ray are corrected. The C2
  family/editor/report scaffolding remains valid.

The detailed reconstruction, source reconciliation, and file-level test matrix
are in [`spikes/c6-hexbeam-geometry.md`](spikes/c6-hexbeam-geometry.md). C6 and
C7 are closed; the optional C7d-C7i follow-ups are tracked there, with C7d,
C7e, C7f, and C7g implemented.

### C7 acceptance (implemented 2026-11-18)

- `HexbeamParameters` carries a shared frame plus 1-5 per-band records; schema
  migration maps an existing single-band design to one band.
- An ADR records the shared-frame/band model, the per-band feed approximation,
  and the selected-band optimizer scope.
- The standard preset is the published G3TXQ 20/17/15/12/10 table with its
  vertical offsets; no invented per-band values. C7b reconciled the single and
  multi-band 20 m row to 218/412/24/130 and updated the reference library,
  evidence, tests, and docs together.
- The editor derives the band count from the selected set; it does not infer an
  arbitrary prefix of the published table. It exposes **Load starting
  dimensions** and an editable per-band table. Published checkboxes seed the
  rows; custom labels, frequencies, and dimensions are allowed in the same
  row order, and the report marks the band set as published, reference-scaled,
  or custom.
- Scene draws all bands on the shared frame. C7e adds a transient active-band
  selector: the selected band's dimensions, feed marker, summary, and detail
  inset are shown, its wires are emphasized, and the other bands stay visible.
  Reports and the construction sheet include per-band rows.
- Feed model is explicit. One selected band is driven per analysis and the
  other bands are passive; the real coax harness, coupling, and balun are
  limitations.
- NEC2C integration covers one driven band at a time. Full multi-band
  optimization remains unavailable with a reason; C7d adds a selected-band
  optimizer that leaves the shared frame and the other bands fixed.
- Evidence stays B for published starting dimensions; performance is not
  claimed. Update `VALIDATION_PLAN.md`, `EVIDENCE_AUDIT.md`, user guide, and
  `CHANGELOG.md`.

### C7 implementation notes

C7a is implemented on 2026-11-18: [ADR-0045](ADR/0045-multiband-hexbeam.md)
records the shared-frame model, per-band radius, one-driven-band feed, schema
55, and optimizer/scaling limits. The domain accepts 1-5 bands, builds ten wires per
band, derives each band's nested radius from the largest band, and exposes
explicit unavailable reasons for multi-band optimization and frequency scaling.

C7b is implemented on 2026-11-18: the published 20/17/15/12/10 preset, the
218/412 single-band reconciliation, band checkboxes, a read-only per-band table,
nested scene rendering with primary-band emphasis, per-band report rows, and
EN/ES help.

C7c is implemented on 2026-11-18: multi-band optimization remains explicitly
unavailable, the feed-harness/inter-band-coupling/balun limitation is visible
in help/evidence/reports, and real NEC2C 20/15/10 m runs completed with one
driven band per analysis and positive input resistance. C7 is complete.

Post-C7 fix on 2026-11-18: **Analyze Bands** now defaults to the bands selected
in the design and passes a band-specific one-source model per analysis; this
removes the negative input resistance and "Simulation failed" results at 15
and 10 m. **Estimate Dimensions...** is enabled with a single-band
reference-scaled starting design.

C7d is implemented on 2026-11-18: **Optimize** targets the active band of a
multi-band HexBeam. The descriptor varies only that band's driver/reflector
halves, tip gap, and height; the shared turning radius, conductor, and the
other bands stay fixed. Validation checks the band's nested frame, conductor
spacing, and adjacent-radius clearance. Each candidate excites the selected
band and is evaluated at its frequency, and the dialog shows the target band.
Full multi-band optimization remains explicitly unavailable.

C7f is implemented on 2026-11-18: the band table is editable and is the source
of truth. Published checkboxes only seed rows. Rows can be added or removed
within 1–5, labels and frequencies can be custom, and untouched cells keep
their exact canonical values. Rows must be ordered from lowest to highest
frequency; the editor and reports mark custom sets, and replacing them with a
published preset requires confirmation.

### Optional HexBeam follow-ups (queued 2026-11-18)

- **C7d — selected-band optimizer — implemented.** Optimize one band at a time
  with the shared frame and the other bands fixed; full-stack optimization is
  not exposed.
- **C7e — active-band dimensions and scene highlight — implemented.** A
  transient selector chooses the band whose cotas and feed marker are shown;
  its wires are emphasized and the other bands remain visible. Not persisted.
- **C7f — editable per-band table and custom band sets — implemented.** Rows
  are editable, can be added/removed, and carry custom labels/frequencies with
  explicit validation and custom-set provenance.
- **C7g — band-aware starting set / whole-stack scaling — implemented.**
  A frequency-first multiband start is possible only as a *scaled reference
  stack*, not as a new optimized design. The editor's primary-frequency field
  now scales the selected published set uniformly within the primary band and
  shows a reference-scaled warning. **Estimate Dimensions** remains a
  single-band helper; no general multiband estimator is provided.
- **C7h — optional 6 m band.** Add the published 6 m row when a source-backed
  row is carried through the same frame-fit tests.
- **C7i — feed harness and inter-band coupling.** Blocked until a traceable
  harness model or measurement exists; the current one-driven-band model keeps
  the other bands passive.

## Adaptive length display units (queued 2026-11-17)

**Status:** spec closed; implementation started. U0–U5 are complete; U6
documentation/help is complete and the manual visual checklist remains. The release plan decides whether the track lands in 0.10.0 or a later
release.
**Decision:** [ADR-0044](ADR/0044-adaptive-length-display-units.md).
**Normative spec:** [`DISPLAY_UNITS_SPEC.md`](DISPLAY_UNITS_SPEC.md).

The current metric display uses meters for every length and millimeters for
wire diameters. That is readable for HF but poor for VHF/UHF construction: a
435 MHz Moxon gap shows `0.007 m`, and its 24.8 cm width rounds to `0.25 m`.
Imperial has the same problem with `0.023 ft`. The fix is a presentation-only
automatic policy, never a frequency-based or global-centimeter switch.

The policy is:

- Metric auto: mm below 1 cm, cm from 1 cm to below 1 m, m at 1 m and above.
- Imperial auto: in below 1 ft, ft at 1 ft and above.
- Scalar fields and dimension labels choose by value; editable and report
  tables choose one unit per table from the largest value and show it in the
  header.
- mm/cm use two decimals, m/ft use three, inches use two. Labels trim trailing
  zeros. Spin boxes keep fixed decimals.
- A field or table unit is frozen while editing and re-evaluated on model,
  preset, optimizer, undo/redo, or preference reload.
- Human-readable construction sheets and reports follow the policy. CSV stays
  canonical meters/mm. DXF stays canonical meters with `$INSUNITS=6` and
  meter dimension text.
- The Units preference keeps an escape hatch: metric auto (default), metric
  fixed in meters, imperial auto (default), and imperial fixed in feet.

Non-goals: per-project units, decimal-separator changes, inch fractions,
automatic radius/diameter units, DXF scaling, and any solver, domain, or schema
change.

### U1 acceptance

- `DisplayUnits`/`LengthPolicy` is a pure, Qt-free formatter with automatic and
  fixed metric/imperial policies, boundary tests, zero/negative handling,
  trimming, and table-unit selection.
- The Units preference stores the system and policy, maps existing
  `metric`/`imperial` values to automatic, and has EN/ES help.
- No scene, form, or report changes yet; the full existing gate stays green.

### U2 acceptance

- `build_scene` and `_Factory` accept `DisplayUnits`; dimension labels,
  summaries, scale bar, and insets use it.
- 28.5/144/435 MHz Moxon, 20 m dipole, and 435 MHz hexbeam scenes cover the
  automatic examples in the spec.
- The scale bar uses unit-aware candidate steps; the minimum-size layout and
  hidden-dimension strip still work; the small-dimension anchor tolerance is
  tightened.
- Existing fixed-unit tests and goldens remain stable; new auto tests are
  focused rather than regenerating every golden.

### U3 acceptance

- Every antenna-family editor uses `LengthFieldSpec` for range, step, decimals,
  suffix, and optional scale hint; no small feature inherits the global
  `0.1 m` minimum.
- Editable tables use one unit per table with the unit in the header; radius
  columns stay mm/in.
- Moxon height no longer inherits Qt's `99.99` maximum; 435 MHz hexbeam
  tip/feed gaps and element separation can be represented.
- Metric/imperial and auto/fixed switches preserve every physical value; field
  suffixes do not change mid-edit.

### U4 acceptance

- Optimization, family optimization, synthesis, parameter sweep, robustness,
  tolerance, design-from-frequency, feed-line, and related dialogs use the same
  policy.
- Every `length_bounds` caller is audited; per-field ranges replace global
  small-feature minimums.
- Plot axes, budgets, and table headers remain legible; EN/ES help covers the
  new unit presentation.

### U5 acceptance

- Construction-sheet design summary, wire schedule, BOM, feed/matching rows,
  and report tables use `DisplayUnits`; the title block states
  `Metric auto (mm/cm/m)` or the selected fixed/imperial policy.
- SVG/PNG/PDF figures follow the UI; CSV remains canonical meters/mm; DXF
  remains canonical meters with `$INSUNITS=6` and meter dimension text.
- HTML, native PDF, package, and CSV/DXF tests cover both automatic and fixed
  policies.

### U6 acceptance

- User guide and `CHANGELOG.md` describe the automatic policy, the fixed
  escape hatch, and the CSV/DXF canonical exception.
- EN/ES help coverage includes the Units preference and unit-bearing table
  headers.
- Light/dark and font-scaling QA covers the sketch, forms, and construction
  sheet; the full gate is green.

### Dependencies and order

U1 is the foundation. U2 and U3 may proceed in parallel after U1. U4 depends on
U3 because it shares the form helpers. U5 depends on U2 and U3 because it
embeds scenes and report rows. U6 closes the track after U2–U5.

Do not start any slice by adding a global current-units singleton, a
`UnitSystem.CM` value, frequency-based selection, or a per-cell table unit.
Those alternatives are rejected in ADR-0044.

## Product experience queue (2026-11-11)

UX1–UX17 are complete. The 0.5 **Decide**, 0.6 **Build**, 0.7 **Measure**, and
0.8 **Explore** releases are closed. UX18–UX20 and UX21–UX24 were implemented on
2026-11-12; the 0.9 **Sustain** slice is complete. UX32–UX38, the
frequency-first starting-dimensions, semantics, pristine-recalculation,
quad-beam-estimator, scale-to-frequency, and creation-tab work, were completed
on 2026-11-17. The adaptive length display-units track (U0–U6) is now active;
U0 closed the spec and ADR, U1 added the formatter and preference, U2 wired the
geometry scenes, and U3 delivered the first small-feature range fixes. U3
remainder–U6 are the next implementation slices.
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
from impedance/SWR point-density feedback, and UX40 was queued the same day
from the 3D-report request. Both are open UX items.
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
[`MATERIALS_REFERENCE.md`](MATERIALS_REFERENCE.md). The candidate table below is
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
  `PROJECT_DECISIONS.md`; do not create an ADR for a default selector.

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
preservation, EN/ES help, and tests are in place. UX33–UX37 remain queued.

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
requested frequency and expose the shared action. UX34–UX37 remain queued.

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
[ADR-0043](ADR/0043-design-versus-analysis-frequency.md). No code or behavior
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
resizing after a managed edit. UX36–UX37 remain queued.

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

**Status:** queued. The feasibility analysis is recorded here; no code or
schema change has been made.

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

- [ ] A table-driven UI test over the generated templates asserts
      `frequency_plan.count >= 100` for every enabled sweep. Cover at least the
      T2FD, vertical, Yagi, end-fed, beverage, loaded-dipole, and two-band
      builders; exclude single-frequency custom mode by design.
- [ ] The Auto (template) view and the Points spin box show 100 for generated
      templates; **Custom** still overrides, and a single-frequency custom plan
      remains count 1.
- [ ] Impedance and SWR charts contain one plotted point per computed
      frequency, the table has one row per frequency, and no interpolation is
      introduced.
- [ ] At 100 points the chart line uses all points; the marker layer is
      bounded and the plot is legible at the minimum supported window width.
      The cursor still snaps to each computed point.
- [ ] A 100-point NEC2C smoke run of a representative generated design
      completes within the 180 s default and returns 100 results; record the
      wall time and keep the test solver-marked.
- [ ] Project save/load round-trips a 100-point result; record the estimated
      compressed size and confirm it stays below the warning threshold for the
      tested models.
- [ ] Update the tests that currently assert 31:
      `tests/ui/test_main_window_presets.py` (T2FD) and
      `tests/ui/test_main_window_simulation.py` (vertical and generated-spec
      fixtures). Rename the "performance-safe defaults" test if the wording no
      longer describes the policy.
- [ ] Update `docs/USER_GUIDE.md`, `docs/VALIDATION_PLAN.md`,
      `docs/MULTIBAND_ANALYSIS_PLAN.md`, and `CHANGELOG.md`. Add a new
      changelog entry; do not rewrite historical release entries.
- [ ] Run the full gate: `ruff check`, `ruff format --check`, both `mypy`
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

## UX40 — Static 3D far-field lobe in the HTML/PDF reports (queue note, 2026-11-18)

**Status:** queued. The feasibility analysis is recorded here; no code or
schema change has been made.

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

- [ ] A new `tests/unit/reporting/test_pattern_lobe.py` uses a regular synthetic
      grid and asserts that the SVG contains the wireframe paths, legend,
      maximum-gain marker, title/description, and ground ring as applicable.
- [ ] Repeated rendering of the same snapshot and language is byte-identical.
- [ ] Free-space and ground patterns both render; the ground ring is absent in
      free space.
- [ ] Missing or non-finite gains do not produce NaN coordinates; a single-cut
      pattern returns the explicit unavailable reason and no SVG.
- [ ] The displayed mesh respects the 19×37 vertex cap and a documented
      segment/path-size bound; stored points are not mutated.
- [ ] HTML tests assert exactly one 3D figure in the primary section, none per
      band, and the localized reason for far-field-disabled and single-cut
      results.
- [ ] The native PDF test confirms the figure is included and adds no new
      `/Subtype /Image` object; the existing vector assertion still passes.
- [ ] Every new static report label is in `REPORT_SPANISH`; the placeholder
      parity and static-label coverage tests pass.
- [ ] A manual A4 light-theme/grayscale check confirms that the figure, legend,
      caption, and marker remain legible and do not overwhelm the two cuts.
- [ ] Update `docs/USER_GUIDE.md` (report contents), `docs/ARCHITECTURE.md`
      (report contents), `docs/VALIDATION_PLAN.md` (report checks), and
      `CHANGELOG.md`. Do not rewrite historical UX26 text; add the new
      decision and link this note.
- [ ] Run the full gate: `ruff check`, `ruff format --check`, both `mypy`
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

## EF1–EF9 — Shortened-EFHW optimizer and model-confidence queue (2026-11-13)

**EF1–EF6, EF7a, EF7b, EF8a, the bounded EF8 feedpoint choke model, and EF9
L/Pi/T matching are implemented.** Automatic L/Pi/T synthesis is available in
the project matching dialog and the design-specific end-fed action. The ordered
plan is:

| ID | Scope | Why it is separate |
|---|---|---|
| EF1 | Preserve model-defined wire partitions in optimizer candidates | Correctness fix; only shortened EFHW descriptors opt in |
| EF2 | Diagnose input-shunt matching-network topology limits | Explains the fixed-network SWR floor without changing results |
| EF3 | Warn about the installation-return proxy and SWR confidence | Visibility only; no numerical change |
| EF4 | Clarify objective semantics and expose best-SWR selection | Product/UI decision; other families keep their defaults |
| EF5 | Recommend action when an optimum hits a search bound | Optimizer guardrail gated by descriptor |
| EF6 | Investigate 40-10 convergence | Needs a segment/load-placement spike before changing the model |
| EF7a | Measured 49:1 transformer reactive preset | Implemented from Squash Practice measurements |
| EF7b | Measured transformer loss and frequency dependence | Implemented from the Squash Practice band-loss table |
| EF8a | User-selectable end-fed return path | Implemented; `auto` preserves legacy behavior |
| EF8 | Common-mode return / coax-shield model | Bounded feedpoint choke model implemented; shack-end/shield-transfer model remains deferred |
| EF9 | Design-specific matching-network optimization | L/Pi/T implemented with automatic synthesis and design Q |

### EF1 — Optimizer structural segmentation (implemented)

The optimizer recalculates candidate segmentation from the target frequency and
the base policy. That is correct for geometry, but it discarded `wire_segments`
entries that are part of the numerical model. In a shortened EFHW the fixed
0.5 m feed section and the 0.10 m loading-coil section must keep three segments
each; otherwise the lumped load lands on a different part of the wire and the
optimizer evaluates a different model from the one the user applies.

Implementation contract:

- `AntennaOptimizerDescriptor` has an optional `structural_segmentation`
  callback. The default is `None`, so every existing family follows the previous
  code path exactly.
- Only the shortened EFHW descriptors (`SHORTENED_80_10` and
  `SHORTENED_40_10`) set the callback. Standard end-fed, sloper, random wire, and
  every other family keep `None`.
- The callback returns the fixed partition counts from
  `endfed_segmentation_overrides()`; the optimizer merges them into the
  recalculated policy and leaves the radiator and other wires on the normal
  target-based counts.
- The merge validates that the wire exists in the candidate model. It lowers
  only the policy's validation minimum when a structural count is below it; all
  wire counts are explicit, so no other wire changes.
- `MAX_BANDWIDTH` sweeps also receive the structural partitions; `None` and
  empty overrides are a no-op.

Acceptance: the 80-10 and 40-10 candidate specs keep the feed and coil sections
at three segments; standard end-fed and a representative non-end-fed family
remain `None` and follow the old path; the full gate is green; no schema,
solver, or UI change. Because the optimizer no longer evaluates a different
mesh, its reported best SWR can shift slightly; the applied design is now the
same model the optimizer scored. Tests:
`tests/unit/application/test_optimize_endfed_segmentation.py`.

### EF2 — Matching-topology diagnostic (implemented)

The internal EFHW unit is an input-shunt L-section (100 pF) plus series leakage
(198 nH), with no output shunt. When the ideal transformer presents a load with
R above the source reference, that topology cannot match it even with ideal C/L.

Implementation contract:

- `MatchingNetworkOrigin` distinguishes `NONE`, `INTERNAL_ENDFED`, and
  `PROJECT` at runtime. It is set by the matching resolver and the end-fed spec
  builder; it is not persisted and is excluded from the model fingerprint.
- `input_shunt_l_network_swr_floor()` returns `R / source` only when the network
  is a two-element input-shunt L-section (or a Pi with no output shunt), the
  series and input-shunt branches are active, and `R > source`. Otherwise it
  returns `None`.
- `LinkBudget` carries the floor so normalization can emit
  `matching_network.topology_limit` with the expected value.
- The diagnostic is emitted only for `INTERNAL_ENDFED` and only when the
  project network is not overriding it. A project network or another family's
  spec never sees the new warning. The model fingerprint is unchanged.

Acceptance met: a shortened EFHW candidate with a high transformed load emits
the warning and its theoretical floor; the same design without the internal
origin emits no topology warning; domain, link, fingerprint, resolution, and
real NEC2C tests pass; EN/ES text is present.

### EF3 — Proxy return and confidence warnings (implemented)

When a shortened EFHW uses the 0.1 m installation-return proxy instead of a real
counterpoise, the editor now adds an explicit warning and the confidence card
marks absolute SWR as informational.

Implementation contract:

- `endfed_model_warning_keys()` adds `endfed.warning.return_proxy` only when
  `installation_return_active` and the preset is `SHORTENED_80_10` or
  `SHORTENED_40_10`.
- `design_evidence_rows()` adds a **Model confidence** row for the shortened
  presets. With the proxy active, it states that the installation return is not
  a physical counterpoise and the real coax/mast/earth path dominates SWR.
  Without the proxy, it states that SWR is informational and the preset is
  judged by R/X convergence.
- The row reaches the Diagnostics confidence card and HTML/PDF reports through
  the existing localized row path. EN/ES report text is present.
- No solver, impedance, SWR, gain, schema, or fingerprint change. Standard
  end-fed, sloper, random wire, and every other family are unchanged.

### EF4 — Objective clarity and best-SWR action (implemented)

`TARGET_IMPEDANCE` minimizes `|Z−50|`, not SWR. The shortened EFHW descriptors
now open in **Minimum SWR**; standard end-fed, sloper, random wire, and every
other family keep their previous default. The dialog shows a hint when the
selected objective candidate has a higher SWR than another feasible candidate,
and adds **Apply Best SWR** independent of the objective. The objective help
states the difference explicitly.

Implementation contract:

- `endfed_descriptor()` selects `MIN_SWR` only when the preset is
  `SHORTENED_80_10` or `SHORTENED_40_10`.
- The dialog selects the feasible candidate with the lowest `metrics["swr"]`,
  builds its parameters through the descriptor, and accepts it. It does not
  change the objective, scoring, or stored result.
- The hint compares the selected candidate's `best_metrics["swr"]` with the
  lowest feasible candidate and appears only when the difference exceeds 0.05.
- The new action has EN/ES text and accessible help.
- No solver, schema, fingerprint, or other-family default changes. A new
  `MIN_MISMATCH` objective based on `|Γ|` remains a separate ADR.

### EF5 — Bound-hit recommendation (implemented)

When the best candidate is at a continuous-variable bound, report it and add a
recommendation to widen the range only if the result is buildable.

Implementation contract:

- `variables_at_bounds()` reports unlocked continuous variables within 1 % of
  their search interval. Integer and choice variables are not reported.
- `AntennaOptimizerDescriptor.recommends_bound_hits` is opt-in and is set only
  by the shortened EFHW descriptors.
- `RecommendationContext.at_bounds` feeds the new
  `optimize.recommend.bound` warning; the dialog already maps variable names to
  localized labels.
- No automatic bound expansion. Other families produce the same recommendations
  as before.

### EF6 — 40-10 convergence investigation (implemented as a documented spike)

The 40-10 preset remains R/X-sensitive at 10/21/51 radiator segments. The spike
tested the two plausible model fixes:

| Coil-section change | 40-10 result | 80-10 result |
|---|---|---|
| 0.10 m, 1–5 segments | no meaningful improvement | — |
| 0.15 m, 3 segments | R spread 1.16 Ω, X spread 4.38 Ω | not tested |
| 0.20 m, 3 segments | R spread 0.71 Ω, X spread 2.85 Ω | not tested |
| 0.30 m, 3 segments | R spread 0.36 Ω, X spread 1.54 Ω | not tested |
| 0.50 m, 3 segments | R spread 0.13 Ω, X spread 0.63 Ω | R/X degrades strongly and does not converge |

A wider section makes 40-10 converge but changes the 80-10 model for the worse,
so there is no single section length that improves both presets. The section
length is a numerical partition, not a measured coil dimension; changing it to
pass the check would be tuning the mesh without a traceable reference. The
decision is therefore:

- keep the 0.10 m section and the R/X convergence policy;
- keep absolute SWR informational for 40-10;
- add a static editor warning `endfed.warning.convergence_40_10` for the
  40-10 preset;
- do not relax the convergence thresholds;
- leave any future model change to a measured transformer/coil reference.

The existing NEC2C integration test continues to assert that 80-10 converges and
40-10 does not. No solver, schema, or numerical change was made.

### EF7a–EF9 — Implemented / blocked

- **EF7a (implemented):** optional measured 49:1 transformer preset from
  Squash Practice's 2xFT114-43, 5T/30T build. It models 198 nH leakage,
  2.7 pF secondary winding capacitance, and 25.8 µH magnetizing inductance as a
  primary-referred shunt/series network. The preset is clearly labeled as a
  reference build, not the user's transformer; the external 100 pF capacitor
  remains separate. Schema 46 adds the persisted model selector.
- **EF7b:** measured transformer loss and frequency dependence. Implemented as
  an optional Squash Practice/AF7NX table at the 80/40/20/10 m band centers,
  with log-frequency interpolation, endpoint clamping, a 49:1 requirement, and
  a separate `transformer_loss_db` result field. KN5L's ~0.3 dB core-loss data
  corroborates the magnitude but was not used to add frequency points.
- **EF8:** common-mode return / coax-shield model. EF8a adds the selectable
  return path and a model-only coax-shield wire approximation; EF8 adds an
  optional measured feedpoint choke R/X as a NEC series load on the shield.
  ADR-0037 records the bounded model. Shack-end placement, frequency-interpolated
  `Zcm(f)`, shield transfer impedance, and absolute common-mode-current
  prediction still require a measurement or a validated model. Do not optimize
  the installation proxy as a physical radial.
- **EF9:** design-specific matching-network optimization. ADR-0038 proposes an
  optional design-specific L-network with precedence project > design-specific >
  internal. It needs schema 50, UI, optimizer variables, and regression
  coverage. Do not add loose C/L variables to the fixed input-shunt network.

### No-impact contract for EF1–EF6

The acceptance rule for every queued item is: **non-shortened end-fed and every
other family produce the same numerical results, diagnostics, and optimizer
defaults unless the item explicitly says otherwise.** New behavior is gated by a
descriptor capability, a preset, or a UI context. Before EF3 starts, capture a
golden matrix of R/X/SWR/gain/efficiency and fixed-seed optimizer results for
representative designs in every family; after each item, diff it. A change in a
non-target family is a regression, not an acceptable side effect.

## Matching-network precedence (2026-11-10 analysis)

G25 models the internal EFHW matching unit. The M queue defines how that model
coexists with the project-level matching network. The agreed policy is an
explicit **Override**, not a cascade:

| Project network | EFHW internal matching | Effective network | Override |
|---|---|---|---|
| none | active | EFHW internal | no |
| none | inactive | none | no |
| active | active | project network | **yes** |
| active | inactive | project network | no |

- The project matching network is global and applies to every design.
- On `EndFedParameters` with `matching_network_active`, it replaces the
  internal matching capacitor and transformer-leakage model. The ideal
  transformer ratio still applies.
- The internal values remain in the design and project file; they are simply
  not applied while the project network exists. Removing the project network
  restores them.
- No cascade of two matching networks is modeled in this stage. This is a
  documented limitation, not a hidden approximation.
- `override_active` is derived from the project network and the design; it is
  not a persisted flag.
- A single resolver must feed every path: simulation, band analysis, family
  optimization, synthesis, the EFHW convergence check, reports, and the UI.
- Before M1, several paths replaced `spec.matching_network` unconditionally, so
  a `None` project network could silently drop the internal EFHW network. M1
  removed that behavior by routing every path through the resolver.

## Progress feedback (2026-11-10 analysis)

The progress-feedback queue follows these rules:

- Use a **determinate** bar only when the unit is real: bands for band
  analysis, evaluations for optimizers. Use an **indeterminate** bar plus
  elapsed time and phase text for a single solver run.
- Estimated optimizers use an upper-bound denominator. The bar must be
  monotonic, must not stick when the engine converges early, and must reach
  100% on finish. Label the value as estimated.
- Do not mix units: `OptimizeAntenna` progress counts evaluations, while the
  dialog budget hint estimates solver runs (evaluations × frequency points ×
  scenarios × seeds). Show evaluations or add a weighted callback before
  showing solver runs.
- The domain and application layers emit plain callbacks; Qt workers
  translate them into signals. Never touch widgets from a worker thread.
- Throttle updates (about 10 Hz or 1% steps) for large budgets and parallel
  workers.
- Keep every user-visible string in `ui/i18n.py` with English and Spanish in
  sync.
- Do not fake a percentage from `timeout_s`, elapsed time, or a fixed
  estimate. If a true per-frequency percentage is required, implement P7
  behind an ADR and benchmark.

## Deferred product work

The 2026-11-04 phase plan is archived. Its open items were reviewed during the
2026-11-09 consolidation. The following are intentionally not in the active
queue because they need a different model, a traceable source, or a product
decision:

| Item | Why it is not active | Tracked in |
|---|---|---|
| Fan-dipole angle optimization and an explicit per-element feed model | Needs a different antenna model, not another scalar correction | [`ROADMAP.md`](ROADMAP.md), [`FAN_DIPOLE_CALIBRATION.md`](FAN_DIPOLE_CALIBRATION.md) |
| Measured or optimized 20/10 m fan-dipole preset | Needs a traceable source or measurement | [`ROADMAP.md`](ROADMAP.md) |
| Gamma match for the Yagi | NEC-2 is unreliable for close-spaced gamma assemblies; the beta/hairpin match is implemented | [`ROADMAP.md`](ROADMAP.md) item 6 |
| Boom-mounting correction | No universal published model; boom mounting is explicitly not modeled | [`ROADMAP.md`](ROADMAP.md) item 14, [`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md) |
| Report-specific metric selection for power, directivity, and realized gain | The UI selector exists; export-specific selection is optional | [`ROADMAP.md`](ROADMAP.md) |
| General radial-screen and transmission-line geometry beyond the current subset | Architectural change with a larger test surface | [`ROADMAP.md`](ROADMAP.md), [`PROJECT_DECISIONS.md`](PROJECT_DECISIONS.md) |
| Custom/imported geometry optimization | Deliberately unavailable because arbitrary geometry has no parameterized topology | [`ADR/0026-family-optimizer-architecture.md`](ADR/0026-family-optimizer-architecture.md) |
| Physical antenna validation | Blocked on measurements; tracked as B4 above | [`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md) |
| Segmented frequency plan in one NEC deck | Closed by ADR-0042; per-band batching retained | [`MULTIBAND_PERFORMANCE.md`](MULTIBAND_PERFORMANCE.md), [ADR-0042](ADR/0042-per-band-frequency-plan.md) |
| True per-frequency simulation progress | Needs an ADR and benchmark to choose between chunked execution and incremental parsing; not justified until simulations are long enough | P7 above, D4 above |
| Live VNA control, additional full-wave engines, and release signing | Need hardware, an engine decision, or release credentials | D1–D3 above, [`ROADMAP.md`](ROADMAP.md) |

## Solver runtime notes (2026-11-08)

The 60 s default was measured against a four-element phased vertical array,
31-point sweep, five pattern snapshots, finite ground:

| Case | Wires | Segments | Wall time |
|---|---:|---:|---:|
| 4 verticals × 4 radials | 20 | 122 | 0.46 s |
| 4 verticals × 36 radials | 148 | 890 | 25.3 s |

The 36-radial case also returned `partial` with negative input resistance and
an absorbing-source warning. Raising the timeout is not a fix for that
numerical result; E4 must diagnose it separately.

E4 found that the quarter-wave radial screens overlap: the 4×36 case had 267
wire crossings. Halving the radial length, or using 2 m radials, removed the
crossings and completed. Doubling the spacing without changing the radial
length also removed crossings, but some frequencies still showed a negative
primary resistance because ideal phase sources can exchange power between
ports. The phased-vertical editor now warns about overlapping screens; the
ideal-source behavior is documented and exposed through the **Sources**
results.

Engineering conclusions:

- **Timeout:** 60 s leaves only about 2.4× headroom over the 890-segment case;
  180 s is a more reasonable default (~7×). Expose an override rather than
  making every simulation wait three minutes when a geometry is actually stuck.
- **Single solve:** do not split a phased array by element. The elements are
  mutually coupled and NEC2C solves one joint matrix. Frequency and pattern
  points inside one deck should not be split initially either; that duplicates
  geometry, matrix setup, and memory.
- **Parallelism:** only independent jobs are candidates: optimizer candidate
  evaluations first, band analysis second. A bounded pool of threads launching
  separate `nec2c` subprocesses is simpler than process-level model
  serialization.
- **Limits:** every worker has its own NEC matrix. Cap workers by both CPU and
  memory, terminate all processes on cancellation, keep result ordering
  deterministic, and use a per-worker timeout.

## C1 — Phased verticals / arrays (completed)

**Status:** completed 2026-11-08. Evidence remains experimental pending a
traceable published array or measurement.

The original blocker was the single-feed model (`AntennaModel.feed`) and the
single `EX` source in the NEC adapter. The delivered work crosses the domain
model, solver port, NEC deck, persistence, scene presentation, optimization,
reports, and validation.

Completed slices:

1. **Model and solver — completed 2026-11-08**
   - `Source` value (wire, offset, amplitude, phase) and optional
     `AntennaModel.sources` with the primary feed as source 1;
   - segmentation locates each source independently;
   - the NEC input writer emits one `EX` card per effective source;
   - the primary feed remains the impedance/SWR reference; the total pattern
     and currents include all sources;
   - schema 24 persists the additional sources;
   - unit and real NEC2C two-source tests pass.
2. **Family — completed 2026-11-08**
   - `PhasedVerticalParameters`: count, spacing, height, base height, radial
     system, amplitude taper, phase progression, azimuth, radius, material,
     ground;
   - feed network is an explicit ideal combining model, not a hidden loss;
   - topology (count, radial system) remains a user choice.
3. **Persistence — completed 2026-11-08**
   - schema-25 migration; phase and element-count ranges are validated;
   - round-trip and migration tests.
4. **Presentation — completed 2026-11-08**
   - scene dimensions for spacing and height, and markers for additional
     sources;
   - pattern/current views and reports.
5. **Optimizer — completed 2026-11-08**
   - family descriptor for geometry and phase/amplitude variables;
   - constraints for spacing and phase/amplitude ranges;
   - NEC2C integration and Apply Best adapter.
6. **Evidence — open**
   - a traceable two-element published array or measurement; otherwise the
     family stays experimental with visible limitations.

Do not start C1 by cloning a vertical N times inside a widget. The multi-source
model and solver contract must land first.

## Recommended order

1. The shortened-EFHW correctness work (G24, G25, G26, G28) is done.
   **G27** is split: transformer loss (EF7b), feedpoint choke (EF8), and
   frequency-dependent coax attenuation (ADR-0039) are done. Remaining pieces
   are analytical ferrite core loss, interpolated shack-end `Zcm(f)`, and the
   coax/choke power-budget audit; each needs traceable data.
2. **H1–H4 are complete.** The help/accessibility queue is closed.
3. **M1–M5 are complete.** The matching-network correctness queue is closed;
   future matching work starts from ADR-0028 and the shared resolver.
4. **P1–P7 are complete.** **P7** and **D4** are closed by ADR-0042: the
   per-band path remains, with bounded parallel workers and the existing
   pattern budget.
5. **B4** waits for a coupled-fan measurement. **C3** is complete for the
   straight-element family with a published NEC-4 reference. Its remaining
   optional work is the ARRL/Cebik 7 MHz swept-element wire variant, which
   needs a separate V-array geometry and has only design-table performance
   evidence. Do not substitute independent ideal sources for the transposed
   feed; the validated model uses `TransmissionLine` phase reversal.
6. **D1–D3** remain deferred until the required hardware, engine, or release
   decision exists. **D4** is closed with P7 by ADR-0042; do not change the
   frequency-plan execution model without the ADR revisit triggers.
7. **R1** is closed as superseded: `v0.4.1` was published with CI-built Linux
   and Windows artifacts, so rerunning the older `v0.4.0` tag is no longer
   required.
8. **UX1–UX24 are complete.** The 0.5 **Decide**, 0.6 **Build**, 0.7
   **Measure**, 0.8 **Explore**, and 0.9 **Sustain** releases are closed.
   UX21–UX24 were added from direct user feedback and completed on
   2026-11-12. UX25–UX29 are complete.
9. **UX25 is complete.** The stainless 304 preset, shared material selector,
   reference row, BOM/report text, and deck tests are closed. Do not bundle
   solver-permeability work, carbon steel, or a custom-material editor into it.
10. **UX26 is complete.** The HTML and PDF simulation reports include deterministic
    geometry and azimuth/elevation pattern cuts. Keep future report rendering
    headless and snapshot-based; do not reuse live-widget captures.
11. **UX27 and UX28 are complete.** The presentation-only terminology work is
    closed. Do not rename domain fields, schema keys, or solver identifiers.
12. **UX29 is complete.** The read-only constructive feed connection is closed.
    Do not change `FeedPoint`, the NEC deck, the solver, or the schema without a
    new ADR.
13. **UX30 is complete.** Per-template material defaults are implemented for new
    designs, while existing designs and source-backed references keep their
    stored material. It changes only the new-design selector; it does not change
    the material presets, solver, schema, or existing projects.
14. **UX31 is complete.** The feed-connection schematic now draws coax as coax,
    with per-interface drawings and terminal labels derived from
    `FeedTerminal.side`. It changes only reporting/UI; it does not change the
    domain, solver, schema, or existing projects.
15. **EF1–EF6, EF7a, EF7b, EF8a, EF8, and EF9 are complete.** The shortened-EFHW optimizer keeps
    the fixed feed and loading-coil partitions, results report the input-shunt
    matching-topology floor only for the internal end-fed unit, the confidence
    card marks absolute SWR as informational with the proxy-return limitation,
    the optimizer defaults to Minimum SWR with an Apply Best SWR action, a
    bound-hit warning names the limiting variables, and the 40-10 convergence
    spike keeps the model unchanged with an explicit informational-SWR warning.
    The optional measured 49:1 transformer preset, its optional measured loss
    table, the selectable end-fed return path, the bounded feedpoint
    common-mode choke, and the design-specific L/Pi/T network are available and
    persisted in schema 50; `auto` preserves the legacy behavior. Automatic
    L/Pi/T synthesis is available with a visible design Q.
16. Product priorities and new antenna candidates live in
    [`ROADMAP.md`](ROADMAP.md), not in this queue.
17. **UX32–UX37 are complete.** The frequency-first starting-dimensions work,
    the frequency-semantics ADR, pristine-only recalculation, the quad-beam
    estimator, and the explicit scale action shipped on 2026-11-17 without
    schema or solver changes.
18. **UX38 is complete.** After a successful antenna creation,
    `_create_project_from_parameters()` selects the Design tab. It covers
    catalog templates, Advisor, and Reference Design Library; Advanced-mode
    semantics, Change Template, imports, variants, schema, and solver are
    unchanged. No new translation or help keys. UX39 and UX40 are the open UX
    items.
19. **U1–U5 are complete; U6 documentation is done.** The shared
    `DisplayUnits` formatter, Units preference, adaptive geometry scenes,
    unit-aware scale bar, all family editors and editable tables, the
    optimization/synthesis/auxiliary dialogs, and construction/report surfaces
    are migrated. `QA_PASS_2026-11-18.md` records the automated gate; only the
    manual desktop light/dark and font-scaling checklist remains before the
    release decision.
20. **UX39 is queued after U6.** Raise generated single-design sweeps to 100
    computed points, keep every point in the chart/table/exports, and bound
    marker density. It does not change band-analysis defaults, the solver, or
    the schema; see the UX39 note above.
21. **UX40 is queued after UX39.** Add one static, deterministic 3D far-field
    lobe to the primary report section, keep it out of the band sections, and
    keep the HTML Qt-free and the PDF vector. It complements, and does not
    replace, the two cuts; see the UX40 note above.

## Technical debt pass (2026-11-08)

- The UI mypy pass now rejects unused ignores, redundant casts, and
  unreachable code. Four obsolete pyqtgraph suppressions were removed, two
  dead feed-wire checks were deleted, and one incorrect PySide6 stub was
  handled with an explicit cast.
- `optimizer_availability` uses `assert_never`, so a new parameter type fails
  type checking instead of silently falling through to an unsupported result.
- Fixed band-analysis cancellation during a solver run: the next unprocessed
  band is recorded as cancelled, so a truncated sequential or parallel batch is
  reported as partial rather than completed.
- Added batch-engine fallback and cancellation tests, plus cancellation
  coverage for sequential and parallel band analysis.
- Added direct tests for the Qt worker adapters (100% coverage), the polar
  pattern paint paths (45% to 98%), and the solver locator fallbacks (69% to
  98%).
- Covered the six remaining element-optimizer entry points (`moxon`, `loop`,
  `vertical`, `inverted_v`, `ringo`, and `zs6bkw`) and the public save/open
  lifecycle: current-path save, Save As suffix/cancel, no-project errors,
  open/cancel/error, and the three unsaved-changes answers.
- Covered the data exports (CSV, sources CSV, pattern CSV, HTML, PDF, pattern
  PNG), the four geometry formats (PNG, SVG, PDF, DXF), and solver discovery
  success/error.
- At the end of that pass, `main_window.py` coverage was **76%** (from 69%)
  and the full suite was **88% total** with 346 fewer missed statements.

## Current baseline

- Schema: **55**.
- Full gate: **3,764 passed, 1 skipped** on 2026-11-18 after the HF6 Moxon
  high-frequency estimator policy, with `NEC2C` auto-detected by the test
  configuration; the skip is the Windows-only console-hiding test on Linux.
- Release: **0.9.0** published on 2026-11-17 with the Touchstone `.s1p`
  round-trip, coaxial feed schematic (UX31), per-template material defaults
  (UX30), and the chart-cursor teardown fix. The tag-triggered CI run
  [`44103244393`](https://github.com/fsclavo/antenna-desk/actions/runs/44103244393)
  completed the wheel/sdist, Linux, Windows, and publish jobs; all six published
  assets and checksums were verified. See
  [`RELEASE_QA_0.9.0.md`](RELEASE_QA_0.9.0.md). **0.8.2** remains the previous
  release (2026-11-16, element-table header sizing fix). See
  [`RELEASE_QA_0.8.2.md`](RELEASE_QA_0.8.2.md).
- Known CI residue: Windows Python 3.11 runs acceptance, integration, and unit
  tests only. Its UI suite is excluded because PySide6/pyqtgraph can corrupt
  the native heap during view teardown; Windows 3.12/3.13 and Linux
  3.11–3.13 run the full UI suite. See
  [`ADR/0025`](ADR/0025-pyside6-version-pin.md). Do not weaken the remaining
  gates.
- Last commits: the per-template material defaults (UX30), the coaxial feed
  schematic (UX31), the Touchstone `.s1p` import/export, the chart-cursor
  teardown guards, the font-scaling and preference test isolation, the
  plotted-window teardown cleanup, the element-table header sizing fix, the
  post-0.8.0 stabilization and visual QA, the LPDA feed classification fix, the
  scaled-dialog screen cap, the P7/D4 benchmark decision, the 0.8.0 release
  publication and QA, the log-periodic family (C3), the automatic Pi/T matching
  synthesis (EF9), the post-0.6.0 QA pass, the 0.6.0 release publication and QA,
  the
  Moxon/Yagi starting frequencies (UX24), the editable BOM costs (UX20), the
  portable project bundle (UX19), the common coax catalog (UX23), the materials
  reference (UX18), the 0.5.0 release publication and QA, the folded-dipole,
  full-wave loop, and Yagi folded-driven feed transformers, the current-balun
  record,
  the side-by-side pattern cuts and metric-aware views (UX21–UX22),
  the reference design library (UX17),
  the guided experiments (UX16),
  the project journal (UX15),
  the tolerance and robustness analysis (UX14),
  the parameter sweeps (UX13),
  the measurement uncertainty card (UX12),
  the sensitivity tuning assistant (UX11),
  the measurement sessions and before/after comparison (UX10),
  the construction pre-flight checks (UX9),
  the integrated component calculators (UX8),
  the construction package and as-built record (UX7),
  the feed-chain loss budget (UX6),
  the 0.4.2 hidden-console release,
  the Windows hidden-console solver fix,
  the 0.4.1 installer release,
  the Windows NSIS installer and R1 tracking,
  the 0.4.0 release publication,
  the shortened-EFHW inverted-L option (G26),
  the impedance-point matching-network action (M4),
  the matching-network precedence ADR and user guide (M5),
  the persisted matching-network design target (M3),
  the matching-network visibility and override warnings (M2),
  the matching-network precedence resolver (M1), the
  results/accessibility help audit (H4), the family-specific
  and parameter-dialog help pass (H3), the common field/section/tab help pass
  (H2), the help/tooltip foundation (H1), the element/synthesis optimizer
  progress bars (P6), the optimizer progress bars (P4–P5), the shared
  task-progress widget and Simulate/band progress (P1–P3), the v0.3.1
  cross-platform dimension-label release and its coverage restoration, the
  nec2c wait fix (E5), shortened loaded EFHW presets
  (G22), the EFHW feed-section/convergence model (G23), the shortened
  horizontal default and convergence-check fix, the fixed loading-coil node
  (G24), the primary matching-unit model (G25), the shortened impedance-only
  convergence policy (G28), multi-view construction sheet, localized report
  diagnostics and evidence, translated catalog names, construction-view pass
  (G1–G18), direct basic-antenna editor, report localization, vector native
  PDF figures, solver timeout and parallel analysis, the biquad/Beverage
  evidence review, and the UI type/coverage debt pass.
