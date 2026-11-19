# Result metrics

These definitions are descriptive. They use the stored frequency sweep and
far-field grid; no metric adds electromagnetic accuracy beyond that sampling.

## SWR bandwidth

The 2:1 bandwidth is the contiguous range around a selected frequency where
`SWR <= 2.0`. Boundaries between a passing and failing sample are linearly
interpolated. If either boundary is outside the sweep, the result is
**unbracketed** and no finite bandwidth is reported; the sampled lower and upper
edges remain available. The SWR chart marks catalog amateur-band edges inside
the visible range.

## Pattern metrics

- **HPBW (azimuth/elevation)**: the -3 dB width of the pattern cut through the
  sampled maximum-gain direction. Azimuth cuts handle 0/360 wrapping; elevation
  cuts use NEC theta from the zenith. The reported pattern resolution is the
  spacing of the stored angular samples, not a solver error estimate.
- **Front-to-back**: forward maximum minus the gain 180 degrees away in azimuth
  at the same elevation.
- **Sidelobe level**: the largest local maximum other than the main peak,
  relative to the main peak. It is limited by the angular grid and is not a
  full sidelobe-integration result.
- **Takeoff angle**: elevation above the horizon (`90 - theta`) at the
  maximum sampled power gain.
- **Efficiency**: structure radiation efficiency from the power budget.
- **Directivity and realized gain**: taken from the stored per-frequency values;
  realized gain includes the transmitter-side feed-chain cascade.

## Circular polarization

At the maximum-gain sample:

- **Axial ratio** is `20 log10(max(AR, 1/AR))`; perfect circular is 0 dB.
- **Sense** maps NEC's polarization text to `RHCP`, `LHCP`, `linear`, or the raw
  label when it is not recognized.
- **Co-pol CP gain** is the total gain plus the elliptical polarization mismatch
  loss `10 log10((1 + AR)^2 / (2 (1 + AR^2)))`. This is a heuristic projection,
  not an independently validated circular gain reference.
- **Cross-pol discrimination** is `20 log10((AR + 1) / (AR - 1))`; it is
  infinite for perfect circular polarization.

The CP values are descriptive and should be checked against a circular
reference or measurement before being used as a performance guarantee.

## CSV and reports

The frequency CSV adds bandwidth, HPBW, front-to-back, sidelobe, takeoff,
efficiency, axial ratio, polarization sense, CP gain, cross-pol discrimination,
and pattern resolution columns. HTML and native PDF reports show the same
metrics at the representative gain frequency.
