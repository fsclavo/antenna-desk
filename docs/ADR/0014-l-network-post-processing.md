# ADR-0014 — L-network post-processing and trap preset

- **Status:** Accepted; precedence extended by ADR-0028
- **Date:** 2026-11-01
- **Supersedes:** the matching-network limitation in ADR-0008

## Context

Feed-line post-processing already transforms antenna-terminal impedance to the
transmitter. Users also need a simple matching network and a practical way to
enter a parallel LC trap. NEC-2 can model a trap as an `LD 1` parallel RLC load,
but a general feedpoint matching network would require extra NEC segments and a
source/network layout that does not fit the canonical one-feed model.

## Decision

1. Add lossless **L**, **Pi**, and **T** network value objects with ideal
   reactive elements. The L network has one series and one shunt element;
   Pi/T use three branches.
2. Evaluate the network analytically in post-processing, before the feed line:
   antenna → matching network → feed line → transmitter.
3. Persist the network as an optional project setting and in each simulation
   spec. Schema v3 remains additive.
4. Show impedance/SWR after the network and line, and add an informational
   diagnostic. Pattern and power gain remain antenna-side.
5. Add a **parallel trap** helper to the load editor: the user enters
   inductance and resonant frequency; the capacitance is calculated and stored
   as a normal `ParallelLoad`/NEC `LD 1` load.
6. Provide automatic L-network synthesis from a load R/X at the design
   frequency. Pi/T are manual designs in this slice.
7. Model component loss through a single Q factor; lossy networks affect input
   impedance/SWR but not the reported antenna pattern or gain.
8. Keep automatic Pi/T synthesis and per-component parasitics out of this slice.

## Consequences

Positive:

- Users can model a practical L-match without editing NEC decks.
- Traps use the existing solver-backed parallel RLC path.
- The network is testable analytically and does not change geometry.

Limitations:

- The network is ideal and lossless.
- Pi/T networks are manual; only L has automatic synthesis.
- The network is evaluated from the simulated antenna impedance, so it does not
  alter current distribution or pattern.
- A single Q models component loss; per-component Q and parasitics are not
  modeled, and network loss is not reflected in reported gain.
