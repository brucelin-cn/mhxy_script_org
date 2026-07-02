from __future__ import annotations

from datetime import datetime
from typing import Iterable


def log(message: str) -> None:
    print(message)

from .models import SchedulerConfig
from .models import TaskResult
from .models import WindowSession


class SchedulerReporter:
    def __init__(self, config: SchedulerConfig) -> None:
        self.config = config
        self.started_at = datetime.now()

    def session_started(self, session: WindowSession) -> None:
        log(
            f"[scheduler] window={session.window_index} "
            f"started missions={','.join(session.mission_order)}"
        )

    def task_started(self, session: WindowSession, task_name: str) -> None:
        log(
            f"[scheduler] window={session.window_index} "
            f"task={task_name} round={session.rounds_completed + 1} start"
        )

    def task_finished(
        self, session: WindowSession, task_name: str, result: TaskResult
    ) -> None:
        log(
            f"[scheduler] window={session.window_index} task={task_name} "
            f"status={result.status} done={result.done} message={result.message}"
        )

    def task_failed(self, session: WindowSession, task_name: str, error: Exception) -> None:
        log(
            f"[scheduler] window={session.window_index} task={task_name} "
            f"failed={type(error).__name__}: {error}"
        )

    def task_skipped(self, session: WindowSession, task_name: str, reason: str) -> None:
        log(
            f"[scheduler] window={session.window_index} task={task_name} skipped={reason}"
        )

    def session_paused(self, session: WindowSession, reason: str) -> None:
        log(f"[scheduler] window={session.window_index} paused={reason}")

    def session_completed(self, session: WindowSession) -> None:
        log(
            f"[scheduler] window={session.window_index} completed "
            f"rounds={session.rounds_completed}"
        )

    def scheduler_completed(self, sessions: Iterable[WindowSession]) -> None:
        summary = ", ".join(
            [
                (
                    f"window={session.window_index}:paused"
                    if session.paused
                    else f"window={session.window_index}:completed"
                )
                for session in sessions
            ]
        )
        log(f"[scheduler] finished {summary}")
