import logging
from pathlib import Path

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
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
from app.automation.scheduler import WindowsTaskScheduler
from app.automation.service import AutomationService
from app.config.settings import APP_DATA_DIR, DATABASE_FILE, AppConfig
from app.database.database import Database
from app.news.service import NewsService
from app.report.exporters import export_report
from app.report.html_renderer import render_analysis_html
from app.report.models import ReportArtifact
from app.report.service import ReportService
from app.ui.pages.automation_page import AutomationPage
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.history_page import HistoryPage
from app.ui.pages.news_page import NewsPage
from app.ui.pages.report_page import ReportPage
from app.ui.pages.sector_page import SectorPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.pages.stats_page import StatsPage
from app.ui.pages.system_page import SystemPage
from app.ui.onboarding import FirstRunWizard
from app.ui.styles import APP_STYLE
from app.logging_setup import LOG_DIR
from app.ui.workers import (
    AnalysisWorker,
    AutomationWorker,
    ConnectionWorker,
    TimeSyncWorker,
)


class MainWindow(QMainWindow):
    def __init__(
        self,
        config: AppConfig | None = None,
        provider_manager: ProviderManager | None = None,
    ):
        super().__init__()

        self.logger = logging.getLogger(
            "StockEventRadar"
        )

        self.config = config or AppConfig()
        self.database = Database()
        self.provider_manager = (
            provider_manager
            or ProviderManager()
        )
        self.analysis_service = AnalysisService(
            self.provider_manager
        )
        self.news_service = NewsService(
            self.database
        )
        self.report_service = ReportService()
        self.task_scheduler = WindowsTaskScheduler()
        self.automation_service = AutomationService(
            config=self.config,
            database=self.database,
            provider_manager=self.provider_manager,
        )

        self.analysis_worker: AnalysisWorker | None = None
        self.automation_worker: AutomationWorker | None = None
        self.time_sync_worker: TimeSyncWorker | None = None
        self.connection_worker: ConnectionWorker | None = None
        self.connection_provider_name: str | None = None
        self.current_report_artifact: ReportArtifact | None = None

        self.setWindowTitle(
            "AI板块事件雷达"
        )
        self.resize(
            1360,
            880,
        )
        self.setMinimumSize(
            360,
            600,
        )

        self._build_ui()
        self._connect_signals()
        self.setStyleSheet(
            APP_STYLE
        )

        self.refresh_database_views()
        self._apply_responsive_layout()

    # =========================================================
    # UI
    # =========================================================

    def _build_ui(self):
        root_widget = QWidget()
        self.setCentralWidget(
            root_widget
        )

        root_layout = QVBoxLayout(
            root_widget
        )
        root_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        root_layout.setSpacing(0)

        self.nav_items = [
            ("今日分析", 0),
            ("历史报告", 1),
            ("板块管理", 2),
            ("新闻源", 3),
            ("数据统计", 4),
            ("晨报 / 报告中心", 5),
            ("自动任务", 6),
            ("AI 设置", 7),
            ("系统与数据", 8),
        ]

        self.mobile_nav = (
            self._create_mobile_nav()
        )
        root_layout.addWidget(
            self.mobile_nav
        )

        content = QWidget()
        content_layout = QHBoxLayout(
            content
        )
        content_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        content_layout.setSpacing(0)

        self.sidebar = (
            self._create_sidebar()
        )

        self.pages = QStackedWidget()

        self.dashboard_page = DashboardPage()
        self.history_page = HistoryPage()
        self.sector_page = SectorPage()
        self.news_page = NewsPage()
        self.stats_page = StatsPage()
        self.report_page = ReportPage()
        self.automation_page = AutomationPage()
        self.settings_page = SettingsPage(
            config=self.config,
            provider_manager=self.provider_manager,
        )
        self.system_page = SystemPage()

        for page in [
            self.dashboard_page,
            self.history_page,
            self.sector_page,
            self.news_page,
            self.stats_page,
            self.report_page,
            self.automation_page,
            self.settings_page,
            self.system_page,
        ]:
            self.pages.addWidget(
                page
            )

        content_layout.addWidget(
            self.sidebar
        )
        content_layout.addWidget(
            self.pages,
            1,
        )

        root_layout.addWidget(
            content,
            1,
        )

        self.switch_page(0)

    def _create_mobile_nav(
        self,
    ) -> QFrame:
        bar = QFrame()
        bar.setObjectName(
            "mobileNav"
        )

        layout = QHBoxLayout(
            bar
        )
        layout.setContentsMargins(
            12,
            8,
            12,
            8,
        )

        title = QLabel(
            "AI板块事件雷达"
        )
        title.setObjectName(
            "mobileNavTitle"
        )

        self.mobile_nav_combo = (
            QComboBox()
        )

        for text, index in (
            self.nav_items
        ):
            self.mobile_nav_combo.addItem(
                text,
                index,
            )

        self.mobile_nav_combo.currentIndexChanged.connect(
            self._mobile_nav_changed
        )

        layout.addWidget(
            title
        )
        layout.addStretch()
        layout.addWidget(
            self.mobile_nav_combo,
            1,
        )

        return bar

    def _mobile_nav_changed(
        self,
    ):
        index = (
            self.mobile_nav_combo
            .currentData()
        )

        if index is not None:
            self.switch_page(
                int(index)
            )

    def _create_sidebar(
        self,
    ) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName(
            "sidebar"
        )
        sidebar.setFixedWidth(
            225
        )

        layout = QVBoxLayout(
            sidebar
        )
        layout.setContentsMargins(
            20,
            25,
            20,
            25,
        )
        layout.setSpacing(9)

        title = QLabel(
            "AI板块事件雷达"
        )
        title.setObjectName(
            "sidebarTitle"
        )

        subtitle = QLabel(
            "Observable Multi-AI Radar"
        )
        subtitle.setObjectName(
            "sidebarSubtitle"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(25)

        self.nav_buttons: list[
            QPushButton
        ] = []

        for text, index in self.nav_items:
            button = QPushButton(
                text
            )
            button.setObjectName(
                "navButton"
            )
            button.setCheckable(
                True
            )
            button.setCursor(
                Qt.CursorShape
                .PointingHandCursor
            )
            button.clicked.connect(
                lambda checked=False,
                i=index:
                self.switch_page(i)
            )

            layout.addWidget(
                button
            )
            self.nav_buttons.append(
                button
            )

        layout.addStretch()

        version = QLabel(
            "v1.0.0 RC1"
        )
        version.setObjectName(
            "versionLabel"
        )
        layout.addWidget(
            version
        )

        return sidebar

    def _connect_signals(
        self,
    ):
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

        self.stats_page.sector_changed.connect(
            self.refresh_sector_trend
        )

        self.report_page.generate_requested.connect(
            self.generate_report
        )
        self.report_page.export_requested.connect(
            self.export_current_report
        )
        self.report_page.copy_requested.connect(
            self.copy_report_summary
        )
        self.report_page.saved_report_requested.connect(
            self.open_saved_report
        )

        self.automation_page.sync_time_requested.connect(
            self.sync_system_time
        )
        self.automation_page.save_task_requested.connect(
            self.save_scheduled_task
        )
        self.automation_page.delete_task_requested.connect(
            self.delete_scheduled_task
        )
        self.automation_page.run_task_requested.connect(
            self.run_scheduled_task_now
        )
        self.automation_page.refresh_requested.connect(
            self.refresh_automation_views
        )

        self.system_page.backup_requested.connect(
            self.backup_database
        )
        self.system_page.restore_requested.connect(
            self.restore_database
        )
        self.system_page.open_data_requested.connect(
            self.open_data_directory
        )
        self.system_page.open_logs_requested.connect(
            self.open_logs_directory
        )
        self.system_page.rerun_onboarding_requested.connect(
            self.rerun_onboarding
        )
        self.system_page.ui_mode_changed.connect(
            self.change_ui_mode
        )

    def switch_page(
        self,
        index: int,
    ):
        self.pages.setCurrentIndex(
            index
        )

        for button_index, button in enumerate(
            self.nav_buttons
        ):
            button.setChecked(
                button_index == index
            )

        combo_index = (
            self.mobile_nav_combo
            .findData(index)
        )

        if combo_index >= 0:
            self.mobile_nav_combo.blockSignals(
                True
            )
            self.mobile_nav_combo.setCurrentIndex(
                combo_index
            )
            self.mobile_nav_combo.blockSignals(
                False
            )

        if index in (
            1,
            2,
            3,
            4,
            5,
            6,
            8,
        ):
            self.refresh_database_views()

        if index == 6:
            self.refresh_automation_views()

        if index == 8:
            self.refresh_system_info()

    def resizeEvent(
        self,
        event,
    ):
        super().resizeEvent(event)
        self._apply_responsive_layout()

    def _apply_responsive_layout(
        self,
    ):
        mode = self.config.ui_mode

        if mode == "desktop":
            mobile = False
        elif mode == "mobile":
            mobile = True
        else:
            mobile = self.width() < 900

        self.sidebar.setVisible(
            not mobile
        )
        self.mobile_nav.setVisible(
            mobile
        )

    def change_ui_mode(
        self,
        mode: str,
    ):
        self.config.ui_mode = mode
        self.config.save()
        self._apply_responsive_layout()

    # =========================================================
    # SQLite-backed views
    # =========================================================

    def refresh_database_views(
        self,
    ):
        custom_sectors = (
            self.database
            .list_custom_sectors()
        )

        self.dashboard_page.set_saved_custom_sectors(
            custom_sectors
        )
        self.sector_page.set_sectors(
            custom_sectors
        )

        runs = (
            self.database
            .list_analysis_runs()
        )

        self.history_page.set_runs(
            runs
        )
        self.report_page.set_runs(
            runs
        )

        self.report_page.set_saved_reports(
            self.database
            .list_saved_reports()
        )

        self.news_page.set_events(
            self.news_service
            .list_events()
        )

        sector_names = (
            self.database
            .list_sector_names()
        )

        self.stats_page.set_sector_names(
            sector_names
        )
        self.stats_page.set_provider_stats(
            self.database
            .list_provider_stats()
        )

        current_sector = (
            self.stats_page
            .current_sector()
        )

        if current_sector:
            self.refresh_sector_trend(
                current_sector
            )
        else:
            self.stats_page.set_trend(
                []
            )

    def refresh_sector_trend(
        self,
        sector_name: str,
    ):
        if not sector_name:
            self.stats_page.set_trend(
                []
            )
            return

        self.stats_page.set_trend(
            self.database
            .list_sector_trends(
                sector_name,
                limit=30,
            )
        )

    def add_custom_sector(
        self,
        name: str,
    ):
        added = self.database.add_custom_sector(
            name
        )

        if not added:
            QMessageBox.information(
                self,
                "未新增",
                "该板块已经存在，或名称为空。",
            )
            return

        self.sector_page.add_success()
        self.refresh_database_views()

    def delete_custom_sector(
        self,
        name: str,
    ):
        answer = QMessageBox.question(
            self,
            "确认删除",
            f"确定删除自定义板块“{name}”吗？",
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self.database.delete_custom_sector(
            name
        )
        self.refresh_database_views()

    # =========================================================
    # Multi-AI analysis + live progress
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
                f"请先在“AI 设置”中配置 "
                f"{research_provider} API Key。",
            )
            self.switch_page(7)
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
            self.config.get_provider_config(
                name
            )
            for name
            in self.provider_manager
            .provider_names()
        }

        if self.config.analysis_mode == "single":
            analyst_names = [
                research_provider
            ]
        else:
            analyst_names = (
                self.config
                .enabled_provider_names()
            )

            if research_provider not in analyst_names:
                analyst_names.insert(
                    0,
                    research_provider,
                )

        needed_names = set(
            analyst_names
        )
        needed_names.add(
            research_provider
        )

        if self.config.judge_enabled:
            needed_names.add(
                self.config
                .judge_provider
            )

        api_keys = {}

        for name in needed_names:
            key = (
                self.config
                .get_api_key(name)
            )

            if key:
                api_keys[
                    name
                ] = key

        self.dashboard_page.prepare_progress(
            research_provider=research_provider,
            analyst_names=analyst_names,
            judge_enabled=self.config.judge_enabled,
            judge_provider=self.config.judge_provider,
        )

        request = {
            "sectors": selected_sectors,
            "research_provider_name": research_provider,
            "analysis_mode": self.config.analysis_mode,
            "judge_enabled": self.config.judge_enabled,
            "judge_provider_name": self.config.judge_provider,
            "provider_settings": provider_settings,
            "api_keys": api_keys,
        }

        self.dashboard_page.set_running(
            True
        )

        self.logger.info(
            "Analysis started | sectors=%s | research=%s | analysts=%s",
            selected_sectors,
            research_provider,
            analyst_names,
        )

        self.analysis_worker = AnalysisWorker(
            analysis_service=self.analysis_service,
            request=request,
        )

        self.analysis_worker.progress_changed.connect(
            self.on_analysis_progress
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

    def on_analysis_progress(
        self,
        event: dict,
    ):
        self.dashboard_page.apply_progress(
            event
        )

    def on_analysis_ready(
        self,
        bundle: AnalysisBundle,
    ):
        self.dashboard_page.apply_progress(
            {
                "percent": 97,
                "stage": "database",
                "status": "running",
                "message": "正在写入 SQLite 历史、Provider 用量与事件池…",
            }
        )

        try:
            run_id = self.database.save_analysis(
                bundle
            )
        except Exception as exc:
            self.logger.exception(
                "Database save failed."
            )

            self.dashboard_page.apply_progress(
                {
                    "percent": 99,
                    "stage": "database",
                    "status": "error",
                    "message": (
                        "分析成功，但数据库保存失败。"
                    ),
                }
            )

            QMessageBox.warning(
                self,
                "数据库保存失败",
                "分析已经成功，但写入 SQLite 失败："
                f"\n\n{exc}",
            )
        else:
            self.logger.info(
                "Analysis saved | run_id=%s",
                run_id,
            )
            self.dashboard_page.mark_saved()

        self.dashboard_page.show_result(
            render_analysis_html(
                bundle.structured
            )
        )

        self.refresh_database_views()

    def on_analysis_error(
        self,
        message: str,
    ):
        self.logger.error(
            "Analysis failed | %s",
            message,
        )

        self.dashboard_page.show_error(
            message
        )

        QMessageBox.critical(
            self,
            "分析失败",
            message,
        )

    def on_analysis_finished(
        self,
    ):
        self.dashboard_page.set_running(
            False
        )
        self.analysis_worker = None

    # =========================================================
    # History
    # =========================================================

    def show_history_run(
        self,
        run_id: int,
    ):
        run = self.database.get_analysis_run(
            run_id
        )

        if not run:
            return

        self.history_page.show_report(
            render_analysis_html(
                run["result"]
            )
        )

    # =========================================================
    # Report Center + archive
    # =========================================================

    def generate_report(
        self,
        run_id: int,
        report_type: str,
    ):
        run = self.database.get_analysis_run(
            run_id
        )

        if not run:
            QMessageBox.warning(
                self,
                "报告生成失败",
                "找不到对应历史分析。",
            )
            return

        provider_results = (
            self.database
            .get_provider_results(
                run_id
            )
        )

        try:
            artifact = self.report_service.generate(
                run=run,
                provider_results=provider_results,
                report_type=report_type,
            )

            self.database.save_report(
                analysis_run_id=run_id,
                artifact=artifact,
            )
        except Exception as exc:
            self.logger.exception(
                "Report generation/archive failed."
            )

            QMessageBox.critical(
                self,
                "报告生成失败",
                str(exc),
            )
            return

        self.current_report_artifact = artifact

        self.report_page.show_artifact(
            artifact.title,
            artifact.html,
        )

        self.report_page.set_saved_reports(
            self.database
            .list_saved_reports()
        )

    def open_saved_report(
        self,
        report_id: int,
    ):
        item = self.database.get_saved_report(
            report_id
        )

        if not item:
            QMessageBox.warning(
                self,
                "打开失败",
                "找不到该归档报告。",
            )
            return

        artifact = ReportArtifact(
            title=item["title"],
            report_type=item["report_type"],
            html=item["html_content"],
            markdown=item["markdown_content"],
            plain_summary=item["plain_summary"],
        )

        self.current_report_artifact = artifact

        self.report_page.show_artifact(
            artifact.title,
            artifact.html,
        )

    def copy_report_summary(
        self,
    ):
        artifact = (
            self.current_report_artifact
        )

        if artifact is None:
            QMessageBox.information(
                self,
                "尚未生成报告",
                "请先生成或打开一份报告。",
            )
            return

        QApplication.clipboard().setText(
            artifact.plain_summary
        )

        QMessageBox.information(
            self,
            "复制成功",
            "报告摘要已经复制到剪贴板。",
        )

    def export_current_report(
        self,
        file_format: str,
    ):
        artifact = (
            self.current_report_artifact
        )

        if artifact is None:
            QMessageBox.information(
                self,
                "尚未生成报告",
                "请先生成或打开一份报告。",
            )
            return

        format_info = {
            "markdown": (
                "Markdown 文件 (*.md)",
                ".md",
            ),
            "html": (
                "HTML 文件 (*.html)",
                ".html",
            ),
            "pdf": (
                "PDF 文件 (*.pdf)",
                ".pdf",
            ),
            "png": (
                "PNG 图片 (*.png)",
                ".png",
            ),
        }

        filter_text, suffix = format_info[
            file_format
        ]

        suggested_name = (
            artifact.title
            .replace("/", "-")
            .replace("\\", "-")
            .replace(":", "-")
            + suffix
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出报告",
            suggested_name,
            filter_text,
        )

        if not file_path:
            return

        if not file_path.lower().endswith(
            suffix
        ):
            file_path += suffix

        try:
            export_report(
                artifact=artifact,
                file_format=file_format,
                file_path=file_path,
            )
        except Exception as exc:
            self.logger.exception(
                "Report export failed."
            )

            QMessageBox.critical(
                self,
                "导出失败",
                str(exc),
            )
            return

        QMessageBox.information(
            self,
            "导出成功",
            "报告已经保存到：\n\n"
            f"{Path(file_path)}",
        )


    # =========================================================
    # Automation center
    # =========================================================

    def refresh_automation_views(
        self,
    ):
        self.automation_page.set_tasks(
            self.database
            .list_scheduled_tasks()
        )
        self.automation_page.set_task_runs(
            self.database
            .list_task_runs(
                limit=100
            )
        )


    def sync_system_time(
        self,
    ):
        if (
            self.time_sync_worker is not None
            and self.time_sync_worker.isRunning()
        ):
            return

        self.automation_page.set_sync_running(
            True
        )

        self.time_sync_worker = (
            TimeSyncWorker()
        )
        self.time_sync_worker.result_ready.connect(
            self.on_time_sync_result
        )
        self.time_sync_worker.finished.connect(
            self.on_time_sync_finished
        )
        self.time_sync_worker.start()

    def on_time_sync_result(
        self,
        success: bool,
        message: str,
    ):
        if success:
            QMessageBox.information(
                self,
                "时间同步完成",
                message
                or "Windows 时间同步请求已完成。",
            )
        else:
            QMessageBox.warning(
                self,
                "时间同步未完成",
                message,
            )

    def on_time_sync_finished(
        self,
    ):
        self.automation_page.set_sync_running(
            False
        )
        self.time_sync_worker = None

    def save_scheduled_task(
        self,
        payload: dict,
    ):
        sectors = payload.get(
            "sectors",
            [],
        )

        if not sectors:
            QMessageBox.warning(
                self,
                "无法保存",
                "自动任务至少需要一个分析板块。",
            )
            return

        try:
            task_id = (
                self.database
                .save_scheduled_task(
                    payload
                )
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "保存任务失败",
                str(exc),
            )
            return

        if payload.get("enabled"):
            success, message = (
                self.task_scheduler
                .register_daily(
                    task_id=task_id,
                    run_time=str(
                        payload.get(
                            "run_time",
                            "07:30",
                        )
                    ),
                )
            )
        else:
            success, message = (
                self.task_scheduler
                .unregister(task_id)
            )

        self.refresh_automation_views()

        if success:
            QMessageBox.information(
                self,
                "任务已保存",
                (
                    f"自动任务 #{task_id} 已保存。\n\n"
                    + (
                        "Windows 每日计划任务已经注册。"
                        if payload.get("enabled")
                        else "任务已停用，Windows 计划任务已移除。"
                    )
                ),
            )
        else:
            QMessageBox.warning(
                self,
                "任务已保存，但系统调度未完成",
                (
                    f"数据库中的任务 #{task_id} 已保存，"
                    "但 Windows Task Scheduler 注册失败：\n\n"
                    f"{message}\n\n"
                    "你仍可以使用“立即执行”测试任务。"
                ),
            )

    def delete_scheduled_task(
        self,
        task_id: int,
    ):
        answer = QMessageBox.question(
            self,
            "删除自动任务",
            f"确定删除自动任务 #{task_id} 吗？",
        )

        if (
            answer
            != QMessageBox.StandardButton.Yes
        ):
            return

        self.task_scheduler.unregister(
            task_id
        )
        self.database.delete_scheduled_task(
            task_id
        )
        self.refresh_automation_views()

    def run_scheduled_task_now(
        self,
        task_id: int,
    ):
        if (
            self.automation_worker is not None
            and self.automation_worker.isRunning()
        ):
            QMessageBox.information(
                self,
                "已有任务运行",
                "请等待当前自动任务完成。",
            )
            return

        self.automation_page.set_task_running(
            True,
            f"正在执行自动任务 #{task_id}…",
        )

        self.automation_worker = (
            AutomationWorker(
                self.automation_service,
                task_id,
            )
        )
        self.automation_worker.progress_changed.connect(
            self.automation_page
            .apply_task_progress
        )
        self.automation_worker.result_ready.connect(
            self.on_automation_result
        )
        self.automation_worker.error_occurred.connect(
            self.on_automation_error
        )
        self.automation_worker.finished.connect(
            self.on_automation_finished
        )
        self.automation_worker.start()

    def on_automation_result(
        self,
        result: dict,
    ):
        self.refresh_database_views()
        self.refresh_automation_views()

        status = result.get(
            "status"
        )

        if status == "success":
            QMessageBox.information(
                self,
                "自动任务完成",
                (
                    "分析、报告和已启用的后续动作均已完成。\n\n"
                    f"分析 ID：{result.get('analysis_run_id')}\n"
                    f"报告 ID：{result.get('report_id')}"
                ),
            )
        else:
            QMessageBox.warning(
                self,
                "自动任务部分完成",
                str(
                    result.get(
                        "message",
                        "",
                    )
                ),
            )

    def on_automation_error(
        self,
        message: str,
    ):
        self.refresh_automation_views()
        QMessageBox.critical(
            self,
            "自动任务失败",
            message,
        )

    def on_automation_finished(
        self,
    ):
        self.automation_page.set_task_running(
            False,
            "任务已结束，可查看下方运行记录。",
        )
        self.automation_worker = None

    # =========================================================
    # System / backup / onboarding
    # =========================================================

    def refresh_system_info(
        self,
    ):
        self.system_page.set_system_info(
            schema_version=(
                self.database
                .schema_version()
            ),
            database_path=str(
                DATABASE_FILE
            ),
            ui_mode=(
                self.config.ui_mode
            ),
            secret_persistent=(
                self.config
                .secret_store_is_persistent()
            ),
        )

    def backup_database(
        self,
    ):
        from datetime import datetime

        default_name = (
            "StockEventRadar-backup-"
            + datetime.now().strftime(
                "%Y%m%d-%H%M%S"
            )
            + ".db"
        )

        file_path, _ = (
            QFileDialog
            .getSaveFileName(
                self,
                "备份数据库",
                default_name,
                "SQLite 数据库 (*.db)",
            )
        )

        if not file_path:
            return

        if not file_path.lower().endswith(
            ".db"
        ):
            file_path += ".db"

        try:
            self.database.backup_database(
                Path(file_path)
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "备份失败",
                str(exc),
            )
            return

        QMessageBox.information(
            self,
            "备份完成",
            "数据库已经备份到：\n\n"
            f"{file_path}",
        )

    def restore_database(
        self,
    ):
        file_path, _ = (
            QFileDialog
            .getOpenFileName(
                self,
                "选择数据库备份",
                "",
                "SQLite 数据库 (*.db);;所有文件 (*.*)",
            )
        )

        if not file_path:
            return

        valid, message = (
            self.database
            .validate_database_file(
                Path(file_path)
            )
        )

        if not valid:
            QMessageBox.critical(
                self,
                "备份无效",
                message,
            )
            return

        answer = QMessageBox.warning(
            self,
            "确认恢复",
            "恢复会用备份内容替换当前本地数据库。\n\n"
            "建议先点击“备份数据库”保存当前数据。\n\n"
            "确定继续吗？",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if (
            answer
            != QMessageBox
            .StandardButton.Yes
        ):
            return

        try:
            self.database.restore_database(
                Path(file_path)
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "恢复失败",
                str(exc),
            )
            return

        self.refresh_database_views()
        self.refresh_system_info()

        QMessageBox.information(
            self,
            "恢复完成",
            "数据库已恢复，当前界面数据已经刷新。",
        )

    def open_data_directory(
        self,
    ):
        APP_DATA_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(APP_DATA_DIR)
            )
        )

    def open_logs_directory(
        self,
    ):
        LOG_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        QDesktopServices.openUrl(
            QUrl.fromLocalFile(
                str(LOG_DIR)
            )
        )

    def rerun_onboarding(
        self,
    ):
        wizard = FirstRunWizard(
            config=self.config,
            provider_manager=(
                self.provider_manager
            ),
            parent=self,
        )
        wizard.exec()

        # Wizard values are saved immediately and the next
        # analysis uses the updated config. The full AI settings
        # page will reflect them after the next app restart.
        self.refresh_system_info()

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
                self.config.research_provider,
            )
        )

        for provider_name, settings in (
            payload.get(
                "providers",
                {},
            ).items()
        ):
            self.config.update_provider_config(
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
                input_price_per_million=settings.get(
                    "input_price_per_million",
                    0.0,
                ),
                output_price_per_million=settings.get(
                    "output_price_per_million",
                    0.0,
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
                    self.config.save_api_key(
                        provider_name,
                        api_key,
                    )
                except Exception as exc:
                    QMessageBox.critical(
                        self,
                        "保存失败",
                        f"{provider_name} API Key 保存失败："
                        f"\n\n{exc}",
                    )
                    return

        self.config.save()
        self.settings_page.mark_saved()

        QMessageBox.information(
            self,
            "保存成功",
            "AI、模型与可选 Token 单价设置已保存。",
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
            or self.config.get_api_key(
                provider_name
            )
        )

        if not api_key:
            QMessageBox.warning(
                self,
                "缺少 API Key",
                f"请先输入 {provider_name} API Key。",
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
                "当前已有一个 Provider 正在进行连接测试。",
            )
            return

        self.connection_provider_name = (
            provider_name
        )

        self.settings_page.set_test_running(
            provider_name,
            True,
        )

        self.connection_worker = ConnectionWorker(
            provider_manager=self.provider_manager,
            provider_name=provider_name,
            api_key=api_key,
            model=model,
            base_url=base_url,
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

    def on_connection_success(
        self,
        result: str,
    ):
        name = (
            self.connection_provider_name
            or ""
        )

        if name:
            self.settings_page.show_test_success(
                name
            )

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
            self.settings_page.show_test_error(
                name
            )

        QMessageBox.critical(
            self,
            "连接失败",
            message,
        )

    def on_connection_finished(
        self,
    ):
        name = (
            self.connection_provider_name
            or ""
        )

        if name:
            self.settings_page.set_test_running(
                name,
                False,
            )

        self.connection_provider_name = None
        self.connection_worker = None
