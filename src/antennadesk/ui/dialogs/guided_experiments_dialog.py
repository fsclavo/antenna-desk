# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided experiments that preset the bounded parameter sweep."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...application.ports.antenna_solver import AntennaSolver
from ...domain.antennas.design import AntennaDesignParameters
from ...domain.design.guided_experiments import (
    GuidedExperimentAvailability,
    GuidedExperimentKey,
    guided_experiments,
)
from ...domain.design.sweep import SweepAxis
from ...domain.optimization.descriptor import AntennaOptimizerDescriptor
from ...domain.projects.project import DesignVariant
from ...domain.simulation.spec import SimulationSpec
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator
from ..units import (
    UnitSystem,
    length_from_m,
    length_unit_key,
    radius_from_m,
    radius_unit_key,
)
from .parameter_sweep_dialog import ParameterSweepDialog, SweepGuide


@dataclass(frozen=True, slots=True)
class _ExperimentText:
    title_key: str
    question_key: str
    step_keys: tuple[str, str, str]
    look_for_key: str
    limits_key: str


_TEXTS: dict[GuidedExperimentKey, _ExperimentText] = {
    GuidedExperimentKey.RESONANCE: _ExperimentText(
        title_key="guided.resonance.title",
        question_key="guided.resonance.question",
        step_keys=(
            "guided.resonance.step.1",
            "guided.resonance.step.2",
            "guided.resonance.step.3",
        ),
        look_for_key="guided.resonance.look_for",
        limits_key="guided.resonance.limits",
    ),
    GuidedExperimentKey.GROUND_HEIGHT: _ExperimentText(
        title_key="guided.ground_height.title",
        question_key="guided.ground_height.question",
        step_keys=(
            "guided.ground_height.step.1",
            "guided.ground_height.step.2",
            "guided.ground_height.step.3",
        ),
        look_for_key="guided.ground_height.look_for",
        limits_key="guided.ground_height.limits",
    ),
    GuidedExperimentKey.INTERACTION: _ExperimentText(
        title_key="guided.interaction.title",
        question_key="guided.interaction.question",
        step_keys=(
            "guided.interaction.step.1",
            "guided.interaction.step.2",
            "guided.interaction.step.3",
        ),
        look_for_key="guided.interaction.look_for",
        limits_key="guided.interaction.limits",
    ),
}


