from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab


LOGIN_DROPDOWN_TEMPLATES = [
    "resources/common/xiala_wanjia.png",
    "resources/common/fallback/xiala_wanjia_20260712.png",
]
ACCOUNT_DROPDOWN_TEMPLATES = [
    "resources/common/fallback/account_dropdown_live_20260712.png",
]
ACCOUNT_ENTER_TEMPLATES = [
    "resources/common/fallback/account_enter_live_20260712.png",
]
ENTER_GAME_TEMPLATES = [
    "resources/common/jinru_youxi.png",
    "resources/common/fallback/jinru_youxi_20260712.png",
    "resources/common/denglu_youxi.png",
    "resources/common/denglu_youxi2.png",
]
MODAL_ENTER_GAME_TEMPLATES = [
    "resources/common/fallback/modal_enter_game_20260712.png",
]
ACCOUNT_MODAL_TEMPLATES = [
    "resources/common/fallback/account_modal_live_20260712.png",
]
SERVER_SELECTED_TEMPLATES = [
    "resources/common/fallback/server_selected_20260712.png",
]
SERVER_BAR_UNSELECTED_TEMPLATES = [
    "resources/common/fallback/server_bar_unselected_20260712.png",
]
SERVER_OPTION_TEMPLATES = [
    "resources/common/fallback/server_option_canruofanxing_20260712.png",
]
LOGIN_DROPDOWN_MATCH_THRESHOLD = 0.5
ENTER_GAME_MATCH_THRESHOLD = 0.7
SERVER_SELECTED_MATCH_THRESHOLD = 0.65
SERVER_BAR_MATCH_THRESHOLD = 0.55
SERVER_OPTION_MATCH_THRESHOLD = 0.65
ACCOUNT_MODAL_MATCH_THRESHOLD = 0.95
ACCOUNT_DROPDOWN_MATCH_THRESHOLD = 0.95
ACCOUNT_ENTER_MATCH_THRESHOLD = 0.95


GAME_WINDOW_TITLES = ["梦幻西游：时空", "梦幻西游:时空", "登录", "되쩌"]


@dataclass
class LauncherWindow:
    hwnd: int
    left: int
    top: int
    width: int
    height: int
    title: str


@dataclass
class SimpleWindow:
    hwnd: int
    left: int
    top: int
    width: int
    height: int
    title: str


def _user32():
    import ctypes

    return ctypes.windll.user32


def is_user_admin() -> bool:
    import ctypes

    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def find_launcher_window() -> Optional[LauncherWindow]:
    import ctypes
    from ctypes import wintypes

    user32 = _user32()
    enum_windows_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    get_window_text_length = user32.GetWindowTextLengthW
    get_window_text = user32.GetWindowTextW
    get_class_name = user32.GetClassNameW
    is_window_visible = user32.IsWindowVisible
    get_window_rect = user32.GetWindowRect

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    matches: list[LauncherWindow] = []

    def _enum_proc(hwnd, lparam):
        if not is_window_visible(hwnd):
            return True
        title_len = get_window_text_length(hwnd)
        title_buf = ctypes.create_unicode_buffer(title_len + 1)
        get_window_text(hwnd, title_buf, title_len + 1)
        class_buf = ctypes.create_unicode_buffer(256)
        get_class_name(hwnd, class_buf, 256)
        title = title_buf.value
        cls = class_buf.value
        if title == "MyPCLauncher_x64r" or cls == "MyPCLauncher_x64r":
            rect = RECT()
            get_window_rect(hwnd, ctypes.byref(rect))
            matches.append(
                LauncherWindow(
                    hwnd=int(hwnd),
                    left=rect.left,
                    top=rect.top,
                    width=rect.right - rect.left,
                    height=rect.bottom - rect.top,
                    title=title,
                )
            )
        return True

    user32.EnumWindows(enum_windows_proc(_enum_proc), 0)
    if not matches:
        return None
    visible_matches = [item for item in matches if item.width > 300 and item.height > 200]
    if visible_matches:
        visible_matches.sort(key=lambda item: item.width * item.height, reverse=True)
        return visible_matches[0]
    matches.sort(key=lambda item: item.width * item.height, reverse=True)
    return matches[0]


