from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


TaskCallable = Callable[["WindowSession"], "TaskResult"]
RecoveryCallable = Callable[["WindowSession", str], None]


@dataclass
class StopCondition:
    mode: str = "any"
    round_limit: Optional[int] = None
    time_limit_minutes: Optional[int] = None
    resource_limit_enabled: bool = False


@dataclass
class RuntimeConfig:
    poll_interval_seconds: float = 2.0
    max_task_failures: int = 3
    max_window_failures: int = 8


@dataclass
class RecoveryConfig:
    level_1: bool = True
    level_2: bool = True
    level_3: bool = False


@dataclass
class ReportingConfig:
    enable_screenshots: bool = False
    enable_ui_reporting: bool = False


@dataclass
class TaskSpec:
    name: str
    enabled: bool = True
    timeout_seconds: int = 600
    done_images: List[str] = field(default_factory=list)
    recovery_levels: List[str] = field(default_factory=list)
    adapter_name: Optional[str] = None
    prepare: Optional[TaskCallable] = None
    run: Optional[TaskCallable] = None
    check_done: Optional[TaskCallable] = None
    recover: Optional[RecoveryCallable] = None


@dataclass
class SchedulerConfig:
    windows: List[int]
    mission_order: List[str]
    stop_condition: StopCondition = field(default_factory=StopCondition)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    recovery: RecoveryConfig = field(default_factory=RecoveryConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    missions: Dict[str, TaskSpec] = field(default_factory=dict)


@dataclass
class TaskResult:
    status: str
    done: bool = False
    message: Optional[str] = None
    state_name: Optional[str] = None
    should_retry: bool = False
    should_skip: bool = False
    should_pause_window: bool = False
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WindowSession:
    window_index: int
    mission_order: List[str]
    current_task: Optional[str] = None
    current_task_index: int = 0
    rounds_completed: int = 0
    failures_in_row: int = 0
    task_failures: Dict[str, int] = field(default_factory=dict)
    paused: bool = False
    completed: bool = False
    last_success_at: Optional[datetime] = None
    last_error: Optional[str] = None
    last_state: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

    def current_mission_name(self) -> Optional[str]:
        if not self.mission_order:
            return None
        return self.mission_order[self.current_task_index]

    def advance_task(self) -> None:
        if not self.mission_order:
            self.completed = True
            return
        self.current_task_index += 1
        if self.current_task_index >= len(self.mission_order):
            self.current_task_index = 0
            self.rounds_completed += 1
