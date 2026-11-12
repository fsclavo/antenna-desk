# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- **Guided, Standard, and Advanced workflow modes.** The mode is selectable
  from the new **View → Workflow mode** menu or the toolbar **Mode** selector,
  persists across windows, and is also available in **Preferences**. Guided
  hides advanced actions and shows a state-derived **Next step** panel;
  Standard keeps the full editor with advanced simulation collapsed; Advanced
  expands the solver, sweep, pattern, and band-analysis controls. Guided mode
  exposes a **Show advanced options** action, so no feature is permanently
  removed.
- The next-step coach follows the project state: create a project, configure
  the solver, simulate, review diagnostics, inspect a high-SWR match, open the
  construction sheet, import a VNA measurement, compare measured and simulated
  results, or export the final report. The panel is available in Guided and
  Standard modes and has English/Spanish help.
- **Installation profiles.** A project can now store named site profiles with
  available height and horizontal space, orientation, support type, ground
  preset, notes, and an optional local image reference. Profiles can be added,
  duplicated, removed, and selected as active; the active profile is shown in
  the design panel and in construction sheets and HTML/PDF reports. Profiles are
  metadata and do not change the antenna model or apply their ground
  automatically. Schema 36 adds the optional profile list and active-profile
  identifier; older projects migrate with no profiles.
- **Antenna advisor.** A new **Help me choose...** entry on the start page and
  in the File menu asks for bands, available height and space, permanent or
  portable use, main operating intent, tuner availability, construction
  effort, pattern preference, and whether one antenna must cover all selected
  bands. It applies hard constraints and returns up to three catalog families
  with fit status, typical space and height, feed arrangement, reasons,
  warnings, evidence, and limitations. The advisor is deterministic, does not
  simulate every candidate, and opens the selected family in its normal editor.
  It uses the active installation profile as initial values and covers the HF
  bands in this first slice.
- **Comparison 2.0.** The comparison dialog now compares two to four designs
  under an explicit common basis: shared frequency sweep, ground, reference
  height, and reference frequency. **Recompute comparison** runs every selected
  design with the same conditions; stored results from different conditions are
  no longer presented as directly comparable. The table adds footprint, maximum
  height, conductor length, wire/load/line counts, and build effort; the band
  summary and SWR/pattern overlays are dynamic. Height mapping is conservative
  and warns when a family keeps its native height. See
  [ADR-0029](docs/ADR/0029-comparison-basis.md).
- **Result confidence and contextual explanations.** The Diagnostics tab now
  starts with a confidence card showing the template evidence level, source,
  tolerance, limitation, modeled scope, and dominant uncertainties. A **What
  does this mean?** selector explains impedance, SWR, efficiency,
  gain/directivity/realized gain, takeoff angle, bandwidth, ground, and
  feed-line/matching losses with practical bilingual text. The card is
  available without a completed simulation because the evidence belongs to the
  design.
- **Feed-chain position and loss budget.** The matching network can now be
  placed at the antenna feedpoint or in the shack before the feed line. The
  chain order is persisted in the project and in simulation specs (schema 37);
  older projects default to feedpoint. Feed-line and matching-network losses are
  now the actual dissipative losses under the modeled impedances, not the
  matched-line value. A new **Feed-Chain Loss Budget...** dialog shows the path,
  per-frequency SWR, mismatch, line, network, balun, delivered, and radiated
  power, and the dominant loss stage. See
  [ADR-0030](docs/ADR/0030-feed-chain-topology.md).

## [0.4.2] - 2026-11-11

### Fixed

- Windows simulations and optimizations no longer flash a console window for
  every `nec2c` process. The adapter now launches the solver with
  `CREATE_NO_WINDOW`, which also removes the console-allocation and window-show
  overhead from repeated optimization evaluations.
- The release workflow now generates `.sha256` assets for the wheel and sdist
  automatically, so every published artifact has a companion checksum.

## [0.4.1] - 2026-11-11

### Added

- Windows releases now include an **NSIS installer** in addition to the portable
  onedir zip. The installer places AntennaDesk under `Program Files`, creates
  Start Menu and Desktop shortcuts, registers an uninstaller in Add/Remove
  Programs, and ships the same bundled `nec2c` and license notices as the zip.
  The release workflow installs NSIS, builds both artifacts with checksums, and
  silently installs, exercises, and uninstalls the packaged app before upload.

### Changed

- The README, documentation index, package metadata, Debian packaging, and
  **About** dialog now credit the author as Fernando Sclavo (LU2EFI).

## [0.4.0] - 2026-11-11

### Added

- Shortened EFHW designs now support an optional **Inverted-L bend**. The editor
  takes the vertical conductor length from the feed, derives the horizontal run
  from the remaining wire length, and shows the resulting top height; the
  straight horizontal installation remains the default. Schema 35 migrates
  older end-fed designs with the bend disabled. The scene, dimensions, wire
  schedule/BOM, design summary, construction sheet, optimizer, and validation
  notes describe the vertical and horizontal sections. The G0KYA starting
  installation is about 8 m vertical and 15 m horizontal; the model uses a sharp
  90° corner and the bend has no independent numerical validation.
- The Impedance/SWR table now offers **Create Project Matching Network...** in
  its context menu. The action uses the raw feed impedance from the solver
  source result divided by the ideal transformer ratio, not the post-chain
  impedance, and preloads the matching-network dialog with the frequency, load
  R/X, and real reference impedance. It is disabled when raw impedance is
  unavailable, confirms replacement of an existing network, and warns when the
  design has active internal EFHW matching.
- The matching-network dialog now stores a project-level design target with
  frequency, load R/X, source impedance, and an optional origin. Schema 34 adds
  the record, removing the project network clears it, and the dialog preloads
  the stored values. The dialog is split into **Design target** and
  **Components**, offers **Use current simulation point** from the raw
  primary-side feed impedance, shows only the component fields that apply to
  the selected L/Pi/T topology, and its enable label and hint now cover all
  three topologies.
- The design panel now has a persistent **Feed & matching** summary with
  separate EFHW internal, project matching-network, feed-line, and balun rows.
  End-fed designs mark their internal matching values as retained but inactive
  while a project network overrides them, disable those fields, and offer
  **Edit project network** and **Remove project network** actions. The
  matching-network and optimizer dialogs show the override warning, and design
  summaries, construction sheets, HTML/PDF reports, and the EFHW construction
  note show the effective project chain and the retained/not-applied state.
- Added the optional UI-help foundation: `Translator.optional()` returns
  translated help or `None`, and `ui/help.py` resolves an explicit key, a
  family override, shared `help.<key>` text, or the existing `<key>_hint`
  fallback. All 33 shared `field.*` labels now have English and Spanish help;
  family editors pair labels with their controls, and the main window exposes
  design, advanced-simulation, action, geometry, and result-tab help. Missing
  help omits the tooltip instead of showing a raw key. The authoring rules are
  in `docs/UI_HELP_STYLE.md`.
- Added accessibility coverage to the help system: `apply_help()` now sets the
  tooltip, the What's This text, and the accessible description together;
  **Help → What's This?** (Shift+F1) exposes the same text without a mouse.
  Result tables, charts, band/pattern/current controls, status indicators, and
  secondary actions have help and accessible descriptions. A bilingual help
  manifest enforces coverage, the length limit, and raw-key rejection.
- Simulate and band analysis now show a shared progress bar in the status bar.
  A single solver run uses an indeterminate bar with elapsed time and phase
  labels (preparing model, running NEC-2, processing results); a multi-band
  analysis uses a determinate counter for the selected bands. Cancelling or
  failing a run resets the bar, and the family and length optimizer dialogs
  now reuse the same widget.
- The family, length, element, and synthesis optimizer dialogs now show a
  determinate progress bar with completed and estimated evaluations. The family
  bar also shows the best score seen so far. Updates are throttled, the estimate
  is labeled, and the bar completes when the optimizer stops early.
- End-fed/EFHW designs now include a fixed **feed section** (0.5 m modeling
  partition of the same wire, three segments) and, when no real counterpoise
  is enabled, a short **installation return** (0.10 m proxy for the coax,
  mast, or earth path). The proxy is not drawn and is excluded from the wire
  schedule, bill of materials, and construction dimensions. The editor
  explains that neither is an extra physical radial, warns when legacy designs
  lack them, and provides a **Check convergence** action over 10/21/51
  radiator segments. The shortened EFHW presets use the same feed section and
  return proxy by default. Schema 32 migrates older projects with both fields
  at zero, preserving their previous model.
- The shortened EFHW loading coil now sits at a fixed model node. The radiator
  is split at the published coil offset into lower, coil, and top sections; the
  coil section stays at three segments, so changing the radiator segmentation
  no longer moves the coil. The wire schedule and bill of materials still
  report one physical conductor. This makes the convergence check measure the
  same antenna at every segment count.
- The shortened EFHW presets now model the published **100 pF matching
  capacitor** as an ideal shunt across the 49:1 transformer primary, together
  with an editable **0.198 µH transformer leakage** starting estimate. The
  leakage value comes from a measured 49:1 transformer, not the exact preset
  build; core loss, winding capacitance, capacitor ESR, choke, ground, and the
  inverted-L bend remain unmodeled. Schema 33 migrates older projects with both
  fields at zero, preserving their previous model.
- The shortened EFHW **Check convergence** verdict now uses **R and X only**
  for the 80-10 and 40-20-10 presets: absolute R spread up to 1 Ω and X spread
  up to 10 Ω. The SWR is shown as informational because the matching unit is
  not fully modeled. With the current model the 80-10 preset is
  impedance-converged and the 40-20-10 preset remains R/X-sensitive. The
  matching capacitor and transformer leakage stay as optimizer context values,
  with an explicit note that they are not optimized until a measured
  transformer model is available.
- Opening a project now reads, decompresses, migrates, and validates it in a
  worker thread with a window-modal busy progress dialog, so large saved
  projects no longer freeze the UI. The project is applied only after
  validation succeeds.