def find_window_by_title(
    title_candidates: list[str],
    min_width: int = 100,
    min_height: int = 100,
) -> Optional[SimpleWindow]:
    import ctypes
    from ctypes import wintypes

    user32 = _user32()
    enum_windows_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    get_window_text_length = user32.GetWindowTextLengthW
    get_window_text = user32.GetWindowTextW
    is_window_visible = user32.IsWindowVisible
    get_window_rect = user32.GetWindowRect

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    matches: list[SimpleWindow] = []

    def _enum_proc(hwnd, lparam):
        if not is_window_visible(hwnd):
            return True
        title_len = get_window_text_length(hwnd)
        title_buf = ctypes.create_unicode_buffer(title_len + 1)
        get_window_text(hwnd, title_buf, title_len + 1)
        title = title_buf.value
        if title not in title_candidates:
            return True
        rect = RECT()
        get_window_rect(hwnd, ctypes.byref(rect))
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        if width < min_width or height < min_height:
            return True
        matches.append(
            SimpleWindow(
                hwnd=int(hwnd),
                left=rect.left,
                top=rect.top,
                width=width,
                height=height,
                title=title,
            )
        )
        return True

    user32.EnumWindows(enum_windows_proc(_enum_proc), 0)
    if not matches:
        return None
    matches.sort(key=lambda item: item.width * item.height, reverse=True)
    return matches[0]


def has_login_window() -> bool:
    if find_window_by_title(GAME_WINDOW_TITLES, min_width=250, min_height=250) is not None:
        return True
    try:
        return pyautogui.locateOnScreen("resources/common/jinru_youxi.png", confidence=0.88) is not None
    except pyautogui.ImageNotFoundException:
        return False


def focus_launcher_window(window: LauncherWindow) -> None:
    user32 = _user32()
    SW_RESTORE = 9
    HWND_TOP = 0
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_SHOWWINDOW = 0x0040
    user32.ShowWindow(window.hwnd, SW_RESTORE)
    user32.SetWindowPos(
        window.hwnd,
        HWND_TOP,
        0,
        0,
        0,
        0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW,
    )
    user32.SetForegroundWindow(window.hwnd)