class GuidedExperimentsDialog(QDialog):
    """Choose one curated experiment and launch it in the sweep dialog."""

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        solver: AntennaSolver,
        descriptor: AntennaOptimizerDescriptor,
        design: DesignVariant,
        base_spec: SimulationSpec,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._solver = solver
        self._descriptor = descriptor
        self._design = design
        self._base_spec = base_spec
        self._selected_parameters: AntennaDesignParameters | None = None
        self._experiments = guided_experiments(
            descriptor,
            design.parameters.frequency_hz,
        )
        self.setWindowTitle(translator.t("guided.title"))
        self.resize(*scaled_dialog_size(860, 640))

        self._intro = QLabel(translator.t("guided.intro"), self)
        self._intro.setWordWrap(True)
        apply_help(self._intro, translator, "guided.list")

        self._list = QListWidget(self)
        for availability in self._experiments:
            text = self._title(availability)
            if not availability.available:
                text = f"{text} — {translator.t(availability.reason_key)}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, availability.key.value)
            if not availability.available:
                item.setFlags(Qt.ItemFlag.NoItemFlags)
            self._list.addItem(item)
        self._list.currentRowChanged.connect(self._selection_changed)
        apply_help(self._list, translator, "guided.list")

        self._details = QLabel(self)
        self._details.setWordWrap(True)
        self._details.setTextFormat(Qt.TextFormat.PlainText)
        self._details.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        apply_help(self._details, translator, "guided.details")

        self._start = QPushButton(translator.t("guided.start"), self)
        self._start.clicked.connect(self._start_experiment)
        apply_help(self._start, translator, "guided.start")
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close,
            parent=self,
        )
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(translator.t("action.close"))
        buttons.rejected.connect(self.reject)

        actions = QHBoxLayout()
        actions.addWidget(self._start)
        actions.addStretch(1)
        actions.addWidget(buttons)

        layout = QVBoxLayout(self)
        layout.addWidget(self._intro)
        layout.addWidget(self._list, 1)
        layout.addWidget(self._details, 2)
        layout.addLayout(actions)

        self._select_initial()
        self._selection_changed()

    def selected_parameters(self) -> AntennaDesignParameters | None:
        return self._selected_parameters

    def _title(self, availability: GuidedExperimentAvailability) -> str:
        return self._translator.t(_TEXTS[availability.key].title_key)

    def _select_initial(self) -> None:
        for row, availability in enumerate(self._experiments):
            if availability.available:
                self._list.setCurrentRow(row)
                return
        self._list.setCurrentRow(0)

    def _selected_availability(self) -> GuidedExperimentAvailability | None:
        row = self._list.currentRow()
        if 0 <= row < len(self._experiments):
            return self._experiments[row]
        return None

    def _selection_changed(self, *_args: object) -> None:
        availability = self._selected_availability()
        if availability is None:
            self._details.clear()
            self._start.setEnabled(False)
            return
        self._details.setText(self._details_text(availability))
        self._start.setEnabled(availability.available)

    def _details_text(self, availability: GuidedExperimentAvailability) -> str:
        t = self._translator.t
        text = _TEXTS[availability.key]
        lines = [
            t(text.title_key),
            t(text.question_key),
            "",
            f"{t('guided.steps')}:",
            *(f"{index}. {t(key)}" for index, key in enumerate(text.step_keys, start=1)),
            "",
        ]
        experiment = availability.experiment
        if experiment is None:
            lines.append(t("guided.unavailable", reason=t(availability.reason_key)))
            return "\n".join(lines)
        plan = experiment.plan
        lines.append(self._axis_text("guided.range_x", plan.x_axis))
        if plan.y_axis is not None:
            lines.append(self._axis_text("guided.range_y", plan.y_axis))
        lines.extend(
            (
                t(
                    "guided.metric",
                    metric=t(f"sweep.metric.{plan.metric.value}"),
                ),
                "",
                f"{t('guided.look_for')}: {t(text.look_for_key)}",
                f"{t('guided.limits')}: {t(text.limits_key)}",
            )
        )
        return "\n".join(lines)

    def _axis_text(self, key: str, axis: SweepAxis) -> str:
        return self._translator.t(
            key,
            variable=self._translator.t(axis.label_key),
            low=self._axis_value(axis, axis.values[0]),
            high=self._axis_value(axis, axis.values[-1]),
            points=axis.count,
        )

    def _axis_value(self, axis: SweepAxis, value: float) -> str:
        if axis.unit == "m":
            unit = self._translator.t(length_unit_key(self._unit_system))
            return f"{length_from_m(value, self._unit_system):.3f} {unit}"
        if axis.unit == "radius":
            unit = self._translator.t(radius_unit_key(self._unit_system))
            return f"{radius_from_m(value, self._unit_system):.4f} {unit}"
        return f"{value:g}"

    def _start_experiment(self) -> None:
        availability = self._selected_availability()
        if availability is None or availability.experiment is None:
            return
        text = _TEXTS[availability.key]
        dialog = ParameterSweepDialog(
            self._translator,
            self._unit_system,
            self._solver,
            self._descriptor,
            self._design,
            self._base_spec,
            self,
            preset_plan=availability.experiment.plan,
            guide=SweepGuide(
                title_key=text.title_key,
                question_key=text.question_key,
                look_for_key=text.look_for_key,
                limits_key=text.limits_key,
            ),
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = dialog.selected_parameters()
        if selected is None:
            return
        self._selected_parameters = selected
        self.accept()
