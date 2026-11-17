# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Default conductor material for each new-design catalog template."""

from __future__ import annotations

from .materials import ALUMINUM, COPPER, STAINLESS_STEEL_304, ConductorMaterial

_ALUMINUM_TEMPLATES = frozenset(
    {
        "yagi",
        "trap_yagi",
        "log_periodic",
        "vertical",
        "ringo",
        "j_pole",
        "slim_jim",
        "discone",
        "phased_vertical",
        "moxon",
        "hexbeam",
        "quad_beam",
        "biquad",
        "double_biquad",
        "half_square",
    }
)
_STAINLESS_TEMPLATES = frozenset({"loaded_vertical"})
_COPPER_TEMPLATES = frozenset(
    {
        "wire_dipole",
        "folded_dipole",
        "bobtail_curtain",
        "beverage",
        "loaded_dipole",
        "endfed",
        "sloper",
        "random_wire",
        "shortened_endfed_80_10",
        "shortened_endfed_40_10",
        "g5rv",
        "zs6bkw",
        "zepp",
        "doublet",
        "fan_dipole",
        "trap_dipole",
        "t2fd",
        "inverted_v",
        "inverted_l",
        "ocfd",
        "loop",
        "delta_loop",
        "quad_loop",
        "magnetic_loop",
        "custom",
    }
)

# All catalog templates must have exactly one material. The coverage test
# compares this mapping with the UI catalog entries.
TEMPLATE_MATERIAL_DEFAULTS: dict[str, ConductorMaterial] = {
    **{key: ALUMINUM for key in _ALUMINUM_TEMPLATES},
    **{key: STAINLESS_STEEL_304 for key in _STAINLESS_TEMPLATES},
    **{key: COPPER for key in _COPPER_TEMPLATES},
}


def default_material_for_template(template_id: str) -> ConductorMaterial:
    """Return the agreed new-design material for a catalog template key."""

    return TEMPLATE_MATERIAL_DEFAULTS.get(template_id, COPPER)
