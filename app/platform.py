from __future__ import annotations

import os
import sys


_ANDROID_ENV_MARKERS = (
    "ANDROID_ARGUMENT",
    "ANDROID_PRIVATE",
    "ANDROID_APP_PATH",
)


def is_android() -> bool:
    """
    Detect Android across CPython versions used by Qt/p4a.

    Important:
    CPython <= 3.12 may report sys.platform == "linux" on Android.
    sys.getandroidapilevel() is Android-only and is available in the
    Python 3.11 runtime used by StockEventRadar Android builds.

    Environment markers are retained as a p4a/Buildozer fallback.
    """
    if sys.platform == "android":
        return True

    if callable(
        getattr(
            sys,
            "getandroidapilevel",
            None,
        )
    ):
        return True

    return any(
        bool(os.environ.get(name))
        for name in _ANDROID_ENV_MARKERS
    )


def is_windows() -> bool:
    return sys.platform.startswith(
        "win"
    )


def is_macos() -> bool:
    return sys.platform == "darwin"


def is_mobile() -> bool:
    return is_android()


def runtime_platform_info() -> dict[str, object]:
    """
    Small diagnostic helper for Android beta troubleshooting.
    Does not expose secrets.
    """
    api_level = None

    getter = getattr(
        sys,
        "getandroidapilevel",
        None,
    )

    if callable(getter):
        try:
            api_level = int(
                getter()
            )
        except Exception:
            api_level = None

    return {
        "sys_platform": sys.platform,
        "android": is_android(),
        "android_api_level": api_level,
        "android_env_markers": [
            name
            for name in _ANDROID_ENV_MARKERS
            if os.environ.get(name)
        ],
    }
