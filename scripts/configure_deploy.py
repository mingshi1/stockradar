from configparser import ConfigParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "pysidedeploy.spec"
DIST_DIR = ROOT / "dist"
DEPLOYMENT_DIR = ROOT / "deployment"
NUITKA_REPORT = DEPLOYMENT_DIR / "nuitka-report.xml"


def main():
    if not SPEC.exists():
        raise SystemExit(
            "pysidedeploy.spec 不存在。请先运行："
            "pyside6-deploy main.py --init --name StockEventRadar -f"
        )

    DIST_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )
    DEPLOYMENT_DIR.mkdir(
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
        fallback="--noinclude-qt-translations=True",
    )

    # RC4: GitHub Actions needs the real Nuitka error, so do not suppress
    # compiler output with --quiet.
    tokens = [
        token
        for token in existing.split()
        if token != "--quiet"
    ]

    additions = [
        "--windows-console-mode=disable",
        "--include-data-dir=resources=resources",
        "--include-data-files=VERSION=VERSION",
        "--assume-yes-for-downloads",
        f"--report={NUITKA_REPORT}",
    ]

    for item in additions:
        if item not in tokens:
            tokens.append(item)

    config.set(
        "nuitka",
        "extra_args",
        " ".join(tokens).strip(),
    )

    with SPEC.open(
        "w",
        encoding="utf-8",
    ) as handle:
        config.write(handle)

    print("Configured:", SPEC)
    print("Executable output directory:", DIST_DIR)
    print("Nuitka diagnostic report:", NUITKA_REPORT)


if __name__ == "__main__":
    main()
