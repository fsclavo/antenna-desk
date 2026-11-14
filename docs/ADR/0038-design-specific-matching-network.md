# ADR-0038 — Design-specific matching network for end-fed antennas

- **Status:** Accepted
- **Date:** 2026-11-14
- **Deciders:** Fernando Sclavo, development
- **Related:** ADR-0028 (matching-network precedence), ADR-0037 (feedpoint
  common-mode choke), EF9 in
  [`../AUTONOMOUS_BACKLOG.md`](../AUTONOMOUS_BACKLOG.md)

## Context

The shortened EFHW presets use a fixed internal matching unit: a 100 pF shunt
across the 49:1 transformer primary plus a series leakage estimate. That unit is
a reference starting point, not a tunable matching network. Its input-shunt
L topology cannot match every transformed load: when the transformed load
resistance is above the 50 Ω source reference, the theoretical SWR floor is
above 1.0 no matter how the capacitor and leakage are adjusted. EF2 reports that
floor, EF4 adds **Apply Best SWR**, and EF5 warns when the optimizer hits a
bound, but none of them can remove the topology limit.

The project-level matching network is global and, per ADR-0028, replaces the
internal end-fed unit. It is not a design-specific solution: changing it affects
every design in the project, it is not part of the antenna's persisted geometry,
and the family optimizer cannot own its variables.

EF7b and EF8/EF8a removed the loss and return-path blockers. This ADR defines
the missing design-specific matching layer without changing the global project
network or the fixed internal reference unit.

## Decision

Add an optional **design-specific matching network** owned by the end-fed
design.

1. The network is stored with `EndFedParameters` and is persisted with the
   design. `None` means no design-specific network.
2. The initial implementation supports an **L-network** only. The domain may
   reuse `LNetwork` and the existing `LNetworkPayload`, but the ADR does not
   authorize Pi/T UI or optimizer variables in phase A.
3. The network operates on the **primary side of the ideal feed transformer**,
   in the same reference plane as the existing internal unit. The ideal
   transformer ratio is applied before the network, exactly as it is in the
   current link budget.
4. Precedence is explicit and remains compatible with ADR-0028:
   **project network > design-specific network > internal fixed unit**.
   When the project network is active, the design-specific network is retained
   but not applied and is reported as overridden, not cascaded.
5. When the design-specific network is active, `endfed_matching_network()`
   returns it instead of the internal fixed unit. The existing internal unit
   values remain in the design for fallback.
6. The family optimizer exposes the L-network component values as bounded
   variables with an explicit group. Topology, `shunt_at_input`, and presence
   are context, not continuous variables. The optimizer must not invent a
   topology or silently switch it.
7. A design-specific network that is active but has no non-zero element is
   invalid. A network that is present but overridden by the project network is
   valid and retained.
8. The UI provides a clear **Design matching network** selector and editable
   L-network values. It must state that a project network overrides it.
9. Results and reports distinguish:
   - internal fixed unit,
   - design-specific network,
   - project network,
   - retained but overridden.
10. Persistence adds the network in schema 50; older projects migrate with
    `None`. The project schema and other families are unchanged.

## Phase A scope

Phase A is deliberately narrow:

- domain field, validation, matching extraction, and precedence;
- L-network only, no automatic synthesis;
- persistence schema 50 and migration;
- optimizer variables for the L-network component values;
- UI selector and editable values;
- reports and EN/ES help;
- unit tests, persistence tests, optimizer determinism tests, UI tests, and a
  regression check that designs without the network produce identical results.

Pi/T topologies, automatic network synthesis, and a matching-network optimizer
objective separate from the existing SWR/target objective are follow-ups. They
require their own ADR or an amendment to this one.

## Consequences

- The optimizer can tune a match that the fixed input-shunt unit cannot reach.
- The design remains self-contained and reproducible; changing a project-level
  network does not silently change every design.
- The user can keep the published internal unit as a fallback by disabling the
  design-specific network.
- More UI and schema surface, plus a new optimizer variable group.
- The network is still an ideal L/C model. Component Q, ESR, pad capacitance,
  balun imbalance, and common-mode effects remain separate models or explicit
  limitations.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Add loose C/L variables to the fixed input-shunt unit | The topology cannot match R > 50 Ω; more variables do not remove the floor and would misrepresent a fixed reference build |
| Use only the global project network | Not design-specific, not persisted with the antenna, and the family optimizer cannot own its variables |
| Auto-synthesize a network and persist it silently | Hidden topology changes are not reproducible; the user must see and approve the topology |
| Support L/Pi/T in the first slice | Expands the optimizer, UI, and validation surface before the precedence and L-network path are proven |
| Change every family to use design-specific networks | Unnecessary risk; only end-fed needs this layer now |

## Validation plan

1. Test precedence: project > design-specific > internal, with no cascading.
2. Test that a design without the network is numerically identical to the
   current model.
3. Test a known L-network input impedance against the existing `LNetwork`
   calculation, not a new formula.
4. Test optimizer determinism, bounds, constraints, and Apply Best with locked
   variables.
5. Test schema 50 round-trip and v49→v50 migration.
6. Test the UI state, help, and retained/overridden reporting.
7. Run the full gate, including NEC2C integration tests.

## Amendment 1 — Automatic L-network design (2026-11-14)

**Status:** Accepted. This amendment authorizes the first automatic-synthesis
slice without changing the Phase A schema.

The design-specific L-network can be populated from the **current simulation
result**:

1. The source point is the antenna-side feed impedance divided by the ideal
   transformer ratio, exactly as `matching_network_design_from_frequency()`
   already does. The raw `FrequencyResult.impedance_ohm` is not used because it
   already includes the matching network and feed line.
2. The network is synthesized with the existing `design_l_network()` function
   at that frequency and source impedance.
3. The result only **populates the editor fields**. It is not applied, saved, or
   simulated until the user confirms the design change.
4. If no L-network solution exists, the UI reports that explicitly; it does not
   fall back to an invented network or a different topology.
5. No new persisted origin field is added. The persisted values are the network
   itself; provenance remains the simulation the user reviewed.
6. The action is available only for the design-specific L-network, not for the
   fixed internal unit or the global project network.

## Open questions

- Should the first UI expose a topology selector with only L enabled, or a
  single “Add L-network” action?
- Should the optimizer default the design network variables to unlocked or
  locked? The ADR recommends unlocked only when the user explicitly enables the
  design network.
- Should the design network be allowed together with the internal unit values
  for comparison, or should the UI hide the internal values while the design
  network is active? The ADR recommends retaining and marking them retained.
