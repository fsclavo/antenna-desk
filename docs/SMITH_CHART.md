# Smith chart

The Smith tab is a presentation of the impedance values already stored in a
simulation result. It does not add a solver run, a new electromagnetic model, or
an accuracy claim.

## Normalization

For a load impedance `Z` and a real reference impedance `Z0`:

```
gamma = (Z - Z0) / (Z + Z0)
Z = Z0 * (1 + gamma) / (1 - gamma)
```

The chart is normalized: the center is `Z0`, the unit circle is `|gamma| = 1`,
constant-resistance circles are normalized to `Z0`, and constant-reactance arcs
are normalized to `Z0`. A 50 Ω load with `Z0 = 50 Ω` maps to the center. A short
maps to `-1`; an ideal open approaches `+1`. The SWR is
`(1 + |gamma|) / (1 - |gamma|)` and is infinite at the boundary.

`SmithPoint` stores the frequency, impedance, reference impedance, reflection
coefficient, and SWR. The domain module
`src/antennadesk/domain/design/smith_chart.py` owns the projection and the
reference-plane selection; the widget only draws the points.

## Reference planes

- **As simulated** uses `FrequencyResult.impedance_ohm`, which is the
  post-chain impedance stored by the normalizer. It includes the project feed
  line, matching network, balun loss model, and ideal feed transformer when they
  are active.
- **Antenna feedpoint** uses the primary `SourceResult.impedance_ohm`. This is
  the raw NEC source impedance before the ideal feed transformer; the feed line
  and matching network are not applied.
- **Feed line only** applies `SimulationSpec.feed_line` to
  `SourceResult.impedance_ohm / feed_transformer_ratio`. It deliberately
  excludes the matching network. It is a preview, not a claim that the preview
  is the full station chain.

The plane selector is disabled for a plane with no data. Multi-source designs
show the primary feed only; per-source values remain in the **Sources** tab.

## Measured overlay

Imported measurement points are normalized to the display `Z0`, not to the
measurement's own reference impedance. If the measurement records a different
reference impedance, the tab reports both values. This is a display conversion;
the measurement record is unchanged.

## Drawing and export

The widget limits the number of drawn symbols for large sweeps. The full locus
is retained in memory and the CSV export writes every simulated and measured
point. PNG and SVG export use a fixed 1200 × 900 canvas and the current theme;
the CSV columns are:

```
series,frequency_hz,resistance_ohm,reactance_ohm,gamma_real,gamma_imag,swr,reference_impedance_ohm
```

## Limitations

- The chart is normalized to a real `Z0`. It does not provide a complex
  reference-impedance chart.
- **Feed line only** excludes the matching network and is not a substitute for
  a full simulation.
- The chart does not preview arbitrary matching-network values. Edit the
  matching network and run the normal simulation to evaluate a new network.
- The chart is a presentation of the stored result; it does not improve the
  accuracy of the segmentation, ground, or solver model.
