# ADR-0028 — Matching-network precedence for end-fed designs

- **Status:** Accepted
- **Date:** 2026-11-11
- **Related:** [ADR-0014](0014-l-network-post-processing.md),
  [ADR-0015](0015-realized-gain-and-directivity.md)
- **Implemented by:** M1 (runtime resolver), M2 (visibility and warnings),
  M3 (persisted design target)

## Context

AntennaDesk has two matching-network models that can apply to the same design:

1. The internal EFHW model introduced with the shortened presets: an ideal
   shunt capacitor across the 49:1 transformer primary plus a transformer
   leakage inductance. It is stored in `EndFedParameters` and is active when
   either value is non-zero.
2. The project-level matching network configured through
   **Simulation → Matching Network...**. It is a lossless L, Pi, or T network
   evaluated at the antenna feed and stored once per project.

Before M1, several simulation paths replaced the internal EFHW network with the
project network unconditionally. A missing project network could therefore
silently drop the internal EFHW matching unit, and nothing explained what the
solver had actually applied. Treating both networks as a cascade would also be
wrong: the internal values describe the transformer primary, while the project
network is a separate feedpoint network. Cascading them would model hardware
that the user did not configure.

The project network is also project-global, while the internal matching model
belongs to one `EndFedParameters` design. The precedence rule must therefore be
stable across designs, presets, simulation paths, optimizers, reports, and the
construction sheet.

## Decision

### 1. An active project network overrides the internal EFHW network

For every `EndFedParameters` design with active internal matching, an active
project matching network replaces the internal matching unit. This applies to
all end-fed presets, not only the shortened ones: standard end-fed, sloper,
random wire, shortened 80-10 m, and shortened 40-20-10 m designs use the same
rule.

| Project network | EFHW internal matching | Effective network | Override |
|---|---|---|---|
| none | active | EFHW internal | no |
| none | inactive | none | no |
| active | active | project network | **yes** |
| active | inactive | project network | no |

An inactive project network is retained in the project and shown in the UI, but
it is not effective. The internal network remains effective in that case.

### 2. The effective network is derived at runtime

A pure resolver, `resolve_matching_network(parameters, project_network)`,
returns the internal, project, effective, and active state. No override flag is
persisted. The simulation uses only the resolved effective network.

Every path must use that resolver: single simulation, band analysis, family
optimization, synthesis, the EFHW convergence check, reports, and the UI. The
ideal feed transformer ratio still applies before the matching network; the
override changes the matching unit, not the transformer.

### 3. The two networks are never cascaded

No cascade of the internal EFHW unit and the project network is modeled. The
solver emits a `matching_network.override` warning when the override is active,
and the matching-network dialog, optimizer dialog, design summary, and
construction sheet state the same limitation. This is a visible approximation,
not a hidden one.

### 4. The internal values are retained, not deleted

The internal capacitor and leakage values remain in the design and project
file. While the override is active, the End-fed editor disables those fields,
labels them as retained but inactive, and offers links to edit or remove the
project network. The persistent **Feed & matching** summary shows the internal
state, the project network, the feed line, and the balun loss separately.

To restore the internal network, remove the project matching network with
**Remove project network** in the summary or the End-fed editor. The effective
network then returns to the internal EFHW model without any other change.

### 5. The project network stays project-global

The project matching network continues to apply to every design in the
project. The design target stored with it (frequency, load R/X, source
impedance, and optional origin) is also project-level. Removing the project
network clears that target; an inactive network retains it.

## Consequences

Positive:

- A project network no longer silently drops the internal EFHW model, and a
  missing project network restores it.
- All simulation and optimization paths use one precedence rule.
- The UI and exported reports state which network was applied and that no
  cascade is modeled.
- Users can keep the internal design values for later while the project network
  is active.

Negative and limitations:

- Only one matching network is effective at a time. A deliberate cascade of the
  transformer-primary matching unit and a separate feedpoint network is not
  modeled.
- The internal EFHW unit remains an ideal capacitor plus leakage estimate; core
  loss, capacitor ESR, and winding capacitance are still not modeled.
- The project network is global, so a design-specific matching network requires
  a separate project.
- The override warning is informational; the solver does not attempt to
  validate whether the user's physical build cascades the two networks.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Cascade the internal EFHW network and the project network | Models two matching units in series that the user did not configure; would require a deliberate multi-network model and measured transformer data |
| Let the project network always win, even when inactive | Makes an inactive configuration silently change the simulation |
| Let the internal network always win | Makes the project-wide matching work appear to do nothing on end-fed designs |
| Persist an override flag | Duplicates state that can be derived and can become inconsistent after edits or undo |
| Delete the internal values when the project network is added | Loses the design intent and makes restoring the internal network destructive |
| Make the matching network design-specific | Conflicts with the existing project-level feed-line and matching configuration; a larger model change is required |

## Follow-ups

- Add a measured transformer model so the internal EFHW matching unit can
  include core loss, ESR, and winding capacitance.
- Revisit cascade support only if users need to model two physical matching
  units in series, with explicit UI and solver contracts.
- M4 adds creating a project matching network directly from an impedance point;
  it inherits this precedence rule unchanged.