- The family optimizer can now run **1–4 seeds** and compare the resulting
  designs. **Thorough** defaults to three consecutive seeds, the best-scoring
  run is selected, and the winning seed is stored in the optimization summary.
  The dialog reports the score and parameter spread, the recommendations warn
  when the designs diverge, and a single seed run keeps the previous behavior.
  Verification metrics include `seed_base`, `seed_requested`, `seed_count`,
  `seed_scored_count`, `seed_evaluations_total`, `seed_score_spread`,
  `seed_parameter_spread`, and `seed_converged`.

### Fixed

- The End-fed **Check convergence** action now keeps at least three segments
  on the auxiliary and return wires, matching the normal simulation, so the
  shortened EFHW presets no longer fail with a negative-resistance error. The
  installation-return proxy now terminates at the ground plane instead of
  floating 0.1 m above it, avoiding a near-short for ground-mounted shortened
  presets. When a segment count fails, the dialog reports the actual error
  diagnostic instead of the first warning.

### Changed

- Documented the matching-network precedence policy in
  [ADR-0028](docs/ADR/0028-matching-network-precedence.md) and the user guide:
  an active project network replaces the internal EFHW matching unit for every
  end-fed design with active internal matching, the two networks are never
  cascaded, the project network is global, and removing it restores the
  internal unit.
- Matching-network precedence for end-fed designs is now explicit: an active
  project matching network replaces the internal EFHW matching capacitor and
  transformer-leakage model, while the internal model remains effective when
  no project network is active. Single simulation, band analysis, family
  optimization, synthesis, and the convergence check share one resolver; the
  override is derived at runtime, reported as the
  `matching_network.override` diagnostic, and cascading two matching networks
  is still not modeled. The ideal transformer ratio is unchanged.
- The shortened EFHW presets now open **horizontally at 10 m** by default,
  matching the standard End-fed template. Set different feed and end heights
  for a sloper or vertical installation.

## [0.3.1] - 2026-11-10

### Fixed

- Construction-view dimension labels no longer overlap when the system font is
  wider than the development font (notably on Windows); a label that cannot be
  placed without overlapping another label is omitted instead of drawn on top.
- Large-font Spanish forms now widen the design panel to the widest form
  instead of being clipped at a fixed 680 px.

## [0.3.0] - 2026-11-10

### Added

- Added two **shortened EFHW** catalog presets with an optional series loading
  coil: **80-10 m** (20.35 m + 110 µH + 2.39 m) and **40-20-10 m** (10.01 m +
  23 µH + 1.85 m), both with a 49:1 transformer. The coil position,
  inductance, and series resistance are editable and persisted in schema 31;
  the matching unit, capacitor, choke, and ground remain documented
  limitations. The 80-10 m reference is G0KYA/EA7EER/G4WIF; the 40-20-10 m
  reference is the radioaficion.com/PA0EJH schematic. Automatic frequency-first
  estimation is disabled for these loaded presets.
- The construction sheet now builds a **multi-view grid**: the dimensioned
  construction view, the complementary front/top view when the family has one,
  and an **isometric 3D view**. The HTML sheet uses a responsive two-column
  grid; the native PDF draws the additional views side by side with captions
  and keeps them vector. Single-view families still get the construction view
  plus the isometric view.
- Native PDF construction sheets and simulation reports now keep the
  construction view, auxiliary view, and simulation charts as **vector
  graphics** when an SVG source is available. The construction sheet falls
  back to the raster preview if SVG rendering fails, and the HTML preview still
  uses PNG. The report charts and construction figures no longer become image
  XObjects in the PDF.
- The **construction sheet**, **HTML simulation report**, and native **PDF**
  exports now follow the UI language. Reporting stays Qt-free and accepts an
  optional labeler; the UI passes `Translator.report`. Table headers, title
  blocks, section headings, evidence rows, design-summary labels, construction
  notes, and chart titles are translated. Technical values, wire identifiers,
  units, and user project names remain canonical.
- Band analysis can now run independent bands in parallel with **1–4 bounded
  workers** in the dialog (command 1–8; the sequential path remains the
  default). Results and progress stay in the selected band order, cancellation
  is propagated to every running band, and completed bands are kept. A
  four-worker benchmark measured **1.3–1.8×** speedup with about 14 MiB of
  additional parent peak RSS; see `docs/MULTIBAND_PERFORMANCE.md`.
- The family optimizer can now evaluate independent candidates in parallel
  with **1–4 bounded workers** in the dialog (default
  `min(4, max(1, CPU count - 1))`); the command accepts 1–8 and defaults to the
  sequential one-worker path. Candidate results remain deterministic and
  ordered, and cancellation is propagated to every in-flight solver process.
  Each worker launches its own solver process, so CPU and memory use grow with
  the worker count.
- Added a first-class **hexbeam** family: a W-shaped driven element and a
  U-shaped reflector on a six-spreader frame, with published G3TXQ 20 m
  starting dimensions, linear frequency scaling, schema-30 persistence,
  catalog route, inline editor, scene dimensions, reports, construction notes,
  and a family optimizer. The model reconstructs the bent wire path; the frame,
  spreader sag, feed balun, and multi-band nesting are not modeled.
- Added **per-source input results** to multi-source simulations: each
  frequency stores the ideal source voltage, current, impedance, amplitude,
  phase, and power for every driven port, and the results view exposes them in
  a **Sources** tab. The HTML report lists the same source inputs, and a
  separate CSV export contains one row per frequency and source. A warning is
  recorded when an ideal source absorbs power. The primary feed remains the
  impedance/SWR reference. This is persisted in schema 29.
- Added a first-class **trapped Yagi** family: a two-band reflector/driven/
  optional-director array with one ideal parallel LC trap pair on every
  element, schema-28 persistence, catalog route, inline editor, scene
  dimensions, reports, construction notes, and a family optimizer. Trap loss,
  boom mounting, feed line, and matching network are not modeled; the family is
  experimental.
- Added a first-class **discone** family: a radial-wire cone and top disc with
  a source across a small apex gap, quarter-wave starting dimensions, schema-27
  persistence, catalog route, inline editor, scene dimensions and summary,
  reports, construction notes, and a family optimizer. The cone and disc are
  wire approximations; the coax, mast, and solid surfaces are not modeled, and
  the family is experimental.
- Added a first-class **quad beam** family: two or three square loops with a
  reflector, driven loop, and optional director, quarter-wave loop and
  fifth-wave spacing starting dimensions, schema-26 persistence, catalog route,
  inline editor, scene dimensions and summary, reports, construction notes, and
  a family optimizer. The boom, spreaders, mast, feed line, and matching network
  are not modeled; the family is experimental pending a traceable design or
  measurement.
- Added a first-class **phased vertical array** family: two to four vertical
  radiators spaced along one line with an ideal linear phase step and amplitude
  taper, a radial screen per element, schema-25 persistence, catalog route,
  inline editor, scene dimensions and additional-source markers, reports,
  construction notes, and a family optimizer. The first vertical is the primary
  feed; the combining network is ideal and the reported impedance/SWR refer only
  to the primary feed. The family is experimental pending a traceable array
  reference or measurement.
- Added optional **additional antenna sources** with amplitude and phase to the
  canonical model. The NEC adapter emits one `EX` card per effective source;
  the primary feed remains the impedance/SWR reference. This is the
  architecture groundwork for phased arrays and is persisted in schema 24.
- Added optimizer **CSV export** with the ranked evaluation log, metrics,
  errors, Pareto flags, and every design variable. The export is independent of
  the project file.
- Added optimizer **space constraints**: an optional maximum turning radius for
  every family and maximum boom length for Yagi/Moxon. Limits are hard
  candidates filters, are reported when violated, and are stored in the
  optimization summary. The turning radius uses the boom midpoint for arrays
  and the feed's horizontal projection for other families.
- Added optional **tapered Yagi element tips**: a shared tip length and smaller
  tip radius add two outer segments to every element, persisted in schema 23.
  The model does not include a boom-mounting correction; use published or
  measured element lengths where the boom and clamps matter.
- Added optional **wire sag** to horizontal wire dipoles: a sampled parabolic
  path replaces the straight span, the feed stays at the center segment, and
  the scene, reports, and construction sheet show the sag and the longer
  conductor path. The option persists in schema 22. Other families remain
  straight; tapered Yagi elements and boom correction are still pending.
- Added a first-class **Loaded / linked dipole**: a center-fed dipole with
  symmetric series R-L loading coils or open links that leave only the center
  section active. It includes schema-21 persistence, catalog route, inline
  editor, scene contract, reports, construction notes, and a family optimizer.
  Coil Q is reported from the explicit series resistance; core loss,
  self-capacitance, and link contact resistance are not modeled.
- Added a first-class **Beverage** receiving antenna: a long horizontal wire
  fed at the near end with an optional resistive termination to ground, a
  one-wavelength starting length, schema-20 persistence, catalog route, inline
  editor, scene contract, reports, construction notes, and a family optimizer.
  The model is experimental; its low gain, pattern, and termination efficiency
  are not independently validated.
- Added first-class **Biquad** and **Double biquad** designs: two or four
  stacked square loops with shared rails, an optional rectangular wire
  reflector, quarter-wave starting dimensions, schema-19 persistence, catalog
  routes, inline editing, scene contracts, reports, construction notes, and a
  family optimizer. The family is classified experimental; gain, feedpoint
  impedance, and bandwidth are not independently validated.
- Added first-class typed **G5RV**, **ZS6BKW**, and **Zepp** designs with inline
  editors, schema-17 persistence, reports, construction rows, scene summaries,
  and family optimizers. Existing custom-generator projects remain loadable;
  the doublet is already a typed dipole radiator plus a project-level feed line.
