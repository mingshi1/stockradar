from __future__ import annotations

from pathlib import Path
import re

import PySide6


ANDROID_PYTHON_VERSION = "3.11.15"
P4A_RELEASE = "v2026.05.09"
CERTIFI_REQUIREMENT = "certifi==2026.7.22"


def _find_buildozer_helper() -> Path:
    pyside_root = (
        Path(PySide6.__file__)
        .resolve()
        .parent
    )

    target = (
        pyside_root
        / "scripts"
        / "deploy_lib"
        / "android"
        / "buildozer.py"
    )

    if not target.exists():
        raise SystemExit(
            "Unable to locate PySide6 Android buildozer.py "
            f"under {pyside_root}"
        )

    return target


def _set_string_value(
    text: str,
    *,
    key: str,
    desired: str,
) -> tuple[str, str]:
    """
    Locate:
        self.set_value("app", "<key>", "<value>")
    without depending on quote style, whitespace, or the exact old value.
    """
    escaped_key = re.escape(key)

    pattern = re.compile(
        r'self\.set_value\(\s*'
        r'["\']app["\']\s*,\s*'
        r'["\']'
        + escaped_key
        + r'["\']\s*,\s*'
        r'(?P<quote>["\'])'
        r'(?P<value>[^"\']*)'
        r'(?P=quote)\s*\)',
        re.MULTILINE,
    )

    match = pattern.search(text)

    if match is None:
        raise SystemExit(
            f"Unable to locate PySide6 Android {key!r} "
            "assignment in buildozer.py."
        )

    current = match.group("value")

    replacement = (
        match.group(0)
        .replace(
            current,
            desired,
            1,
        )
    )

    patched = (
        text[: match.start()]
        + replacement
        + text[match.end() :]
    )

    return patched, current


def _patch_requirements(
    text: str,
) -> str:
    desired = (
        f"python3=={ANDROID_PYTHON_VERSION},"
        f"hostpython3=={ANDROID_PYTHON_VERSION},"
        "shiboken6,PySide6,"
        f"{CERTIFI_REQUIREMENT}"
    )

    patched, current = _set_string_value(
        text,
        key="requirements",
        desired=desired,
    )

    current_tokens = {
        part.split(
            "==",
            1,
        )[0].strip()
        for part in current.split(",")
        if part.strip()
    }

    required_tokens = {
        "python3",
        "shiboken6",
        "PySide6",
    }

    if not required_tokens.issubset(
        current_tokens
    ):
        raise SystemExit(
            "Found Android requirements assignment, "
            "but it does not look like the expected "
            f"PySide6 helper: {current!r}"
        )

    return patched


def _patch_p4a_branch(
    text: str,
) -> str:
    patched, _ = _set_string_value(
        text,
        key="p4a.branch",
        desired=P4A_RELEASE,
    )

    return patched


def _verify(
    text: str,
):
    required_fragments = [
        f"python3=={ANDROID_PYTHON_VERSION}",
        f"hostpython3=={ANDROID_PYTHON_VERSION}",
        "shiboken6",
        "PySide6",
        CERTIFI_REQUIREMENT,
        P4A_RELEASE,
    ]

    missing = [
        fragment
        for fragment in required_fragments
        if fragment not in text
    ]

    if missing:
        raise SystemExit(
            "Patch verification failed; missing: "
            + ", ".join(missing)
        )


def main():
    target = _find_buildozer_helper()

    text = target.read_text(
        encoding="utf-8"
    )

    text = _patch_requirements(
        text
    )
    text = _patch_p4a_branch(
        text
    )

    _verify(
        text
    )

    target.write_text(
        text,
        encoding="utf-8",
    )

    print(
        "Patched PySide6 Android deploy helper:"
    )
    print(
        f"  {target}"
    )
    print(
        "  requirements = "
        f"python3=={ANDROID_PYTHON_VERSION},"
        f"hostpython3=={ANDROID_PYTHON_VERSION},"
        "shiboken6,PySide6,"
        f"{CERTIFI_REQUIREMENT}"
    )
    print(
        f"  p4a.branch = {P4A_RELEASE}"
    )


if __name__ == "__main__":
    main()
