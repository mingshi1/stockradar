from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.ai.manager import ProviderManager
from app.analysis.models import AnalysisBundle
from app.analysis.service import AnalysisService
from app.config.settings import AppConfig
from app.database.database import Database
from app.news.service import NewsService
from app.report.html_renderer import render_analysis_html
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.history_page import HistoryPage
from app.ui.pages.news_page import NewsPage
from app.ui.pages.sector_page import SectorPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.styles import APP_STYLE
from app.ui.workers import AnalysisWorker, ConnectionWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = AppConfig()
        self.database = Database()
        self.provider_manager = ProviderManager()
        self.analysis_service = AnalysisService(
            self.provider_manager
        )
        self.news_service = NewsService(
            self.database
        )

        self.analysis_worker: AnalysisWorker | None = None
        self.connection_worker: ConnectionWorker | None = None

        self.setWindowTitle("AI板块事件雷达")
        self.resize(1250, 800)
        self.setMinimumSize(1000, 650)

        self._build_ui()
        self._connect_signals()
        self.setStyleSheet(APP_STYLE)

        self.refresh_database_views()

    def _build_ui(self):
        root_widget = QWidget()
        self.setCentralWidget(root_widget)

        root_layout = QHBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = self._create_sidebar()

        self.pages = QStackedWidget()

        self.dashboard_page = DashboardPage()
        self.history_page = HistoryPage()
        self.sector_page = SectorPage()
        self.news_page = NewsPage()
        self.settings_page = SettingsPage(
            config=self.config,
            provider_manager=self.provider_manager,
        )

        for page in [
            self.dashboard_page,
            self.history_page,
            self.sector_page,
            self.news_page,
            self.settings_page,
        ]:
            self.pages.addWidget(page)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.pages, 1)

        self.switch_page(0)

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 25, 20, 25)
        layout.setSpacing(10)

        title = QLabel("AI板块事件雷达")
        title.setObjectName("sidebarTitle")

        subtitle = QLabel("Event Radar")
        subtitle.setObjectName("sidebarSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(30)

        self.nav_buttons: list[QPushButton] = []

        nav_items = [
            ("今日分析", 0),
            ("历史报告", 1),
            ("板块管理", 2),
            ("新闻源", 3),
            ("设置", 4),
        ]

        for text, index in nav_items:
            button = QPushButton(text)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )
            button.clicked.connect(
                lambda checked=False, i=index:
                self.switch_page(i)
            )

            layout.addWidget(button)
            self.nav_buttons.append(button)

        layout.addStretch()

        version = QLabel("v0.5.0")
        version.setObjectName("versionLabel")
        layout.addWidget(version)

        return sidebar

    def _connect_signals(self):
        self.dashboard_page.analyze_requested.connect(
            self.start_analysis
        )

        self.settings_page.save_requested.connect(
            self.save_settings
        )
        self.settings_page.test_requested.connect(
            self.test_api_connection
        )

        self.sector_page.add_requested.connect(
            self.add_custom_sector
        )
        self.sector_page.delete_requested.connect(
            self.delete_custom_sector
        )

        self.history_page.run_selected.connect(
            self.show_history_run
        )

    def switch_page(self, index: int):
        self.pages.setCurrentIndex(index)

        for button_index, button in enumerate(
            self.nav_buttons
        ):
            button.setChecked(button_index == index)

        if index in (1, 2, 3):
            self.refresh_database_views()

    # =========================================================
    # SQLite-backed views
    # =========================================================

    def refresh_database_views(self):
        custom_sectors = self.database.list_custom_sectors()

        self.dashboard_page.set_saved_custom_sectors(
            custom_sectors
        )
        self.sector_page.set_sectors(
            custom_sectors
        )

        self.history_page.set_runs(
            self.database.list_analysis_runs()
        )

        self.news_page.set_events(
            self.news_service.list_events()
        )

    def add_custom_sector(self, name: str):
        added = self.database.add_custom_sector(name)

        if not added:
            QMessageBox.information(
                self,
                "未新增",
                "该板块已经存在，或名称为空。",
            )
            return

        self.sector_page.add_success()
        self.refresh_database_views()

    def delete_custom_sector(self, name: str):
        answer = QMessageBox.question(
            self,
            "确认删除",
            f"确定删除自定义板块“{name}”吗？",
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self.database.delete_custom_sector(name)
        self.refresh_database_views()

    # =========================================================
    # Analysis
    # =========================================================

    def start_analysis(self, selected_sectors: list[str]):
        if not selected_sectors:
            QMessageBox.warning(
                self,
                "没有选择板块",
                "请至少选择一个板块。",
            )
            return

        provider_name = self.config.provider
        model = self.config.model
        api_key = self.config.get_api_key(
            provider_name
        )

        if not api_key:
            QMessageBox.warning(
                self,
                "尚未配置 API",
                "请先进入“设置”页面配置 API Key。",
            )
            self.switch_page(4)
            return

        if (
            self.analysis_worker is not None
            and self.analysis_worker.isRunning()
        ):
            return

        self.dashboard_page.set_running(True)

        self.analysis_worker = AnalysisWorker(
            analysis_service=self.analysis_service,
            api_key=api_key,
            provider_name=provider_name,
            model=model,
            sectors=selected_sectors,
        )

        self.analysis_worker.result_ready.connect(
            self.on_analysis_ready
        )
        self.analysis_worker.error_occurred.connect(
            self.on_analysis_error
        )
        self.analysis_worker.finished.connect(
            self.on_analysis_finished
        )
        self.analysis_worker.start()

    def on_analysis_ready(self, bundle: AnalysisBundle):
        try:
            self.database.save_analysis(bundle)
        except Exception as exc:
            QMessageBox.warning(
                self,
                "数据库保存失败",
                "分析已经成功，但写入 SQLite 失败：\n\n"
                f"{exc}",
            )

        html_content = render_analysis_html(
            bundle.structured
        )
        self.dashboard_page.show_result(
            html_content
        )

        self.refresh_database_views()

    def on_analysis_error(self, message: str):
        self.dashboard_page.show_error(message)

        QMessageBox.critical(
            self,
            "分析失败",
            message,
        )

    def on_analysis_finished(self):
        self.dashboard_page.set_running(False)
        self.analysis_worker = None

    # =========================================================
    # History
    # =========================================================

    def show_history_run(self, run_id: int):
        run = self.database.get_analysis_run(run_id)

        if not run:
            return

        self.history_page.show_report(
            render_analysis_html(
                run["result"]
            )
        )

    # =========================================================
    # Settings
    # =========================================================

    def save_settings(
        self,
        provider_name: str,
        model: str,
        api_key: str,
    ):
        self.config.provider = provider_name
        self.config.model = model
        self.config.save()

        if api_key:
            try:
                self.config.save_api_key(
                    provider_name,
                    api_key,
                )
            except Exception as exc:
                QMessageBox.critical(
                    self,
                    "保存失败",
                    f"API Key 保存失败：\n\n{exc}",
                )
                return

        self.settings_page.mark_saved()

        QMessageBox.information(
            self,
            "保存成功",
            "AI 设置已保存。",
        )

    def test_api_connection(
        self,
        provider_name: str,
        model: str,
        entered_api_key: str,
    ):
        api_key = entered_api_key

        if not api_key:
            api_key = self.config.get_api_key(
                provider_name
            )

        if not api_key:
            QMessageBox.warning(
                self,
                "缺少 API Key",
                "请先输入 API Key。",
            )
            return

        if (
            self.connection_worker is not None
            and self.connection_worker.isRunning()
        ):
            return

        self.settings_page.set_test_running(True)

        self.connection_worker = ConnectionWorker(
            provider_manager=self.provider_manager,
            api_key=api_key,
            provider_name=provider_name,
            model=model,
        )

        self.connection_worker.success.connect(
            self.on_connection_success
        )
        self.connection_worker.error_occurred.connect(
            self.on_connection_error
        )
        self.connection_worker.finished.connect(
            self.on_connection_finished
        )

        self.connection_worker.start()

    def on_connection_success(self, result: str):
        self.settings_page.show_test_success()

        QMessageBox.information(
            self,
            "连接成功",
            "AI API 工作正常。\n\n"
            f"模型回复：{result}",
        )

    def on_connection_error(self, message: str):
        self.settings_page.show_test_error()

        QMessageBox.critical(
            self,
            "连接失败",
            message,
        )

    def on_connection_finished(self):
        self.settings_page.set_test_running(False)
        self.connection_worker = None
