# QA strategy

**Status:** proposal; Phase 0 implemented on 2026-11-04
**Date:** 2026-11-04
**Scope:** test infrastructure, static analysis, CI, and numerical/experimental
validation for the current codebase and the next two milestones.

This document complements [`VALIDATION_PLAN.md`](VALIDATION_PLAN.md). That file
defines *what* counts as evidence and the three validation levels. This one
defines *how* the project produces, enforces, and scales that evidence.

## 1. Baseline

Measured on 2026-11-04:

| Fact | Value |
|---|---|
| Collected tests | 1,286 |
| Passing locally with `NEC2C` set | 1,286 passed, 1 skipped (PyNEC) in about 76 s |
| Fast unit-test lane | 713 passed, 1 skipped in about 7.4 s (`pytest -m "fast and not slow"`) |
| Slowest test | 7.4 s (`test_g5rv_default_budgeted_pattern_completes`) |
| UI test isolation | fixed 2026-11-04: deferred deletes were not dispatched, so widgets from one test stayed alive and a later test spent ~66 s in a nested event loop. The teardown in `tests/conftest.py` now closes windows and dispatches `DeferredDelete`; the full suite went from 142 s to 56 s |
| Test files | 153 (88 unit, 11 integration, 1 acceptance, 53 UI) |
| Custom pytest markers | 7 (`science`, `solver`, `cross_engine`, `slow`, `fast`, `golden`, `ui`), with `fast`/`ui`/`solver` applied by path or fixture |
| `parametrize` uses | 32 |
| `skipif` uses | 10 |
| Largest test file | `tests/ui/test_main_window_presets.py`, 828 lines. The 1,442-line nec2c adapter file is split into four modules |
| Source lines | 46,323 total; 30,144 in `ui/` |
| Type-checked lines | ~16,000 strict, plus all 75 `ui/` files under a permissive pass |
| Coverage, full suite with solver (measured) | 85 % total; domain 91 %, simulation 91 %, persistence 94 %, application 92 %, importers 91 %, reporting 87 %, ui 82 % |
| Coverage enforcement | per-package gates in the `coverage` CI job, one point below the measured baseline |
| Timing sensitivity | one UI failure appeared under coverage instrumentation at ~32 % while another pytest process ran concurrently. The polarization commit added deterministic posted-event processing in `tests/ui/helpers.py`; re-verify under coverage before treating it as open |
| ADR files | 24, numbered 0001–0023 with a duplicated `0014` |
| CI | 4 workflows, green; Linux + Windows, Python 3.11/3.12/3.13 |
| Property-based tests | unit round trips, azimuth range, importer fuzzing, all 13 estimator families, and project/migration round trips with Hypothesis 6.170 |
| Mutation testing | weekly `mutmut` on `formulas.py` and `intent.py`: 123/175 killed, 52 message-only equivalents, behavioural score 100 % |
| Benchmarks in CI | 3 report-only cases: NEC output parser, pattern metrics, compressed project save/load |
| Cross-engine numerical checks | 3 free-space cases against nec2++ via PyNEC (dipole, folded dipole, quad loop) |
| Template evidence entries | 25/25 catalog templates, enforced by a test |
| Reference corpus | 12 curated MMANA models, SHA-256 manifest, structural and NEC2C smoke tests |
| Different-method oracles | 4 analytical cases (short dipole R and D, small loop R, half-wave D) |
| Independent RF math oracle | scikit-rf 2.2.0 (BSD-3, dev-only): 11 tests for feed lines, L/Pi/T networks, cascades, and gain |
| Cross-engine oracle | PyNEC 2.3.4 (GPL-3, optional group): 3 free-space cases, 0.1 Ω and 0.05 dB |
| Segment-convergence tests | 2: free space and finite ground |
| Physics-invariant tests | 5: power budget, pattern integral, rotation, and the integration helper (NEC2C) |
| `docs/VALIDATION_PLAN.md` test count | fixed (was 788, now 1,259) |

