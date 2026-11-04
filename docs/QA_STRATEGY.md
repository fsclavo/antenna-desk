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
| Collected tests | 1,139 |
| Passing locally without solver | 1,062 passed in 44 s |
| Passing locally with `NEC2C` set | 1,139 passed in 59 s |
| Slowest test | 4.9 s (`test_g5rv_dense_sweep_uses_pattern_snapshots`) |
| UI test isolation | fixed 2026-11-04: deferred deletes were not dispatched, so widgets from one test stayed alive and a later test spent ~66 s in a nested event loop. The teardown in `tests/conftest.py` now closes windows and dispatches `DeferredDelete`; the full suite went from 142 s to 56 s |
| Test files | 138 (81 unit, 3 integration, 1 acceptance, 53 UI) |
| Custom pytest markers | 0 |
| `parametrize` uses | 24 |
| `skipif` uses | 2 |
| Largest test file | `tests/integration/simulation/test_nec2c_adapter.py`, 1,442 lines. The 3,654-line main-window file is split into eight feature modules; the largest is 828 lines |
| Source lines | 46,323 total; 30,144 in `ui/` |
| Type-checked lines | ~16,000 strict, plus 58 of 75 `ui/` files under a permissive ratchet; 17 UI files (219 errors) remain excluded |
| Coverage, full suite with solver (measured) | 85 % total; domain 91 %, simulation 91 %, persistence 94 %, application 92 %, importers 83 %, reporting 87 %, ui 82 % |
| Coverage enforcement | per-package gates in the `coverage` CI job, one point below the measured baseline |
| Timing sensitivity | one UI failure appeared under coverage instrumentation at ~32 % while another pytest process ran concurrently. The polarization commit added deterministic posted-event processing in `tests/ui/helpers.py`; re-verify under coverage before treating it as open |
| ADR files | 24, numbered 0001–0023 with a duplicated `0014` |
| CI | 4 workflows, green; Linux + Windows, Python 3.11/3.12/3.13 |
| Property-based tests | unit round trips, azimuth range, and importer fuzzing with Hypothesis 6.170 |
| Mutation testing | 0 |
| Cross-engine numerical checks | 0 |
| Segment-convergence tests | 2: free space and finite ground |
| Physics-invariant tests | 0 |
| `docs/VALIDATION_PLAN.md` test count | fixed in Phase 0 (was 788, now 1,139) |

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
- Tag the 77 solver tests with `@pytest.mark.solver` instead of relying only on
  `skipif`, so `pytest -m solver` is meaningful and `pytest -m "not solver"` is
  the default fast lane.
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

**Acceptance.** `uv run pytest -m "not solver"` runs in 44 s today; tagging the
slow tests to reach a sub-20 s lane is still pending. `uv run pytest -m solver`
runs only the 77 solver tests. The main-window suite is split by feature and no
main-window module exceeds 1,000 lines. The next candidate is
`test_nec2c_adapter.py` at 1,442 lines.

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
  importers 83, reporting 87, ui 82. Thresholds sit one point below and ratchet.
  The importer fuzz tests raised that package from 75 to 83, so its gate moved
  from 74 to 82.
- A single coverage lane is enough: the full suite with coverage takes 78 s.
  The two-lane plan was based on the pre-isolation 10-minute run.
- Add mutation testing with `mutmut` (BSD-3, Unix only) on `domain/` and
  `simulation/` in a nightly job. Target ≥ 80 % killed. Annotate equivalent
  mutants explicitly; do not lower the target to hide survivors.
- (implemented 2026-11-04) `hypothesis` 6.170 (MPL-2.0, dev-only) covers unit
  round trips, azimuth range, and the three untrusted-input parsers. The fuzz
  tests found two real defects: `parse_nec2_deck(",")` raised `IndexError`, and
  `normalize_azimuth_degrees(-1e-15)` returned `360.0`. Both are fixed with
  deterministic regression tests.
- Remaining: geometry invariants and project/migration round trips.

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
  `src/antennadesk/ui` with `check_untyped_defs = true`. The 17 files with
  existing errors (219 total) are listed in an `exclude` ratchet; the other 58
  are checked in CI. New UI files are checked by default. Remove entries as
  files reach zero errors.
- Extend ruff with `S` (bandit), `PT` (pytest style), `T20` (no `print` in
  `src/`), and `RUF100`. Evaluate `ANN` for `src/` separately.
- Add an SPDX header check for new source files, matching the existing headers.
- Keep the PySide6 pin below 6.10 and record the reason in the ADR, not only in
  a comment.

**Acceptance.** `uv run mypy` covers `ui/` at the agreed level; ruff reports no
new categories; every source file has an SPDX header.

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

