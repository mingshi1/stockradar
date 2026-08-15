import sys


def is_android() -> bool:
    return sys.platform == "android"


def is_windows() -> bool:
    return sys.platform.startswith("win")


def is_macos() -> bool:
    return sys.platform == "darwin"


def is_mobile() -> bool:
    return is_android()
