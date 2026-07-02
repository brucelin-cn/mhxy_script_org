from __future__ import annotations

from datetime import datetime
from typing import Callable

from .models import SchedulerConfig
from .models import TaskResult
from .models import TaskSpec
from .models import WindowSession
from .recovery import recover_window


def register_task_adapters(config: SchedulerConfig) -> None:
    registry: dict[str, Callable[[WindowSession], TaskResult]] = {
        "baotu": _run_baotu,
        "mijing": _run_mijing,
        "dati": _run_dati,
        "yabiao": _run_yabiao,
        "shimeng": _run_shimeng,
    }

    for task_name, spec in config.missions.items():
        if task_name not in registry:
            continue
        spec.run = registry[task_name]
        spec.prepare = _prepare_session
        spec.check_done = _check_done_image_factory(spec)
        spec.recover = lambda session, level, _task_name=task_name: recover_window(
            session, level
        )


def _prepare_session(session: WindowSession) -> TaskResult:
    from mhxy import init

    if session.config is None:
        session.config = init(idx=session.window_index)
    else:
        init(idx=session.window_index, config=session.config, changWinPos=False)
    return TaskResult(status="success", done=False, state_name="prepared")


def _run_baotu(session: WindowSession) -> TaskResult:
    from mhxy import gotoActivity
    from mhxy_baotu import Baotu

    started = datetime.now()
    task = Baotu(config=session.config)
    if gotoActivity(r"resources/richang/baotu.png"):
        task.mission()
    task.do()
    return TaskResult(
        status="success",
        done=True,
        state_name="baotu_done",
        payload={"duration_seconds": (datetime.now() - started).total_seconds()},
    )


def _run_mijing(session: WindowSession) -> TaskResult:
    from mhxy import gotoActivity
    from mhxy_mijing import MiJing

    started = datetime.now()
    if not gotoActivity(r"resources/richang/mijing.png"):
        return TaskResult(
            status="soft_fail",
            should_skip=True,
            message="mijing activity not available",
            state_name="activity_missing",
        )
    MiJing(config=session.config).do()
    return TaskResult(
        status="success",
        done=True,
        state_name="mijing_done",
        payload={"duration_seconds": (datetime.now() - started).total_seconds()},
    )


def _run_dati(session: WindowSession) -> TaskResult:
    from mhxy_dati import DaTi

    started = datetime.now()
    task = DaTi(config=session.config)
    if not task.findThenExec():
        return TaskResult(
            status="soft_fail",
            should_skip=True,
            message="no dati activity available",
            state_name="activity_missing",
        )
    return TaskResult(
        status="success",
        done=True,
        state_name="dati_done",
        payload={"duration_seconds": (datetime.now() - started).total_seconds()},
    )


def _run_yabiao(session: WindowSession) -> TaskResult:
    from mhxy import gotoActivity
    from mhxy_yabiao import YaBiao

    started = datetime.now()
    if not gotoActivity(r"resources/richang/yabiao.png"):
        return TaskResult(
            status="soft_fail",
            should_skip=True,
            message="yabiao activity not available",
            state_name="activity_missing",
        )
    YaBiao(config=session.config).do()
    return TaskResult(
        status="success",
        done=True,
        state_name="yabiao_done",
        payload={"duration_seconds": (datetime.now() - started).total_seconds()},
    )


def _run_shimeng(session: WindowSession) -> TaskResult:
    from mhxy import gotoActivity
    from mhxy_shimeng import Shimeng

    started = datetime.now()
    if not gotoActivity(r"resources/richang/shimeng2.png"):
        return TaskResult(
            status="soft_fail",
            should_skip=True,
            message="shimeng activity not available",
            state_name="activity_missing",
        )
    task = Shimeng(config=session.config)
    task.autoClosEnable(True)
    task.mission()
    return TaskResult(
        status="success",
        done=True,
        state_name="shimeng_done",
        payload={"duration_seconds": (datetime.now() - started).total_seconds()},
    )


def _check_done_image_factory(spec: TaskSpec) -> Callable[[WindowSession], TaskResult]:
    def _check_done(session: WindowSession) -> TaskResult:
        from mhxy import Util
        from mhxy import cooldown

        for pic in spec.done_images:
            if Util.locateCenterOnScreen(pic) is not None:
                return TaskResult(
                    status="success",
                    done=True,
                    state_name="done_image_matched",
                    message=pic,
                )
        cooldown(0.2)
        return TaskResult(status="success", done=False, state_name="done_image_missing")

    return _check_done