- **Power conservation:** `P_in = P_rad + P_loss` within 1 % for every run.
- **Pattern integration:** integrate the far-field power pattern over the sphere
  and derive directivity; compare with the solver's reported gain plus structure
  efficiency within 0.2 dB. This validates pattern parsing and normalization,
  which today are checked only at the single maximum-gain point.
- **Reciprocity:** for a two-port case, `Z12 = Z21` within 1 %.
- **Rotation invariance:** rotating the antenna azimuth by 90° rotates the
  pattern and leaves the maximum gain unchanged within 0.05 dB. The
  polarization milestone already added a free-space NEC check that compares
  each vertical Yagi and Moxon with its horizontal design rotated around the
  boom. That is a self-consistency test: valuable, but it does not replace an
  independent reference. Keep it and classify it as such.

**Acceptance.** Each invariant is an integration test that runs with `NEC2C`.

**Effort.** M.

#### 3.5.3 Cross-engine oracle

`PyNEC`/`necpp` 2.3.4 (GPL-3.0-only, Python ≥ 3.11) wraps `nec2++`, an
independent C++ rewrite of NEC-2.

**Change.** Add it as a dev-only dependency and run a small canonical set
(dipole, folded dipole, quad loop, Yagi) comparing impedance within 1 % and gain
within 0.2 dB.

**Limitation, stated explicitly:** `nec2++` uses the same thin-wire EFIE
formulation, so this catches implementation and adapter bugs, not formulation
errors. It does not replace the published references.

**Acceptance.** A nightly job compares both engines and reports deltas.

**Effort.** M.

#### 3.5.4 Different-method oracle (offline)

To catch formulation-level errors shared by every NEC-2 derivative, compare two
or three canonical cases against a different numerical method: FDTD (openEMS) or
FEM. Run it manually, commit the results with provenance (engine, version,
mesh, boundary conditions), and treat them as golden values.

**Acceptance.** Two golden cases with a documented method difference and an
explained delta. Not part of CI.

**Effort.** L, one-off.

#### 3.5.5 Independent RF math oracle

The feed-line, matching-network, transformer, and cascade math is pure
two-port algebra. `scikit-rf` 2.2.0 (BSD-3, dev-only) provides an independent
implementation of transmission-line physics, ABCD/S-parameter conversion, and
network cascading.

**Change.** Add `scikit-rf` to the dev group and validate:

- ideal line input impedance against the closed-form `Zin` expression;
- velocity factor and electrical length;
- matched-line attenuation;
- L, Pi, and T network S-parameters;
- transformer ratio and cascade order.

This runs on every platform, needs no solver, and closes a module that today is
checked only against values computed inside the same codebase.

**Acceptance.** At least one test per construct, comparing against `skrf` with a
stated tolerance.

**Effort.** M.

#### 3.5.6 Closed-form references for estimators

`docs/ANTENNA_DESIGN_ESTIMATORS.md` requires a source, assumptions, confidence,
and tolerance for every frequency-first estimator. Today the tests check
*formula consistency*, not agreement with a published value.

**Change.** Add published closed-form anchors, each verified against the printed
edition before use:

- half-wave dipole input impedance and directivity (Balanis, *Antenna Theory*);
- short dipole directivity;
- small-loop radiation resistance;
- folded-dipole 4× resistance rule (already covered by the ARRL check);
- NEC-2 User's Guide examples for the solver, already in place.

Record the edition and page in the test docstring. Do not transcribe a value
from a secondary web source.

**Acceptance.** Every estimator with a closed-form oracle has at least one
published-value test.

**Effort.** M.

#### 3.5.7 Evidence registry as code

**Problem.** `VALIDATION_PLAN.md` already carries a stale test count (788 vs
1,121). The evidence level of each family lives only in prose, so it drifts.

**Change.** Add a machine-readable registry (a module or a JSON file) mapping
each antenna family to: evidence level (A reference-backed, B published
heuristic, C experimental), source, tolerance, and known limitation. A test
asserts that every registered family has an entry and that the docs table is
generated from the registry. CI fails on drift.

**Acceptance.** Adding a family without an evidence entry fails the build.

**Effort.** M.

#### 3.5.8 Reference corpus pipeline

`reference_data/` is correctly gitignored because it is copyrighted, but that
also means nothing verifies it is present or current, and none of the 644 MMANA
models feeds a test.

**Change.**

- Add `scripts/fetch_reference_data.py` with a manifest of file names, sizes,
  and SHA-256 checksums, plus a documented source for each.
- Add a test that skips when the corpus is absent and fails in the nightly job
  when it is expected but missing.
- Wire 10–20 MMANA models with published results into reference tests, starting
  with simple dipoles and beams.

