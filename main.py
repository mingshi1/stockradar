import os
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.ai.manager import ProviderManager
from app.automation.service import AutomationService
from app.config.settings import AppConfig
from app.database.database import Database
from app.logging_setup import setup_logging
from app.ui.main_window import MainWindow
from app.ui.onboarding import FirstRunWizard


APP_VERSION = "1.0.0-rc4.6"


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


def run_scheduled_task(
    task_id: int,
) -> int:
    # No main window is shown. QApplication remains available for
    # Qt PDF generation used by the automatic report exporter.
    app = QApplication(
        [sys.argv[0]]
    )
    _set_app_metadata(app)

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


def main():
    setup_logging()

    task_id = _task_id_from_args()

    if task_id is not None:
        raise SystemExit(
            run_scheduled_task(
                task_id
            )
        )

    app = QApplication(sys.argv)
    _set_app_metadata(app)

    config = AppConfig()
    provider_manager = (
        ProviderManager()
    )

    if not config.onboarding_complete:
        wizard = FirstRunWizard(
            config=config,
            provider_manager=(
                provider_manager
            ),
        )
        wizard.exec()

    window = MainWindow(
        config=config,
        provider_manager=(
            provider_manager
        ),
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
