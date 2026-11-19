# Segmentation convergence study

The convergence study runs the same canonical wire model at four segment
densities:

| Density | Segment length |
|---|---|
| `0.10 λ` | coarse |
| `0.05 λ` | default target |
| `0.025 λ` | fine |
| `0.0125 λ` | finest |

The ladder is a self-consistency check, not an accuracy proof. A flat curve can
still be wrong if the model or the reference data is wrong. Cross-engine
comparison or measurement is a separate validation step.

## Per-density result

Each density records:

- total segments and each wire's segment count;
- segment length, radius, and segment/radius ratio per wire;
- resistance, reactance, impedance magnitude, and SWR at the design frequency;
- maximum power gain and takeoff angle at the coarsest and finest densities;
- segmentation diagnostics and any solver error.

The study uses the existing segmentation policy, `resolve_model_quality`, and
`validate_segmentation`. It does not add a new solver or an accuracy claim.
Cancelling keeps completed densities and marks the study partial.

## Verdict thresholds

The verdict compares the two finest valid densities. Relative changes use the
larger of the two values in the denominator; reactance change is normalized by
the impedance magnitude.

| Metric | Converged | Marginal | Not converged |
|---|---:|---:|---:|
| Resistance | ≤ 2 % | ≤ 5 % | > 5 % |
| Reactance / `|Z|` | ≤ 2 % | ≤ 5 % | > 5 % |
| `|Z|` | ≤ 2 % | ≤ 5 % | > 5 % |
| SWR | ≤ 0.05 | ≤ 0.125 | > 0.125 |
| Gain (pattern ends) | ≤ 0.2 dB | ≤ 0.5 dB | > 0.5 dB |
| Takeoff (pattern ends) | ≤ 2° | ≤ 5° | > 5° |

If the study is cancelled, fewer than two densities are valid, or a density is
invalid, the verdict is **incomplete** or **not converged**; the table still
shows every completed/invalid row. Pattern metrics are only compared at the
coarsest and finest densities.

The CSV export uses one row per density with the verdict, error, and
`wire_id:segments:segment/radius` metrics.