The suite is in good shape for its size. The gaps are not "more tests"; they are
*stronger oracles*, *enforced thresholds*, and *consistency between code, docs,
and CI*.

## 2. Principles

1. **Test the oracle, not only the code.** A green suite proves execution, not
   correctness. Every numerical assertion must name an independent source and a
   tolerance rationale.
2. **Prefer independent implementations over self-consistency.** A test that
   compares the adapter with itself catches typos, not physics.
3. **CI is the gate; local tooling is the fast lane.** Local checks must not
   report a weaker result than CI.
4. **Thresholds are enforced, not documented.** Coverage, mutation score, and
   evidence levels fail the build when they regress.
5. **No invented numbers.** A reference value enters a test only after being
   verified against the printed or published source.

## 3. Workstreams

### 3.1 Test taxonomy and infrastructure

**Problem.** There are no markers, so there is no way to select a fast lane, a
solver lane, or a science lane. `test_main_window.py` was a 3,654-line monolith
that was hard to navigate and slow to run in isolation; it is now split.

**Change.**

- Register markers in `pyproject.toml`: `science`, `solver`, `ui`, `slow`,
  `golden`. `--strict-markers` is already enabled, so unregistered markers fail.
- (done 2026-11-05) `tests/conftest.py` adds `fast` to unit tests, `ui` to UI
  tests, and `solver` to tests that request the solver fixture.
  `pytest -m "fast and not slow"` runs 713 tests in about 7 s.
- Add `tests/factories.py` with builders for `AntennaModel`, `SimulationSpec`,
  `Wire`, and `SimulationResult` to remove repeated literal construction.
- (done 2026-11-04) Split `tests/ui/test_main_window.py` into feature modules:
  project, simulation, templates, presets, optimization, imports,
  design-from-frequency, and undo. Shared helpers live in
  `tests/ui/main_window_support.py` and the `window` fixture in
  `tests/ui/conftest.py`.
- Replace copy-pasted per-family tests with `@pytest.mark.parametrize` over the
  family registry where the assertion is structural.
- Add `--durations=20` to the local command and track the top ten slow tests.
- Add a flaky-test policy: UI tests wait on Qt signals or an explicit condition,
  never on fixed sleeps. Run the UI suite under coverage in the nightly job to
  expose timing sensitivity, and record the outcome in the job summary.
- Keep the UI teardown order-independent: close windows and dispatch
  `QEvent.Type.DeferredDelete` after every UI test. Without it, a test's runtime
  depends on what ran before, as the 66 s regression showed.

**Acceptance.** `uv run pytest -m "fast and not slow"` runs 713 tests in about
7 s, below the 20 s target. `uv run pytest -m solver` selects the solver tests,
and `uv run pytest -m "not slow"` skips the two G5RV pattern-budget tests. The
main-window suite is split by feature and no main-window module exceeds 1,000
lines. The nec2c adapter suite is also split into mechanics, references,
families, and patterns modules.

**Effort.** M.

### 3.2 Coverage and test strength

**Problem.** Coverage is configured but never measured, so nobody knows which
domain rules are unexercised. Line coverage alone would not prove the tests
catch regressions.

**Change.**

- (implemented 2026-11-04) The `coverage` CI job builds `nec2c`, runs the full
  suite with `--cov --cov-branch`, uploads `coverage.xml`, and gates each package
  with `coverage report --format=total --include=... --fail-under=...`.
  Measured: total 85, domain 91, simulation 91, persistence 94, application 92,
  importers 91, reporting 87, ui 82. Thresholds sit one point below and ratchet.
  The fuzz tests and the NEC deck error-path tests raised importers from 75 to
  91, so its gate moved from 74 to 88.
- A single coverage lane is enough: the full suite with coverage takes 78 s.
  The two-lane plan was based on the pre-isolation 10-minute run.
