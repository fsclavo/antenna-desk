# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""State and translation tests for the shared task-progress widget."""

from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.widgets.task_progress import TaskProgressBar, TaskProgressState


def test_idle_widget_is_hidden(qtbot: QtBot) -> None:
    progress = TaskProgressBar(Translator(Language.ENGLISH))
    qtbot.addWidget(progress)

    assert progress.isHidden() is True
    assert progress.state is TaskProgressState.IDLE
    assert progress.text == ""


def test_indeterminate_progress_tracks_elapsed_time(qtbot: QtBot) -> None:
    progress = TaskProgressBar(Translator(Language.ENGLISH))
    qtbot.addWidget(progress)

    progress.begin_indeterminate("progress.preparing")
    progress.set_elapsed(7)

    assert progress.isHidden() is False
    assert progress.state is TaskProgressState.RUNNING
    assert progress.is_indeterminate is True
    assert progress.text == "Preparing model... · 7 s"
    assert progress.elapsed_seconds == 7


def test_determinate_progress_clamps_and_updates_text(qtbot: QtBot) -> None:
    progress = TaskProgressBar(Translator(Language.ENGLISH))
    qtbot.addWidget(progress)

    progress.begin_determinate(4, "progress.analyzing_bands")
    progress.set_progress(
        2,
        "status.bands_progress",
        index=2,
        total=4,
        band="20m",
    )
    progress.set_progress(9)

    assert progress.is_indeterminate is False
    assert progress.progress_maximum == 4
    assert progress.progress_value == 4
    assert progress.text.startswith("Band 2/4: 20m")


def test_cancelling_and_terminal_states(qtbot: QtBot) -> None:
    progress = TaskProgressBar(Translator(Language.ENGLISH))
    qtbot.addWidget(progress)
    progress.begin_determinate(3, "progress.analyzing_bands")

    progress.mark_cancelling()
    assert progress.state is TaskProgressState.CANCELLING
    assert progress.text == "Cancelling..."

    progress.complete()
    assert progress.state is TaskProgressState.COMPLETED
    assert progress.text == "Completed"
    assert progress.progress_value == 1

    progress.cancel()
    assert progress.state is TaskProgressState.CANCELLED
    assert progress.text == "Cancelled"

    progress.fail()
    assert progress.state is TaskProgressState.ERROR
    assert progress.text == "Failed"

    progress.reset()
    assert progress.state is TaskProgressState.IDLE
    assert progress.isHidden() is True
    assert progress.text == ""


def test_retranslate_updates_an_active_task(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    progress = TaskProgressBar(translator)
    qtbot.addWidget(progress)
    progress.begin_indeterminate("progress.running_solver")

    translator.set_language(Language.SPANISH)
    progress.retranslate()

    assert progress.text.startswith("Ejecutando NEC-2...")
