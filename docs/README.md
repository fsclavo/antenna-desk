# Documentation index

AntennaDesk documentation is split by purpose. Use this page to find the source
of truth before adding another planning document.

## Source of truth

| Question | Document |
|---|---|
| What are we building, and in what product order? | [`ROADMAP.md`](ROADMAP.md) |
| What are we working on now? | [`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md) |
| Is this antenna template validated? | [`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md), [`VALIDATION_PLAN.md`](VALIDATION_PLAN.md) |
| Why was a technical decision made? | [`PROJECT_DECISIONS.md`](PROJECT_DECISIONS.md), [`ADR/`](ADR/) |
| How is the system structured? | [`ARCHITECTURE.md`](ARCHITECTURE.md), [`DOMAIN_MODEL.md`](DOMAIN_MODEL.md) |
| How do I use the application? | [`USER_GUIDE.md`](USER_GUIDE.md) |
| How do I build and release it? | [`RELEASE.md`](RELEASE.md) |
| How is the solver integrated? | [`SOLVER_ADAPTER.md`](SOLVER_ADAPTER.md) |
| How is the construction sketch generated? | [`GEOMETRY_PRESENTATION.md`](GEOMETRY_PRESENTATION.md) |
| Where do the starting dimensions come from? | [`ANTENNA_DESIGN_ESTIMATORS.md`](ANTENNA_DESIGN_ESTIMATORS.md) |

## Planning

- [`ROADMAP.md`](ROADMAP.md) — product direction, milestones, product backlog,
  and the ordered antenna expansion backlog.
- [`AUTONOMOUS_BACKLOG.md`](AUTONOMOUS_BACKLOG.md) — the only active execution
  queue: dependencies, blockers, acceptance criteria, and the current test
  baseline.
- [`EVIDENCE_AUDIT.md`](EVIDENCE_AUDIT.md) — evidence level, promotion history,
  and remaining experimental templates.
- [`VALIDATION_PLAN.md`](VALIDATION_PLAN.md) — validation workflow and the
  generated evidence table.
- [`PROJECT_DECISIONS.md`](PROJECT_DECISIONS.md) — confirmed product decisions.
- [`../CHANGELOG.md`](../CHANGELOG.md) — released and unreleased behavior
  changes.

## Engineering

- [`antennadesk-development-blueprint.md`](antennadesk-development-blueprint.md)
  — product and architecture blueprint.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — layer boundaries and data flow.
- [`DOMAIN_MODEL.md`](DOMAIN_MODEL.md) — canonical antenna, simulation, and
  project values.
- [`SOLVER_ADAPTER.md`](SOLVER_ADAPTER.md) — NEC process adapter contract.
- [`GEOMETRY_PRESENTATION.md`](GEOMETRY_PRESENTATION.md) — sketch and dimension
  contract.
- [`ANTENNA_DESIGN_ESTIMATORS.md`](ANTENNA_DESIGN_ESTIMATORS.md) — estimator
  sources, assumptions, confidence, and tolerances.
- [`QA_STRATEGY.md`](QA_STRATEGY.md) — test lanes and quality gate.
- [`EXPERIMENTAL_VALIDATION_PROTOCOL.md`](EXPERIMENTAL_VALIDATION_PROTOCOL.md) —
  how experimental templates are validated.
- [`RELEASE.md`](RELEASE.md) — packaging, signing, and release checklist.
- [`../AGENTS.md`](../AGENTS.md) — repository instructions for contributors and
  agents.

## Measurements and plans

- [`MULTIBAND_PERFORMANCE.md`](MULTIBAND_PERFORMANCE.md) — per-band benchmark,
  parallel worker measurement, and architecture decision.
- [`FAN_DIPOLE_CALIBRATION.md`](FAN_DIPOLE_CALIBRATION.md) — fan-dipole
  investigation and the deferred angle work.
- [`MULTIBAND_ANALYSIS_PLAN.md`](MULTIBAND_ANALYSIS_PLAN.md) — implementation
  plan for the per-band analysis architecture.
- [`OPTIMIZER_PHASE_A_PLAN.md`](OPTIMIZER_PHASE_A_PLAN.md) — family optimizer
  foundation (completed).
