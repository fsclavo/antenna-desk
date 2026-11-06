# Multiband performance measurement

**Date:** 2026-11-04  
**Status:** measured; keep the per-band architecture for now  
**Script:** [`scripts/benchmark_multiband.py`](../scripts/benchmark_multiband.py)

This note records the Phase 2 decision from
[`PENDING_WORK_PLAN.md`](PENDING_WORK_PLAN.md). It measures the existing
per-band `AnalyzeBands` path against the real `nec2c` adapter; it is not a
synthetic unit benchmark.

## Environment and method

- Linux 7.0.0, AMD Ryzen 7 5825U, 16 threads.
- `nec2c 1.3.3`.
- 15 impedance/SWR points per band.
- 5 pattern frequencies per band at a 5° pattern step.
- Six representative cases: OCFD, G5RV at 3/5/8 bands, and a fan dipole at
  3/8 bands.
- Each produced band run is recorded in a project; the compressed project size
  is measured with `JsonProjectRepository.serialized_size()`.
- Peak RSS is the process maximum reported by `resource.getrusage()` and is
  cumulative across the cases in one process. It is an upper-bound indicator,
  not an isolated per-case measurement.

Reproduce with:

```bash
uv run python scripts/benchmark_multiband.py \
  --nec2c spikes/phase0/build/nec2c
```

## Results

| Design | Bands | Sweep points/band | Pattern freqs/band | Seconds | Compressed MB | Peak RSS MiB | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| OCFD 40 m | 3 | 15 | 5 | 0.46 | 1.96 | 64 | ok |
| G5RV | 3 | 15 | 5 | 0.49 | 2.27 | 168 | ok |
| G5RV | 5 | 15 | 5 | 0.78 | 3.61 | 182 | ok |
| G5RV | 8 | 15 | 5 | 1.27 | 5.94 | 268 | ok |
| Fan dipole 40/20/10 m | 3 | 15 | 5 | 0.45 | 2.75 | 400 | ok |
| Fan dipole wide | 8 | 15 | 5 | 1.35 | 7.35 | 400 | ok |

All six batches completed without solver errors or partial results.

## Decision

Keep the current **one solver run per band** architecture.

The measured batches are small compared with the 32 MB warning and 64 MB
project limit, and the wall time for eight bands is around one second on this
machine. A segmented `FrequencyPlan` and multi-`FR` deck would add a
cross-cutting contract change without a demonstrated need at this point.

Revisit the decision only if one of these becomes true:

- routine runs use 1–2° patterns or much denser sweeps;
- the supported band count or typical point count grows substantially;
- a representative low-end target machine shows user-visible delays; or
- raw solver output becomes a practical project-size problem.

The single-band `SimulationSpec`/`RunSimulation` boundary remains the
regression baseline.