def capture_launcher_window(window: LauncherWindow) -> np.ndarray:
    image = ImageGrab.grab(window=window.hwnd)
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def capture_simple_window(window: SimpleWindow) -> np.ndarray:
    # ponytail: grab the on-screen rectangle; window=hwnd can miss modal child layers in this game.
    image = ImageGrab.grab(
        bbox=(window.left, window.top, window.left + window.width, window.top + window.height)
    )
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def locate_template(
    haystack: np.ndarray,
    template_path: str | Path,
    threshold: float = 0.88,
) -> Optional[tuple[int, int, int, int, float]]:
    template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
    if template is None:
        raise FileNotFoundError(f"Template not found: {template_path}")
    result = cv2.matchTemplate(haystack, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val < threshold:
        return None
    height, width = template.shape[:2]
    return (max_loc[0], max_loc[1], width, height, float(max_val))


def click_template_in_window(
    window: SimpleWindow | LauncherWindow,
    template_path: str | Path,
    threshold: float = 0.88,
    optional: bool = False,
) -> dict:
    haystack = (
        capture_launcher_window(window)
        if isinstance(window, LauncherWindow)
        else capture_simple_window(window)
    )
    match = locate_template(haystack, template_path, threshold=threshold)
    if match is None:
        return {
            "ok": False,
            "optional": optional,
            "reason": "template not matched",
            "template": str(template_path),
        }

    x, y, width, height, score = match
    screen_x = window.left + x + width // 2
    screen_y = window.top + y + height // 2
    pyautogui.click(screen_x, screen_y)
    return {
        "ok": True,
        "template": str(template_path),
        "score": score,
        "click": {"x": screen_x, "y": screen_y},
    }


def click_template_on_screen(
    template_path: str | Path,
    threshold: float = 0.88,
    optional: bool = False,
) -> dict:
    try:
        match = pyautogui.locateCenterOnScreen(str(template_path), confidence=threshold)
    except pyautogui.ImageNotFoundException:
        match = None
    if match is None:
        return {
            "ok": False,
            "optional": optional,
            "reason": "template not matched",
            "template": str(template_path),
        }
    pyautogui.click(match.x, match.y)
    return {
        "ok": True,
        "template": str(template_path),
        "click": {"x": match.x, "y": match.y},
    }


def click_first_template_in_window(
    window: SimpleWindow | LauncherWindow,
    template_paths: list[str | Path],
    threshold: float = 0.88,
    optional: bool = False,
) -> dict:
    last_result = {
        "ok": False,
        "optional": optional,
        "reason": "template not matched",
        "template": str(template_paths[0]),
    }
    for template_path in template_paths:
        result = click_template_in_window(window, template_path, threshold=threshold, optional=optional)
        if result.get("ok"):
            return result
        last_result = result
    return last_result


def click_first_template_on_screen(
    template_paths: list[str | Path],
    threshold: float = 0.88,
    optional: bool = False,
) -> dict:
    last_result = {
        "ok": False,
        "optional": optional,
        "reason": "template not matched",
        "template": str(template_paths[0]),
    }
    for template_path in template_paths:
        result = click_template_on_screen(template_path, threshold=threshold, optional=optional)
        if result.get("ok"):
            return result
        last_result = result
    return last_result


def is_server_selected(window: SimpleWindow | LauncherWindow | None) -> bool:
    if window is None:
        return False
    haystack = (
        capture_launcher_window(window)
        if isinstance(window, LauncherWindow)
        else capture_simple_window(window)
    )
    for template_path in SERVER_SELECTED_TEMPLATES:
        if locate_template(haystack, template_path, threshold=SERVER_SELECTED_MATCH_THRESHOLD) is not None:
            return True
    return False


def is_server_login_visible(window: SimpleWindow | LauncherWindow | None) -> bool:
    if window is None:
        return False
    haystack = (
        capture_launcher_window(window)
        if isinstance(window, LauncherWindow)
        else capture_simple_window(window)
    )
    for template_path in SERVER_BAR_UNSELECTED_TEMPLATES + SERVER_SELECTED_TEMPLATES + ENTER_GAME_TEMPLATES:
        threshold = ENTER_GAME_MATCH_THRESHOLD
        if template_path in SERVER_BAR_UNSELECTED_TEMPLATES:
            threshold = SERVER_BAR_MATCH_THRESHOLD
        elif template_path in SERVER_SELECTED_TEMPLATES:
            threshold = SERVER_SELECTED_MATCH_THRESHOLD
        if locate_template(haystack, template_path, threshold=threshold) is not None:
            return True
    return False


def click_server_bar(window: SimpleWindow | LauncherWindow) -> dict:
    haystack = (
        capture_launcher_window(window)
        if isinstance(window, LauncherWindow)
        else capture_simple_window(window)
    )
    for template_path in SERVER_BAR_UNSELECTED_TEMPLATES:
        match = locate_template(haystack, template_path, threshold=SERVER_BAR_MATCH_THRESHOLD)
        if match is None:
            continue
        x, y, width, height, score = match
        screen_x = window.left + x + width - 32
        screen_y = window.top + y + height // 2
        pyautogui.click(screen_x, screen_y)
        return {
            "ok": True,
            "template": str(template_path),
            "score": score,
            "click": {"x": screen_x, "y": screen_y},
        }
    return {
        "ok": False,
        "reason": "server bar not matched",
        "template": str(SERVER_BAR_UNSELECTED_TEMPLATES[-1]),
    }


def click_server_option(window: SimpleWindow | LauncherWindow) -> dict:
    return click_first_template_in_window(
        window,
        SERVER_OPTION_TEMPLATES,
        threshold=SERVER_OPTION_MATCH_THRESHOLD,
    )


def is_account_modal_visible(window: SimpleWindow | LauncherWindow | None) -> bool:
    if window is None:
        return False
    haystack = (
        capture_launcher_window(window)
        if isinstance(window, LauncherWindow)
        else capture_simple_window(window)
    )
    for template_path in ACCOUNT_DROPDOWN_TEMPLATES:
        if locate_template(haystack, template_path, threshold=ACCOUNT_DROPDOWN_MATCH_THRESHOLD) is not None:
            return True
    return False


def click_account_enter_game(threshold: float = 0.88) -> dict:
    if not is_user_admin():
        return {"ok": False, "reason": "launcher automation requires administrator privileges"}

    enter_threshold = min(threshold, ACCOUNT_ENTER_MATCH_THRESHOLD)
    window = find_window_by_title(GAME_WINDOW_TITLES, min_width=250, min_height=250)
    if window is None:
        return {"ok": False, "reason": "account modal window not found"}
    if not is_account_modal_visible(window):
        return {"ok": False, "reason": "account modal not visible", "hwnd": window.hwnd}

    result = click_first_template_in_window(
        window,
        ACCOUNT_ENTER_TEMPLATES,
        threshold=enter_threshold,
    )
    result["hwnd"] = window.hwnd
    if not result.get("ok"):
        result["reason"] = "account enter-game button not matched"
    return result


def click_server_enter_game(threshold: float = 0.88) -> dict:
    if not is_user_admin():
        return {"ok": False, "reason": "launcher automation requires administrator privileges"}

    enter_threshold = min(threshold, ENTER_GAME_MATCH_THRESHOLD)
    window = find_window_by_title(GAME_WINDOW_TITLES, min_width=250, min_height=250)
    if window is None:
        return {"ok": False, "reason": "server login window not found"}
    if is_account_modal_visible(window):
        return {"ok": False, "reason": "account modal still visible", "hwnd": window.hwnd}

    server_selected = is_server_selected(window)
    dropdown_result = {"ok": True, "optional": True, "reason": "server already selected"}
    if not server_selected:
        dropdown_result = click_server_bar(window)
        if not dropdown_result.get("ok"):
            dropdown_result["hwnd"] = window.hwnd
            return dropdown_result
        pyautogui.sleep(0.5)
        server_option_result = click_server_option(window)
        dropdown_result["server_option"] = server_option_result
        if not server_option_result.get("ok"):
            return {
                "ok": False,
                "reason": "server option not matched",
                "template": str(SERVER_OPTION_TEMPLATES[-1]),
                "hwnd": window.hwnd,
                "dropdown": dropdown_result,
            }
        pyautogui.sleep(0.8)
        if not is_server_selected(window):
            return {
                "ok": False,
                "reason": "server still not selected after click",
                "hwnd": window.hwnd,
                "dropdown": dropdown_result,
            }
        pyautogui.sleep(0.5)

    enter_result = click_first_template_in_window(window, ENTER_GAME_TEMPLATES, threshold=enter_threshold)
    enter_result["hwnd"] = window.hwnd
    enter_result["dropdown"] = dropdown_result
    if not enter_result.get("ok"):
        enter_result["reason"] = "server enter-game button not matched"
    return enter_result


def click_start_game(
    template_path: str | Path = "resources/launcher/start_game_btn.png",
    threshold: float = 0.88,
) -> dict:
    if not is_user_admin():
        return {"ok": False, "reason": "launcher automation requires administrator privileges"}

    window = find_launcher_window()
    if window is None:
        return {"ok": False, "reason": "launcher window not found"}

    focus_launcher_window(window)
    pyautogui.sleep(0.5)
    window = find_launcher_window() or window
    result = click_template_in_window(window, template_path, threshold=threshold)
    if not result.get("ok"):
        result["hwnd"] = window.hwnd
        result["reason"] = "start button not matched"
        return result
    result["hwnd"] = window.hwnd
    return result


def click_login_enter_game(
    dropdown_template_path: str | Path = "resources/common/xiala_wanjia.png",
    template_path: str | Path = "resources/common/jinru_youxi.png",
    threshold: float = 0.88,
) -> dict:
    # ponytail: compatibility shim; main flow should call account-enter then server-enter explicitly.
    window = find_window_by_title(GAME_WINDOW_TITLES, min_width=250, min_height=250)
    if is_account_modal_visible(window):
        return click_account_enter_game(threshold=threshold)
    return click_server_enter_game(threshold=threshold)


if __name__ == "__main__":
    assert "梦幻西游：时空" in GAME_WINDOW_TITLES
    assert "登录" in GAME_WINDOW_TITLES
    assert isinstance(is_user_admin(), bool)
