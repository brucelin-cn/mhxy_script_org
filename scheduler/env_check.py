from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Iterable
from typing import List
from typing import Optional


@dataclass
class DependencyStatus:
    package: str
    module: str
    ok: bool
    required: bool = True
    version: Optional[str] = None
    error: Optional[str] = None


CORE_DEPENDENCIES = [
    ("pyautogui", "pyautogui", True),
    ("pydirectinput", "pydirectinput", True),
    ("pygetwindow", "pygetwindow", True),
    ("pyperclip", "pyperclip", True),
    ("playsound", "playsound", False),
    ("Pillow", "PIL", True),
    ("psutil", "psutil", True),
]


def check_dependencies(
    dependencies: Iterable[tuple[str, str, bool]] = CORE_DEPENDENCIES,
) -> List[DependencyStatus]:
    results: List[DependencyStatus] = []
    for package_name, module_name, required in dependencies:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, "__version__", None)
            results.append(
                DependencyStatus(
                    package=package_name,
                    module=module_name,
                    ok=True,
                    required=required,
                    version=str(version) if version is not None else None,
                )
            )
        except Exception as error:
            results.append(
                DependencyStatus(
                    package=package_name,
                    module=module_name,
                    ok=False,
                    required=required,
                    error=f"{type(error).__name__}: {error}",
                )
            )
    return results


def format_dependency_report(results: Iterable[DependencyStatus]) -> str:
    lines = []
    missing = []
    for item in results:
        if item.ok:
            suffix = f" version={item.version}" if item.version else ""
            lines.append(f"[ok] {item.package} ({item.module}){suffix}")
            continue
        label = "missing" if item.required else "optional"
        lines.append(f"[{label}] {item.package} ({item.module}) -> {item.error}")
        if item.required:
            missing.append(item.package)
    if missing:
        lines.append("")
        lines.append("Install command:")
        lines.append(f"python -m pip install {' '.join(missing)}")
    return "\n".join(lines)


def missing_packages(results: Iterable[DependencyStatus]) -> List[str]:
    return [item.package for item in results if not item.ok and item.required]
