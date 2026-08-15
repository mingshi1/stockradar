from configparser import ConfigParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "pysidedeploy.spec"
DIST_DIR = ROOT / "dist"


def main():
    if not SPEC.exists():
        raise SystemExit(
            "pysidedeploy.spec 不存在。请先运行："
            "pyside6-deploy main.py --init --name StockEventRadar -f"
        )

    # pyside6-deploy finalize() copies the built executable to exec_directory.
    # Ensure that destination exists before deployment starts.
    DIST_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    config = ConfigParser(
        interpolation=None
    )
    config.read(
        SPEC,
        encoding="utf-8",
    )

    if not config.has_section("app"):
        config.add_section("app")

    if not config.has_section("nuitka"):
        config.add_section("nuitka")

    config.set(
        "app",
        "title",
        "StockEventRadar",
    )
    config.set(
        "app",
        "exec_directory",
        str(DIST_DIR),
    )
    config.set(
        "app",
        "icon",
        str(
            ROOT
            / "resources"
            / "app_icon.ico"
        ),
    )

    config.set(
        "nuitka",
        "mode",
        "onefile",
    )

    existing = config.get(
        "nuitka",
        "extra_args",
        fallback="--quiet --noinclude-qt-translations=True",
    )

    additions = [
        "--windows-console-mode=disable",
        "--include-data-dir=resources=resources",
        "--include-data-files=VERSION=VERSION",
    ]

    for item in additions:
        if item not in existing:
            existing += " " + item

    config.set(
        "nuitka",
        "extra_args",
        existing.strip(),
    )

    with SPEC.open(
        "w",
        encoding="utf-8",
    ) as handle:
        config.write(handle)

    print(
        "Configured:",
        SPEC,
    )
    print(
        "Executable output directory:",
        DIST_DIR,
    )


if __name__ == "__main__":
    main()
