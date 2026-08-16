from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

from PySide6.QtCore import QStandardPaths, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
)


APP_VERSION = "1.0.0-rc4.17"


def _stage(
    message: str,
):
    line = (
        f"[StockEventRadar] {message}"
    )

    print(
        line,
        flush=True,
    )

    try:
        location = (
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppDataLocation
            )
        )

        if location:
            root = Path(
                location
            )
            root.mkdir(
                parents=True,
                exist_ok=True,
            )

            with (
                root
                / "startup_stage.log"
            ).open(
                "a",
                encoding="utf-8",
            ) as fp:
                fp.write(
                    line + "\n"
                )
    except Exception:
        pass



def _task_id_from_args() -> int | None:
    if "--run-task" not in sys.argv:
        return None

    index = sys.argv.index(
        "--run-task"
    )

    if index + 1 >= len(sys.argv):
        raise SystemExit(
            "--run-task 需要任务 ID。"
        )

    try:
        return int(
            sys.argv[index + 1]
        )
    except Exception as exc:
        raise SystemExit(
            "任务 ID 必须是整数。"
        ) from exc


def _set_app_metadata(
    app: QApplication,
):
    app.setApplicationName(
        "AI板块事件雷达"
    )
    app.setOrganizationName(
        "StockEventRadar"
    )
    app.setApplicationVersion(
        APP_VERSION
    )

    icon_path = (
        Path(__file__).resolve().parent
        / "resources"
        / "app_icon.png"
    )

    if icon_path.exists():
        app.setWindowIcon(
            QIcon(str(icon_path))
        )


def _startup_log_path() -> Path:
    try:
        location = (
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppDataLocation
            )
        )

        if location:
            root = Path(location)
        else:
            root = Path.home() / "StockEventRadar"
    except Exception:
        root = Path.home() / "StockEventRadar"

    root.mkdir(
        parents=True,
        exist_ok=True,
    )

    return root / "startup_crash.log"


def _record_startup_crash(
    exc: BaseException,
) -> str:
    details = "".join(
        traceback.format_exception(
            type(exc),
            exc,
            exc.__traceback__,
        )
    )

    try:
        path = _startup_log_path()
        path.write_text(
            details,
            encoding="utf-8",
        )
        return (
            f"{details}\n\n"
            f"Log: {path}"
        )
    except Exception:
        return details


def _show_startup_error(
    details: str,
):
    try:
        app = (
            QApplication.instance()
            or QApplication(sys.argv)
        )
        _set_app_metadata(app)

        box = QMessageBox()
        box.setIcon(
            QMessageBox.Icon.Critical
        )
        box.setWindowTitle(
            "AI板块事件雷达启动失败"
        )
        box.setText(
            "应用启动时发生错误。"
        )
        box.setInformativeText(
            "RC4.11 已记录详细错误，"
            "请把这个提示截图发给开发者。"
        )
        box.setDetailedText(
            details[-6000:]
        )
        box.exec()
    except Exception:
        pass


def run_scheduled_task(
    task_id: int,
) -> int:
    from app.ai.manager import (
        ProviderManager,
    )
    from app.automation.service import (
        AutomationService,
    )
    from app.config.settings import (
        AppConfig,
    )
    from app.database.database import (
        Database,
    )

    app = QApplication(
        [sys.argv[0]]
    )
    _set_app_metadata(app)
    app.setStyleSheet(
        get_app_style()
    )

    config = AppConfig()
    database = Database()
    provider_manager = (
        ProviderManager()
    )
    service = AutomationService(
        config=config,
        database=database,
        provider_manager=provider_manager,
    )

    try:
        result = service.run_task(
            task_id
        )
    except Exception as exc:
        print(
            f"Scheduled task #{task_id} failed: {exc}",
            file=sys.stderr,
        )
        return 1

    print(
        f"Scheduled task #{task_id}: "
        f"{result.get('status')}"
    )
    return 0


def _run_gui() -> int:
    # Imports are intentionally deferred until startup error handling
    # is active. This is especially useful on Android where missing
    # packaged Python dependencies otherwise look like an instant crash.
    from app.ai.manager import (
        ProviderManager,
    )
    from app.config.settings import (
        AppConfig,
    )
    from app.logging_setup import (
        setup_logging,
    )
    from app.ui.main_window import (
        MainWindow,
    )
    from app.platform import (
        is_android,
        runtime_platform_info,
    )
    from app.ui.onboarding import (
        FirstRunWizard,
        MobileFirstRunDialog,
    )
    from app.ui.styles import (
        get_app_style,
    )

    setup_logging()

    _stage(
        "Runtime platform: "
        f"{runtime_platform_info()}"
    )

    app = (
        QApplication.instance()
        or QApplication(sys.argv)
    )
    _set_app_metadata(app)

    config = AppConfig()
    provider_manager = (
        ProviderManager()
    )

    if not config.onboarding_complete:
        if is_android():
            onboarding = MobileFirstRunDialog(
                config=config,
                provider_manager=(
                    provider_manager
                ),
            )
            onboarding.exec()
        else:
            wizard = FirstRunWizard(
                config=config,
                provider_manager=(
                    provider_manager
                ),
            )
            wizard.exec()

    _stage(
        "MainWindow stage: constructing"
    )

    window = MainWindow(
        config=config,
        provider_manager=(
            provider_manager
        ),
    )

    _stage(
        "MainWindow stage: constructed"
    )

    if is_android():
        def show_mobile_window():
            _stage(
                "MainWindow stage: showing"
            )

            window.show()

            _stage(
                "MainWindow stage: shown"
            )

            # Let the native Android window establish its geometry
            # before the mobile page-margin/layout pass.
            QTimer.singleShot(
                120,
                window.apply_android_layout_after_show,
            )

        # Start the Qt application event loop first.  This avoids a
        # synchronous top-level QWidget.show() while the previous
        # onboarding dialog/native geometry transition is unwinding.
        QTimer.singleShot(
            0,
            show_mobile_window,
        )
    else:
        window.show()
        _stage(
            "MainWindow stage: shown"
        )

    return app.exec()


def main():
    try:
        task_id = _task_id_from_args()

        if task_id is not None:
            raise SystemExit(
                run_scheduled_task(
                    task_id
                )
            )

        raise SystemExit(
            _run_gui()
        )

    except SystemExit:
        raise
    except BaseException as exc:
        details = (
            _record_startup_crash(
                exc
            )
        )

        print(
            details,
            file=sys.stderr,
        )

        _show_startup_error(
            details
        )

        raise SystemExit(1)


if __name__ == "__main__":
    main()
