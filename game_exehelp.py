import os
import signal
import subprocess
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import psutil


@dataclass
class GameExeConfig:
    game_path: Path
    launcher_path: Path


def load_game_exe_config(config_path: str = "resources/common.ini") -> GameExeConfig:
    parser = ConfigParser()
    ini_path = Path(config_path)
    if not ini_path.exists():
        raise FileNotFoundError(f"Config file not found: {ini_path}")
    parser.read(ini_path, encoding="utf-8")
    return GameExeConfig(
        game_path=Path(parser.get("main", "path")),
        launcher_path=Path(parser.get("main", "launcher")),
    )


def _normalize_path(path: str | Path) -> str:
    return os.path.normcase(os.path.normpath(str(path)))


def run_exe(exe_path: str | Path) -> subprocess.Popen:
    return subprocess.Popen(
        [str(exe_path)],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def find_process_by_exe(exe_path: str | Path) -> Optional[psutil.Process]:
    expected = _normalize_path(exe_path)
    for proc in psutil.process_iter(["pid", "exe", "name"]):
        try:
            proc_exe = proc.info.get("exe")
            if proc_exe and _normalize_path(proc_exe) == expected:
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None


def has_exe(exe_path: str | Path) -> bool:
    return find_process_by_exe(exe_path) is not None


def stop_exe(exe_path: str | Path) -> bool:
    stopped = False
    expected = _normalize_path(exe_path)
    for proc in psutil.process_iter(["pid", "exe", "name"]):
        try:
            proc_exe = proc.info.get("exe")
            if proc_exe and _normalize_path(proc_exe) == expected:
                os.kill(proc.pid, signal.SIGTERM)
                stopped = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return stopped


class GameExeHelp:
    def __init__(self, config_path: str = "resources/common.ini") -> None:
        self.config_path = config_path
        self.config = load_game_exe_config(config_path)
        self.exepath = str(self.config.game_path)
        self.launcher = str(self.config.launcher_path)

    def validate_paths(self) -> list[str]:
        errors = []
        if not self.config.game_path.exists():
            errors.append(f"game exe not found: {self.config.game_path}")
        if not self.config.launcher_path.exists():
            errors.append(f"launcher exe not found: {self.config.launcher_path}")
        return errors

    def runExe(self) -> subprocess.Popen:
        return run_exe(self.launcher)

    def stopExe(self) -> bool:
        return stop_exe(self.exepath)

    def hasExe(self) -> bool:
        return has_exe(self.exepath)

    def status(self) -> dict:
        process = find_process_by_exe(self.exepath)
        return {
            "running": process is not None,
            "pid": None if process is None else process.pid,
            "game_path": self.exepath,
            "launcher_path": self.launcher,
            "path_errors": self.validate_paths(),
        }
