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
from app.ui.workers import (
    AnalysisWorker,
    ConnectionWorker,
)


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

        self.analysis_worker: (
            AnalysisWorker | None
        ) = None
        self.connection_worker: (
            ConnectionWorker | None
        ) = None
        self.connection_provider_name: (
            str | None
        ) = None

        self.setWindowTitle(
            "AI板块事件雷达"
        )
        self.resize(1280, 820)
        self.setMinimumSize(
            1050,
            680,
        )

        self._build_ui()
        self._connect_signals()
        self.setStyleSheet(
            APP_STYLE
        )

        self.refresh_database_views()

    def _build_ui(self):
        root_widget = QWidget()
        self.setCentralWidget(
            root_widget
        )

        root_layout = QHBoxLayout(
            root_widget
        )
        root_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        root_layout.setSpacing(0)

        sidebar = (
            self._create_sidebar()
        )

        self.pages = QStackedWidget()

        self.dashboard_page = (
            DashboardPage()
        )
        self.history_page = (
            HistoryPage()
        )
        self.sector_page = (
            SectorPage()
        )
        self.news_page = (
            NewsPage()
        )
        self.settings_page = (
            SettingsPage(
                config=self.config,
                provider_manager=(
                    self.provider_manager
                ),
            )
        )

        for page in [
            self.dashboard_page,
            self.history_page,
            self.sector_page,
            self.news_page,
            self.settings_page,
        ]:
            self.pages.addWidget(page)

        root_layout.addWidget(
            sidebar
        )
        root_layout.addWidget(
            self.pages,
            1,
        )

        self.switch_page(0)

    def _create_sidebar(
        self,
    ) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName(
            "sidebar"
        )
        sidebar.setFixedWidth(210)

        layout = QVBoxLayout(
            sidebar
        )
        layout.setContentsMargins(
            20,
            25,
            20,
            25,
        )
        layout.setSpacing(10)

        title = QLabel(
            "AI板块事件雷达"
        )
        title.setObjectName(
            "sidebarTitle"
        )

        subtitle = QLabel(
            "Multi-AI Event Radar"
        )
        subtitle.setObjectName(
            "sidebarSubtitle"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(30)

        self.nav_buttons: list[
            QPushButton
        ] = []

        nav_items = [
            ("今日分析", 0),
            ("历史报告", 1),
            ("板块管理", 2),
            ("新闻源", 3),
            ("AI 设置", 4),
        ]

        for text, index in nav_items:
            button = QPushButton(
                text
            )
            button.setObjectName(
                "navButton"
            )
            button.setCheckable(True)
            button.setCursor(
                Qt.CursorShape
                .PointingHandCursor
            )
            button.clicked.connect(
                lambda checked=False,
                i=index:
                self.switch_page(i)
            )

            layout.addWidget(button)
            self.nav_buttons.append(
                button
            )

        layout.addStretch()

        version = QLabel(
            "v0.6.0"
        )
        version.setObjectName(
            "versionLabel"
        )
        layout.addWidget(version)

        return sidebar

    def _connect_signals(self):
        self.dashboard_page \
            .analyze_requested \
            .connect(
                self.start_analysis
            )

        self.settings_page \
            .save_requested \
            .connect(
                self.save_settings
            )

        self.settings_page \
            .test_requested \
            .connect(
                self.test_api_connection
            )

        self.sector_page \
            .add_requested \
            .connect(
                self.add_custom_sector
            )

        self.sector_page \
            .delete_requested \
            .connect(
                self.delete_custom_sector
            )

        self.history_page \
            .run_selected \
            .connect(
                self.show_history_run
            )

    def switch_page(
        self,
        index: int,
    ):
        self.pages.setCurrentIndex(
            index
        )

        for button_index, button in (
            enumerate(
                self.nav_buttons
            )
        ):
            button.setChecked(
                button_index == index
            )

        if index in (
            1,
            2,
            3,
        ):
            self.refresh_database_views()

    # =========================================================
    # SQLite
    # =========================================================

    def refresh_database_views(self):
        custom_sectors = (
            self.database
            .list_custom_sectors()
        )

        self.dashboard_page \
            .set_saved_custom_sectors(
                custom_sectors
            )

        self.sector_page \
            .set_sectors(
                custom_sectors
            )

        self.history_page \
            .set_runs(
                self.database
                .list_analysis_runs()
            )

        self.news_page \
            .set_events(
                self.news_service
                .list_events()
            )

    def add_custom_sector(
        self,
        name: str,
    ):
        added = (
            self.database
            .add_custom_sector(name)
        )

        if not added:
            QMessageBox.information(
                self,
                "未新增",
                "该板块已经存在，"
                "或名称为空。",
            )
            return

        self.sector_page \
            .add_success()

        self.refresh_database_views()

    def delete_custom_sector(
        self,
        name: str,
    ):
        answer = (
            QMessageBox.question(
                self,
                "确认删除",
                f"确定删除自定义板块"
                f"“{name}”吗？",
            )
        )

        if (
            answer
            != QMessageBox
            .StandardButton.Yes
        ):
            return

        self.database \
            .delete_custom_sector(name)

        self.refresh_database_views()

    # =========================================================
    # Multi-AI analysis
    # =========================================================

    def start_analysis(
        self,
        selected_sectors: list[str],
    ):
        if not selected_sectors:
            QMessageBox.warning(
                self,
                "没有选择板块",
                "请至少选择一个板块。",
            )
            return

        research_provider = (
            self.config
            .research_provider
        )

        research_key = (
            self.config
            .get_api_key(
                research_provider
            )
        )

        if not research_key:
            QMessageBox.warning(
                self,
                "缺少联网研究 API",
                f"请先在“AI 设置”中"
                f"配置 {research_provider} "
                "API Key。",
            )
            self.switch_page(4)
            return

        if (
            self.analysis_worker
            is not None
            and self.analysis_worker
            .isRunning()
        ):
            return

        provider_settings = {
            name:
            self.config
            .get_provider_config(name)
            for name
            in self.provider_manager
            .provider_names()
        }

        needed_names = set(
            self.config
            .enabled_provider_names()
        )
        needed_names.add(
            research_provider
        )

        if self.config.judge_enabled:
            needed_names.add(
                self.config
                .judge_provider
            )

        api_keys = {
            name:
            self.config
            .get_api_key(name)
            for name in needed_names
            if self.config
            .get_api_key(name)
        }

        request = {
            "sectors": (
                selected_sectors
            ),
            "research_provider_name": (
                research_provider
            ),
            "analysis_mode": (
                self.config
                .analysis_mode
            ),
            "judge_enabled": (
                self.config
                .judge_enabled
            ),
            "judge_provider_name": (
                self.config
                .judge_provider
            ),
            "provider_settings": (
                provider_settings
            ),
            "api_keys": api_keys,
        }

        self.dashboard_page \
            .set_running(True)

        self.analysis_worker = (
            AnalysisWorker(
                analysis_service=(
                    self.analysis_service
                ),
                request=request,
            )
        )

        self.analysis_worker \
            .result_ready \
            .connect(
                self.on_analysis_ready
            )

        self.analysis_worker \
            .error_occurred \
            .connect(
                self.on_analysis_error
            )

        self.analysis_worker \
            .finished \
            .connect(
                self.on_analysis_finished
            )

        self.analysis_worker.start()

    def on_analysis_ready(
        self,
        bundle: AnalysisBundle,
    ):
        try:
            self.database \
                .save_analysis(bundle)
        except Exception as exc:
            QMessageBox.warning(
                self,
                "数据库保存失败",
                "分析已经成功，"
                "但写入 SQLite 失败："
                f"\n\n{exc}",
            )

        self.dashboard_page \
            .show_result(
                render_analysis_html(
                    bundle.structured
                )
            )

        self.refresh_database_views()

    def on_analysis_error(
        self,
        message: str,
    ):
        self.dashboard_page \
            .show_error(message)

        QMessageBox.critical(
            self,
            "分析失败",
            message,
        )

    def on_analysis_finished(self):
        self.dashboard_page \
            .set_running(False)

        self.analysis_worker = None

    # =========================================================
    # History
    # =========================================================

    def show_history_run(
        self,
        run_id: int,
    ):
        run = (
            self.database
            .get_analysis_run(
                run_id
            )
        )

        if not run:
            return

        self.history_page \
            .show_report(
                render_analysis_html(
                    run["result"]
                )
            )

    # =========================================================
    # Settings
    # =========================================================

    def save_settings(
        self,
        payload: dict,
    ):
        self.config.research_provider = (
            payload.get(
                "research_provider",
                "DeepSeek",
            )
        )
        self.config.analysis_mode = (
            payload.get(
                "analysis_mode",
                "multi",
            )
        )
        self.config.judge_enabled = bool(
            payload.get(
                "judge_enabled",
                False,
            )
        )
        self.config.judge_provider = (
            payload.get(
                "judge_provider",
                self.config
                .research_provider,
            )
        )

        for provider_name, settings in (
            payload.get(
                "providers",
                {},
            ).items()
        ):
            self.config \
                .update_provider_config(
                    provider_name,
                    enabled=settings.get(
                        "enabled",
                        False,
                    ),
                    model=settings.get(
                        "model",
                        "",
                    ),
                    base_url=settings.get(
                        "base_url",
                        "",
                    ),
                )

            api_key = str(
                settings.get(
                    "api_key",
                    "",
                )
            ).strip()

            if api_key:
                try:
                    self.config \
                        .save_api_key(
                            provider_name,
                            api_key,
                        )
                except Exception as exc:
                    QMessageBox.critical(
                        self,
                        "保存失败",
                        f"{provider_name} "
                        "API Key 保存失败："
                        f"\n\n{exc}",
                    )
                    return

        self.config.save()
        self.settings_page \
            .mark_saved()

        QMessageBox.information(
            self,
            "保存成功",
            "Multi-AI 设置已保存。",
        )

    def test_api_connection(
        self,
        provider_name: str,
        entered_api_key: str,
        model: str,
        base_url: str,
    ):
        api_key = (
            entered_api_key
            or self.config
            .get_api_key(
                provider_name
            )
        )

        if not api_key:
            QMessageBox.warning(
                self,
                "缺少 API Key",
                f"请先输入 "
                f"{provider_name} API Key。",
            )
            return

        if (
            self.connection_worker
            is not None
            and self.connection_worker
            .isRunning()
        ):
            QMessageBox.information(
                self,
                "正在测试",
                "当前已有一个 Provider "
                "正在进行连接测试。",
            )
            return

        self.connection_provider_name = (
            provider_name
        )

        self.settings_page \
            .set_test_running(
                provider_name,
                True,
            )

        self.connection_worker = (
            ConnectionWorker(
                provider_manager=(
                    self.provider_manager
                ),
                provider_name=(
                    provider_name
                ),
                api_key=api_key,
                model=model,
                base_url=base_url,
            )
        )

        self.connection_worker \
            .success \
            .connect(
                self.on_connection_success
            )
        self.connection_worker \
            .error_occurred \
            .connect(
                self.on_connection_error
            )
        self.connection_worker \
            .finished \
            .connect(
                self.on_connection_finished
            )

        self.connection_worker.start()

    def on_connection_success(
        self,
        result: str,
    ):
        name = (
            self.connection_provider_name
            or ""
        )

        if name:
            self.settings_page \
                .show_test_success(name)

        QMessageBox.information(
            self,
            "连接成功",
            f"{name} API 工作正常。"
            f"\n\n模型回复：{result}",
        )

    def on_connection_error(
        self,
        message: str,
    ):
        name = (
            self.connection_provider_name
            or ""
        )

        if name:
            self.settings_page \
                .show_test_error(name)

        QMessageBox.critical(
            self,
            "连接失败",
            message,
        )

    def on_connection_finished(self):
        name = (
            self.connection_provider_name
            or ""
        )

        if name:
            self.settings_page \
                .set_test_running(
                    name,
                    False,
                )

        self.connection_provider_name = (
            None
        )
        self.connection_worker = None
