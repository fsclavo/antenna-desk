# ADR-0039 — Frequency-dependent coaxial attenuation

- **Status:** Accepted
- **Date:** 2026-11-14
- **Deciders:** Fernando Sclavo, development
- **Related:** G27 in [`../AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md)

## Context

`FeedLine` previously used one constant `matched_loss_db_per_100m` value at
every frequency. The materials catalog selected a datasheet point, usually at
100 MHz, and the simulation applied that value unchanged across HF. That is
acceptable for a first estimate but wrong for a frequency sweep: coax loss rises
with frequency, and the error is largest at the low and high ends of the sweep.

Manufacturer datasheets publish attenuation at several frequencies. The values
are measured or nominal, not a universal law, and they apply only to the named
cable construction. Extrapolating a table outside its documented range would
create numbers the source does not support.

## Decision

`FeedLine` accepts an optional ordered attenuation table:

- each point is a `LossPoint(frequency_hz, loss_db)` in dB/100 m;
- a table requires at least two points, strictly increasing frequencies, and a
  non-empty source;
- values are interpolated linearly in **log frequency** inside the table range;
- outside the table range the endpoint values are used, and preflight emits a
  warning that the plan exceeds the documented range;
- when no table is present, the existing constant `matched_loss_db_per_100m`
  behavior is unchanged.

The first source-backed presets are:

- **Belden 8219 RG-58A/U** (foam PE, 73 % velocity factor): 1–1000 MHz;
- **Belden 8267 RG-213/U** (solid PE, 66 % velocity factor): 1–4000 MHz.

The existing catalog electrical values are retained as the 100 MHz reference
point. Selecting a catalog cable also fills the attenuation table and its
source. Manual edits clear the table and switch the line back to a constant
loss, so a user cannot accidentally combine a custom fixed value with a stale
manufacturer table.

This is a post-processing feed-line model. It does not model connector loss,
mismatch-dependent additional loss, temperature, aging, water ingress, or a
different cable construction with the same RG type.

## Consequences

- Link budgets and transmitter-end impedance use a source-backed loss curve
  inside the documented range.
- Existing projects and simulations with constant-loss lines are unchanged.
- The table is persisted in schema 51; older projects migrate with an empty
  table and their previous constant loss.
- Preflight warns when a frequency plan leaves the documented range instead of
  silently claiming accuracy.
- The model remains a nominal datasheet model, not a measurement of the user's
  installed cable.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Keep one 100 MHz value | Wrong across a sweep and hides the frequency dependence |
| Fit a power law from one point | Invents a slope the datasheet does not provide |
| Extrapolate the table silently | Claims accuracy outside the documented range |
| Use a universal RG-type curve | Different constructions share the RG label but not the loss |
| Add connector/installation loss now | No traceable per-installation data; keep it separate |

## Validation plan

1. Test log-frequency interpolation and endpoint clamping.
2. Test source and ordering validation.
3. Test the RG-58A and RG-213 catalog tables against their datasheet values.
4. Test schema 51 round-trip and v50→v51 migration.
5. Test the preflight warning outside the table range.
6. Test that a constant-loss feed line is numerically unchanged.
7. Run the full gate.
