# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import Any

import pytest

from antennadesk.persistence.constants import SCHEMA_VERSION
from antennadesk.persistence.errors import ProjectFormatError, UnsupportedSchemaVersion
from antennadesk.persistence.migrations import migrate_document


def _document(version: int) -> dict[str, Any]:
    return {
        "format": "antennadesk-project",
        "schema_version": version,
        "project": {},
    }


def test_current_version_is_an_identity() -> None:
    document = _document(SCHEMA_VERSION)
    assert migrate_document(document) == document


def test_migrations_are_applied_in_order() -> None:
    calls: list[int] = []

    def migrate_1_to_2(data: dict[str, Any]) -> dict[str, Any]:
        calls.append(1)
        migrated = dict(data)
        migrated["from_v1"] = True
        return migrated

    def migrate_2_to_3(data: dict[str, Any]) -> dict[str, Any]:
        calls.append(2)
        migrated = dict(data)
        migrated["from_v2"] = True
        return migrated

    result = migrate_document(
        _document(1),
        target_version=3,
        migrations={1: migrate_1_to_2, 2: migrate_2_to_3},
    )

    assert calls == [1, 2]
    assert result["schema_version"] == 3
    assert result["from_v1"] is True
    assert result["from_v2"] is True


def test_future_version_is_rejected() -> None:
    with pytest.raises(UnsupportedSchemaVersion) as error:
        migrate_document(
            _document(SCHEMA_VERSION + 1),
            target_version=SCHEMA_VERSION,
        )
    assert error.value.found == SCHEMA_VERSION + 1
    assert error.value.supported == SCHEMA_VERSION


def test_missing_migration_is_rejected() -> None:
    with pytest.raises(ProjectFormatError, match="no migration"):
        migrate_document(_document(1), target_version=2, migrations={})


def test_unknown_format_is_rejected() -> None:
    document = _document(1)
    document["format"] = "something-else"
    with pytest.raises(ProjectFormatError, match="format"):
        migrate_document(document)


@pytest.mark.parametrize("version", ["1", True, 0, -1, None])
def test_invalid_schema_versions_are_rejected(version: object) -> None:
    document = _document(1)
    document["schema_version"] = version
    with pytest.raises(ProjectFormatError, match="schema_version"):
        migrate_document(document)


