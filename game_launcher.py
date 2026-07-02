import argparse
import json
import time

from game_exehelp import GameExeHelp


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

    helper.runExe()
    if args.wait_seconds > 0:
        time.sleep(args.wait_seconds)

    _print_result(
        {
            "action": args.action,
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
