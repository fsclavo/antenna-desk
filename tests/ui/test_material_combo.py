# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from PySide6.QtWidgets import QComboBox
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.materials import (
    CONDUCTOR_MATERIALS,
    STAINLESS_STEEL_304,
)
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.material_combo import (
    populate_material_combo,
    retranslate_material_combo,
)


def test_populate_material_combo_uses_the_shared_order(qtbot: QtBot) -> None:
    combo = QComboBox()
    qtbot.addWidget(combo)
    translator = Translator(Language.ENGLISH)

    populate_material_combo(combo, translator)

    assert combo.count() == len(CONDUCTOR_MATERIALS)
    assert [combo.itemData(index) for index in range(combo.count())] == list(CONDUCTOR_MATERIALS)
    assert combo.itemText(2) == "Stainless steel 304"


def test_retranslate_material_combo_preserves_the_selection(qtbot: QtBot) -> None:
    combo = QComboBox()
    qtbot.addWidget(combo)
    translator = Translator(Language.ENGLISH)
    populate_material_combo(combo, translator)
    combo.setCurrentIndex(2)

    translator.set_language(Language.SPANISH)
    retranslate_material_combo(combo, translator)

    assert combo.currentData() == STAINLESS_STEEL_304
    assert combo.itemText(0) == "Cobre"
    assert combo.itemText(2) == "Acero inoxidable 304"