def test_v1_migration_adds_horizontal_orientation() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 1,
        "project": {
            "designs": [
                {
                    "parameters": {
                        "frequency_hz": 7_100_000.0,
                        "total_length_m": 20.0,
                        "height_m": 8.0,
                    }
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0]["parameters"]["orientation"] == "horizontal"
    assert migrated["project"]["simulation_runs"] == []
    assert "orientation" not in document["project"]["designs"][0]["parameters"]


def test_v2_migration_adds_simulation_runs() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 2,
        "project": {
            "designs": [],
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["simulation_runs"] == []
    assert "simulation_runs" not in document["project"]


def test_v3_migration_adds_optional_band_metadata() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 3,
        "project": {
            "simulation_runs": [
                {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "design_id": "00000000-0000-0000-0000-000000000002",
                    "created_at": "2026-11-03T12:00:00Z",
                    "result": {},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["simulation_runs"][0]["band_id"] is None
    assert migrated["project"]["simulation_runs"][0]["batch_id"] is None


def test_v5_migration_adds_optional_design_band_plans() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 5,
        "project": {
            "designs": [{"antenna_type": "wire_dipole", "parameters": {}}],
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0]["band_plan"] is None
    assert "band_plan" not in document["project"]["designs"][0]


def test_v6_migration_adds_horizontal_polarization_to_arrays() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 6,
        "project": {
            "designs": [
                {"antenna_type": "yagi", "parameters": {}},
                {"antenna_type": "moxon", "parameters": {}},
                {"antenna_type": "wire_dipole", "parameters": {}},
                {"antenna_type": "custom", "parameters": {}},
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0]["parameters"]["polarization"] == "horizontal"
    assert migrated["project"]["designs"][1]["parameters"]["polarization"] == "horizontal"
    assert "polarization" not in migrated["project"]["designs"][2]["parameters"]
    assert "polarization" not in migrated["project"]["designs"][3]["parameters"]
    assert "polarization" not in document["project"]["designs"][0]["parameters"]


def test_v7_migration_adds_top_hat_fields_to_verticals() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 7,
        "project": {
            "designs": [
                {
                    "antenna_type": "vertical",
                    "parameters": {},
                    "antenna": {
                        "wires": [
                            {
                                "id": "top-hat-1",
                                "start": {"x_m": 0.0, "y_m": 0.0, "z_m": 9.0},
                                "end": {"x_m": 0.5, "y_m": 0.0, "z_m": 9.0},
                            },
                            {
                                "id": "top-hat-2",
                                "start": {"x_m": 0.0, "y_m": 0.0, "z_m": 9.0},
                                "end": {"x_m": 0.0, "y_m": 0.5, "z_m": 9.0},
                            },
                        ]
                    },
                },
                {
                    "antenna_type": "vertical",
                    "parameters": {},
                    "antenna": {"wires": []},
                },
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {},
                    "antenna": {"wires": []},
                },
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    first = migrated["project"]["designs"][0]["parameters"]
    assert first["top_hat_enabled"] is True
    assert first["top_hat_wire_count"] == 2
    assert first["top_hat_radius_m"] == pytest.approx(0.5)
    second = migrated["project"]["designs"][1]["parameters"]
    assert second["top_hat_enabled"] is False
    assert second["top_hat_wire_count"] == 0
    assert second["top_hat_radius_m"] == 0.0
    assert "top_hat_enabled" not in migrated["project"]["designs"][2]["parameters"]
    assert "top_hat_enabled" not in document["project"]["designs"][0]["parameters"]


def test_v7_migration_marks_negative_resistance_runs() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 7,
        "project": {
            "designs": [],
            "simulation_runs": [
                {
                    "result": {
                        "status": "completed",
                        "frequencies": [
                            {"impedance_real_ohm": -10.0},
                            {"impedance_real_ohm": -5.0},
                        ],
                        "diagnostics": [],
                    }
                }
            ],
        },
    }

    migrated = migrate_document(document)

    result = migrated["project"]["simulation_runs"][0]["result"]
    assert result["status"] == "error"
    assert result["diagnostics"][0]["code"] == "normalization.negative_resistance"
    assert result["diagnostics"][0]["severity"] == "error"


def test_v8_migration_keeps_existing_designs_unchanged() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 8,
        "project": {
            "designs": [
                {"antenna_type": "wire_dipole", "parameters": {"frequency_hz": 7_100_000.0}}
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]
    assert "inverted_l" not in migrated["project"]["designs"][0]


def test_v9_migration_adds_vertical_orientation_to_loops() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 9,
        "project": {
            "designs": [
                {
                    "antenna_type": "loop",
                    "parameters": {"frequency_hz": 7_100_000.0, "sides": 4},
                },
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"frequency_hz": 7_100_000.0},
                },
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0]["parameters"]["orientation"] == "vertical"
    assert "orientation" not in migrated["project"]["designs"][1]["parameters"]


def test_v10_migration_keeps_existing_designs_unchanged() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 10,
        "project": {
            "designs": [{"antenna_type": "loop", "parameters": {"frequency_hz": 7_100_000.0}}]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v11_migration_adds_straight_driven_yagi_defaults() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 11,
        "project": {
            "designs": [
                {"antenna_type": "yagi", "parameters": {}},
                {"antenna_type": "loop", "parameters": {}},
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    yagi = migrated["project"]["designs"][0]["parameters"]
    assert yagi["driven_folded"] is False
    assert yagi["driven_fold_spacing_m"] == pytest.approx(0.1)
    assert "driven_folded" not in migrated["project"]["designs"][1]["parameters"]


def test_v12_migration_adds_no_match_yagi_defaults() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 12,
        "project": {
            "designs": [
                {"antenna_type": "yagi", "parameters": {}},
                {"antenna_type": "magnetic_loop", "parameters": {}},
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    yagi = migrated["project"]["designs"][0]["parameters"]
    assert yagi["match_type"] == "none"
    assert yagi["match_length_m"] == pytest.approx(0.2)
    assert yagi["match_spacing_m"] == pytest.approx(0.1)
    assert "match_type" not in migrated["project"]["designs"][1]["parameters"]


def test_v13_migration_adds_project_balun_loss_field() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 13,
        "project": {
            "designs": [],
            "simulation_runs": [
                {
                    "result": {
                        "status": "completed",
                        "frequencies": [{"impedance_real_ohm": 50.0}],
                        "diagnostics": [],
                    }
                }
            ],
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert "balun_loss" in migrated["project"]
    assert migrated["project"]["balun_loss"] is None
    assert "balun_loss_db" in migrated["project"]["simulation_runs"][0]["result"]["frequencies"][0]


def test_v14_migration_repairs_undersized_yagi_match_hardware() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 14,
        "project": {
            "designs": [
                {
                    "antenna_type": "yagi",
                    "parameters": {
                        "elements": [
                            {"position_m": 0.0, "length_m": 1.0, "radius_m": 0.00635},
                            {"position_m": 0.2, "length_m": 1.0, "radius_m": 0.00635},
                        ],
                        "driven_index": 1,
                        "match_type": "beta_hairpin",
                        "match_length_m": 0.019,
                        "match_spacing_m": 0.01,
                    },
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    parameters = migrated["project"]["designs"][0]["parameters"]
    assert parameters["match_spacing_m"] == pytest.approx(0.0254)
    assert parameters["match_length_m"] == pytest.approx(0.0508)


def test_v15_migration_introduces_the_self_contained_vertical_arrays() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 15,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v29_migration_introduces_the_hexbeam_design_type() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 29,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v28_migration_introduces_per_source_results() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 28,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v27_migration_introduces_the_trap_yagi_design_type() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 27,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v26_migration_introduces_the_discone_design_type() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 26,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v25_migration_introduces_the_quad_beam_design_type() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 25,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v24_migration_introduces_the_phased_vertical_design_type() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 24,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v23_migration_introduces_additional_sources() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 23,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v22_migration_introduces_tapered_yagi_tips() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 22,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v21_migration_introduces_optional_dipole_sag() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 21,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v20_migration_introduces_the_loaded_dipole_design_type() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 20,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v19_migration_introduces_the_beverage_design_type() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 19,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v30_migration_adds_endfed_loading_coil_defaults() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 30,
        "project": {
            "designs": [
                {
                    "antenna_type": "endfed",
                    "parameters": {"length_m": 20.0},
                },
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                },
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    endfed = migrated["project"]["designs"][0]["parameters"]
    assert endfed["loading_coil_enabled"] is False
    assert endfed["loading_coil_offset_m"] == 0.0
    assert endfed["loading_coil_inductance_h"] == 0.0
    assert endfed["loading_coil_resistance_ohm"] == 0.0
    assert "loading_coil_enabled" not in migrated["project"]["designs"][1]["parameters"]


def test_v30_migration_tolerates_a_missing_project() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 30,
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert "project" not in migrated


def test_v30_migration_tolerates_non_list_designs() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 30,
        "project": {"designs": {"not": "a list"}},
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"] == {"not": "a list"}


def test_v30_migration_tolerates_an_endfed_design_without_parameters() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 30,
        "project": {
            "designs": [
                {
                    "antenna_type": "endfed",
                    "parameters": None,
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0]["parameters"] is None


def test_v18_migration_introduces_biquad_design_types() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 18,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v17_migration_introduces_persisted_optimization_summaries() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 17,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v16_migration_introduces_typed_doublet_and_zepp_designs() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 16,
        "project": {
            "designs": [
                {
                    "antenna_type": "wire_dipole",
                    "parameters": {"total_length_m": 20.0},
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0] == document["project"]["designs"][0]


def test_v4_migration_adds_optional_transformer_ratios() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 4,
        "project": {
            "designs": [
                {"antenna_type": "ocfd", "parameters": {}},
                {"antenna_type": "custom", "parameters": {}},
                {"antenna_type": "wire_dipole", "parameters": {}},
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0]["parameters"]["transformer_ratio"] == 1.0
    assert migrated["project"]["designs"][1]["parameters"]["feed_transformer_ratio"] == 1.0
    assert "transformer_ratio" not in migrated["project"]["designs"][2]["parameters"]


def test_v31_migration_adds_endfed_feed_section_and_installation_return() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 31,
        "project": {
            "designs": [
                {
                    "antenna_type": "endfed",
                    "parameters": {
                        "frequency_hz": 7_100_000.0,
                        "length_m": 20.0,
                        "feed_height_m": 10.0,
                        "end_height_m": 10.0,
                        "transformer_ratio": 49.0,
                    },
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    parameters = migrated["project"]["designs"][0]["parameters"]
    assert parameters["feed_section_length_m"] == 0.0
    assert parameters["installation_return_length_m"] == 0.0
    assert "feed_section_length_m" not in document["project"]["designs"][0]["parameters"]


def test_v32_migration_adds_the_endfed_matching_network_fields() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 32,
        "project": {
            "designs": [
                {
                    "antenna_type": "endfed",
                    "parameters": {
                        "frequency_hz": 7_100_000.0,
                        "length_m": 20.0,
                        "transformer_ratio": 49.0,
                    },
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    parameters = migrated["project"]["designs"][0]["parameters"]
    assert parameters["matching_capacitance_f"] == 0.0
    assert parameters["transformer_leakage_inductance_h"] == 0.0
    assert "matching_capacitance_f" not in document["project"]["designs"][0]["parameters"]


def test_v33_migration_adds_the_matching_network_design_target() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 33,
        "project": {
            "matching_network": {
                "topology": "l",
                "series_inductance_h": 1e-6,
                "shunt_capacitance_f": 100e-12,
            }
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["matching_network_design"] is None
    assert "matching_network_design" not in document["project"]


def test_v39_migration_adds_the_project_journal() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 39,
        "project": {"name": "Site"},
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["journal_entries"] == []
    assert "journal_entries" not in document["project"]


def test_v39_migration_tolerates_a_missing_project() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 39,
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert "project" not in migrated


def test_v38_migration_adds_measurement_sessions() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 38,
        "project": {
            "name": "Site",
            "measurements": [
                {"id": "measurement", "name": "Field sweep"},
                {"id": "legacy", "name": "Legacy"},
            ],
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["measurement_sessions"] == []
    assert all(
        measurement["session_id"] is None for measurement in migrated["project"]["measurements"]
    )
    assert "measurement_sessions" not in document["project"]
    assert all(
        "session_id" not in measurement for measurement in document["project"]["measurements"]
    )


def test_v37_migration_adds_the_construction_record() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 37,
        "project": {"name": "Site"},
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["construction_record"] is None
    assert "construction_record" not in document["project"]


def test_v36_migration_adds_the_matching_network_position() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 36,
        "project": {
            "matching_network": {
                "topology": "l",
                "series_inductance_h": 1e-6,
                "shunt_capacitance_f": 100e-12,
            },
            "simulation_runs": [{"result": {"spec": {}}}],
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["matching_network_position"] == "feedpoint"
    assert (
        migrated["project"]["simulation_runs"][0]["result"]["spec"]["matching_network_position"]
        == "feedpoint"
    )
    assert "matching_network_position" not in document["project"]


def test_v35_migration_adds_installation_profiles() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 35,
        "project": {"name": "Site"},
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["installation_profiles"] == []
    assert migrated["project"]["active_installation_profile_id"] is None
    assert "installation_profiles" not in document["project"]


def test_v34_migration_adds_the_endfed_bend_fields() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 34,
        "project": {
            "designs": [
                {
                    "antenna_type": "endfed",
                    "parameters": {
                        "frequency_hz": 7_100_000.0,
                        "length_m": 20.0,
                        "transformer_ratio": 49.0,
                    },
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    parameters = migrated["project"]["designs"][0]["parameters"]
    assert parameters["bend_enabled"] is False
    assert parameters["bend_vertical_length_m"] == 0.0
    assert "bend_enabled" not in document["project"]["designs"][0]["parameters"]
