from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import List

from .config import load_scheduler_config
from .models import SchedulerConfig
from .models import TaskResult
from .models import WindowSession
from .reporter import SchedulerReporter
from .task_specs import attach_task_specs


class SchedulerRunner:
    def __init__(self, config: SchedulerConfig) -> None:
        self.config = attach_task_specs(config)
        self.reporter = SchedulerReporter(self.config)
        self.started_at = datetime.now()
        self.sessions = self._build_sessions()

    @classmethod
    def from_file(cls, path: str = "resources/scheduler/scheduler.json") -> "SchedulerRunner":
        return cls(load_scheduler_config(path))

    def run(self) -> List[WindowSession]:
        for session in self.sessions:
            self.reporter.session_started(session)

        while not self._should_stop():
            active_progress = False
            for session in self.sessions:
                if session.completed or session.paused:
                    continue
                self._run_next_task(session)
                active_progress = True
                if self._should_stop():
                    break
                time.sleep(self.config.runtime.poll_interval_seconds)
            if not active_progress:
                break

        for session in self.sessions:
            if session.completed:
                self.reporter.session_completed(session)
            elif not session.paused:
                session.completed = True
                self.reporter.session_completed(session)
        self.reporter.scheduler_completed(self.sessions)
        return self.sessions

    def _build_sessions(self) -> List[WindowSession]:
        mission_order = [
            name
            for name in self.config.mission_order
            if name in self.config.missions and self.config.missions[name].enabled
        ]
        return [
            WindowSession(window_index=window_index, mission_order=list(mission_order))
            for window_index in self.config.windows
        ]

    def _run_next_task(self, session: WindowSession) -> None:
        task_name = session.current_mission_name()
        if task_name is None:
            session.completed = True
            return
        session.current_task = task_name
        spec = self.config.missions[task_name]
        self.reporter.task_started(session, task_name)
        try:
            if spec.prepare is not None:
                spec.prepare(session)
            result = spec.run(session) if spec.run is not None else TaskResult(status="hard_fail")
            if spec.check_done is not None and result.status == "success":
                done_result = spec.check_done(session)
                if done_result.done:
                    result.message = done_result.message or result.message
            self._handle_result(session, spec, result)
            self.reporter.task_finished(session, task_name, result)
        except Exception as error:
            self.reporter.task_failed(session, task_name, error)
            self._handle_exception(session, spec, error)

    def _handle_result(self, session: WindowSession, spec, result: TaskResult) -> None:
        session.last_state = result.state_name
        session.last_error = result.message
        if result.status == "success":
            session.failures_in_row = 0
            session.task_failures[spec.name] = 0
            session.last_success_at = datetime.now()
            session.advance_task()
            if self._round_limit_reached(session):
                session.completed = True
            return

        failures = session.task_failures.get(spec.name, 0) + 1
        session.task_failures[spec.name] = failures
        session.failures_in_row += 1
        if result.should_skip or failures >= self.config.runtime.max_task_failures:
            self.reporter.task_skipped(session, spec.name, result.message or result.status)
            session.advance_task()
        else:
            self._recover(session, spec)

        if result.should_pause_window or session.failures_in_row >= self.config.runtime.max_window_failures:
            session.paused = True
            self.reporter.session_paused(session, result.message or result.status)

        if self._round_limit_reached(session):
            session.completed = True

    def _handle_exception(self, session: WindowSession, spec, error: Exception) -> None:
        failures = session.task_failures.get(spec.name, 0) + 1
        session.task_failures[spec.name] = failures
        session.failures_in_row += 1
        session.last_error = str(error)
        if failures >= self.config.runtime.max_task_failures:
            self.reporter.task_skipped(session, spec.name, str(error))
            session.advance_task()
        else:
            self._recover(session, spec)
        if session.failures_in_row >= self.config.runtime.max_window_failures:
            session.paused = True
            self.reporter.session_paused(session, str(error))
        if self._round_limit_reached(session):
            session.completed = True

    def _recover(self, session: WindowSession, spec) -> None:
        for level in spec.recovery_levels:
            if not self._recovery_enabled(level):
                continue
            if spec.recover is not None:
                spec.recover(session, level)
            break

    def _recovery_enabled(self, level: str) -> bool:
        recovery = self.config.recovery
        return {
            "level_1": recovery.level_1,
            "level_2": recovery.level_2,
            "level_3": recovery.level_3,
        }.get(level, False)

    def _round_limit_reached(self, session: WindowSession) -> bool:
        round_limit = self.config.stop_condition.round_limit
        return round_limit is not None and session.rounds_completed >= round_limit

    def _should_stop(self) -> bool:
        if not self.sessions:
            return True
        if all(session.completed or session.paused for session in self.sessions):
            return True
        time_limit = self.config.stop_condition.time_limit_minutes
        if time_limit is not None and datetime.now() - self.started_at >= timedelta(minutes=time_limit):
            return True
        return False
