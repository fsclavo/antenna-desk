# Autonomous execution backlog

**Date:** 2026-11-10
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
| C3 | Log-periodic | L | transposed feed-line model | **Blocked 2026-11-08:** independent ideal voltage sources with alternating polarity produced a negative primary-feed resistance in NEC2C. A real transposed boom feed line must be modeled before this family can ship; do not approximate it with independent sources. |
| ~~C4~~ | ~~Discone~~ | L | none | **Done 2026-11-08:** radial-wire cone and disc with apex feed gap, schema 27, editor, scene, reports, construction notes, and optimizer. Evidence stays C because the wire approximation and feed transition are not validated. |
| ~~C5~~ | ~~Trapped / multiband Yagi~~ | L | trap model reuse | **Done 2026-11-08:** two-band trapped Yagi with ideal parallel LC trap pairs on each element, schema 28, editor, scene, reports, construction notes, and optimizer. Evidence stays C because trap loss and boom mounting are not modeled. |
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
| ~~G25~~ | ~~Model the 49:1 matching unit and primary 100 pF capacitor~~ | L | G24; traceable transformer data/measurement; 40-20-10 schematic | **Done 2026-11-10 with limitations:** the 100 pF capacitor is confirmed as a shunt across the transformer primary (G0KYA; K1RF; G4AON; PA0EJH/PA3HHO describe the input side) and is modeled through `PiNetwork` as an input shunt plus series leakage, never as a series load in the radiator. Schema 33 adds `matching_capacitance_f` and `transformer_leakage_inductance_h`; older projects migrate with both at zero, and new shortened presets start at 100 pF and 0.198 µH. The leakage value is a starting estimate from Squash Practice's measured 49:1 transformer, not the exact preset build; core loss, capacitor ESR, winding capacitance, the choke, ground, and the inverted-L bend remain unmodeled. UI hints, summaries, construction notes, evidence, and tests are updated; the published SWR remains a trend, not a hard reference. |
| G26 | Inverted-L option for the shortened EFHW | M | G24 | Add an optional bend (vertical rise plus horizontal run) using the G0KYA starting installation (about 8 m vertical and 15 m horizontal) while keeping the straight horizontal default. Update the scene, dimensions, construction notes, reports, and tests. Do not treat the bend as a new antenna family. |
| G27 | Optional transformer, common-mode choke, and coaxial loss models | L | G25; measured transformer insertion loss/core data; common-mode current model or measurement; manufacturer coax attenuation data | **Blocked/deferred as a whole until measurements or traceable datasets exist. Do not ship a partial slice.** Scope: (1) frequency-dependent coax attenuation with source/provenance and interpolation only inside the documented range, reusing `FeedLine`; (2) measured transformer insertion-loss table or fit, reusing `BalunLoss`, plus optional analytical ferrite core loss (KN5L) only with complex permeability, core geometry, winding, load, and excitation data; (3) common-mode choke characterization (G3TXQ-style `Zcm(f)`) without counting `Rcm` as differential loss unless a common-mode current model or measurement exists; (4) a power-budget and evidence audit that prevents double counting with NEC conductor loss and preserves ideal behavior when every optional loss is disabled. All loss fields stay optional and off/zero by default; no invented loss numbers. |
| ~~G28~~ | ~~Shortened EFHW convergence and optimizer policy~~ | M | G24, G25 | **Done 2026-11-10:** shortened presets use an impedance-only convergence verdict: absolute R spread up to 1 Ω and X spread up to 10 Ω; SWR is shown as informational because the matching unit is not fully modeled. With the current model the 80-10 preset is impedance-converged and the 40-20-10 preset remains R/X-sensitive. The matching capacitor and transformer leakage stay as optimizer context values; the optimizer dialog states that they are not optimized until a measured transformer model is available. Unit, UI, optimizer-registry, and NEC2C integration tests cover the policy; the published SWR remains a trend and the evidence level is unchanged. |
| ~~E4~~ | ~~Diagnose high-radial phased-array runtime and numerical validity~~ | S–M | C1 | **Done 2026-11-08:** 4×36 quarter-wave radial screens produced 267 wire crossings, 890 segments, 25.3 s, and negative primary resistance. Halving the radial length or using 2 m radials removed the crossings and completed. The editor now warns when `2 × radial length > element spacing`; ideal-source power absorption remains documented separately. |
| ~~E5~~ | ~~Diagnose low CPU during family optimization~~ | S | none | **Done 2026-11-10:** the nec2c adapter slept 50 ms per solver run even when `nec2c` finished in about 1 ms. It now uses `Popen.wait(timeout=...)`, which returns as soon as the child exits and keeps the interval only for cancellation checks. A 226-evaluation dipole optimization went from 11.8 s to 0.47 s on one worker and from 5.2 s to 0.30 s on four. Local-search batching was measured and reverted: it did not reduce wall time and changed evaluation counts. |
| ~~E6~~ | ~~Multi-seed verification for Thorough~~ | M | E2 | **Done 2026-11-10:** the optimizer runs 1–4 consecutive seeds (Thorough defaults to 3), selects the best-scoring result, and stores the winning seed and verification metrics. The dialog shows the score/parameter spread and warns when the designs diverge; integer and choice variables must match exactly. A real 40/20/10 m OCFD run with three seeds converged to 20.90311 m with score spread 0.0 and parameter spread 4.7e-8. |
| H1 | Tooltip/help infrastructure and UI help style guide | S | none | Add the `help.<key>` translation convention and `Translator.optional()`; add a Qt-only `ui/help.py` helper that resolves an explicit help key, a family-specific override, then an existing `<key>_hint` fallback. Extend `FormLabels` to set tooltips on labels and paired controls and refresh them in `retranslate()`; give `DipoleForm._label` the same behavior. Document a short style guide (1–2 sentences, 80–180 characters, plain text with manual line breaks where needed, no formulas, no full documentation, prioritize fields users cannot infer from the label). Tests cover key resolution, fallback, retranslation, and raw-key avoidance. No domain, solver, persistence, or dependency changes. |
| H2 | Common field, section, tab, and action tooltips | S–M | H1 | Cover the 33 shared `field.*` labels (frequency, length, height, azimuth, wire diameter/radius, material, ground, soil preset, permittivity, conductivity, reference impedance, sweep, template, etc.) plus the main sections: design panel, advanced simulation, sweep, pattern, band plan, solver, results tabs, geometry controls, and primary actions. Set help on both labels and controls, keep label help available for disabled widgets, and keep English and Spanish in sync. Tests assert label/control/tab/action tooltips and the disabled-label fallback. |
| H3 | Family-specific and dialog tooltips | M–L | H1, H2 | Add help for the remaining family-specific labels (OCFD feed/transformer, Yagi/Moxon elements/match/polarization, vertical radials/loading coil/top hat, trap dipole/Yagi, magnetic loop, phased vertical, quad/hexbeam, discone, Beverage, loaded dipole, etc.) and the parameter rows in the 19 dialog layouts (feed line, loads, matching network, balun loss, transmission lines, optimizer, synthesis, custom, measurement). Add per-family overrides for ambiguous shared keys such as `field.height` and `field.spacing`, reuse existing `*_hint` text where appropriate, and do not duplicate the user guide. Describe model semantics only; do not add numerical references or performance promises. |
| H4 | Results, tables, accessibility, and help coverage audit | S–M | H3 | Add tooltips to result tab headers, technical table headers, chart controls, status indicators, and remaining secondary actions. Add `accessibleDescription` and an optional **What's This?** mode for longer explanations so tooltips are not the only keyboard path. Add a coverage manifest/test that every new field or section has English and Spanish help, enforce the length limit, and reject raw keys. Document the maintenance rule in `AGENTS.md` or the UI documentation. Manual QA covers light/dark themes, 100–200% scaling, Spanish text, and disabled controls. |
| M1 | Effective matching-network precedence for EFHW | M | G25 | Implement the agreed **Override** policy: a project matching network replaces the internal EFHW matching capacitor/leakage when `matching_network_active`; with no project network, the internal network remains active. Derive `override_active`; do not persist a flag. Use one pure resolver in single simulation, band analysis, family optimization, synthesis, and the EFHW convergence check. Keep the ideal transformer ratio. Add the `matching_network.override` diagnostic and tests for the four precedence cases; document that cascade is not modeled. |
| M2 | Matching-network visibility and override warnings | M | M1 | Add a persistent **Feed & matching** summary to the design panel with separate rows for EFHW design matching, project matching, feed line, and balun. In EndFed forms, mark internal matching values as retained but inactive while override is active, with a link to edit or remove the project network. Show the override warning in the Matching Network dialog and the optimizer dialog; update construction-sheet and design-summary rows plus the EFHW construction note. Tests cover visibility, retranslation, and hiding when there is no override. |
| M3 | Persist the matching-network design target and preload the dialog | S–M | M1 | Add a project-level `MatchingNetworkDesign` record (frequency, load R/X, source impedance, optional origin) and persist it with schema 34 (or the next available migration); clear it when the project network is removed. Preload the dialog with stored values, add **Use current simulation point**, split Design target from Components, fix the L-only label and irrelevant Pi/T fields, and update the hint. Tests cover apply → optimize → reopen, schema round trip, and undo/redo. |
| M4 | Create a project matching network from an impedance point | S–M | M3 | Add a context menu to the Impedance/SWR table: **Create Project Matching Network...**. Use the raw feed impedance from `source_results` (divide by the transformer ratio) rather than the post-chain `FrequencyResult.impedance_ohm`; pass frequency, load R/X, and the real reference impedance. Warn or disable when raw impedance is unavailable. Confirm replacement of an existing network and warn when the design is an EFHW with internal matching (override). Tests cover raw versus post-chain, active transformer/line/network, cancellation, and preload. |
| M5 | Matching-network precedence ADR and user documentation | S | M1 | Record the Override policy, scope (all `EndFedParameters` with active internal matching), no-cascade limitation, project-global behavior, and how to restore the internal network. Update `docs/USER_GUIDE.md` and `CHANGELOG.md`; reference the new ADR from the matching-network documentation. |
| ~~P1~~ | ~~Shared task-progress widget and state model~~ | S | none | **Done 2026-11-10:** added `ui/widgets/task_progress.py` with explicit idle/running/cancelling/completed/cancelled/error states, indeterminate and determinate modes, an elapsed-time suffix, translated text keys, and reset/finish helpers. Tests cover state transitions, translation, and idle visibility. No domain, solver, or persistence changes. |
| ~~P2~~ | ~~Simulation progress feedback~~ | S | P1 | **Done 2026-11-10:** `MainWindow` shows an indeterminate status-bar bar with elapsed time and preparing/running/processing phases from `SimulationWorker.phase`; finish, failure, and cancellation reset it. Tests cover the lifecycle and elapsed text. |
| ~~P3~~ | ~~Band-analysis progress bar~~ | S | P1 | **Done 2026-11-10:** the existing `BandAnalysisWorker.progress(index, total, band)` signal drives a determinate bar and the `Band i/n: band` label; the status text now stays on "Analyzing bands..." while the analysis runs. Tests cover the shared start path, progress updates, and reset. |
| ~~P4~~ | ~~Family optimizer progress bar~~ | S–M | P1 | **Done 2026-11-10:** `FamilyOptimizationWorker` forwards the existing command progress callback as a Qt signal; the dialog shows a determinate bar with completed/estimated evaluations and the best score, throttles updates, caps running progress below 100%, and completes, cancels, or fails with the result. Tests cover forwarding, estimation text, cancellation, and terminal states. |
| ~~P5~~ | ~~Length optimizer progress bar~~ | S–M | P1 | **Done 2026-11-10:** `OptimizeDipoleLengthCommand` now reports evaluation progress; `OptimizationWorker` forwards it and the dialog shows a determinate bar using `max_evaluations + 2 * len(sensitivity_offsets_m)` as the estimated denominator. Finish, cancellation, and failure set terminal states; tests cover monotonic counts and the dialog progress lifecycle. |
| P6 | Element and synthesis optimizer progress bars | M | P1, P4, P5 | Extend the pattern to `OptimizeElementsCommand` and `SynthesizeAntennaCommand`, their workers, and their dialogs. Use each command's maximum evaluation budget as the estimated denominator, throttle updates, and complete on finish. Tests cover each dialog's bar and cancellation. |
| P7 | True per-frequency simulation progress | L | P2; ADR; benchmark; D4 decision | **Deferred until a benchmark shows a practical need.** Choose between chunked frequency-plan execution and version-tolerant incremental output parsing. Chunking must aggregate `SimulationResult` safely and preserve source, pattern, feed-line, matching-network, and cancellation semantics; parsing must handle partial writes. Add an ADR and benchmark before implementation. Do not use `timeout_s` or elapsed time as a fake percentage. |
| D1 | Live VNA/hardware control | L | hardware | Blocked/deferred; do not start without a device |
| D2 | Additional full-wave engines | L | engine choice | Deferred until a concrete engine is selected |
| D3 | GPG/Authenticode signing | M | release credentials | Deferred; requires signing keys and a release decision |
| D4 | Segmented frequency plan in one NEC deck | M | solver benchmark | Deferred; current per-band batching is intentional |

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
- The current code replaces `spec.matching_network` unconditionally in several
  paths, so a `None` project network can silently drop the internal EFHW
  network. M1 must remove that behavior before adding more matching-network
  UI.

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
| Segmented frequency plan in one NEC deck | Deferred until a benchmark shows a practical need | [`MULTIBAND_PERFORMANCE.md`](MULTIBAND_PERFORMANCE.md), D4 above |
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

