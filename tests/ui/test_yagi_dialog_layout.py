# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""UX50 layout contract for the wide Yagi generator dialog."""

from __future__ import annotations

import pytest
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QAbstractScrollArea, QApplication, QFormLayout
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.yagi_dialog import YagiDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.preferences import FontSize, FontSizeController
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.yagi_form import YagiForm

LEFT_KEYS = (
    "field.frequency",
    "field.height",
    "field.azimuth",
    "field.polarization",
    "yagi.radius",
    "yagi.taper_length",
    "yagi.taper_radius",
    "yagi.mast_diameter",
    "yagi.mast_offset",
    "yagi.guy_count",
    "yagi.guy_anchor",
    "yagi.guy_diameter",
)
RIGHT_KEYS = (
    "field.material",
    "field.ground",
    "field.soil_preset",
    "field.permittivity",
    "field.conductivity",
    "yagi.driven",
    None,
    "yagi.fold_spacing",
    "field.transformer_ratio",
    "yagi.match_type",
    "yagi.match_length",
    "yagi.match_spacing",
)


def _row_keys(form: QFormLayout) -> tuple[str | None, ...]:
    keys: list[str | None] = []
    for row in range(form.rowCount()):
        label_item = form.itemAt(row, QFormLayout.ItemRole.LabelRole)
        label = label_item.widget() if label_item is not None else None
        keys.append(label.objectName() if label is not None else None)
    return tuple(keys)


def _show(dialog: YagiDialog, qtbot: QtBot, width: int, height: int) -> None:
    dialog.resize(width, height)
    dialog.show()
    qtbot.wait(10)
    QApplication.processEvents()


def test_wide_dialog_uses_two_columns_in_the_expected_order(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    form = dialog._form

    assert form._wide_layout is True
    assert form._feed_form is not None
    assert _row_keys(form._geometry_form) == LEFT_KEYS
    assert _row_keys(form._feed_form)[:6] == RIGHT_KEYS[:6]
    assert _row_keys(form._feed_form)[7:] == RIGHT_KEYS[7:]
    folded_item = form._feed_form.itemAt(6, QFormLayout.ItemRole.FieldRole)
    assert folded_item is not None
    assert folded_item.widget() is form._driven_folded


def test_sidebar_yagi_form_stays_single_column(qtbot: QtBot) -> None:
    form = YagiForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)

    assert form._wide_layout is False
    assert form._feed_form is None
    assert "yagi.mast_diameter" in _row_keys(form._geometry_form)
    assert "field.material" in _row_keys(form._geometry_form)


def test_transformer_row_lives_in_the_right_column_and_hides(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    _show(dialog, qtbot, 920, 860)
    form = dialog._form
    assert form._feed_form is not None

    assert form._feed_form.indexOf(form._transformer) >= 0
    assert form._geometry_form.indexOf(form._transformer) == -1
    assert form._transformer.isHidden() is True

    form._driven_folded.setChecked(True)
    qtbot.wait(10)

    assert form._transformer.isVisible() is True
    assert form._transformer_label.isVisible() is True


def test_dialog_minimum_height_is_bounded_by_the_scroll_area(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    assert dialog.minimumSizeHint().height() <= 640
    assert dialog._scroll.widgetResizable() is True
    assert dialog._scroll.widget() is dialog._form


@pytest.mark.parametrize("language", [Language.ENGLISH, Language.SPANISH])
def test_dialog_fits_without_scrolling_at_the_default_height(
    qtbot: QtBot,
    language: Language,
) -> None:
    dialog = YagiDialog(Translator(language), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    _show(dialog, qtbot, 920, 860)

    assert dialog._scroll.verticalScrollBar().maximum() == 0
    assert dialog._scroll.horizontalScrollBar().maximum() == 0


def test_table_grows_when_extra_height_is_available(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    _show(dialog, qtbot, 920, 972)

    assert dialog._scroll.verticalScrollBar().maximum() == 0
    assert dialog._table.height() > dialog._table.minimumHeight()


def test_table_does_not_drive_the_form_width(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.SPANISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    assert dialog._table.sizeAdjustPolicy() is QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored


@pytest.mark.parametrize("language", [Language.ENGLISH, Language.SPANISH])
def test_actions_stay_visible_when_the_form_scrolls(
    qtbot: QtBot,
    language: Language,
) -> None:
    dialog = YagiDialog(Translator(language), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    _show(dialog, qtbot, 920, 640)

    assert dialog._buttons.isVisible() is True
    button_rect = dialog._buttons.geometry()
    assert button_rect.top() >= 0
    assert button_rect.bottom() <= dialog.rect().bottom()
    assert dialog._scroll.verticalScrollBar().maximum() > 0
    assert dialog._scroll.horizontalScrollBar().maximum() == 0


def test_actions_stay_visible_with_a_warning_and_ten_elements(
    qtbot: QtBot,
) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    for _ in range(5):
        dialog._add_element()
    dialog._table.item(1, 2).setText("5.000")
    _show(dialog, qtbot, 920, 640)

    assert dialog._table.rowCount() == 10
    assert dialog._form._frequency_warning.isVisible() is True
    assert dialog._buttons.isVisible() is True
    button_rect = dialog._buttons.geometry()
    assert button_rect.bottom() <= dialog.rect().bottom()
    assert dialog._scroll.verticalScrollBar().maximum() > 0
    assert dialog._scroll.horizontalScrollBar().maximum() == 0


def test_dialog_avoids_horizontal_scrolling_with_large_spanish(
    qtbot: QtBot,
) -> None:
    app = QApplication.instance()
    assert isinstance(app, QApplication)
    controller = FontSizeController(QFont("Sans Serif", 10))
    controller.apply(FontSize.LARGE)
    try:
        dialog = YagiDialog(Translator(Language.SPANISH), UnitSystem.METRIC)
        qtbot.addWidget(dialog)
        _show(dialog, qtbot, 920, 640)

        assert dialog._form.minimumSizeHint().width() <= dialog._scroll.viewport().width()
        assert dialog._scroll.horizontalScrollBar().maximum() == 0
        assert dialog._buttons.isVisible() is True
        assert dialog._buttons.geometry().bottom() <= dialog.rect().bottom()
    finally:
        controller.apply(FontSize.MEDIUM)
