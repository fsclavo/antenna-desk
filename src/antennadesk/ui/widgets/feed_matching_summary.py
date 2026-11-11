# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Persistent feed-line and matching-network summary for the design panel."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.balun import BalunLoss
from ...domain.antennas.design import AntennaDesignParameters
from ...domain.antennas.endfed import EndFedParameters
from ...domain.antennas.feed_line import FeedLine
from ...domain.antennas.matching_network import MatchingNetwork
from ...domain.design.matching_resolution import resolve_matching_network
from ...reporting.design_summary import matching_network_description
from ..help import apply_help
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_unit_key


class FeedMatchingSummary(QGroupBox):
    """Show the internal EFHW, project, feed-line, and balun state."""

    edit_network_requested = Signal()
    remove_network_requested = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._parameters: AntennaDesignParameters | None = None
        self._project_network: MatchingNetwork | None = None
        self._feed_line: FeedLine | None = None
        self._balun_loss: BalunLoss | None = None

        self._endfed_label = QLabel(self)
        self._project_label = QLabel(self)
        self._feed_line_label = QLabel(self)
        self._balun_label = QLabel(self)
        self._endfed_value = self._value_label()
        self._project_value = self._value_label()
        self._feed_line_value = self._value_label()
        self._balun_value = self._value_label()

        form = QFormLayout()
        form.addRow(self._endfed_label, self._endfed_value)
        form.addRow(self._project_label, self._project_value)
        form.addRow(self._feed_line_label, self._feed_line_value)
        form.addRow(self._balun_label, self._balun_value)

        self._warning = QLabel(self)
        self._warning.setWordWrap(True)
        self._warning.setStyleSheet("color: #8a5a00;")
        self._edit_button = QPushButton(self)
        self._edit_button.setFlat(True)
        self._edit_button.clicked.connect(self.edit_network_requested)
        self._remove_button = QPushButton(self)
        self._remove_button.setFlat(True)
        self._remove_button.clicked.connect(self.remove_network_requested)
        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.addWidget(self._edit_button)
        actions.addWidget(self._remove_button)
        actions.addStretch(1)
        self._warning_container = QWidget(self)
        warning_layout = QVBoxLayout(self._warning_container)
        warning_layout.setContentsMargins(0, 0, 0, 0)
        warning_layout.addWidget(self._warning)
        warning_layout.addLayout(actions)
        self._warning_container.setVisible(False)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._warning_container)
        self.retranslate()

    def _value_label(self) -> QLabel:
        label = QLabel(self)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        return label

    def set_state(
        self,
        parameters: AntennaDesignParameters | None,
        project_network: MatchingNetwork | None,
        feed_line: FeedLine | None,
        balun_loss: BalunLoss | None,
    ) -> None:
        self._parameters = parameters
        self._project_network = project_network
        self._feed_line = feed_line
        self._balun_loss = balun_loss
        self._refresh()

    def retranslate(self) -> None:
        self.setTitle(self._translator.t("feed_matching.title").replace("&", "&&"))
        self._endfed_label.setText(self._translator.t("feed_matching.endfed"))
        self._project_label.setText(self._translator.t("feed_matching.project"))
        self._feed_line_label.setText(self._translator.t("feed_matching.feed_line"))
        self._balun_label.setText(self._translator.t("feed_matching.balun"))
        self._edit_button.setText(self._translator.t("feed_matching.edit"))
        self._remove_button.setText(self._translator.t("feed_matching.remove"))
        self._warning.setText(self._translator.t("feed_matching.override_warning"))
        apply_help(self, self._translator, "section.feed_matching")
        apply_help(self._warning, self._translator, "feed_matching.override")
        apply_help(self._edit_button, self._translator, "action.matching_network")
        apply_help(self._remove_button, self._translator, "feed_matching.remove")
        self._refresh()

    def _refresh(self) -> None:
        parameters = self._parameters
        if parameters is None:
            values = (self._translator.t("feed_matching.none"),) * 4
            for label, value in zip(
                (
                    self._endfed_value,
                    self._project_value,
                    self._feed_line_value,
                    self._balun_value,
                ),
                values,
                strict=True,
            ):
                label.setText(value)
            self._warning_container.setVisible(False)
            return

        resolution = resolve_matching_network(parameters, self._project_network)
        self._endfed_value.setText(self._endfed_text(parameters, resolution.override_active))
        self._project_value.setText(self._project_network_text())
        self._feed_line_value.setText(self._feed_line_text())
        self._balun_value.setText(self._balun_text())
        self._warning_container.setVisible(resolution.override_active)

    def _endfed_text(self, parameters: AntennaDesignParameters, override_active: bool) -> str:
        if not isinstance(parameters, EndFedParameters):
            return self._translator.t("feed_matching.not_applicable")
        if not parameters.matching_network_active:
            return self._translator.t("feed_matching.none")
        status = self._translator.t(
            "feed_matching.retained" if override_active else "feed_matching.active"
        )
        return self._translator.t(
            "feed_matching.internal_value",
            capacitance=f"{parameters.matching_capacitance_f * 1e12:g}",
            leakage=f"{parameters.transformer_leakage_inductance_h * 1e6:g}",
            status=status,
        )

    def _project_network_text(self) -> str:
        network = self._project_network
        if network is None:
            return self._translator.t("feed_matching.none")
        state = self._translator.t(
            "feed_matching.active" if network.is_active else "feed_matching.inactive"
        )
        return self._translator.t(
            "feed_matching.network_state",
            network=matching_network_description(network, self._translator.report),
            state=state,
        )

    def _feed_line_text(self) -> str:
        feed_line = self._feed_line
        if feed_line is None or not feed_line.is_active:
            return self._translator.t("feed_matching.none")
        unit = self._translator.t(length_unit_key(self._unit_system))
        return self._translator.t(
            "feed_matching.feed_line_value",
            impedance=f"{feed_line.characteristic_impedance_ohm:g}",
            length=f"{length_from_m(feed_line.length_m, self._unit_system):.2f}",
            unit=unit,
            velocity=f"{feed_line.velocity_factor:g}",
        )

    def _balun_text(self) -> str:
        balun = self._balun_loss
        if balun is None or not balun.is_active:
            return self._translator.t("feed_matching.none")
        return self._translator.t(
            "feed_matching.balun_value",
            loss=f"{balun.reference_loss_db:.2f}",
            frequency=f"{balun.reference_frequency_hz / 1e6:.3f}",
            exponent=f"{balun.exponent:g}",
        )