- [`OPTIMIZER_PHASE_C_PLAN.md`](OPTIMIZER_PHASE_C_PLAN.md) — advanced optimizer
  modes (completed).

## Architecture decisions

- [ADR-0001 — MVP electromagnetic engine](ADR/0001-solver-selection.md)
- [ADR-0002 — Report and data export formats](ADR/0002-report-formats.md)
- [ADR-0003 — Project schema v2 and dipole orientation](ADR/0003-project-schema-v2.md)
- [ADR-0004 — Persist simulation runs in project schema v3](ADR/0004-simulation-run-persistence.md)
- [ADR-0005 — Folded dipole and loop templates](ADR/0005-new-wire-geometries.md)
- [ADR-0006 — Series and parallel RLC loads on wires](ADR/0006-series-loads.md)
- [ADR-0007 — Custom straight-wire designs](ADR/0007-custom-wire-designs.md)
- [ADR-0008 — Feed line as post-processing](ADR/0008-feed-line-post-processing.md)
- [ADR-0009 — Catalog generators and experimental templates](ADR/0009-catalog-and-experimental-templates.md)
- [ADR-0010 — First-class generator templates](ADR/0010-first-class-generator-templates.md)
- [ADR-0011 — Bounded feed-point impedance synthesis](ADR/0011-bounded-impedance-synthesis.md)
- [ADR-0012 — Geometry presentation scene and dimension layout](ADR/0012-geometry-presentation.md)
- [ADR-0013 — Frequency-first dimension estimation](ADR/0013-frequency-first-dimension-estimation.md)
- [ADR-0014 — L-network post-processing and trap preset](ADR/0014-l-network-post-processing.md)
- [ADR-0015 — Realized gain and directivity](ADR/0015-realized-gain-and-directivity.md)
- [ADR-0016 — Transmission line as geometry](ADR/0016-transmission-line-as-geometry.md)
- [ADR-0017 — Simulation storage budget and automatic pattern resolution](ADR/0017-simulation-storage-budget.md)
- [ADR-0018 — T2FD termination and transformer model](ADR/0018-t2fd-termination-and-transformer.md)
- [ADR-0019 — Far-field pattern snapshots decoupled from the impedance sweep](ADR/0019-pattern-snapshots.md)
- [ADR-0020 — Higher project storage budget for pattern-rich runs](ADR/0020-higher-pattern-storage-budget.md)
- [ADR-0021 — Lossless compressed project files](ADR/0021-compressed-project-files.md)
- [ADR-0022 — Multiband analysis by per-band batches](ADR/0022-multiband-analysis-by-band-batches.md)
- [ADR-0023 — Yagi and Moxon horizontal/vertical polarization](ADR/0023-yagi-moxon-polarization.md)
- [ADR-0024 — Project Undo/Redo and chart cursors](ADR/0024-undo-redo-and-chart-cursors.md)
- [ADR-0025 — PySide6 version pin and Qt upgrade policy](ADR/0025-pyside6-version-pin.md)
- [ADR-0026 — Family optimizer descriptors on a shared hybrid engine](ADR/0026-family-optimizer-architecture.md)
- [ADR-0027 — Construction view policy and wire schedule](ADR/0027-construction-view-policy.md)

## Archive

- [`archive/PENDING_WORK_PLAN_2026-11-04.md`](archive/PENDING_WORK_PLAN_2026-11-04.md)
  — superseded phase plan, kept for decision history.
- [`spikes/phase0-solver-evaluation.md`](spikes/phase0-solver-evaluation.md) —
  NEC engine evaluation.
- [`../spikes/phase0/README.md`](../spikes/phase0/README.md) — reproducible
  solver spike.

## Rules for new documents

- Do not create another backlog. Active work belongs in
  `AUTONOMOUS_BACKLOG.md`; product scope belongs in `ROADMAP.md`.
- Evidence changes belong in `EVIDENCE_AUDIT.md` and the machine-readable
  registry, not in a separate plan.
- Once a plan is superseded, move it to `docs/archive/` and link it from this
  index.
- Keep one source of truth per question. Cross-link instead of copying status.

## Authorship

AntennaDesk is developed by Fernando Sclavo (LU2EFI). See
[`../AUTHORS.md`](../AUTHORS.md) for attribution and [`../LICENSE`](../LICENSE)
for the license terms.