- Replaced the mixed optimization paths with a **family optimizer
  architecture**. Each supported typed family has an explicit descriptor and
  QA coverage; there is no generic dipole fallback. The shared engine combines
  deterministic differential evolution with bounded local refinement, searches
  all geometry, feed, and family-load variables jointly, and keeps topology,
  frequency, ground, and material as user context. The dialog exposes every
  variable, lock controls, objective and constraints, Fast/Balanced/Thorough
  budgets with automatic extension, a reproducible seed, ranked results,
  sensitivity, and Apply Best routed through an exhaustive editor adapter.
  Magnetic loops, random wires, and arbitrary custom/imported geometry report
  an explicit unavailable reason instead of falling back.
- Optimization now supports **band-aware** and **robust** operating modes, a
  descriptive **Pareto front**, deterministic post-run recommendations, and a
  compact **optimization summary** persisted with each design in schema 18.
  Band-aware runs aggregate worst-case metrics across editable band edges;
  robust runs add ± dimensional-tolerance corners and a variance penalty.
  Summaries keep the mode, objective, status, seed, evaluation count, winning
  vector, metrics, and recommendation keys without storing every evaluation.
- Added a first-class **Half square / Bobtail curtain** family. Both variants
  share one self-contained vertical-array editor, are fed at a top junction
  with an adjustable feed offset, persist in schema 16, and include catalog
  routes, geometry dimensions, reports, and a construction sheet. The default
  dimensions scale Cebik's published 7.15 MHz 62.4 x 39 ft and 125 x 38 ft
  starting geometries; pattern, ground, and matching remain unvalidated.
- The EndFed template is now labeled **End-fed half-wave (EFHW)** and offers
  explicit 40/20/10 m preset buttons using the published ARRL 66/33/16 ft
  lengths, 49:1 transformer, and 0.05λ counterpoise starting point.
- Top-loaded vertical reports, construction sheets, and scene summaries now
  include the capacitive-hat wire count and radius. A mixed radial/top-hat/
  loading-coil scene contract covers the existing vertical template.
- Added a project-level **Balun/Unun loss** model with a frequency-dependent
  power-law fit. It reduces realized gain and is reported per frequency without
  changing geometry, impedance, or SWR; the setting is saved with the project
  and simulation runs.
- Yagi designs now support an optional **beta/hairpin match**: the straight
  driven element is split at the centre, a shorted two-conductor stub runs along
  the boom, and the feed sits across the driven-element gap. A gamma match is
  documented as deferred because NEC-2 close-spaced gamma assemblies are
  unreliable; the matching-network dialog remains the equivalent.
- Yagi designs now support an optional **folded driven element**: two parallel
  conductors with end connectors and adjustable spacing. The NBS 5-element
  preset can be loaded with the published folded geometry. The feed impedance
  changes with the fold spacing and remains a simulation/tuning result.
- Added a first-class **Magnetic loop** generator: a vertical small loop with a
  top gap, ideal series tuning capacitor with ESR, conductor-loss simulation,
  efficiency and SWR-bandwidth reporting, schema-11 persistence, a dedicated
  editor, catalog route, reports, and construction sheet. A coupling loop and
  detailed capacitor loss model are not included; the template is experimental.
- Vertical and loaded-vertical editors now offer a **Radial system** selector
  with starting presets for no radials, ground radials, elevated radials, and
  a dense ground-screen approximation. The presets set the base/radial-plane
  height, radial count, and radial length; the numeric fields remain editable
  and the preset itself is not persisted.

### Changed

- The optimizer adds **Minimum SWR at operating frequencies**, which balances
  the RMS SWR at the OCFD harmonics inside each selected band (for example 7.1,
  14.2, and 28.4 MHz) and at band centers for other families. The **Thorough**
  profile now runs at least 1,500 global and 1,000 local candidate evaluations
  before the frequency/scenario multiplier, instead of a few hundred
  candidates.
- The family optimizer now starts with installation context unchecked:
  installation height, feed-point placement, conductor radius/diameter, and
  transformer/balun ratios. They remain selectable; excluding them marks the
  run as partial. The default search focuses on the dimensions users typically
  tune.
- Reports now localize diagnostic messages and the evidence registry's source,
  tolerance, and limitation text. Diagnostics use the existing
  `diagnostic.<code>` catalog with an English fallback for unknown codes;
  evidence text is translated per template and field. Tests enforce coverage of
  every diagnostic code and every evidence entry.
- The **wire dipole**, **folded dipole**, and **loop** catalog entries now open
  the same full variable editor used after creation instead of a multi-page
  wizard. The editor starts from frequency-aware estimator dimensions, keeps
  the frequency/height/ground/material defaults, hides the Family and Template
  rows (the template is already selected in the catalog), and asks for the
  project name after the template is accepted. Delta and quad loop entries
  still preselect three or four sides.
- Consolidated the planning documents: [`docs/ROADMAP.md`](docs/ROADMAP.md) is
  the product scope and antenna backlog, `docs/AUTONOMOUS_BACKLOG.md` is the
  only active execution queue, and the 2026-11-04 phase plan moved to
  [`docs/archive/`](docs/archive/PENDING_WORK_PLAN_2026-11-04.md). Added
  [`docs/README.md`](docs/README.md) as the documentation index.
- The **Moxon** reference preset now scales the published Cebik 20 m wire
  dimensions to the current frequency and preserves the current height,
  ground, wire radius, polarization, and material. The **half-square/bobtail**
  reference preset does the same from its 7.15 MHz Cebik dimensions and also
  preserves the feed offset. Scaled geometry is a heuristic starting point;
  only the exact published frequency case is reference-backed. The Ringo and
  vertical-mobile example buttons now show their fixed frequency in the label.
- Beam construction views now carry their build dimensions: the Yagi plan
  labels every element (E1, E2, …) and each inter-element spacing; the Moxon
  adds a tip-detail inset with both tip lengths and the gap; the hexbeam adds
  the spreader angle, turning radius, and a half-detail inset with the four
  segment lengths; the trapped Yagi labels all element lengths and spacings and
  adds a symmetric trap-detail inset; the quad beam labels each loop and the
  director spacing. Detail insets are larger so the labels remain legible.
- The discone construction view now shows the full cone angle and reports the
  half-angle and radial step; phased verticals label each additional source
  with its phase and amplitude; the biquad dimensions the loop-side stack; and
  the quad beam adds a driven-loop front detail inset with the square side.
- Single-wire and vertical construction views now dimension the feed offset
  and every load position. The loaded dipole measures link/coil offsets from
  the feed, the trap dipole measures trap positions from the wire start,
  verticals dimension the loading-coil height and top-hat radius,
  half-square/bobtail dimension a nonzero feed offset below the top, and fan
  dipoles label each leg and report included angles and end heights in the
  construction sheet.
- The geometry panel now exposes a single **Construction** view plus **3D**.
  Construction resolves to the projection that shows the family's principal
  plane: front for vertical antennas, top for horizontal beams and loops, top
  for the cubical quad, and front with a top inset for non-planar models.
  Edge-on projections are no longer offered as construction views. The
  construction sheet and native PDF now include a wire schedule with every
  wire's endpoints, length, diameter, material, and the primary feed point.
  They also embed the rendered construction view; the dialog preview loads the
  same image through a document resource. When Construction is a top view, the
  sheet adds an **Installation view (front)** with height, ground line, and
  feed height. For front-view families whose top layout adds information
  (fan dipole, inverted V/L, end-fed wire, Beverage), the sheet adds a **Top
  layout** view instead. The sheet also has a title block (project, design, antenna,
  frequency, units, date) and a bill of materials with conductor totals grouped
  by material and diameter, plus load, line, and source counts. The wire
  schedule can also be exported as CSV from **File → Export → Export wire
  schedule CSV... and the grouped conductor totals as **Export bill of
  materials CSV...**. The sheet also carries an **Evidence and limitations**
  section with the template's evidence level, source, tolerance, and the
  unmodeled items (frame, boom, balun, trap loss, and so on).
- Every linear construction dimension now matches the distance between its
  anchors within 1% or 5 mm; a contract test covers every family in elevation
  and plan. Sloped custom wires no longer show a 3D feed offset on a projected
  plan anchor.
- The geometry sketch now has a **compact layout** for small panes: smaller
  header, margins, offsets, and label font; detail insets are hidden when the
  pane is too small, and the hidden-dimension notice points to the schedule.
  A compact strip below the sketch now lists the hidden dimension values, so
  they remain visible without enlarging the drawing.**.
- The **biquad** and **Beverage** starting dimensions are now classified as
  published evidence (B) instead of experimental (C). The biquad claim covers
  the quarter-wave loop side and eighth-wave reflector spacing; the Beverage
  claim covers the one-wavelength length and 500 Ω nominal termination. The
  wire-reflector construction, termination ground system, gain, and feedpoint
  impedance remain explicit limitations. Double biquad and loaded dipole remain
  experimental after the same review.
- The default solver timeout is now **180 s** instead of 60 s and can be
  adjusted from 10–3600 s in **Advanced simulation → Solver**. It applies to
  single simulations, band analysis, and family optimizations.
- The discone now defaults to a heuristic broadband band plan from 0.5x to 1.5x
  its design frequency instead of the current amateur band only. The model and
  its limitations are unchanged.

### Fixed

- Optimizer evaluations now derive the segmentation from each candidate
  geometry instead of freezing the starting design's segment counts. An
  identical candidate therefore produces the same solver input regardless of
  the geometry used to start the optimization. Robust tolerance now perturbs
  only active variables, so locked installation context is not silently varied.
- **Apply Best** no longer discards the optimization summary during the
  post-apply form write-back. The summary is preserved when the form rewrites
  identical parameters, loads, and transmission lines, and invalidated when the
  geometry actually changes.
- In **band-aware** and **robust** modes, **Apply Best** now applies the best
  nominal parameters and immediately runs the full band analysis for the
  current band plan, so the Bands tab and per-band charts show the optimized
  geometry; robust mode analyzes the nominal case, not the tolerance corners.
  Single-frequency mode still runs one simulation.
