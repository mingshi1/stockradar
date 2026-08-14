import sys

from PySide6.QtWidgets import QApplication

from app.logging_setup import setup_logging
from app.ui.main_window import MainWindow


def main():
    setup_logging()

    app = QApplication(sys.argv)
    app.setApplicationName("AI板块事件雷达")
    app.setOrganizationName("StockEventRadar")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