- (implemented 2026-11-04) `mutmut` 3.8 (BSD-3, Unix only) runs weekly on
  `domain/design/formulas.py` and `domain/design/intent.py`. The first run
  produced 175 mutants, 123 killed (70 %). The 52 survivors are message-only
  mutations of `name=` arguments and `raise ValueError("...")` literals, so the
  behavioural score is 100 % of non-equivalent mutants. The run found three
  real gaps that are now tested: a sub-meter half-wave length, the default
  radial length, and the lower included-angle bound. The weekly job is
  report-only until the operator set is narrowed or the messages are asserted.
- (implemented 2026-11-04) `hypothesis` 6.170 (MPL-2.0, dev-only) covers unit
  round trips, azimuth range, and the three untrusted-input parsers. The fuzz
  tests found two real defects: `parse_nec2_deck(",")` raised `IndexError`, and
  `normalize_azimuth_degrees(-1e-15)` returned `360.0`. Both are fixed with
  deterministic regression tests.
- (implemented 2026-11-05) `hypothesis` also covers the canonical geometry and
  persistence: every estimator family must produce a valid model, and project
  documents plus the v1-to-current migration must round-trip. The geometry
  properties found three real edge cases: OCFD and horizontal Yagi/Moxon
  estimates with zero height, and vertical Yagi/Moxon arrays below ground
  clearance. These are fixed with clamping or an explicit estimator error.

**Acceptance.** CI fails on a coverage regression. The nightly mutation job
reports a score and a survivor list. Each importer has at least one Hypothesis
test and one malformed-input test.

**Effort.** L.

### 3.3 Typing and static analysis

**Problem.** Strict mypy covers `src/antennadesk` minus `ui/`. That leaves
30,144 of 46,323 source lines (65 %) unchecked, including all signal wiring
between the domain and the widgets.

**Change.**

- (implemented 2026-11-04) `mypy_ui.ini` runs a permissive pass over
  `src/antennadesk/ui` with `check_untyped_defs = true`. All 75 files are
  checked in CI; the `exclude` ratchet reached zero. New UI files are checked
  by default.
- (done 2026-11-05) Ruff enables `S` (bandit), `PT` (pytest style), `T20`
  (no `print` in `src/`), and `ANN` (annotations). Tests ignore `S101`,
  `PT011`, and `ANN`; CLI entry points ignore `T201`; runtime assertions in the
  source were replaced with explicit guards or early returns.
- Add an SPDX header check for new source files, matching the existing headers.
- (done 2026-11-05) Keep the PySide6 pin below 6.12 and record the reason in
  ADR-0025, not only in a comment.

**Acceptance.** `uv run mypy` plus `uv run mypy --config-file mypy_ui.ini`
cover `ui/` at the agreed level; ruff reports no new categories; every source
file has an SPDX header.

**Effort.** L (incremental, one module per session).

### 3.4 CI/CD and supply chain

**Problem.** The CI is solid but has avoidable cost and blind spots: no
dependency cache, no coverage, no artifacts on failure, no concurrency
cancellation, and a `paths` filter that ignores `docs/`, `scripts/`, and
`packaging/`. Actions are pinned by tag, not by SHA.

**Change.**

- Replace `python -m pip install uv` with `astral-sh/setup-uv` pinned by SHA,
  `enable-cache: true`, `prune-cache: true`.
- Add `concurrency: {group: ci-${{ github.ref }}, cancel-in-progress: true}`.
- Extend `paths` to `scripts/**`, `packaging/**`, and `CHANGELOG.md`
  (implemented). `docs/**` waits for a docs check, so a typo fix does not run
  the full matrix. `examples/**` is already covered.
- Remove the duplicated Linux 3.12 cell: the `quality` job already runs it.
- Upload `coverage.xml`, `junit.xml`, and the pytest failure log as artifacts.
- Add a `schedule:` nightly job: full matrix, solver on both platforms,
  mutation testing, benchmark, and `reference_data` checks.
