import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.ai.manager import ProviderManager
from app.config.settings import AppConfig
from app.logging_setup import setup_logging
from app.ui.main_window import MainWindow
from app.ui.onboarding import FirstRunWizard


def main():
    setup_logging()

    app = QApplication(sys.argv)
    app.setApplicationName(
        "AI板块事件雷达"
    )
    app.setOrganizationName(
        "StockEventRadar"
    )
    app.setApplicationVersion(
        "0.9.3"
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
