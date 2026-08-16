from __future__ import annotations

from pathlib import Path
import PySide6


ANDROID_PYTHON_VERSION = "3.11.15"
P4A_RELEASE = "v2026.05.09"


def main():
    pyside_root = Path(PySide6.__file__).resolve().parent

    candidates = [
        pyside_root
        / "scripts"
        / "deploy_lib"
        / "android"
        / "buildozer.py",
        pyside_root
        / "scripts"
        / "deploy_lib"
        / "android"
        / "buildozer.py",
    ]

    target = next(
        (path for path in candidates if path.exists()),
        None,
    )

    if target is None:
        raise SystemExit(
            "Unable to locate PySide6 Android buildozer.py "
            f"under {pyside_root}"
        )

    text = target.read_text(encoding="utf-8")

    old_requirements = (
        'self.set_value("app", "requirements", '
        '"python3,shiboken6,PySide6")'
    )
    new_requirements = (
        'self.set_value("app", "requirements", '
        f'"python3=={ANDROID_PYTHON_VERSION},'
        f'hostpython3=={ANDROID_PYTHON_VERSION},'
        'shiboken6,PySide6")'
    )

    if old_requirements in text:
        text = text.replace(
            old_requirements,
            new_requirements,
            1,
        )
    elif new_requirements not in text:
        raise SystemExit(
            "PySide6 buildozer.py requirements line did not match "
            "the expected Qt 6.11.1 implementation."
        )

    old_branch = (
        'self.set_value("app", "p4a.branch", "develop")'
    )
    new_branch = (
        f'self.set_value("app", "p4a.branch", "{P4A_RELEASE}")'
    )

    if old_branch in text:
        text = text.replace(
            old_branch,
            new_branch,
            1,
        )
    elif new_branch not in text:
        raise SystemExit(
            "PySide6 buildozer.py p4a.branch line did not match "
            "the expected Qt 6.11.1 implementation."
        )

    target.write_text(
        text,
        encoding="utf-8",
    )

    verify = target.read_text(encoding="utf-8")

    required_fragments = [
        f"python3=={ANDROID_PYTHON_VERSION}",
        f"hostpython3=={ANDROID_PYTHON_VERSION}",
        P4A_RELEASE,
    ]

    for fragment in required_fragments:
        if fragment not in verify:
            raise SystemExit(
                f"Patch verification failed: {fragment}"
            )

    print("Patched PySide6 Android deploy helper:")
    print(f"  {target}")
    print(
        "  requirements = "
        f"python3=={ANDROID_PYTHON_VERSION},"
        f"hostpython3=={ANDROID_PYTHON_VERSION},"
        "shiboken6,PySide6"
    )
    print(f"  p4a.branch = {P4A_RELEASE}")


if __name__ == "__main__":
    main()
