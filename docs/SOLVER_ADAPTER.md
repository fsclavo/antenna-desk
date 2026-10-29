# Solver adapter

## Purpose

The solver adapter translates the canonical `AntennaModel` and a
`SimulationSpec` to an engine-specific input, runs the engine in a controlled
process, parses its output, and normalizes the result. The domain and the GUI
never see NEC cards or solver-specific text.

## Interface

The application depends on the `AntennaSolver` port:

```python
class AntennaSolver(Protocol):
    def capabilities(self) -> SolverCapabilities: ...
    def validate(self, model: AntennaModel, spec: SimulationSpec) -> tuple[Diagnostic, ...]: ...
    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: ProgressCallback | None = None,
        cancel_token: CancelToken | None = None,
    ) -> SimulationResult: ...
    def version(self) -> SolverMetadata: ...
```

`run` returns a normalized `SimulationResult` that contains the raw input and
output text. Expected failures are represented in the result status and
diagnostics. A missing executable, timeout, cancellation, non-zero exit,
oversized output, or parser failure does not raise into the application.

`progress_callback` exists for future engines that expose real progress. The
nec2c adapter does not call it because nec2c does not report progress.

## NEC-2 input generation

The input writer generates:

- `CM`/`CE` comments with an ASCII-safe model name.
- One `GW` card per wire, using tags starting at 1 and the segment count from
  the segmentation policy.
- `GE 1` for ground models, or `GE 0` for free space.
- `GN 1` for perfect ground, or `GN 0 0 0 0 epsr sigma` for finite ground.
- `EK` when the extended thin-wire kernel is requested.
- One `LD 5` conductivity card per wire when
  `SimulationSpec.include_conductor_losses` is true.
- One `FR` frequency or sweep card in MHz.
- One `EX` voltage source at the chosen feed segment.
- An `RP` far-field card when requested, otherwise an `XQ` execution card.
- `EN` to end the deck.

The feed offset is mapped to the segment that contains it. A feed at a segment
boundary produces a warning. A feed at a wire end is allowed but produces a
warning.

## Execution and cancellation

- The engine runs with an argument list, never through a shell.
- The executable path is resolved and checked before use.
- Input and output files use short names in a short temporary directory to
  avoid nec2c's input-name buffer limit.
- The process is polled; cancellation terminates it and reaps the child.
- A timeout terminates the process and returns an `error` result.
- stdout and stderr are captured. The output file is size-limited.
- The temporary directory is removed after the run; raw text is kept in the
  result.

## Parsing and normalization

The parser reads:

- Frequency blocks.
- Antenna input parameters: voltage, current, complex impedance, admittance,
  and input power.
- Segment currents and coordinates.
- Power budget: input, radiated, structure loss, network loss, efficiency.
- Far-field pattern: theta, phi, vertical/horizontal/total power gain, axial
  ratio, tilt, polarization, and E-field components.

The normalizer:

- Selects the impedance for the requested feed tag and segment.
- Computes SWR with the explicit reference impedance from `SimulationSpec`.
- Maps currents and far-field points to immutable domain results.
- Computes a deterministic SHA-256 fingerprint of the model and spec.
- Sets status to `completed`, `partial`, `cancelled`, or `error`.
- Adds structured diagnostics for missing blocks, segmentation warnings, and
  execution failures.

The far-field values are NEC **power gains** in dB. With a perfect conductor
and no lossy loads, power gain equals directivity. Conductor and resistive-load
losses are included when enabled. Realized gain is not computed in Phase 2.

## Reference validation

The adapter is validated against the printed NEC-2 User's Guide values:

- Example 1, free space: `82.6979 + j46.3060 Ω` at 299.8 MHz.
- Example 3, perfect ground: `106.437 + j9.90578 Ω` at 30 MHz.
- Example 3, finite ground: `111.117 + j11.0075 Ω` at 30 MHz.

It also checks the half-wave dipole maximum power gain against the standard
`2.15 dBi` value with a tolerance of `0.2 dB`, and the SWR of the Example 1
impedance against the computed value `2.351965` at 50 Ω.

## Current limitations

- Conductor conductivity is emitted through `LD 5` when
  `SimulationSpec.include_conductor_losses` is true (the default). Set it to
  false to reproduce perfect-conductor reference cases. Relative permeability
  is not emitted.
- Series and parallel RLC loads are emitted as `LD 0`/`LD 1` on one segment.
  General networks, transmission lines, and radial ground screens are not
  implemented.
- Only free-space, perfect, and finite ground models are emitted.
- The segmentation policy is a documented heuristic with optional per-wire
  overrides; explicit segment counts
  are used for reference cases.
- Results are not persisted in the project file yet.
- No progress reporting, because nec2c does not provide real progress data.
- The parser is version-sensitive; the engine commit is pinned and the parser
  has unit tests with fixed output.

## Tests and CI

- Unit tests cover the input writer, parser, SWR normalization, segmentation,
  frequency plans, far-field requests, and fingerprints.
- Integration tests run the real nec2c binary when `NEC2C` points to it.
- GitHub Actions builds nec2c on Linux and Windows, then runs the integration
  tests on both platforms.
