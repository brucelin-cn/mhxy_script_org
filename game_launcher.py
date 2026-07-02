import argparse
import json
import time

from game_exehelp import GameExeHelp
from game_exehelp import GameLaunchError


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch or manage MHXY game process")
    parser.add_argument(
        "action",
        nargs="?",
        choices=["start", "stop", "restart", "status"],
        default="start",
        help="Action to execute",
    )
    parser.add_argument(
        "--wait-seconds",
        default=5,
        type=float,
        help="Wait time after start/restart before optional follow-up actions",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print status as JSON",
    )
    parser.add_argument(
        "--skip-if-running",
        action="store_true",
        help="Do not relaunch if game exe is already running",
    )
    parser.add_argument(
        "--elevated",
        action="store_true",
        help="Request administrator elevation when starting the launcher",
    )
    parser.add_argument(
        "--target",
        choices=["launcher", "game"],
        default="launcher",
        help="Choose whether to start the launcher or the game executable directly",
    )
    args = parser.parse_args()

    helper = GameExeHelp()

    if args.action == "status":
        _print_status(helper, as_json=args.json)
        return

    path_errors = helper.validate_paths()
    if path_errors:
        _fail(path_errors, as_json=args.json)

    if args.action == "stop":
        stopped = helper.stopExe()
        _print_result(
            {
                "action": "stop",
                "stopped": stopped,
                "status": helper.status(),
            },
            as_json=args.json,
        )
        return

    if args.action == "restart":
        helper.stopExe()
        time.sleep(1)

    if args.skip_if_running and helper.hasExe():
        _print_result(
            {
                "action": args.action,
                "started": False,
                "reason": "already running",
                "status": helper.status(),
            },
            as_json=args.json,
        )
        return

    try:
        if args.elevated:
            if args.target == "game":
                helper.runGameExeElevated()
            else:
                helper.runExeElevated()
        else:
            if args.target == "game":
                helper.runGameExe()
            else:
                helper.runExe()
    except GameLaunchError as error:
        _fail([str(error)], as_json=args.json)
    if args.wait_seconds > 0:
        time.sleep(args.wait_seconds)

    _print_result(
        {
            "action": args.action,
            "target": args.target,
            "started": True,
            "status": helper.status(),
        },
        as_json=args.json,
    )


def _print_status(helper: GameExeHelp, as_json: bool) -> None:
    _print_result(helper.status(), as_json=as_json)


def _print_result(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    for key, value in payload.items():
        print(f"{key}: {value}")


def _fail(errors: list[str], as_json: bool) -> None:
    payload = {"ok": False, "errors": errors}
    _print_result(payload, as_json=as_json)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
