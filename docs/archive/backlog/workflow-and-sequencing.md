# Historical backlog — workflow and sequencing

> **Historical design notes, captured 2026-11-20.** Not current
> guidance. Current status: [`../../STATUS.md`](../../STATUS.md); active
> queue: [`../../AUTONOMOUS_BACKLOG.md`](../../AUTONOMOUS_BACKLOG.md).

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


## Recommended order

**Active product sequence (2026-11-19):** wave 0 of the product trust and
station track (TS1–TS7 and DL9) is **done 2026-11-19**. DL1 and DL2 are done;
DL5 is next. Wave 2 is in progress (DL3/DL6 partial, DL7 spike complete); DL4
and post-1.2 remain queued. The numbered
items below are historical context for completed or blocked work; the queue
table and §Product trust and station wave above are the executable order.

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
    [`ROADMAP.md`](../../ROADMAP.md), not in this queue.
17. **UX32–UX37 are complete.** The frequency-first starting-dimensions work,
    the frequency-semantics ADR, pristine-only recalculation, the quad-beam
    estimator, and the explicit scale action shipped on 2026-11-17 without
    schema or solver changes.
18. **UX38 is complete.** After a successful antenna creation,
    `_create_project_from_parameters()` selects the Design tab. It covers
    catalog templates, Advisor, and Reference Design Library; Advanced-mode
    semantics, Change Template, imports, variants, schema, and solver are
    unchanged. No new translation or help keys. UX39–UX41 are complete.
19. **U1–U5 are complete; U6 documentation is done.** The shared
    `DisplayUnits` formatter, Units preference, adaptive geometry scenes,
    unit-aware scale bar, all family editors and editable tables, the
    optimization/synthesis/auxiliary dialogs, and construction/report surfaces
    are migrated. `docs/archive/qa/QA_PASS_2026-11-18.md` records the automated gate; only the
    manual desktop light/dark and font-scaling checklist remains before the
    release decision.
20. **UX39 is complete (2026-11-19).** Generated single-design sweeps default
    to 100 points, including the two-band and G5RV/ZS6BKW/Zepp presets. Every
    computed point remains in the chart line, table, cursor, and exports; only
    the visible marker layer is bounded. It did not change band-analysis
    defaults, the solver, or the schema; see the UX39 note above.
21. **UX40 is complete (2026-11-19).** One static, deterministic 3D
    far-field wireframe is in the primary report section only; the HTML stays
    Qt-free and the PDF stays vector. It complements, and does not replace, the
    two cuts; see the UX40 note above.
22. **UX41 is complete (2026-11-19).** The optimizer names the modes
    **Single frequency**, **Band-edge sweep**, and **Robust (dimensional
    tolerance)**, shows the resolved band/frequency count and plan source, and
    documents that Analyze Bands is optional and Robust does not change the
    band plan. The unused descriptor capability flags were removed; see the
    UX41 note above.