- The nec2c adapter now waits for the solver process with
  `Popen.wait(timeout=...)` instead of a fixed 50 ms polling sleep. A
  226-evaluation optimization dropped from 11.8 s to 0.47 s on one worker and
  from 5.2 s to 0.30 s on four workers; cancellation checks remain at 50 ms
  intervals.
- The antenna catalog now shows each template's translated name instead of the
  raw `catalog.<type>.description` key. Custom item data uses Qt user roles, so
  the description no longer overwrites the visible text; the detail pane shows
  the family, description, and evidence level.
- The Beverage construction view no longer discards its length dimension: the
  far-end selection now chooses the endpoint farther from the feed.
- The hexbeam span dimension now anchors to the widest tips, and the drawn
  tip-to-tip gap is the actual clear distance between the tips rather than the
  published construction parameter.
- The magnetic-loop drawing no longer labels a polygon chord as the loop
  diameter; the circumscribed diameter stays in the summary and schedule.
- The discone plan view no longer draws vertical heights on the plan's Y axis.
- J-Pole and Slim Jim construction views now dimension the feed offset, base
  height, stub or upper/lower sections, gap, and spacing, with distinct labels
  for repeated values.
- Hidden-dimension notices are now drawn separately from the elided summary, so
  they remain visible when the summary is truncated.
- Band analysis now records the next unprocessed band as cancelled when a
  cancellation arrives during a solver run, so a truncated sequential or
  parallel batch is reported as partial instead of completed.
- The phased vertical editor now warns when adjacent radial screens overlap
  because twice the radial length exceeds the element spacing. Intersecting
  screens can produce unstable NEC impedance or negative primary resistance;
  shorten the radials, increase spacing, or model the bonded screen explicitly.
- The trapped-Yagi trap loads are now registered as template-managed loads, so
  editing the design or converting templates preserves them instead of treating
  them as user-added loads.
- **Apply Best** now uses the family-specific editor adapter. A half-square or
  bobtail-curtain result updates the shared array editor instead of passing
  `ScvParameters` to the basic dipole form; the same exhaustive adapter covers
  every other supported typed family.
- Removed an intermittent PySide6 shutdown crash in the optimizer dialogs by
  letting the dialog and Python own the worker thread and worker object instead
  of deleting them from the thread's own `finished` signal.

## [0.2.0] - 2026-11-06

### Added

- The loop editor now supports **vertical** and **horizontal / sky-loop**
  orientation. Horizontal loops use plan view by default, keep their polygon
  when dimensioned and reported, and persist in schema 10 with existing loops
  migrated as vertical.
- Added a first-class **Inverted L** generator: a vertical section fed at the
  base, a horizontal top run, configurable base height and azimuth, a
  dedicated editor, catalog route, schema-9 persistence, geometry dimensions,
  reports, construction sheet, and tests. It is labeled experimental until an
  independent reference exists.
- Finite-ground editors now offer a **Soil preset** list with typical starting
  values for average soil / clay, rich soil / loam, dry sand, rocky soil, fresh
  water, and salt water. The permittivity and conductivity fields remain
  editable; changing either value switches the preset to **Custom / measured**.
  The presets are broad HF starting points, not measured site data.
- Persistent UI font-size presets (**Small**, **Normal**, **Large**) in
  **Edit → Preferences...**. Normal restores the system default; the choice is
  applied at startup. Standard widgets, custom-painted sketches, pattern views,
  chart axes and legends, and the start-page headline follow the preset.
  Exported reports keep their fixed typography.
- **Edit → Preferences...** now sets language, display units, and font size in
  one dialog. Language and units persist across restarts, and dialog initial
  sizes follow the font preset. The language selector includes **System** to
  follow the operating system, and **Restore Defaults** returns to System,
  metric units, and Normal font size. The redundant Language, Units, and Font
  Size submenus were removed; Preferences is the single entry point.
- Mutation testing now includes `dipole.py`: 240/304 mutants killed (79 %), and
  the 64 survivors are message-only. The run found and fixed a missing
  conductor-material assertion in `to_antenna()`.
- CI has a report-only benchmark job for the NEC output parser, pattern metrics,
  and compressed project save/load. It uploads `benchmark.json` and does not
  enforce a threshold yet.
- The test suite has a fast unit-test lane: `pytest -m "fast and not slow"`
  runs 735 tests in about 6 s. `fast`, `ui`, and `solver` markers are applied
  automatically by path or fixture; the two G5RV pattern-budget tests are
  marked `slow`.
- Every native artifact now carries `COPYING`, `THIRD_PARTY_NOTICES.md`, the
  LGPL-3.0 text, installed dependency license files, and the nec2c source
  tarball/patch. The packaging build fails when a required notice is missing.
- An SPDX header test checks the copyright and GPL-3.0-or-later identifier in
  Python, shell, PowerShell, spec, and desktop source files. The desktop entry
  now carries the header.
- Re-measured coverage after the property, i18n, and catalog tests: 85 % total,
  importers 90 %. The importers gate moved from 88 to 89; the other gates were
  already one point below their measured values.
- A changelog structure test checks the Unreleased entry, release dates,
  unique versions, descending order, and Keep a Changelog subsection names.
- A static UI translation test checks every literal key passed to the
  translator and every literal text setter, so missing keys and untranslated
  labels fail the build.
- Hypothesis property tests now cover all 13 estimator families and the
  project document, repository, and v1-to-current migration round trips. The
  geometry properties found and fixed the zero-height and vertical-array
  clearance edge cases below.
- Yagi and Moxon designs now support selectable **horizontal or vertical
  polarization** while keeping the boom horizontal. Vertical Yagi elements
  rotate around the boom; the Moxon rectangle lies in a vertical plane. Height
  remains the boom centerline and the geometry is rejected when the elements or
  rectangle would reach the ground. Existing designs and projects default to
  horizontal. Project schema version 7 migrates them explicitly.
- The 3D pattern high-resolution paint mesh now uses a 40% coarser angular
  step for large patterns, reducing vertex and segment counts by about half.
  Stored far-field data, cuts, and exports are unchanged.
- Added a reproducible multiband benchmark. The measured 3/5/8-band batches
  keep the per-band solver architecture; see `docs/MULTIBAND_PERFORMANCE.md`.
- OCFD and End-fed generators now label the frequency as the fundamental/design
  frequency and let the user choose the harmonic analysis band plan at
  creation. The plan is persisted with the design, restored on reopen, and does
  not change geometry. Random-wire uses the same selector for its tuner-assisted
  80–10 m analysis plan.
- **Zepp** catalog preset: half-wave end-fed radiator with a real two-conductor
  quarter-wave matching stub. One conductor feeds the radiator, the second is
  open at the antenna end, and the feed is the middle of the base connector.
  The 1:1 common-mode choke is an explicit construction requirement because
  NEC-2 cannot model it; the coax and common-mode current are not modeled. The
  preset includes starting dimensions from frequency and an odd-harmonic
  analysis plan. Projects saved with the earlier simplified transmission-line
  geometry keep their saved wires.
- Construction sheets now handle custom-generator wires instead of raising an
  error. The Zepp sheet lists the radiator, matching stub, conductor spacing,
  estimated stub impedance, and the unmodeled 1:1 choke requirement.
- T2FD now has a frequency-first **Estimate Dimensions...** path using the
  Cebik wide-long broadband starting rule. It requires the lowest and highest
  design frequencies and preserves the current termination and transformer.
- ZS6BKW has a template-specific optimizer for dipole wire length and matching
  line length, while keeping the line impedance and velocity factor fixed.
- **ZS6BKW** catalog preset with a 28.4 m / 400 Ω / 13.6 m Cebik/W4RNL
  reference variant and a 27.5 m / 450 Ω / 12.2 m commercial variant, modeled
  with a lossless geometry transmission line. The default band analysis uses
  the 40/20/17/12/10 m no-ATU set and a 61-point 7.0–29.7 MHz sweep.
- **Simulation sweep** in **Advanced simulation** provides Auto (template) and
  Custom Start/Stop/Points modes for every antenna family, including generated
  templates that previously used a fixed sweep with no UI control.
- During a band analysis, the **Pattern** frequency selector now lists pattern
  frequencies from every analyzed band and switches the active band when one is
  selected. The **Bands** tab remains synchronized.
- Band analysis now applies the global **Pattern frequencies** policy inside
  each band instead of forcing one snapshot per band.
- The main window now starts on a **Start an antenna project** page instead of
  creating a demo 40 m dipole. **New Antenna...** creates the first project and
  **Open Project...** loads an existing file; project and design controls appear
  only after a project is open.
- **Estimate Dimensions...** now refines only the template already loaded in the
  editor. The dialog preselects the current family, preloads its frequency and
  template-specific fields, and refuses to replace the template. Templates
  without an estimator show the action disabled with an explanation.
- OCFD designs support an optional ideal feed transformer, defaulting to the
  common 4:1 balun for new designs while old projects remain untransformed.
  The ratio is editable, applies to impedance/SWR/realized gain, and preserves
  pattern geometry. Custom designs also carry an optional transformer ratio.
- Pattern charts, polar plots, the 3D lobe, and cursor readouts can now switch
  between power gain, directivity, and realized gain.
- Pattern PNG export on a band analysis now writes one image per band into a
  selected folder while preserving the current pattern selection.
- Multiband analysis for G5RV, OCFD, end-fed/random-wire/sloper, fan dipole,
  trap dipole, T2FD, and doublet designs. **Analyze Bands...** runs the existing solver
  once per selected band, stores band/batch metadata on simulation runs, and
  adds a **Bands** results tab with best SWR, gain, takeoff angle, efficiency,
  and status. Band summaries are included in CSV, HTML, and PDF exports.