- Add Dependabot for `github-actions` and `uv`.
- Pin every action by commit SHA; add a comment with the human-readable version.
- Add `uv lock --check` and an OSV or `pip-audit` scan of `uv.lock`.
- Add a bundle smoke test: build the frozen artifact, run `--version` and
  `--check-solver`, assert the bundled `nec2c` is found.
- License audit: ADR 0001 already records that the `nec2c` fork is GPL-3 and
  that distribution requires shipping the engine source, `COPYING`, and
  notices. The remaining work is to verify that every artifact actually does
  it (`packaging/debian/copyright`, the AppImage, and the Windows bundle), and
  to add a test that fails when the notice files are missing.

**Acceptance.** A change to `scripts/` or `packaging/` runs CI. A failing job
uploads its artifacts. The nightly job is green or files an issue. No action is
referenced by a mutable tag.

**Effort.** M.

### 3.5 Science validation: numerical (level 2)

This is the core gap. The current references cover a dipole, a folded dipole, a
quad loop, a Moxon, a Yagi, and a few NEC-2 User's Guide examples. Everything
else is structural or heuristic.

#### 3.5.1 Segmentation convergence and NEC-2 modeling guidelines

The NEC-2 User's Guide, Part III, Section II
(<https://www.nec2.org/part_3/secii.html>) states:

- segment length Δ ≤ 0.1 λ in general, ≤ 0.05 λ in critical regions;
- Δ < 10⁻³ λ must be avoided;
- Δ/a > 8 for < 1 % error with the thin-wire kernel; the extended kernel
  extends the limit to Δ/a ≈ 2.

`SegmentationPolicy` defaults to 0.05 λ but did not check Δ/a, did not warn about
very short segments, and had no convergence test. The default was an unverified
assumption.

**Change (implemented 2026-11-04).**

- `validate_segmentation` already reported `segmentation.segment_too_long`,
  `segmentation.few_segments`, and `segmentation.segment_too_thin`. It now also
  reports `segmentation.segment_too_short` (Δ < 1e-3 λ) and
  `segmentation.radius_ratio_low` (2 ≤ Δ/a < 8 with the thin-wire kernel), and
  its messages carry the computed Δ/λ and Δ/a. All are warnings.
- `tests/integration/simulation/test_segmentation_convergence.py` sweeps 7 to 81
  segments on the 30.48 m dipole at 4.8 MHz in free space and at 8 m over finite
  ground. For n ≥ 31 it checks R within 0.1 Ω (free space) or 0.15 Ω (finite
  ground) and X within 0.25 Ω or 0.3 Ω of the 61-segment solution; at n = 21 it
  checks the impedance magnitude within 1 %. Refining to 81 segments must not
  increase the error.
- The tolerances come from the observed convergence at the densities the guide
  recommends, not from an independent physical oracle.

**Acceptance.** The default policy is justified by a test, not by a comment.

**Effort.** M.

#### 3.5.2 Physical invariants

These checks need no external reference and catch adapter and normalization bugs
that reference comparisons miss.

**Change (implemented 2026-11-04).**
`tests/integration/simulation/test_physical_invariants.py` runs with `NEC2C`:

- **Power conservation:** `P_in = P_rad + P_loss` within 1 % for a free-space
  dipole with conductor losses, and the reported efficiency matches
  `100 · P_rad / P_in` within 0.1 percentage points.
- **Pattern integration:** integrate the power pattern over the sphere and
  derive directivity; compare with the reported directivity within 0.1 dB. The
  test also checks that a synthetic isotropic pattern integrates to 0 dBi.
  A lossless dipole's directivity and maximum power gain agree within 0.01 dB.
- **Rotation invariance:** rotating the dipole azimuth by 90° rotates the
  pattern and leaves the maximum gain unchanged within 0.05 dB.

**Reciprocity is deliberately omitted.** It requires a two-port antenna model,
which the canonical model does not represent. The link two-ports are validated
separately against scikit-rf. Adding a two-port antenna model only for this
test would be scope without a user-facing capability.

**Acceptance.** Each invariant is an integration test that runs with `NEC2C`.

**Effort.** M.

#### 3.5.3 Cross-engine oracle

`PyNEC`/`necpp` 2.3.4 (GPL-3.0-only, Python ≥ 3.11) wraps `nec2++`, an
independent C++ rewrite of NEC-2.

**Change (implemented 2026-11-04).** PyNEC lives in the optional `cross-engine`
dependency group, because PyPI has manylinux wheels but no Windows ones; the
Windows and macOS matrix never installs it. A dedicated Linux job builds
`nec2c`, syncs the group, and runs
`tests/integration/simulation/test_necpp_cross_engine.py`. The test compares
three free-space geometries (dipole, folded dipole, and quad loop) built from
the same canonical model and segmentation policy:

- impedance within 0.1 Ω;
- maximum gain within 0.05 dB.

Observed deltas are 0.03–0.07 Ω and at most 0.02 dB.

**Limitation, stated explicitly:** `nec2++` uses the same thin-wire EFIE
formulation, so this catches implementation and adapter bugs, not formulation
errors. It does not replace the published references.

**Acceptance.** A dedicated job compares both engines and reports deltas.

**Effort.** M.

#### 3.5.4 Different-method oracle (offline)

To catch formulation-level errors shared by every NEC-2 derivative, compare
canonical cases against a different numerical method: FDTD (openEMS) or FEM.

**Change (implemented 2026-11-04, analytical substitute).** No FDTD or FEM
engine is available in this environment (openEMS and Meep are absent and there
is no package manager access). `tests/integration/simulation/test_analytical_oracle.py`
uses published closed forms instead, which are independent of the moment
method:

- short-dipole radiation resistance `20π²(l/λ)²` and directivity `1.5`;
- small-loop radiation resistance `31171 (N²A/λ²)²`;
- half-wave dipole directivity `1.643`.

The four cases run in 0.3 s with `NEC2C`. The small-loop check uses a 15 %
tolerance because the uniform-current formula is approximate at `C = 0.1 λ`
(observed difference about 12 %); the other cases match within 1–3 %.

**Remaining:** a true FDTD/FEM golden case. It needs an engine, a mesh, and
boundary conditions, and stays an offline task for an environment that can
install one.

**Acceptance.** Two golden cases with a documented method difference and an
explained delta.

**Effort.** L, one-off.

#### 3.5.5 Independent RF math oracle

The feed-line, matching-network, transformer, and cascade math is pure
two-port algebra. `scikit-rf` 2.2.0 (BSD-3) is an independent implementation of
transmission-line physics and network algebra.

**Change (implemented 2026-11-04).** `scikit-rf` is a dev-only dependency.
`tests/unit/domain/test_two_port_skrf.py` builds each circuit with both
libraries and compares the input impedance:

- feed line, lossless and lossy, with velocity factor and matched attenuation;
- L network in both shunt positions;
- Pi and T networks;
- feed line plus matching network cascade;
- `Abcd.__matmul__` order;
- `transducer_gain_db` against the scikit-rf S-parameters.

The eleven tests run in 0.3 s, need no solver, and match the independent
implementation to better than 1e-9 relative. There is no transformer two-port
class to compare; the end-fed ratio is a scalar.

**Cost.** Dev-only: it adds numpy, scipy, and pandas to the development
environment (all BSD-3), not to the application bundle.

**Acceptance.** At least one test per construct, comparing against `skrf` with a
stated tolerance.

**Effort.** M.

#### 3.5.6 Closed-form references for estimators

`docs/ANTENNA_DESIGN_ESTIMATORS.md` requires a source, assumptions, confidence,
and tolerance for every frequency-first estimator. The tests mostly checked
*formula consistency*, not agreement with a published value.

**Change (implemented 2026-11-04, dimension anchors).** The estimator output is
a length, so the anchors validate the published length rules:

- half-wave: ARRL `468/f` → `0.4758 λ`;
- quarter-wave: ARRL `234/f` → `0.2379 λ`;
- 5/8-wave: ARRL `585/f` → `0.5948 λ`.

`tests/unit/domain/design/test_formulas.py` compares each factor with the
published conversion within 0.5 %, and `test_estimators.py` compares the
estimated dipole and vertical heights end to end. The anchor found that the
5/8-wave factor lacked the end-effect correction used by the other two; it is
now `0.625 × 0.95` and the estimate is labeled empirical.

Balanis impedance and directivity values were considered and deliberately not
added: they describe an idealized `0.5 λ` dipole, while the estimator produces a
`0.475 λ` practical length, so a direct comparison would be misleading. The
NEC-2 User's Guide examples and the ARRL gain test already cover the solver's
absolute accuracy.

**Acceptance.** Every estimator with a closed-form oracle has at least one
published-value test.

**Effort.** M.

#### 3.5.7 Evidence registry as code

**Problem.** `VALIDATION_PLAN.md` already carried a stale test count (788 vs
1,121). The evidence level of each template lived only in prose, so it drifted.

**Change (implemented 2026-11-04).** `src/antennadesk/domain/design/evidence.py`
maps every catalog template to evidence level (A reference-backed, B
published/heuristic, C experimental), source, tolerance, and known limitation.
`tests/unit/domain/design/test_evidence.py` imports the catalog and asserts
that the registry keys equal the catalog keys, so a new template fails the build
until it declares its evidence. The same test compares the generated Markdown
table with the block in `docs/VALIDATION_PLAN.md`; `scripts/render_evidence_table.py`
regenerates it.

**Acceptance.** Adding a template without an evidence entry fails the build.

**Effort.** M.

#### 3.5.8 Reference corpus pipeline

`reference_data/` is correctly gitignored because it is copyrighted, but that
also means nothing verified it was present or current, and none of the 644
MMANA models fed a test.

**Change (implemented 2026-11-04, structural evidence).**

- `reference_data.manifest.json` lists 12 curated MMANA-GAL models with size and
  SHA-256. `scripts/check_reference_data.py --check` verifies them and
  `--write` regenerates the manifest. The corpus is not downloaded: the files
  are copyrighted and supplied by the project owner.
- `tests/integration/reference/test_mmana_corpus.py` imports each model and
  runs a NEC2C smoke simulation, asserting a completed status, positive
  resistance, and finite gain. It skips at module level when the corpus is
  absent, so CI does not run it.
- These are **structural regression** tests, not numerical validation: the
  corpus does not contain published expected results. The models cover
  dipoles, a folded dipole, an inverted-V, verticals, a loop, two beams, two
  VHF antennas, and a small magnetic loop.

**Acceptance.** The corpus is reproducible, and at least ten models are used as
evidence.

**Effort.** L.

### 3.6 Science validation: experimental (level 3)

Level 3 is currently deferred. The VNA import exists, but no measurement is
recorded as validation evidence.

**Change (protocol implemented 2026-11-04; measurement pending).**

- Adopt IEEE Std 149-2021, *Recommended Practice for Antenna Measurements*, as
  the protocol reference: reference plane, range evaluation, gain standard, and
  uncertainty budget.
- `docs/EXPERIMENTAL_VALIDATION_PROTOCOL.md` defines the equipment, site
  record, calibration, impedance/SWR, gain comparison, pattern cuts, and a GUM
  uncertainty budget for a half-wave dipole.
- The measurement schema extension is deferred until a real measurement exists.
  The protocol lists the proposed fields (instrument, reference antenna,
  cable loss, expanded uncertainty) and stores the budget in `notes` and the
  attached files in the meantime.
- Compare measured and simulated results, and explain the difference in terms of
  the documented uncertainty rather than a tolerance.

**Acceptance.** One measurement with an uncertainty budget, stored in the
project format, compared against simulation, with the delta explained.

**Effort.** L, and it requires physical access to a VNA and a suitable site.

### 3.7 Consistency and documentation

**Problem.** English and Spanish strings are maintained by hand; a parity test
now guards the tables, but documentation can still drift from code.

**Change.**

- (done 2026-11-04) `tests/unit/ui/test_i18n.py` checks both translation tables
  for identical keys, blank values, placeholder parity, duplicate literal keys,
  and the missing-key fallback.
- (done 2026-11-05) `tests/unit/ui/test_i18n_usage.py` scans `ui/` for literal
  keys passed to `t()`, `_label()`, and `_add_row()`, and rejects non-technical
  literals in the visible text setters. It found and fixed three missing keys
  and the untranslated wizard placeholder.
- (done 2026-11-04) ADR numbering: 24 ADRs, 0001–0024, with
  `tests/unit/test_adr_numbering.py` asserting unique, contiguous numbers and a
  heading that matches the filename. The duplicate `0014` was resolved:
  undo/redo is now `0024`, and L-network stays `0014`.
- (done 2026-11-05) Estimator-registry and catalog-route consistency:
  `tests/ui/test_catalog_routing.py` checks that every catalog entry has the
  expected estimator support, that every estimator type is covered by at least
  one catalog route, that the parameter-to-catalog identity matches (with the
  documented doublet alias), that New Antenna covers every entry, and that the
  catalog evidence label matches the evidence registry level. The evidence
  registry itself is covered in 3.5.7.
- Add a `CHANGELOG.md` entry check for user-visible changes.
- Turn the `AGENTS.md` definition of done into a checklist template used by the
  milestone review.

**Acceptance.** A missing translation or a stale table fails the build.

**Effort.** S–M.

### 3.8 Performance and scalability

**Problem.** The suite takes 62 s and the UI suite is the slow part. Multiband
runs are benchmarked manually (`scripts/benchmark_multiband.py`) but not
tracked.

**Change.**

- (done 2026-11-05) `pytest-benchmark` covers the NEC output parser, pattern
  metrics (`max_power_gain_db` and `front_to_back_db`), and compressed project
  save/load. The CI benchmark job is report-only and uploads `benchmark.json`.
- Track peak RSS and wall time for 3, 5, and 8 bands; fail on a documented
  regression threshold.
- Enforce a suite runtime budget in CI and report the ten slowest tests.
- Keep the existing run-size budget tests and extend them to the new families.

**Acceptance.** A performance regression produces a visible CI signal, not a
surprise in a release.

**Effort.** M.

## 4. Phases

Each phase is independently shippable.

### Phase 0 — Quick wins (implemented 2026-11-04)

1. `NEC2C` auto-detection in `tests/conftest.py`, so the local command does not
   silently skip the solver tests. Done, with a pytest header line that reports
   the solver path.
2. Register markers and tag the solver tests. Done: `science`, `solver`,
   `slow`, `golden`, `ui`.
3. Extend the CI `paths` filter and add `concurrency`. Done for `scripts/**`,
   `packaging/**`, and `CHANGELOG.md`. `docs/**` is deferred to Phase 1, where
   a docs check will exist; triggering the full matrix for a typo fix would only
   burn runner minutes.
4. Replace the manual uv install with `setup-uv` and caching. Done in `ci.yml`
   and `package.yml`. `release.yml` is left unchanged on purpose; it needs a
   release dry run before touching the publishing path.
5. Fix the stale test count in `VALIDATION_PLAN.md`. Done at the time: 1,121
   tests, 77 of them solver tests. The suite now has 1,259 tests, 102 of them
   solver tests.

### Phase 0.1 — UI test isolation (implemented 2026-11-04)

`test_theme.py` took 66 s in a full run and 0.4 s alone. The profile showed the
time inside a nested `QEventLoop` from `qtbot.wait`, not in the geometry view.
`deleteLater` schedules the deletion but the deferred-delete events were never
dispatched, so widgets from `test_main_window.py` stayed alive and the next test
paid for their paint and palette events.

The teardown in `tests/conftest.py` now calls `closeAllWindows()`,
`sendPostedEvents(None, QEvent.Type.DeferredDelete)`, and `processEvents()`
before collecting. The full suite went from 142 s to 56 s, faster than before
the polarization commit.

### Phase 1 — Foundation (one week)

1. (done 2026-11-04) Coverage measurement and per-package thresholds.
2. (done 2026-11-04) mypy coverage for `ui/` via `mypy_ui.ini`, started
   permissively with a ratchet; all 75 files are checked.
3. (done 2026-11-05) Hypothesis for units, the three importers, all estimator
   families, and project/migration round trips; the geometry properties found
   and fixed the zero-height and vertical-array clearance edge cases.
4. (done 2026-11-04) i18n parity test:
   `tests/unit/ui/test_i18n.py` checks both languages, blank entries,
   placeholder parity, duplicate literal keys, and the fallback path.
5. (done 2026-11-04) Split `test_main_window.py` into eight feature modules
   (`project`, `simulation`, `templates`, `presets`, `optimization`, `imports`,
   `design_from_frequency`, `undo`), with shared `FakeSolver` and `window`
   fixture moved to `main_window_support.py` and `tests/ui/conftest.py`. The
   original 3,654-line file is gone; the largest module is 828 lines.

### Phase 2 — Science oracles (complete 2026-11-04)

1. (done 2026-11-04) Segmentation diagnostics and the convergence test.
2. (done 2026-11-04) Physical invariants: power, pattern integral, rotation.
3. (done 2026-11-04) `scikit-rf` oracle for the two-port math.
4. (done 2026-11-04) `PyNEC` cross-engine job.
5. (done 2026-11-04) Published closed-form anchors for the estimators: ARRL
   `468/f`, `234/f`, and `585/f` within 0.5 %.
6. (done 2026-11-04) Evidence registry as code.

### Phase 3 — Scale (ongoing)

1. (started 2026-11-04) Mutation testing on the domain and simulation layers:
   weekly `mutmut` on `formulas.py` and `intent.py`, to be widened as the
   operator set is understood.
2. (started 2026-11-04) Reference corpus pipeline: 12 curated MMANA models with a checksum manifest, used for structural regression and a NEC2C smoke run. No published numerical results yet.
3. (partly done 2026-11-04) Different-method oracle: four analytical closed-form cases replace FDTD/FEM, which is not installable here. A true FDTD/FEM golden case remains offline.
4. Level 3 measurement protocol and one recorded measurement.
5. Benchmark and memory tracking.

## 5. Metrics

Track these over time; they are the definition of "better QA" for this project:

| Metric | Target |
|---|---|
| Solver tests executed in CI | 102/102 on Linux and Windows |
| Solver tests executed locally | 102/102 when the binary exists |
| Domain coverage (line + branch) | ≥ 95 % |
| Coverage gates by package | pass; thresholds ratchet up |
| UI files under mypy | 75/75 |
| Mutation score, non-equivalent mutants | ≥ 80 %; 100 % on the current focused subset (raw 70 %) |
| Families with evidence level A or B | all, or an explicit C with a visible warning |
| Templates with an evidence entry | 25/25, enforced by a test |
| Reference tests with a named source | 100 % |
| Numeric assertions with a tolerance rationale | 100 % |
| Doc-code drift tests | 0 failures |
| Flaky tests per week | 0; a new flake is fixed or quarantined with an issue |
| Suite runtime, fast lane | < 20 s |
| Suite runtime, full | < 60 s |

## 6. Deliberately out of scope

- **100 % coverage.** It rewards executing lines, not checking behavior.
- **Mutation testing on `ui/`.** The signal-to-noise ratio is poor and the run
  is slow.
- **FDTD/FEM in CI.** Heavy, no wheels, and not needed on every pull request.
- **Strict mypy on `ui/` in one step.** It would block feature work for days.
- **Replacing `nec2c`.** The adapter boundary is correct; add oracles around it
  instead.
- **Inventing reference values from simulation output.** Prohibited by
  `AGENTS.md` and by `VALIDATION_PLAN.md`.
