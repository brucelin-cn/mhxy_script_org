from __future__ import annotations

from .adapters import register_task_adapters
from .models import SchedulerConfig


def attach_task_specs(config: SchedulerConfig) -> SchedulerConfig:
    register_task_adapters(config)
    return config