- The 3D radiation-pattern wireframe is colored by gain (green, yellow, red)
  with a min/max dBi legend, while keeping the lobe interior transparent.
- The 3D lobe maximum-gain marker now reports the takeoff angle above the
  ground plane (or elevation for free-space models) alongside the gain.
- End-fed designs support a user-selectable counterpoise (drop plus horizontal
  wire) and an ideal feed transformer ratio. The one-time estimator starts with
  a 49:1 transformer and a 0.05λ counterpoise as application starting points.
- Frequency-first vertical estimation supports the half-wave form
  (`0.5λ × 0.95`) in addition to quarter-wave and five-eighth-wave, with a
  matching warning for the high half-wave feed impedance.
- Vertical templates support an optional series loading coil at a selected
  height above the base. A loaded vertical / mobile whip catalog preset starts
  with a 2.0 m radiator, four short radials, and an editable 10 µH coil as
  application starting points.
- Trap-dipole templates support two parallel LC traps, automatic trap
  capacitance from the target frequency and inductance, and a starting-dimension
  helper for the low and high bands.
- T2FD (terminated folded dipole) templates support a broadband 800 Ω series
  termination, an ideal feed transformer, horizontal or vertical geometry, and
  a Cebik wide-long starting-dimension helper (`300/F` span, `10/F` spacing).
- Catalog presets for a sloper, a random wire, and a doublet. Sloper and random
  wire use the end-fed template with preset metadata; the doublet creates a
  center-fed dipole and configures a project-level open-wire feed line.
- Directivity and realized gain are now separated from NEC power gain. The
  results summary and reports show power gain, directivity, realized gain, and
  the mismatch, feed-line, and matching-network loss components. The feed
  line, matching network, and ideal transformer are evaluated as a two-port
  cascade; the pattern charts remain NEC power gain.
- Transmission lines can be modeled as geometry: a lossless two-port between
  two wire offsets, persisted with the design, emitted as NEC `TL` cards,
  drawn as dashed construction lines, and edited from the design panel. This is
  separate from the transmitter feed-line post-processing model.
- G5RV catalog preset with the published 102 ft dipole and a 300 Ω / 8.84 m or
  450 Ω / 10.36 m lossless geometry matching line, plus a 41-point wideband
  custom sweep.
- Simulations choose the finest pattern resolution that fits the project size
  budget. Custom designs expose an Auto (max) setting, an estimated-size
  indicator, and a pattern-disabled fallback; generated templates coarsen the
  selected resolution automatically and report an informational diagnostic.
  Oversized solver output now reports a specific `solver.output_too_large`
  diagnostic.
- Sweeps longer than five points now compute the far-field pattern at
  amateur-band snapshots while keeping every impedance/SWR point. Custom designs
  can choose Auto (bands), 5, 9, 13, 17, or 21 pattern frequencies. The pattern tab
  lists the snapshots, so a 200-point G5RV sweep can show nine bands at 5°
  instead of a 30° pattern at every point. The project-size budget accounts for
  the sweep and pattern snapshot counts separately.
- Added `docs/QA_STRATEGY.md` and the Phase 0 test tooling: the suite now
  auto-detects `spikes/phase0/build/nec2c` so solver tests do not skip silently
  on a developer machine, registers `science`, `solver`, `slow`, `golden`, and
  `ui` markers, and the CI caches the uv environment. The UI teardown now
  dispatches deferred deletes, which cuts the full suite from 142 s to 56 s.
- Added a coverage job with per-package thresholds, a permissive mypy pass over
  58 of the 75 UI modules (`mypy_ui.ini`), English/Spanish translation parity
  tests, and Hypothesis property tests for units and the three importers. The
  3,654-line main-window test module is split into eight feature modules, and
  the two-port math is cross-checked against scikit-rf. Every catalog template
  now has a machine-readable evidence entry, rendered into the validation plan.
  The solver is also cross-checked against nec2++ for three canonical
  geometries, physical invariants cover power balance, pattern-integral
  directivity, and rotation invariance, and weekly mutation testing runs
  `mutmut` on the design formulas and intent. A curated MMANA corpus with a
  checksum manifest now covers structural regression and a NEC2C smoke run,
  and analytical closed forms cover the short-dipole and small-loop limits.
  The 1,442-line nec2c adapter test module is split into four modules.
- Added `docs/EXPERIMENTAL_VALIDATION_PROTOCOL.md`, the level 3 measurement
  protocol for a half-wave dipole with an IEEE 149-2021 / GUM uncertainty
  budget. No measurement is recorded yet.

### Changed

- Multiband results now place the **Bands** tab first and add a **Band**
  selector above the result tabs, available from every view. Double-clicking a
  band opens its impedance/SWR charts, and those titles include the active band
  name.
- Saving a project now serializes and compresses the payload in a worker thread
  and shows a modal **Preparing project...** progress dialog for large projects.
  The payload is serialized once and then written atomically, so the Qt event
  loop stays responsive and Linux does not show a “not responding” warning.
- Raised the compressed project-size warning to **32 MB** and the hard limit to
  **64 MB**, keeping room for longer sweeps and high-resolution pattern
  snapshots. The save warning and compaction guidance are unchanged.
- Added a published **102 in mobile-whip** example to the loaded-vertical
  generator: 14.1 MHz, 2.5908 m radiator, and a 4.511 µH base loading coil from
  K7MEM/ARRL. The `loaded_vertical` evidence level moved to B for that preset
  only; arbitrary loaded verticals remain experimental.
- Added a **Cushcraft AR-6** starting-dimensions preset to the Ringo generator:
  52 MHz, 3.05 m radiator, 0.33 m ring, and a 0.05 m ring-height modeling
  assumption. It remains evidence level C because the matching-ring model is
  simplified.
- The vertical generator now supports a **capacitive top hat**: a configurable
  number of horizontal wires at the radiator top, with radius and wire count.
  The hat survives the custom-wire round trip.
- The loaded-vertical editor now exposes **coil Q** and keeps it consistent with
  the series resistance and coil reactance. Q remains an input aid; vehicle
  ground and mast effects remain outside the model.
- Reviewed the remaining level C templates for Phase 5. `ringo`, `fan_dipole`,
  `random_wire`, and `custom` were not promoted because the published sources
  describe different geometries or installation details than the current
  models. The review, sources, and model gaps are recorded in
  [`docs/EVIDENCE_AUDIT.md`](docs/EVIDENCE_AUDIT.md).
- Audited the experimental templates in
  [`docs/EVIDENCE_AUDIT.md`](docs/EVIDENCE_AUDIT.md). The delta loop, vertical,
  and inverted-V generators moved from evidence level C to B after checking
  their published length rules, with explicit tolerances and regression tests.
  The J Pole and Slim Jim estimators also moved from C to B after checking
  M0UKD's 0.75λ section rule and the G2BCX 2 m Slim Jim length. The end-fed
  estimator moved to B after matching the ARRL EFHW kit's 66/33/16 ft lengths
  and PA9X's 0.05λ counterpoise rule. The trap dipole moved to B after checking
  the W3DZZ 33/22 ft sections and its 7.1 MHz, 5.024 µH / 100 pF traps. The
  sloper moved to B after matching the Chameleon LEFS Feather's 66.5 ft
  radiator and 3 ft → 25 ft deployment. The doublet moved to B after checking
  the 94 ft radiator and 41 ft of 450 Ω line. The Zepp moved to B after
  replacing the simplified transmission-line model with the published
  3/4-wave, real two-conductor stub topology. The remaining experimental
  templates and their next evidence needs are documented.
- CI now pins every action by commit SHA, runs `uv lock --check` and
  `pip-audit --skip-editable`, and Dependabot tracks GitHub Actions and Python
  dependencies. Dependabot keeps PySide6 in its own group so Qt upgrades are
  evaluated deliberately instead of riding along with routine updates.
- Updated pydantic from 2.14.1 to 2.14.3, which includes the 2.14.2 security
  fixes. PySide6 is handled in a separate update.
- Updated PySide6 from 6.9.3 to 6.11.3 after the full CI matrix and a repeated
  shutdown stress of the main window and pyqtgraph views. The 6.12 exclusion
  remains; ADR-0025 records the evaluation and the upgrade procedure.
- Ruff now enables bandit (`S`), pytest-style (`PT`), `T20`, and annotation
  (`ANN`) checks. Runtime assertions in the source were replaced with explicit
  guards or early returns; tests exempt `S101`/`PT011`/`ANN`, and CLI entry
  points exempt `T201`.
- Catalog evidence labels now follow the evidence registry: the J Pole, Slim
  Jim, end-fed, inverted-V, OCFD, and vertical entries say “published starting
  dimensions” instead of “experimental”. Tests cross-check estimator support,
  catalog identity, New Antenna routes, and both language tables.
- Renumbered the duplicate ADR 0014: undo/redo is now ADR 0024. Added tests for
  unique, contiguous ADR numbering and matching headings.
- All 75 UI modules, including the antenna wizard, are now type-checked: the
  mypy UI ratchet is closed.
- **New Variant...** is now **New Design in Project...**, and the design
  selector, menus, comparison dialog, and history labels use “design” instead of
  “variant”.
- The basic wire/folded/loop template field is read-only and has a **Change...**
  button. **Change Template...** preselects the current catalog entry and still
  requires confirmation before replacing the design.
- Specialized antenna generators now choose the template first and ask for the
  project name afterwards, with a suggested band/template name.
- **Simulation pattern** and **Band analysis** now live in a collapsible
  **Advanced simulation** section below the design form. The design form starts
  directly under the Apply/Estimate/Optimize action bar.
- **Apply design** remains an explicit save without simulation, while
  **Simulate** saves the current form values and runs the solver.
- Fan dipole **Simulate** now analyzes every distinct element band
  automatically and opens the Bands tab, so a 10 m element is no longer hidden
  by a 40 m-only sweep. The estimator warning and user guide now call out the
  V-angle/coupling shift on the highest band.
