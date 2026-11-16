# Autonomous execution backlog

**Date:** 2026-11-13
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
| P7 | True per-frequency simulation progress | L | P2; ADR; benchmark; D4 decision | **Deferred until a benchmark shows a practical need.** Choose between chunked frequency-plan execution and version-tolerant incremental output parsing. Chunking must aggregate `SimulationResult` safely and preserve source, pattern, feed-line, matching-network, and cancellation semantics; parsing must handle partial writes. Add an ADR and benchmark before implementation. Do not use `timeout_s` or elapsed time as a fake percentage. |
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
| D1 | Live VNA/hardware control | L | hardware | Blocked/deferred; do not start without a device |
| D2 | Additional full-wave engines | L | engine choice | Deferred until a concrete engine is selected |
| D3 | GPG/Authenticode signing | M | release credentials | Deferred; requires signing keys and a release decision |
| D4 | Segmented frequency plan in one NEC deck | M | solver benchmark | Deferred; current per-band batching is intentional |

## Product experience queue (2026-11-11)

UX1–UX17 are complete. The 0.5 **Decide**, 0.6 **Build**, 0.7 **Measure**, and
0.8 **Explore** releases are closed. UX18–UX20 and UX21–UX24 were implemented on
2026-11-12; the 0.9 **Sustain** slice is complete. The next product slice is not
selected yet. UX21–UX24 were added from direct user feedback and completed the
same day. UX25 and UX26 were queued on 2026-11-13 and completed the same day.
UX27 and UX28 were added the same day from terminology feedback; UX27 and UX28
were completed on 2026-11-13.
UX29 was added and completed the same day from feed-connection feedback.
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
  project materials.
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
- Copper remains the default; existing copper/aluminum projects and tests are
  unchanged.
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

1. The shortened-EFHW correctness work (G24, G25, G26, G28) is done.
   **G27** is split: transformer loss (EF7b), feedpoint choke (EF8), and
   frequency-dependent coax attenuation (ADR-0039) are done. Remaining pieces
   are analytical ferrite core loss, interpolated shack-end `Zcm(f)`, and the
   coax/choke power-budget audit; each needs traceable data.
2. **H1–H4 are complete.** The help/accessibility queue is closed.
3. **M1–M5 are complete.** The matching-network correctness queue is closed;
   future matching work starts from ADR-0028 and the shared resolver.
4. **P1–P6 are complete.** **P7** remains deferred until an ADR and benchmark
   show a practical need.
5. **B4** waits for a coupled-fan measurement. **C3** is complete for the
   straight-element family with a published NEC-4 reference. Its remaining
   optional work is the ARRL/Cebik 7 MHz swept-element wire variant, which
   needs a separate V-array geometry and has only design-table performance
   evidence. Do not substitute independent ideal sources for the transposed
   feed; the validated model uses `TransmissionLine` phase reversal.
6. **D1–D3** remain deferred until the required hardware, engine, or release
   decision exists. **D4** stays deferred; coordinate it with P7 before
   changing the frequency-plan execution model.
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
13. **EF1–EF6, EF7a, EF7b, EF8a, EF8, and EF9 are complete.** The shortened-EFHW optimizer keeps
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
14. Product priorities and new antenna candidates live in
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

- Schema: **52**.
- Full gate: **3,219 passed, 1 skipped** with `NEC2C` and the optional
  `cross-engine` group; the skip is the Windows-only console-hiding test on
  Linux. Rerun without PyNEC if the environment lacks it.
- Release: **0.8.0** published on 2026-11-16 with the log-periodic family and
  automatic Pi/T matching synthesis. The tag-triggered CI run
  [`43931919975`](https://github.com/fsclavo/antenna-desk/actions/runs/43931919975)
  completed the wheel/sdist, Linux, Windows, and publish jobs; all six published
  assets and checksums were verified. See
  [`RELEASE_QA_0.8.0.md`](RELEASE_QA_0.8.0.md). **0.7.1** remains the previous
  release.
- Last commits: the post-0.6.0 QA pass, the 0.6.0 release publication and QA, the
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