1. The shortened-EFHW correctness work (G24, G25, G28) is done. **G26** is
   optional. **G27** stays blocked/deferred as a whole until measurements or
   traceable datasets exist; do not implement only one loss category in the
   meantime.
2. **H1** is the next non-optional foundation for the tooltip/help queue;
   **H2–H4** follow.
3. **P1–P5 are complete.** **P6** extends the progress pattern to element and
   synthesis optimization. **P7** remains deferred until an ADR and benchmark
   show a practical need.
4. **M1** is the matching-network correctness foundation; **M2** makes the
   override visible, **M3** adds the design-target persistence, **M4** adds
   the impedance-point context menu, and **M5** records the decision. Do M1
   and M2 before M3; M3 needs the next schema migration.
5. **B4** waits for a coupled-fan measurement. **C3** is blocked on a
   transposed boom feed-line model; do not substitute independent ideal
   sources, because NEC2C reported negative primary-feed resistance in the
   prototype.
6. **D1–D3** remain deferred until the required hardware, engine, or release
   decision exists. **D4** stays deferred; coordinate it with P7 before
   changing the frequency-plan execution model.
7. Product priorities and new antenna candidates live in
   [`ROADMAP.md`](ROADMAP.md), not in this queue.

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

- Schema: **33**.
- Full gate: **2,365 passed, 0 skipped** with `NEC2C` and the optional
  `cross-engine` group; rerun without PyNEC if the environment lacks it.
- Last commits: the optimizer progress bars (P4–P5), the shared task-progress
  widget and Simulate/band progress (P1–P3), the v0.3.1 cross-platform
  dimension-label release and its coverage restoration, the nec2c wait fix
  (E5), shortened loaded EFHW presets
  (G22), the EFHW feed-section/convergence model (G23), the shortened
  horizontal default and convergence-check fix, the fixed loading-coil node
  (G24), the primary matching-unit model (G25), the shortened impedance-only
  convergence policy (G28), multi-view construction sheet, localized report
  diagnostics and evidence, translated catalog names, construction-view pass
  (G1–G18), direct basic-antenna editor, report localization, vector native
  PDF figures, solver timeout and parallel analysis, the biquad/Beverage
  evidence review, and the UI type/coverage debt pass.