- The fan-element optimizer now has a synchronized Band selector and a Band
  column, preselects the band active in the Bands tab, warns when the target
  frequency and selected elements disagree, and recomputes segmentation for the
  target frequency. Its default frequency is the lowest element band rather than
  a stale design frequency, and it explains that unchecked elements still
  affect the antenna.
- Project schema version 6 adds optional per-design analysis band plans on top
  of the version 5 transformer fields. Older projects migrate without changing
  their geometry or results.
- Project schema version 5 adds optional OCFD/custom feed-transformer ratios
  on top of the version 4 band/batch run metadata. Older projects migrate
  without changing their geometry or results.
- Project schema version 4 adds optional `band_id` and `batch_id` metadata to
  simulation runs. Version 3 projects migrate without changing their data.
- The design panel now has one action bar (**Apply design**, **Estimate
  Dimensions...**, **Optimize...**) and a compact global **Simulation pattern**
  group. The duplicate per-form pattern controls and bottom Apply/Optimize
  buttons were removed.
- Pattern resolution and pattern-frequency controls are now global to every
  antenna family. Generated dipoles, Yagis, loops, verticals, and future
  templates use the same Auto (max)/Auto (bands) policy as the G5RV and get 1°
  or 2° band snapshots when they fit the compressed budget.
- The 3D pattern view draws a coarser display mesh while rotating or zooming
  and returns to the full-resolution wireframe when the movement stops. This
  keeps 1° and 2° patterns responsive without removing stored data.
- Project files are now compact JSON compressed losslessly with gzip. Existing
  plain-JSON projects still load. The 32 MB hard limit and 20 MB warning apply
  to the compressed file, so a 200-point G5RV with 13 band snapshots at 2° is
  about 8 MB, and nine band snapshots at 1° is about 20 MB.
- The project storage budget is now 24 MB compressed, with a save warning above 20 MB and
  a 32 MB hard limit. This lets pattern-rich runs keep more band snapshots and
  a finer angular step: a 200-point G5RV with 13, 17, or 21 snapshots uses
  5°, and with five snapshots it can use 2°.

### Fixed

- Yagi folded and beta/hairpin matching hardware can no longer be saved with
  spacing or length smaller than twice the driven-element radius. Changing the
  Yagi frequency no longer rescales the matching hardware. Schema 15 repairs
  previously saved undersized values to four radii spacing and eight radii
  hairpin length, which avoids overlapping conductors and NEC-2 segment-length
  warnings that produced negative input resistance.
- Yagi optimization now keeps the element count fixed. It only adjusts the
  selected element lengths and boom gaps; it no longer adds or removes
  directors.
- Yagi optimization now preserves the starting director-length taper and
  inter-director gap trend. Adjacent directors and gaps cannot invert the
  initial shape, so a DL6WU start stays DL6WU-like and the NBS preset keeps its
  published small non-monotonicity.
- The Bands page no longer appears as a floating table over the results tabs
  before the first multiband analysis. It stays hidden until the analysis
  inserts it.
- Finite-ground simulations with conductors at or near ground level now add a
  warning that the 1 cm NEC clearance is not a buried-wire model. The warning
  explains that impedance and gain can be numerically unreliable and points to
  a sensitivity study, measurement, or a higher radial plane.
- Vertical top-hat parameters are now persisted in schema version 8. Version 7
  projects that already contain `top-hat-*` wires migrate the radius and wire
  count from the saved geometry instead of failing the consistency check.
- Simulations with negative input resistance are no longer marked completed
  without gains. They report a diagnostic explaining that the passive model is
  invalid and that the radial height or ground model must be corrected; the
  pattern views no longer appear silently empty.
- Switching the language now retranslates every antenna-family editor, not only
  the dipole form. The Preferences dialog applies the change consistently to
  all open forms.
- Switching display units now converts every antenna-family editor and keeps
  its physical dimensions; previously only the dipole form and the sketch
  changed units. **Ctrl+,** opens the Preferences dialog.
- The main editor panel now reserves enough width for the widest family form
  at the active language and font preset, avoiding a horizontal scrollbar at
  **Large**. The Preferences dialog uses translated OK/Cancel labels.
- The G5RV, ZS6BKW, Zepp, and Doublet dialogs now show wire radius in mm or
  inches. The custom-wire table and the design comparison table also use the
  selected display units for radius, diameter, lengths, and heights.
- Fan-dipole, Yagi, and load tables size their columns to their headers, so
  Spanish headers are no longer clipped at **Large**.
- The Yagi editor now populates its driven-element selector when it starts from
  the default preset.
- Three translation keys used by the UI were missing and rendered as raw keys:
  `dialog.all_files`, `error.import_nec`, and `measurement.impedance_error`.
  The antenna wizard placeholder now uses `wizard.project_placeholder`.
- Estimator edge cases found by the new geometry property tests: OCFD and
  horizontal Yagi/Moxon estimates with zero height now clamp to 0.01 m, and
  vertical Yagi/Moxon estimates whose elements would cross the ground raise a
  clear unsupported-estimate error instead of a domain validation error.
- Five-eighth-wave vertical estimates now apply the same end-effect factor as
  the quarter- and half-wave estimates, matching the ARRL 585/f practical
  formula. The estimated radiator is about 5% shorter than before, and the
  estimate is labeled empirical instead of physical.
- A NEC deck line containing only separators (for example `,`) no longer raises
  an `IndexError`; it is ignored like a blank line. Imported files are untrusted
  data, so the parser now reports malformed cards as `ValueError`.
- `normalize_azimuth_degrees` now returns `0.0` for tiny negative angles. The
  modulo result (`360.0 - 1e-15`) rounded to exactly `360.0`, which violated
  the documented `[0, 360)` range.
- Added segmentation diagnostics `segmentation.segment_too_short` and
  `segmentation.radius_ratio_low`, with the computed Δ/λ and Δ/a in the
  message, following the NEC-2 User's Guide modeling guidelines. The solver
  integration suite now includes a segmentation-convergence study of the
  30.48 m dipole in free space and over finite ground.
- Frequency-first estimator geometries stay above ground: inverted-V estimates
  widen the included angle (and raise the apex if needed), fan-dipole estimates
  use distinct progressively narrower element angles, and end-fed estimates
  clamp an unreachable end height. Fan dipoles now reject two elements with the
  same included angle because their wires would overlap.
- Ground-mounted vertical radials are raised 1 cm in the NEC deck. A freshly
  estimated vertical with finite ground previously failed with `nec2c exited
  with code 255` because the radials lay exactly on the ground plane. Wires
  below ground now produce a clear `geometry.below_ground` diagnostic instead.
- NEC `LD` and `TL` cards now use local segment numbers within each wire tag;
  loads on wires after the first were previously mapped to global segment
  numbers.

## [0.1.0] - 2026-11-02

### Added

- Project-level Undo/Redo for applied design, variant, template, load, feed-line,
  matching-network, measurement, and estimator changes, with protected
  simulation-run history.
- Hover cursors on impedance, SWR, pattern, currents, and measurement charts
  with nearest-point readouts and theme-aware overlays.
- Menu ergonomics: standard File/Edit order, Change Template in the Design
  menu, grouped Import/Export entries, and Language/Units under Tools.
- The design panel now leads with **Estimate Dimensions...** as the primary
  frequency-first action; Change Template remains in the Design menu and keeps
  its Ctrl+Shift+T shortcut.
- Single-sourced package version from `antennadesk.__version__`, About-dialog
  version display, and a Hatchling wheel/sdist build with a package smoke-test
  workflow.
- Native release packages: Linux AppImage, Debian `.deb`, and Windows onedir
  zip recipes with bundled `nec2c`, application icons, SHA-256 checksums, and
  optional GPG or Authenticode signing hooks.
- Tag-triggered release workflow that builds the wheel/sdist, AppImage, Debian
  package, and Windows zip and attaches them to the GitHub release.
- Shared PyInstaller bundle builder and a packaging cleanup script so local
  validation can run in temporary directories without orphan build artifacts.
- Optional release signing: detached GPG signatures for every artifact,
  embedded AppImage signatures, and Windows Authenticode for both executables.
- `antennadesk --version` for packaged-application smoke tests.
- Frequency-first dimension estimation for dipoles, folded dipoles, loops,
  verticals (1/4λ, 1/2λ, and 5/8λ), inverted-V, fan dipoles, end-fed, OCFD,
  J Pole, Slim Jim, Ringo, Yagi (2–32 elements from the DL6WU trimming
  reference), and Moxon (Cebik reference scaled by frequency).
- `Design → Design from Frequency...` dialog with assumptions, warnings,
  confidence, sources, dimension table, apply-to-current-design flow, and an
  optional one-step handoff to the matching optimizer or synthesis dialog.
- Applied estimates persist their method, confidence, assumptions, warnings,
  tolerance, and source identifiers as optional design provenance; editing the
  design clears it.
- Estimator provenance is shown in HTML reports and PDF construction/simulation
  sheets alongside the design dimensions.
- Yagi frequency changes rescale the current element table by wavelength, and a
  warning flags element dimensions that do not match the current frequency.
- Traceable estimator contract with source identifiers and explicit unsupported
  cases for custom geometry and Yagi element counts outside 2–32.
- Phase 1 domain model for units, geometry, conductors, feed points, ground
  models, environments, and horizontal half-wave dipoles.
- Immutable project and design-variant model with validation.
- Versioned JSON project format with atomic saves and a migration framework.
- Create, save, open, and edit-length use cases.
- A 40 m dipole example project.
- Unit, integration, and acceptance tests for Phase 1.
- Architecture, domain-model, and validation-plan documentation.
- CI for lint, formatting, type checking, and tests on Linux and Windows.
- Phase 2 simulation model: frequency plans, far-field requests, segmentation
  policy, solver metadata/capabilities, and normalized results.
