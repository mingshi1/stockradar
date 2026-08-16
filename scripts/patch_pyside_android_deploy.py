from __future__ import annotations

import ast
from pathlib import Path
import PySide6

ANDROID_PYTHON_VERSION = "3.11.15"
P4A_RELEASE = "v2026.05.09"
ANDROID_REQUIREMENTS = (
    f"python3=={ANDROID_PYTHON_VERSION},"
    f"hostpython3=={ANDROID_PYTHON_VERSION},"
    "certifi==2026.5.20,"
    "shiboken6,PySide6"
)


def _target_file() -> Path:
    target = (
        Path(PySide6.__file__).resolve().parent
        / "scripts"
        / "deploy_lib"
        / "android"
        / "buildozer.py"
    )
    if not target.exists():
        raise SystemExit(
            f"Unable to locate PySide6 Android buildozer.py: {target}"
        )
    return target


def _line_offsets(text: str) -> list[int]:
    offsets = [0]
    pos = 0
    for line in text.splitlines(keepends=True):
        pos += len(line)
        offsets.append(pos)
    return offsets


def _span(node: ast.AST, offsets: list[int]) -> tuple[int, int]:
    return (
        offsets[node.lineno - 1] + node.col_offset,
        offsets[node.end_lineno - 1] + node.end_col_offset,
    )


def _is_set_value_call(node: ast.AST, option: str) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if not (
        isinstance(func, ast.Attribute)
        and func.attr == "set_value"
        and len(node.args) >= 3
    ):
        return False

    section, key = node.args[0], node.args[1]
    return (
        isinstance(section, ast.Constant)
        and section.value == "app"
        and isinstance(key, ast.Constant)
        and key.value == option
    )


def _replace_calls(text: str) -> tuple[str, set[str]]:
    tree = ast.parse(text)
    offsets = _line_offsets(text)
    replacements = []

    for node in ast.walk(tree):
        if _is_set_value_call(node, "requirements"):
            start, end = _span(node, offsets)
            replacements.append((
                start,
                end,
                'self.set_value("app", "requirements", '
                f'"{ANDROID_REQUIREMENTS}")',
                "requirements",
            ))
        elif _is_set_value_call(node, "p4a.branch"):
            start, end = _span(node, offsets)
            replacements.append((
                start,
                end,
                'self.set_value("app", "p4a.branch", '
                f'"{P4A_RELEASE}")',
                "p4a.branch",
            ))

    patched = set()
    for start, end, replacement, name in sorted(
        replacements, key=lambda item: item[0], reverse=True
    ):
        text = text[:start] + replacement + text[end:]
        patched.add(name)

    return text, patched


def _show_relevant(text: str):
    for number, line in enumerate(text.splitlines(), 1):
        lower = line.lower()
        if "requirements" in lower or "p4a.branch" in lower:
            print(f"{number:4}: {line}")


def main():
    target = _target_file()
    original = target.read_text(encoding="utf-8")

    print("Qt helper:", target)
    print("Before:")
    _show_relevant(original)

    try:
        patched_text, patched = _replace_calls(original)
    except SyntaxError as exc:
        print("WARNING: Qt helper AST parse failed:", exc)
        print("Continuing with Buildozer APP_* environment overrides.")
        return

    missing = {"requirements", "p4a.branch"} - patched
    if missing:
        print(
            "WARNING: Qt helper structure changed; not patched:",
            ", ".join(sorted(missing)),
        )
        print("Continuing with Buildozer APP_* environment overrides.")

    if patched:
        target.write_text(patched_text, encoding="utf-8")

    verify = target.read_text(encoding="utf-8")
    print("After:")
    _show_relevant(verify)

    if "requirements" in patched:
        for fragment in (
            "python3==3.11.15",
            "hostpython3==3.11.15",
            "certifi==2026.5.20",
        ):
            if fragment not in verify:
                raise SystemExit(f"Patch verification failed: {fragment}")

    if "p4a.branch" in patched and P4A_RELEASE not in verify:
        raise SystemExit("Patch verification failed: p4a.branch")

    print("Qt Android helper configuration completed.")


if __name__ == "__main__":
    main()
