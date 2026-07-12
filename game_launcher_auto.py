import argparse
import json

from game_exehelp import GameExeHelp
from game_launcher_flow import is_account_modal_visible
from game_launcher_flow import is_server_login_visible
from game_launcher_flow import click_start_game
from game_launcher_flow import click_account_enter_game
from game_launcher_flow import click_server_enter_game


def main() -> None:
    parser = argparse.ArgumentParser(description="Automate official MHXY launcher")
    parser.add_argument(
        "action",
        nargs="?",
        choices=["start-game", "account-enter", "server-enter", "enter-game", "full-start"],
        default="full-start",
        help="Launcher automation action",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.88,
        help="Template match threshold",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print result as JSON",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Retry count for enter-game clicks",
    )
    args = parser.parse_args()

    helper = GameExeHelp()

    if args.action == "start-game":
        result = click_start_game(threshold=args.threshold)
    elif args.action == "account-enter":
        result = _retry_account_enter(args.threshold, args.retries)
    elif args.action == "server-enter":
        result = _retry_server_enter(args.threshold, args.retries)
    elif args.action == "enter-game":
        result = _retry_enter_game(args.threshold, args.retries)
    else:
        if helper.hasExe():
            account_result = _retry_account_enter(args.threshold, args.retries)
            server_result = _retry_server_enter(args.threshold, args.retries)
            result = {
                "ok": server_result.get("ok", False),
                "step": "server-enter",
                "start_result": {"ok": True, "reason": "game already running"},
                "account_result": account_result,
                "server_result": server_result,
            }
        else:
            start_result = click_start_game(threshold=args.threshold)
            if not start_result.get("ok"):
                result = {"ok": False, "step": "start-game", "detail": start_result}
            else:
                import time

                time.sleep(5)
                account_result = _retry_account_enter(args.threshold, args.retries)
                time.sleep(2)
                server_result = _retry_server_enter(args.threshold, args.retries)
                result = {
                    "ok": server_result.get("ok", False),
                    "step": "server-enter",
                    "start_result": start_result,
                    "account_result": account_result,
                    "server_result": server_result,
                }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(0 if result.get("ok") else 1)

    print(result)
    raise SystemExit(0 if result.get("ok") else 1)


def _retry_enter_game(threshold: float, retries: int) -> dict:
    account_result = _retry_account_enter(threshold, retries)
    if not account_result.get("ok"):
        return {"ok": False, "reason": "account enter failed", "account_result": account_result}
    return _retry_server_enter(threshold, retries)


def _retry_account_enter(threshold: float, retries: int) -> dict:
    import time

    last_result = {"ok": False, "reason": "account modal window not found"}
    for attempt in range(1, max(1, retries) + 1):
        last_result = click_account_enter_game(threshold=threshold)
        if not last_result.get("ok"):
            time.sleep(1)
            continue
        time.sleep(2)
        if not is_account_modal_visible(_current_window()):
            last_result["login_closed"] = True
            last_result["attempt"] = attempt
            return last_result
        last_result["login_closed"] = False
        last_result["attempt"] = attempt
    return last_result


def _retry_server_enter(threshold: float, retries: int) -> dict:
    import time

    last_result = {"ok": False, "reason": "server login window not found"}
    for attempt in range(1, max(1, retries) + 1):
        current_window = _current_window()
        if current_window is None:
            return {
                "ok": True,
                "reason": "server step already completed",
                "login_closed": True,
                "attempt": attempt,
            }
        if is_account_modal_visible(current_window):
            last_result = {
                "ok": False,
                "reason": "account modal still visible",
                "attempt": attempt,
            }
            time.sleep(1)
            continue
        last_result = click_server_enter_game(threshold=threshold)
        if not last_result.get("ok"):
            time.sleep(1)
            continue
        time.sleep(3)
        if not is_server_login_visible(_current_window()):
            last_result["login_closed"] = True
            last_result["attempt"] = attempt
            return last_result
        last_result["login_closed"] = False
        last_result["attempt"] = attempt
    return last_result


def _current_window():
    from game_launcher_flow import find_window_by_title, GAME_WINDOW_TITLES

    return find_window_by_title(GAME_WINDOW_TITLES, min_width=250, min_height=250)


if __name__ == "__main__":
    main()