- `nec2c` solver adapter with input generation, process execution,
  cancellation, timeouts, output parsing, SWR normalization, currents, power
  budget, and far-field patterns.
- Conductor conductivity (`LD 5`) support, toggleable for perfect-conductor
  reference cases.
- Reference validation against the NEC-2 User's Guide examples.
- A reproducible reference-simulation script for the production adapter.
- Phase 3 guided GUI: main window, dipole wizard, design panel, 2D geometry
  view, asynchronous simulation with cancellation, results charts, and
  diagnostics.
- English/Spanish UI and metric/imperial presentation units.
- PySide6 and PyQtGraph dependencies, with PySide6 pinned below 6.10 to avoid a
  shutdown crash observed with 6.12.
- Offscreen UI tests with `pytest-qt`.
- Dimensioned construction-sketch geometry view with total and per-leg
  dimensions, height dimension, feed/center/end markers, ground hatching,
  scale bar, and azimuth compass.
- Elevation and plan view modes, plus optional vertical exaggeration for
  low-height layouts.
- Phase 4 design-variant management: add, rename, delete, and switch variants.
- A/B comparison dialog with metrics, SWR overlay, and gain-pattern overlay.
- Currents tab and resonance markers on impedance/SWR sweeps.
- CSV export and self-contained HTML reports with inline SVG charts.
- Phase 5 bounded dipole length optimization with min/max limits, target
  reactance, evaluation log, and ±10/25 mm sensitivity probes.
- Optimization dialog with worker thread, cancellation, and apply-best-length
  flow.
- Printable/HTML construction sheet with leg lengths, feed position, simulated
  result, resonance, and construction notes.
- Phase 6 first slice: vertical center-fed dipole template and orientation
  selector in the form and wizard.
- Project schema version 2 with dipole orientation and an explicit v1 to v2
  migration.
- Vertical geometry sketch, orientation-aware construction sheet, and NEC-2
  Example 3 reference validation.
- Persisted simulation runs in project schema version 3, including normalized
  results, diagnostics, and raw solver text; v2 projects migrate to an empty
  run list.
- Simulation save/reopen flow: the latest run per variant is restored for
  comparison, reports, and construction sheets across sessions.
- Solver integration jobs on Linux and Windows.
- Phase 6 second slice: parametric folded-dipole and regular-polygon loop
  templates, antenna-type union, and type/geometry consistency validation.
- Antenna-type selector with conditional spacing/sides fields; design
  conversion updates the derived geometry and switches multi-wire designs to
  Plan view.
- Generic New Antenna wizard with type selection, type-aware geometry and
  review pages, and the current design type as the initial choice.
- Additive schema v3 payloads for folded dipole and loop parameters, with
  round-trip and mismatch tests; existing wire-dipole documents are unchanged.
- Multi-wire geometry rendering, type-aware construction sheets and HTML
  reports, and mixed-geometry comparison.
- Geometry-view roles clarified: Plan carries construction dimensions (including
  feed legs and folded/loop measurements); Elevation shows installation height,
  feed height, and ground for all geometries. Folded plans show two elements
  with exaggerated spacing, and elevation adds a two-conductor section; loop
  plans show a circle with diameter, circumference, and side count fitted to
  the view, and loop elevation shows a vertical edge-on line with bottom height
  and diameter.
- Folded dipole and loop solver integration tests run against `nec2c`; these
  currently provide topology and sanity coverage, not independent impedance
  references.
- UI diagnostics for known stable codes are localized; the raw English
  solver message remains in the tooltip.
- Native PDF construction sheet with type-aware dimensions, simulation rows,
  notes, and footer.
- Native PDF simulation report with design/configuration tables, impedance
  table, resonance, SVG-derived charts, diagnostics, and footer.
- Compact simulation history action that keeps only the latest run per design,
  reducing project size.
- Save-time warning when a project exceeds 8 MB and a clear block above the
  10 MB native-file limit.
- Independent ARRL Antenna Book reference checks for free-space dipole gain
  and the folded-dipole gain/pattern/resistance relationship.
- Far-field pattern CSV export with frequency, angles, gains, polarization,
  and E-field components, plus PNG export of the current pattern view and
  geometry view.
- Custom straight-wire antennas with a coordinate editor, persistence, and
  simulation flow; optimization is disabled for custom designs.
- Practical NEC-2 deck import (GW, EX, FR, GE/GN, LD 0/1) into custom designs,
  with warnings for unsupported cards.
- Basic MMANA-GAL `.maa` geometry/source import into custom designs; ground and
  loads are explicitly reported as not imported.
- NEC import accepts comma-separated cards; custom wire editing reports short,
  overlapping, and crossing wires.
- Maximum-gain and maximum-efficiency optimization objectives, a weighted
  balanced SWR + gain objective, an experimental ground-radial wire generator
  in the custom editor, an ARRL free-space quad-loop resistance reference, load
  markers in Plan/3D geometry views, and conversion from a template to custom
  wires.
- Configurable pattern resolution (10°, 5°, 2°, or 1°) with point-count
  estimates, and a 100-point default for the frequency sweep.
- Series and parallel RLC loads on wires: validation, load editor,
  design/persistence support, NEC `LD 0`/`LD 1` export, and
  report/construction-sheet rows.
- Isometric 3D geometry view with ground grid, feed marker, axes, and scale.
- Polar pattern diagram in the Pattern tab with selectable azimuth/elevation
  cuts, alongside the existing line chart. The UI requests a full phi sweep.
- Projected 3D radiation-pattern wireframe in a separate Pattern sub-tab.
- Azimuth polar plots show the antenna direction and default to the
  highest-gain elevation cut; above-ground elevation cuts use open arcs to
  avoid a misleading closed lobe.
- Per-wire segmentation overrides and a feed-aligned count heuristic; the UI
  derives counts from the selected model, gives short folded connectors at
  least three segments, and persists the overrides additively in schema v3.
- Palette-aware diagram theme: the geometry sketch and pyqtgraph charts follow
  the GUI light/dark palette, including backgrounds, axes, labels, grids, and
  series colors, with runtime updates when the palette changes.
- Renderer-neutral geometry scene and orthographic view policy: the sketch now
  projects the canonical wire model instead of synthesizing circles or lines
  per antenna type, with true front/plan views, shape-aware auto-selection,
  collision-aware dimension placement, detail insets, and a scriptable scene
  that can later feed SVG, PDF, or DXF export.
- Semantic construction dimensions for loops, folded dipoles, J Pole/Slim Jim,
  Ringo, Yagi, Moxon, end-fed, inverted-V, fan dipole, vertical, OCFD, and
  generic custom wires, including a gap detail inset for Slim Jim, a spacing
  detail inset for closely spaced folded dipoles, Moxon tip/gap dimensions,
  and a top inset for Ringo/radial verticals.
- Legacy custom generator designs keep their semantic Yagi/Vertical/summary
  labels instead of falling back to a generic wire count.
- The geometry header reports when low-priority dimensions had to be hidden
  for space at small window sizes.
- Vector geometry export to SVG and PDF from the same scene used by the
  on-screen sketch.
- `docs/GEOMETRY_PRESENTATION.md`: normative presentation contract, required
  tests, anti-patterns, and Definition of Done for new antenna families.
- Contract tests covering wire preservation, default views, dimension validity,
  layout collisions, presentation-type registration, and catalog routing for
  both New Antenna and Change Template.
- Angular construction dimensions for inverted-V and fan-dipole included
  angles, with collision-aware arc and label placement.
- Layered DXF export of the current geometry scene, including wires, feed/load
  markers, linear dimensions, angular dimensions, and a title, using `ezdxf`
  (MIT, GPL-3.0-compatible).
- Deterministic scene snapshots for every antenna family and 2D view, with an
  explicit update command for intentional shape changes.
- Performance-safe simulation defaults: 0.05λ segmentation target and 31-point
  sweeps for generated templates, fixing 60-second timeouts on large radial
  vertical models while keeping reference cases explicitly fine-segmented.
- Interactive isometric geometry rotation with mouse drag and double-click
  reset.

### Changed

- Release signing is optional and deferred for the initial release. Unsigned
  native packages are published with SHA-256 checksums; GPG and Authenticode
  hooks remain available for later releases.
- Refreshed the roadmap, README, architecture, domain-model, validation-plan,
  and user-guide status to reflect the completed catalog, estimators,
  measurements, optimization, matching, and packaging work.
- Removed redundant New Antenna, Open Project, and Save toolbar buttons; the
  actions remain available in the File menu and by keyboard shortcut.
- Added an optional uniform feed line with characteristic impedance, length,
  velocity factor, matched loss, transmitter-side impedance/SWR, project/run
  persistence, diagnostics, and dialog integration.
- Added a parametric Yagi generator with an editable element table, driven
  element selection, and an NBS TN-688 5-element starting preset.
- Added an experimental inverted-V generator with apex height, leg length,
  included angle, azimuth, geometry preview, and editable custom-wire output.
- Consolidated antenna creation into a searchable **New Antenna** catalog with
  an Antenna Type selector and family grouping; removed per-type New menu
  entries.
- Separated antenna Family from Template in the design panel, including
  generated custom designs.
- Reorganized the menu bar into File, Design, Simulation, Tools, Language,
  Units, and Help, with Import/Export, Variants, and Custom Wires submenus.
- Added an experimental vertical generator with an optional radial plane and
  catalog entry.
- Added generator editing for inverted-V designs, automatic elevation view for
  vertical-plane multi-wire geometry, and 100-point sweep controls for custom
  and generated designs.
- Added Change Template to replace the current design from the antenna catalog.
- Generalized Edit Generator to Yagi and vertical designs by reconstructing
  their parameters from custom geometry.
- Inverted-V now defaults to finite ground, and the 3D pattern view draws the
  ground plane for grounded models.
- Localized ground and material selector labels in the generator and custom
  antenna dialogs.