**Acceptance.** The corpus is reproducible, and at least ten models are used as
evidence.

**Effort.** L.

### 3.6 Science validation: experimental (level 3)

Level 3 is currently deferred. The VNA import exists, but no measurement is
recorded as validation evidence.

**Change.**

- Adopt IEEE Std 149-2021, *Recommended Practice for Antenna Measurements*, as
  the protocol reference: reference plane, range evaluation, gain standard, and
  uncertainty budget.
- Extend the measurement schema with uncertainty fields: instrument, cable and
  connector losses, reference plane, calibration date, and an estimated
  expanded uncertainty.
- Document a repeatable procedure for one reference antenna (a half-wave dipole
  is the cheapest defensible case) and record the result in `docs/`.
- Compare measured and simulated results, and explain the difference in terms of
  the documented uncertainty rather than a tolerance.

**Acceptance.** One measurement with an uncertainty budget, stored in the
project format, compared against simulation, with the delta explained.

**Effort.** L, and it requires physical access to a VNA and a suitable site.

### 3.7 Consistency and documentation

**Problem.** English and Spanish strings are maintained by hand with no parity
test. Documentation drifts from code, as the test count already shows.

**Change.**

- Add a test that both translation tables have identical keys, no empty values,
  and no placeholder mismatch.
- Add a test that every user-visible string in `ui/` resolves through
  `ui/i18n.py`.
- Add doc-code consistency tests for the evidence registry, the estimator
  registry, the catalog routes, and ADR numbering. There are 24 ADR files
  numbered 0001–0023, and `0014` is used twice
  (`0014-l-network-post-processing.md` and
  `0014-undo-redo-and-chart-cursors.md`); renumber one and add a uniqueness
  test.
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

- Add `pytest-benchmark` cases for the output parser, pattern metrics, and
  project save/load.
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
   silently skip 77 tests. Done, with a pytest header line that reports the
   solver path.
2. Register markers and tag the solver tests. Done: `science`, `solver`,
   `slow`, `golden`, `ui`.
3. Extend the CI `paths` filter and add `concurrency`. Done for `scripts/**`,
   `packaging/**`, and `CHANGELOG.md`. `docs/**` is deferred to Phase 1, where
   a docs check will exist; triggering the full matrix for a typo fix would only
   burn runner minutes.
4. Replace the manual uv install with `setup-uv` and caching. Done in `ci.yml`
   and `package.yml`. `release.yml` is left unchanged on purpose; it needs a
   release dry run before touching the publishing path.
5. Fix the stale test count in `VALIDATION_PLAN.md`. Done: 1,121 tests, 77 of
   them solver tests.

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
   permissively with a 17-file ratchet; 58 of 75 files are checked.
3. (partly done 2026-11-04) Hypothesis for units and the three importers,
   including a fuzz corpus; geometry and persistence are pending.
4. (done 2026-11-04) i18n parity test:
   `tests/unit/ui/test_i18n.py` checks both languages, blank entries,
   placeholder parity, duplicate literal keys, and the fallback path.
5. (done 2026-11-04) Split `test_main_window.py` into eight feature modules
   (`project`, `simulation`, `templates`, `presets`, `optimization`, `imports`,
   `design_from_frequency`, `undo`), with shared `FakeSolver` and `window`
   fixture moved to `main_window_support.py` and `tests/ui/conftest.py`. The
   original 3,654-line file is gone; the largest module is 828 lines.

### Phase 2 — Science oracles (two weeks)

1. (done 2026-11-04) Segmentation diagnostics and the convergence test.
2. Physical invariants: power, pattern integral, reciprocity, rotation.
3. `scikit-rf` oracle for the two-port math.
4. `PyNEC` cross-engine job.
5. Published closed-form anchors for the estimators.
6. Evidence registry as code.

### Phase 3 — Scale (ongoing)

1. Mutation testing on the domain and simulation layers.
2. Reference corpus pipeline and the first ten MMANA cases.
3. Different-method golden cases.
4. Level 3 measurement protocol and one recorded measurement.
5. Benchmark and memory tracking.

## 5. Metrics

Track these over time; they are the definition of "better QA" for this project:

| Metric | Target |
|---|---|
| Solver tests executed in CI | 77/77 on Linux and Windows |
| Solver tests executed locally | 77/77 when the binary exists |
| Domain coverage (line + branch) | ≥ 95 % |
| Coverage gates by package | pass; thresholds ratchet up |
| UI files under mypy | 58/75 now, ratchet to 75 |
| Mutation score, `domain/` + `simulation/` | ≥ 80 % killed |
| Families with evidence level A or B | all, or an explicit C with a visible warning |
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
