from __future__ import annotations

from .models import WindowSession


def recover_window(session: WindowSession, level: str) -> None:
    from mhxy import allEscapeTeam
    from mhxy import cooldown
    from mhxy import init
    from mhxy import log

    if session.config is None:
        session.config = init(idx=session.window_index)

    if level == "level_1":
        _recover_level_1()
        return
    if level == "level_2":
        init(idx=session.window_index, config=session.config, changWinPos=False)
        return
    if level == "level_3":
        allEscapeTeam(bugFix=True)
        cooldown(2)
        init(idx=session.window_index, config=session.config, changWinPos=False)
        return
    log(f"[scheduler] unknown recovery level: {level}")


def _recover_level_1() -> None:
    from mhxy import Util
    from mhxy import cooldown

    # Close common dialogs and pull the task bar back into a stable state.
    for _ in range(3):
        Util.leftClick(-1.5, 3.5)
        cooldown(0.5)
