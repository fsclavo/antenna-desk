# ADR-0001 — MVP electromagnetic engine

- **Status:** Accepted
- **Date:** 2026-10-28
- **Approved:** 2026-10-29 by Fernando Sclavo
- **Deciders:** Fernando Sclavo, development
- **Phase:** 0 — Technical spike

## Context

AntennaDesk is a local-first desktop application, GPL-3.0-or-later, for Linux
and Windows. The MVP needs to simulate a half-wave dipole and obtain input
impedance, SWR, frequency sweeps, currents, and far-field patterns. The
blueprint forbids writing a custom solver in the MVP and requires resolving
the license and distribution risk before starting the GUI.

Phase 0 had to compare NEC-2/nec2c, NEC2++/PyNEC, and alternatives in terms of
license, integration, portability, available results, maintenance, and
packaging, with a reproducible case on Linux and Windows.

## Decision

Adopt **nec2c 1.3.3** (the `KJ7LNW/nec2c` fork at commit
`55be1e0e3fe5ee9dad4ce6050711450d19c562fd`) as the MVP engine, integrated as
an **external process** through a custom adapter. The engine version is pinned
by commit and a Windows portability patch is maintained in
`spikes/phase0/patches/nec2c-windows.patch`.

NEC2++/PyNEC are not runtime dependencies. They are reserved as a second
cross-check engine for Phase 2 validation. xnec2c is used only as a technical
and UX reference.

## Rationale

1. **Compatible license:** upstream nec2c is public domain; the fork declares
   GPL-3.0, compatible with the project license.
2. **Portability:** builds on Linux with `cc` and on Windows with MinGW/Zig
   after a small patch for `getopt`, `sigaction`, and `times()`.
3. **Isolation:** running as a process means a solver crash cannot close the
   application, and cancellation is controllable.
4. **Results:** provides impedance, currents, power, and far-field patterns; a
   21-frequency sweep with patterns took about 6 ms.
5. **Validation:** reproduces the values printed in the NEC-2 User's Guide
   (Examples 1 and 3) with differences below `0.01 Ω`.
6. **Packaging:** a single C executable with no additional runtime; lower cost
   than a C++ library or a Python extension.

## Consequences

### Positive

- The engine is decoupled from the domain, GUI, and project format.
- Each run can be cancelled, limited, and logged.
- The adapter can normalize output without depending on a native API.
- The project can change engines later without touching the domain.

### Negative

- A text parser must be written and maintained.
- The Windows patch must be maintained across nec2c upgrades.
- GPL distribution requires shipping the engine source, COPYING, and notices.
- The output format is not a formal contract; the engine version must be
  pinned.

### Neutral

- NEC2++ offers a richer API but adds a heavier C++ dependency.
- PyNEC is convenient for prototypes but does not publish Windows wheels for
  2.3.4.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| NEC2++ as a library | Couples the app to a C++ library; higher packaging cost and native-crash risk |
| PyNEC in-process | No Windows wheels; couples the app to the Python version and extension ABI |
| xnec2c | GTK GUI, not a library; useful only as a reference |
| Original NEC-2 Fortran | Requires gfortran and maintenance of historical code; no MVP advantage |
| Writing a custom solver | Out of scope and contrary to the reuse principle |

## Evidence

- `spikes/phase0/README.md`: reproduction steps, cases, and results.
- `docs/spikes/phase0-solver-evaluation.md`: full comparison.
- `spikes/phase0/expected/reference_values.json`: manual values and
  tolerances.
- `spikes/phase0/scripts/run_reference.py`: 19 checks, all passing on Linux
  and on the Windows binary.
- `.github/workflows/solver-spike.yml`: Linux/Windows CI executed on
  2026-10-29, `19/19` checks on both platforms.

Spike result:

```text
nec2_manual_example1          Z=82.6980+46.3060j  (manual 82.6979+46.3060j)
nec2_manual_example3_perfect  Z=106.4400+9.9055j  (manual 106.437+9.90578j)
nec2_manual_example3_finite   Z=111.1200+11.0080j (manual 111.117+11.0075j)
19/19 checks passed
```

## Risks

| Risk | Mitigation |
|---|---|
| nec2c output format changes | Pin commit; parser fixtures; regression tests |
| Windows patch becomes stale | Windows CI; reproducible build; review on upgrade |
| Long paths rejected by nec2c | Short temporary directory and relative names in the adapter |
| GPL non-compliance in the installer | Include source, COPYING, notices; legal review |
| Validation limited to two examples | Expand reference cases in Phase 2 |
| Fork loses maintenance | Upstream is public domain; revert to 1.3.1 or keep the patch |

## Follow-up

1. Keep the commit and source SHA-256 pinned in the build.
2. In Phase 2, implement the real adapter with a tested parser, cancellation,
   time limits, logs, and stderr capture.
3. Add reference cases for ground, loads, verticals, and loops before adding
   those geometries.
4. Review the license and distribution text with legal counsel before the
   first public release.
