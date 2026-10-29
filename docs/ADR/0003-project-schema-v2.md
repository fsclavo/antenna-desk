# ADR-0003 — Project schema v2 and dipole orientation

- **Status:** Accepted
- **Date:** 2026-10-29
- **Deciders:** Fernando Sclavo, development
- **Phase:** 6 — New geometry

## Context

Phase 5 supported only horizontal center-fed dipoles. Phase 6 adds a vertical
center-fed dipole using the same canonical single-wire model. The orientation
must be persisted so reopening a project reconstructs the same geometry.
Existing project files use schema version 1 and do not contain the field.

Inferring orientation from the wire coordinates is possible but fragile and
would make the persisted design intent implicit. Keeping the optional field in
schema version 1 without a version bump would make the schema contract
ambiguous.

## Decision

- Add `orientation` (`horizontal` or `vertical`) to `DipoleParameters` with a
  default of `horizontal`.
- Bump the native project schema to **version 2**.
- Migrate version 1 documents explicitly by adding
  `parameters.orientation = "horizontal"` to every design.
- Keep the migration registry explicit and test both the real v1 to v2 path and
  future-version rejection.
- Preserve the example project as a version 1 migration fixture; new saves are
  written as version 2.

## Consequences

### Positive

- Design intent is explicit and reconstructable after reopening.
- Existing projects continue to open without manual edits.
- The migration framework is exercised by a real schema change.
- Future geometry changes have a clear versioning pattern.

### Negative

- The project schema and persistence mapping gain another field.
- Tests must cover both the migrated v1 representation and the v2 round trip.
- Consumers of the JSON format must account for the version change.

### Neutral

- The solver adapter does not change: a vertical dipole is still a straight
  wire in the canonical model.
- No simulation results are persisted yet; that remains a future schema
  change.

## Alternatives considered

| Alternative | Reason for rejection |
|---|---|
| Infer orientation from wire coordinates | Ambiguous, fragile, and hides design intent |
| Add a separate antenna type | The canonical model is still a single-wire dipole; unnecessary |
| Add an optional field without a version bump | Makes the schema version meaningless |
| Store only the wire geometry | Loses the editable design parameters |

## Follow-up

1. Add loops and folded dipoles as new templates with reference tests.
2. Persist simulation runs in a later schema version with a migration.
3. Keep migration tests mandatory for every schema change.