- Added drag rotation, wheel zoom, and double-click reset to the 3D radiation
  pattern view.
- Clip below-ground pattern points from the 3D view for grounded models.
- Fix the 3D projection so positive height is drawn above the ground plane in
  both pattern and geometry views.
- Increase the default radiation-pattern resolution from 10° to 5°, doubling
  the angular points per axis.
- Raise the vertical generator's default base/radial-plane height to 0.25 m to
  avoid numerical instability over finite ground.
- Added an experimental off-center-fed dipole generator with feed-offset,
  catalog, editing, and persistence integration.
- Promoted OCFD to a first-class template with an inline design-panel editor and
  native project persistence.
- Promoted Yagi, inverted-V, and vertical generators to first-class templates
  with inline editors, native persistence, and reporting support.
- Added inline editing, schema round trips, and reporting coverage for all
  first-class generators.
- Added delta-loop and quad-loop catalog presets that initialize the loop editor
  with three or four sides.
- Added an experimental first-class Moxon rectangle generator with inline
  editing, catalog, persistence, and reporting support.
- Added an experimental first-class fan dipole generator with editable pairs,
  catalog, persistence, and reporting support.
- Added an experimental first-class end-fed wire generator with optional sloping
  geometry, catalog, persistence, and reporting support.
- Added experimental first-class J Pole and Slim Jim generators with inline
  editors, catalog, persistence, and reporting support.
- Added an experimental first-class Ringo vertical with a base matching ring,
  catalog, persistence, and reporting support.
- Raised J Pole and Ringo default base/ring heights to 0.25 m so their ground
  connectors do not lie in the finite-ground plane.
- Added dedicated J Pole and Slim Jim plan/elevation views with radiator, stub,
  spacing, and template-specific labels.
- Fixed Slim Jim geometry headers when the antenna model name is the generic
  variant name.
- Corrected Slim Jim topology: a folded rectangle with horizontal top and
  bottom connectors and a gap in one vertical leg between the radiator and
  matching stub.
- Placed the impedance and SWR charts side by side and reduced the default
  geometry pane height to give results more room.
- Change Template is always reachable from the Design menu and with
  Ctrl+Shift+T.
- Added VNA CSV import for R/X, S11 real/imaginary, and magnitude/phase data,
  persisted measurements, measurement conditions/reference plane, and a
  measured/simulated SWR tab.
- Persist generator metadata (`generator_id`, `generator_name`) in custom
  designs and show it in the custom design panel.
- Fixed NEC `EX` source segment numbering for feeds on tags other than the
  first wire.
- Length optimization is generalized to the primary dimension: wire/folded
  element length or loop circumference. `EditDipoleLength` remains limited to
  wire dipoles.
- Optimization objective selector: target reactance, minimum SWR, maximum SWR
  bandwidth, maximum power gain, maximum efficiency, or balanced SWR + gain,
  with objective-specific limits, weights, and grid resolution.
- Added bounded two-variable impedance synthesis for OCFD, J Pole, and Slim Jim
  designs. It searches length/feed ratio or radiator/feed-offset (stub for Slim
  Jim) over user bounds, evaluates at the target frequency, and applies the best
  dimensions for a full validation sweep.
- Added a target-impedance objective to dimension optimization. It accepts a
  selectable complex target `R + jX` and ranks candidates by impedance error;
  OCFD and end-fed wire designs can now be length-optimized against that
  target.
- Optimization and synthesis result tables are ranked from best to worst by the
  active objective, with a visible rank column, the original evaluation number,
  and failed evaluations last. Synthesis rows also show the complex impedance
  error against the target.
- Measurement comparison now plots measured and simulated SWR, resistance,
  reactance, or impedance magnitude, and reports measured/simulated series
  resonances with their frequency difference.
- Measurements can now be edited (metadata and conditions) and deleted from
  the Measurements tab, with project persistence and confirmation before
  deletion.
- Added a reference-backed Moxon validation test using the published 20 m wire
  dimensions and free-space gain, impedance, and front-to-back values from
  L. B. Cebik, W4RNL.
- Added a published/heuristic OCFD sanity test for the 0.2 L feedpoint
  resistance range and the documented trend toward lower R as the feed moves
  toward the centre.
- Fixed the frequency-first J Pole estimate: the non-folded J Pole now uses the
  total 3/4-wave height and a 40% stub feed point; Slim Jim keeps its half-wave
  radiator estimate.
- Added parameterized domain and NEC smoke tests for every frequency-first
  estimator, including folded dipole, end-fed, OCFD, Ringo, J Pole/Slim Jim,
  Yagi, Moxon, loops, verticals, inverted-V, and fan dipoles.
- Recalibrated the Ringo estimator for the simplified Ringo geometry, improving
  the 146 MHz estimate from a very high SWR to approximately 1.3.
- Added a **Load 20 m wire reference preset** button to the Moxon editor and
  marked that preset as reference-backed in the catalog.
- Added a bounded multi-variable coordinate-search optimizer in the domain.
- Added the first multi-element Yagi workflow: select element lengths and boom
  gaps, set a target R/X, constrain the search around the current dimensions,
  enforce a minimum gap and keep the first element fixed, review a ranked
  evaluation table, and apply the best geometry for a full simulation. Radii
  remain fixed in this slice.
- Yagi optimization now supports target impedance, maximum power gain, and
  maximum front-to-back ratio objectives. Gain and F/B evaluations use the
  far-field pattern; the ranked table reports the selected objective.
- Added bounded fan-dipole element-length optimization against a target
  impedance, with selectable elements, search bounds, ranked evaluations, and
  apply-and-simulate flow.
- Added bounded Moxon optimization of width, spacing, reflector tip, and driven
  tip for target impedance, maximum gain, or maximum front-to-back ratio.
- Unified the Yagi, fan-dipole, and Moxon element optimizers on a shared
  bounded evaluation engine while keeping their template-specific dialogs.
- The shared engine now drives a generic multi-element dialog used by Yagi,
  fan-dipole, and Moxon optimization, with template-specific variables and
  builders.
- Added a weighted multi-objective mode for multi-element optimization,
  combining gain, front-to-back, SWR penalty, and efficiency with transparent
  user weights.
- Multi-objective results now include a Pareto rank column, with successive
  non-dominated fronts computed from the selected metrics.
- Optimization result rows can be selected to apply a specific candidate or
  Pareto compromise instead of only the best weighted score.
- Multi-element optimization supports integer variables; vertical radial count,
  loop side count, and Ringo ring sides are searched discretely.
- Yagi optimization can include element count as a discrete variable. Added
  directors follow the DL6WU reference scaled to frequency, the driven element
  is preserved, and gaps keep a fixed 0.1 m minimum.
- Loop optimization now preserves the selected loop shape and side count, and
  documents that full-wave loops normally need a balun or matching network for
  a 50 Ω system.
- The loop estimator applies a NEC-2-calibrated polygon correction, so quad,
  delta, and generic loops start near resonance instead of several percent
  short. The loop optimizer starts its target resistance at 100 Ω for a 2:1
  balun.
- Target-impedance searches report SWR relative to the target resistance;
  folded dipoles, loops, OCFDs, and 5/8-wave verticals now show their matching
  limitation explicitly.
- Removed the obsolete template-specific optimization dialogs and workers; the
  generic dialog is now the only multi-element optimization UI.
- Replaced the separate optimization menu actions with one **Optimize...**
  action that dispatches from the current template, plus an Optimize button in
  the design panel. Frequency-first estimation is now **Estimate Dimensions...**.
- Added the AntennaDesk application icon and a Linux desktop-entry file for
  release packaging.
- Added a lossless L matching network evaluated before the feed line, with
  project/run persistence and impedance/SWR diagnostics.
- The matching-network dialog can auto-design an L section from a load R/X at
  the design frequency, or report that a single L section cannot match it.
- Matching-network support now includes manual Pi and T topologies with
  project/run persistence and input-impedance evaluation.
- Matching networks can include component loss through a Q factor; loss is
  reflected in input impedance/SWR, not in reported antenna gain.
- Added a parallel-trap helper to the load editor that computes capacitance from
  inductance and resonant frequency.

- Documentation and README are now in English.

### Fixed

- Geometry view now resets zoom, pan, and vertical exaggeration when the model
  changes, so switching antennas always fits the new drawing.
- Change Template now handles the Delta loop and Quad loop catalog entries and
  opens the loop wizard with 3 or 4 sides instead of silently keeping the
  previous design.
- Quad and delta loops are drawn as their real polygons; vertical loops use a
  front view and their plan view is correctly shown edge-on.
- End-fed sloping wires, Yagi/Moxon elements, Ringo rings, J Pole stubs, and
  loads are no longer collapsed or hidden by type-specific shortcuts.
- Slim Jim feed offset is measured from the stub base, and loop top height is
  exact for odd side counts and rotated azimuths.
- End-fed wire length now means the physical conductor length, not just its
  horizontal run; steep slopes are rejected when they exceed the wire length.
- Dimension labels are measured, prioritized, and placed with collision
  avoidance; units and translations are rebuilt on change.
- The geometry compass labels the X/Y axes, matching the documented +X toward
  +Y azimuth convention.

## [0.1.0.dev0] - 2026-10-29

### Added

- Phase 0 solver spike selecting `nec2c 1.3.3` as the external NEC-2 engine.
- Reproducible reference cases from the NEC-2 User's Guide.
- Linux and Windows build scripts, including a Windows portability patch.
- GitHub Actions workflow for the solver spike.
- Project documentation: blueprint, ADR-0001, project decisions, and solver
  evaluation.

[Unreleased]: https://github.com/fsclavo/antenna-desk/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/fsclavo/antenna-desk/releases/tag/v0.2.0
[0.1.0]: https://github.com/fsclavo/antenna-desk/releases/tag/v0.1.0
[0.1.0.dev0]: https://github.com/fsclavo/antenna-desk/releases/tag/v0.1.0.dev0
