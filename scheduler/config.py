from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .models import RecoveryConfig
from .models import ReportingConfig
from .models import RuntimeConfig
from .models import SchedulerConfig
from .models import StopCondition
from .models import TaskSpec


DEFAULT_CONFIG_PATH = Path("resources/scheduler/scheduler.json")


def load_scheduler_config(path: str | Path = DEFAULT_CONFIG_PATH) -> SchedulerConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    missions = {
        name: _build_task_spec(name, mission_raw)
        for name, mission_raw in raw.get("missions", {}).items()
    }

    return SchedulerConfig(
        windows=list(raw.get("windows", [])),
        mission_order=list(raw.get("mission_order", [])),
        stop_condition=StopCondition(**raw.get("stop_condition", {})),
        runtime=RuntimeConfig(**raw.get("runtime", {})),
        recovery=RecoveryConfig(**raw.get("recovery", {})),
        reporting=ReportingConfig(**raw.get("reporting", {})),
        missions=missions,
    )


def dump_scheduler_config(config: SchedulerConfig) -> Dict[str, Any]:
    return {
        "windows": config.windows,
        "mission_order": config.mission_order,
        "stop_condition": config.stop_condition.__dict__,
        "runtime": config.runtime.__dict__,
        "recovery": config.recovery.__dict__,
        "reporting": config.reporting.__dict__,
        "missions": {
            name: {
                "enabled": spec.enabled,
                "timeout_seconds": spec.timeout_seconds,
                "done_images": spec.done_images,
                "recovery_levels": spec.recovery_levels,
            }
            for name, spec in config.missions.items()
        },
    }


def _build_task_spec(name: str, raw: Dict[str, Any]) -> TaskSpec:
    return TaskSpec(
        name=name,
        enabled=raw.get("enabled", True),
        timeout_seconds=int(raw.get("timeout_seconds", 600)),
        done_images=list(raw.get("done_images", [])),
        recovery_levels=list(raw.get("recovery_levels", [])),
        adapter_name=raw.get("adapter_name"),
    )
