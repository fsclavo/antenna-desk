# Confirmed project decisions

**Date:** 2026-10-28  
**Owner:** Fernando Sclavo  
**Status:** initial decisions confirmed to start the project

This record preserves the answers given before Phase 0. It does not replace
ADRs: when a decision has technical alternatives and architectural
consequences, it is documented in `docs/ADR/`.

## License and ownership

- Project license: **GPL-3.0-or-later**.
- Copyright: **2026 Fernando Sclavo**.
- Short SPDX headers in source files.
- Documentation under the same GPL-3.0-or-later license.
- Binary distribution includes sources and packaging scripts.
- Contributions use **DCO** (`Signed-off-by`), without a CLA.
- Allowed dependencies: GPLv3-compatible licenses only (MIT, BSD, Apache-2.0,
  LGPLv3, GPLv3); no proprietary or GPLv2-only code.

## Engine and validation

- MVP engine: **nec2c 1.3.3** as an external process, pinned by commit and
  kept with a maintained Windows patch. See
  `docs/ADR/0001-solver-selection.md`.
- Cross-check alternative: **NEC2++/PyNEC**, not a runtime dependency.
- **xnec2c** is used only as a technical and UX reference.
- Independent sources available: **MMANA-GAL** samples and the **ARRL Antenna
  Book**; they will be used to expand validation.
- Solver correctness is validated strictly. Experimental antennas and
  arbitrary geometries do not require an external reference to be designed,
  but they must be labeled as experimental and must not claim validated
  accuracy. See `docs/ROADMAP.md`.

## Platforms and environment

- Linux and Windows.
- Local validation on Linux; Windows validation in GitHub Actions.
- Python `>=3.11`; CI matrix 3.11–3.13.
- Environment and dependencies with `uv` + `uv.lock`.
- GitHub Actions CI from the start.

## Architecture and domain

- Hexagonal architecture / ports and adapters.
- Domain code must not import PySide6, SciPy, or concrete solver libraries.
- Persistence: **dataclasses** in the domain; **Pydantic v2** only at the
  persistence/schema-validation boundary.
- Internal geometry convention: right-handed axes, **Z up**, azimuth from
  North, elevation above the horizon; explicit mapping to NEC theta/phi.
- Units: **metric and imperial selectable in preferences**; the domain uses
  canonical units (meters, Hz, ohms).
- Python package: `antennadesk`.
- Project format: `.antennadesk` (versioned JSON).
- Bands: **HF, VHF, and UHF from the start**, without promising accuracy
  outside the model supported by the engine.

## Product and UX

- UI in **Spanish and English**; identifiers and code in English.
- Documentation and README in English.
- i18n through `ui/i18n.py` in Phase 3; migrate to Qt Linguist `.ts`/`.qm`
  if the string catalog grows.
- Local-first, with no accounts, cloud, or mandatory telemetry.

## Quality and workflow

- Strict `mypy` for domain and application code.
- `Ruff` for lint and formatting.
- `pytest` for unit, integration, and acceptance tests.
- Coverage is a supporting signal, not proof of electromagnetic validity.
- Short-lived branches and pull requests.
- **Conventional Commits**.
- Phase 0 before the GUI; do not scaffold the whole roadmap.

## Decisions still requiring an ADR

- Final architecture and boundaries.
- Units and angular conventions (concrete implementation).
- Project format and migrations.
- Simulation execution and cancellation.
- 3D visualization strategy.
- Import/export formats.
- Linux/Windows packaging.
