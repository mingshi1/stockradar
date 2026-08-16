from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QTime, QTimer, Qt, Signal
from app.platform import is_android

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)


DEFAULT_SECTORS = [
    "黄金",
    "科创芯片",
    "通信",
    "军工/卫星",
    "化工",
    "有色金属",
    "白酒/食品饮料",
    "家电/汽车",
]


class AutomationPage(QWidget):
    sync_time_requested = Signal()
    save_task_requested = Signal(object)
    delete_task_requested = Signal(int)
    run_task_requested = Signal(int)
    refresh_requested = Signal()

    def __init__(self):
        super().__init__()

        self._tasks: dict[int, dict] = {}
        self._selected_task_id: int | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        if is_android():
            scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

        body = QWidget()
        self.layout = QVBoxLayout(body)
        self.layout.setContentsMargins(
            12 if is_android() else 28,
            12 if is_android() else 24,
            12 if is_android() else 28,
            18 if is_android() else 28,
        )
        self.layout.setSpacing(
            12 if is_android() else 18
        )

        title = QLabel("自动任务中心")
        title.setStyleSheet(
            (
                "font-size:20px;font-weight:700;"
                if is_android()
                else "font-size:24px;font-weight:700;"
            )
        )

        subtitle = QLabel(
            (
                "配置并测试自动分析任务。联网失败时会等待 5 分钟后"
                "自动重试 1 次。Android Beta 的系统级后台调度仍受"
                "系统后台限制。"
            )
            if is_android()
            else (
                "每天自动执行板块研究、生成报告，并保存到你指定的目录。"
                " Windows 使用系统任务计划程序，因此主界面无需一直打开。"
            )
        )
        subtitle.setWordWrap(True)

        self.layout.addWidget(title)
        self.layout.addWidget(subtitle)

        self._build_time_group()
        self._build_task_group()
        self._build_task_list()
        self._build_run_history()

        self.layout.addStretch()
        scroll.setWidget(body)
        outer.addWidget(scroll)

        self.timer = QTimer(self)
        self.timer.timeout.connect(
            self._tick_clock
        )
        self.timer.start(1000)
        self._tick_clock()

    # ---------------------------------------------------------
    # Time
    # ---------------------------------------------------------

    def _build_time_group(self):
        group = QGroupBox("时间与时区")
        layout = (
            QVBoxLayout(group)
            if is_android()
            else QHBoxLayout(group)
        )

        self.clock_label = QLabel()
        self.clock_label.setStyleSheet(
            "font-size:18px;font-weight:600;"
        )

        self.timezone_label = QLabel()
        self.timezone_label.setWordWrap(True)

        text_box = QVBoxLayout()
        text_box.addWidget(self.clock_label)
        text_box.addWidget(self.timezone_label)

        self.sync_button = QPushButton(
            "同步 Windows 时间"
        )
        self.sync_button.clicked.connect(
            self.sync_time_requested.emit
        )
        self.sync_button.setVisible(
            not is_android()
        )

        layout.addLayout(text_box, 1)
        layout.addWidget(self.sync_button)

        self.layout.addWidget(group)

    def _tick_clock(self):
        now = datetime.now().astimezone()

        self.clock_label.setText(
            now.strftime("%Y-%m-%d %H:%M:%S")
        )
        self.timezone_label.setText(
            f"时区：{now.tzinfo}　UTC 偏移：{now.strftime('%z')}"
        )

    def set_sync_running(
        self,
        running: bool,
    ):
        self.sync_button.setEnabled(
            not running
        )
        self.sync_button.setText(
            "正在同步…"
            if running
            else "同步 Windows 时间"
        )

    # ---------------------------------------------------------
    # Task editor
    # ---------------------------------------------------------

    def _build_task_group(self):
        group = QGroupBox(
            "每日任务设置"
        )
        form = QFormLayout(group)

        if is_android():
            form.setRowWrapPolicy(
                QFormLayout.RowWrapPolicy.WrapAllRows
            )
            form.setFieldGrowthPolicy(
                QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
            )
            form.setHorizontalSpacing(
                6
            )
            form.setVerticalSpacing(
                8
            )

        self.task_name = QLineEdit(
            "每日晨报"
        )

        self.task_enabled = QCheckBox(
            (
                "启用任务"
                if is_android()
                else "启用 Windows 每日计划任务"
            )
        )
        self.task_enabled.setChecked(True)

        self.run_time = QTimeEdit()
        self.run_time.setDisplayFormat(
            "HH:mm"
        )
        self.run_time.setTime(
            QTime(7, 30)
        )

        self.analysis_mode = QComboBox()
        self.analysis_mode.addItem(
            "跟随当前 AI 设置",
            "current",
        )
        self.analysis_mode.addItem(
            "单模型",
            "single",
        )
        self.analysis_mode.addItem(
            "Multi-AI",
            "multi",
        )

        self.report_type = QComboBox()
        self.report_type.addItem(
            "30秒晨报",
            "morning",
        )
        self.report_type.addItem(
            "标准报告",
            "standard",
        )
        self.report_type.addItem(
            "Multi-AI共识报告",
            "consensus",
        )
        self.report_type.addItem(
            "深度研究报告",
            "deep",
        )

        self.sectors_edit = QPlainTextEdit()
        self.sectors_edit.setPlaceholderText(
            "每行一个板块，或用逗号分隔"
        )
        self.sectors_edit.setMaximumHeight(
            125
        )
        self.sectors_edit.setPlainText(
            "\n".join(DEFAULT_SECTORS)
        )

        self.generate_pdf = QCheckBox(
            "自动生成 PDF"
        )
        self.generate_pdf.setChecked(True)

        self.report_directory = QLineEdit()
        self.report_directory.setPlaceholderText(
            "留空使用默认目录；也可以选择 D 盘或其它文件夹"
        )

        self.choose_report_directory = QPushButton(
            "选择目录"
        )
        self.choose_report_directory.clicked.connect(
            self._choose_report_directory
        )

        report_dir_row = QWidget()
        report_dir_layout = (
            QVBoxLayout(
                report_dir_row
            )
            if is_android()
            else QHBoxLayout(
                report_dir_row
            )
        )
        report_dir_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        report_dir_layout.addWidget(
            self.report_directory,
            1,
        )
        report_dir_layout.addWidget(
            self.choose_report_directory,
        )

        form.addRow(
            "任务名称",
            self.task_name,
        )
        form.addRow(
            "任务状态",
            self.task_enabled,
        )
        form.addRow(
            "每日时间",
            self.run_time,
        )
        form.addRow(
            "分析模式",
            self.analysis_mode,
        )
        form.addRow(
            "报告类型",
            self.report_type,
        )
        form.addRow(
            "分析板块",
            self.sectors_edit,
        )
        form.addRow(
            "报告文件",
            self.generate_pdf,
        )
        if not is_android():
            form.addRow(
                "报告保存目录",
                report_dir_row,
            )

        buttons = (
            QGridLayout()
            if is_android()
            else QHBoxLayout()
        )

        self.new_task_button = QPushButton(
            "新建任务"
        )
        self.save_task_button = QPushButton(
            "保存任务"
        )

        self.new_task_button.clicked.connect(
            self.clear_task_editor
        )
        self.save_task_button.clicked.connect(
            self._emit_save_task
        )

        if is_android():
            buttons.addWidget(
                self.new_task_button,
                0,
                0,
            )
            buttons.addWidget(
                self.save_task_button,
                0,
                1,
            )
        else:
            buttons.addWidget(
                self.new_task_button
            )
            buttons.addWidget(
                self.save_task_button
            )
            buttons.addStretch()

        form.addRow("", buttons)

        self.save_feedback = QLabel()
        self.save_feedback.setObjectName(
            "statusLabel"
        )
        self.save_feedback.setWordWrap(
            True
        )
        self.save_feedback.setVisible(
            False
        )

        form.addRow(
            "",
            self.save_feedback,
        )

        self.layout.addWidget(group)

    def _emit_save_task(self):
        self.set_save_feedback(
            "正在保存任务…",
            success=None,
        )

        name = self.task_name.text().strip()
        sectors = self._parse_sectors(
            self.sectors_edit.toPlainText()
        )

        payload = {
            "id": self._selected_task_id,
            "name": name or "每日任务",
            "enabled": (
                self.task_enabled.isChecked()
            ),
            "run_time": (
                self.run_time.time().toString(
                    "HH:mm"
                )
            ),
            "sectors": sectors,
            "analysis_mode": (
                self.analysis_mode.currentData()
            ),
            "report_type": (
                self.report_type.currentData()
            ),
            "generate_pdf": (
                self.generate_pdf.isChecked()
            ),
            "report_directory": (
                self.report_directory.text().strip()
            ),
        }

        self.save_task_requested.emit(
            payload
        )

    def _choose_report_directory(
        self,
    ):
        start = (
            self.report_directory.text().strip()
            or ""
        )

        directory = (
            QFileDialog.getExistingDirectory(
                self,
                "选择每日自动报告保存目录",
                start,
            )
        )

        if directory:
            self.report_directory.setText(
                directory
            )

    @staticmethod
    def _parse_sectors(
        value: str,
    ) -> list[str]:
        normalized = (
            value
            .replace("，", ",")
            .replace("；", ",")
            .replace(";", ",")
            .replace("\n", ",")
        )

        result = []

        for item in normalized.split(","):
            sector = item.strip()

            if sector and sector not in result:
                result.append(sector)

        return result

    def clear_task_editor(self):
        self._selected_task_id = None

        if hasattr(
            self,
            "save_feedback",
        ):
            self.set_save_feedback(
                "",
                success=None,
            )
        self.task_name.setText(
            "每日晨报"
        )
        self.task_enabled.setChecked(True)
        self.run_time.setTime(
            QTime(7, 30)
        )
        self.analysis_mode.setCurrentIndex(0)
        self.report_type.setCurrentIndex(0)
        self.sectors_edit.setPlainText(
            "\n".join(DEFAULT_SECTORS)
        )
        self.generate_pdf.setChecked(True)
        self.report_directory.clear()

    @staticmethod
    def _display_status(
        value,
    ) -> str:
        raw = str(
            value or "-"
        ).strip()

        mapping = {
            "running": "运行中",
            "success": "成功",
            "failed": "失败",
            "waiting": "等待重试",
            "partial": "部分完成",
        }

        return mapping.get(
            raw.lower(),
            raw,
        )

    # ---------------------------------------------------------
    # Tasks table
    # ---------------------------------------------------------

    def _build_task_list(self):
        group = QGroupBox(
            "已保存任务"
        )
        layout = QVBoxLayout(group)

        self.task_table = QTableWidget(
            0,
            6,
        )
        self.task_table.setHorizontalHeaderLabels([
            "ID",
            "名称",
            "时间",
            "状态",
            "最近运行",
            "最近结果",
        ])
        self.task_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.task_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.task_table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )
        self.task_table.itemSelectionChanged.connect(
            self._load_selected_task
        )

        if is_android():
            self.task_table.verticalHeader().setVisible(
                False
            )
            self.task_table.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.task_table.setMinimumHeight(
                180
            )
            self.task_table.setMaximumHeight(
                270
            )

            # Hide desktop-only bookkeeping columns.
            self.task_table.setColumnHidden(
                0,
                True,
            )
            self.task_table.setColumnHidden(
                4,
                True,
            )

            header = self.task_table.horizontalHeader()
            header.setSectionResizeMode(
                1,
                QHeaderView.ResizeMode.Stretch,
            )
            header.setSectionResizeMode(
                2,
                QHeaderView.ResizeMode.ResizeToContents,
            )
            header.setSectionResizeMode(
                3,
                QHeaderView.ResizeMode.ResizeToContents,
            )
            header.setSectionResizeMode(
                5,
                QHeaderView.ResizeMode.ResizeToContents,
            )

        buttons = (
            QGridLayout()
            if is_android()
            else QHBoxLayout()
        )

        self.run_now_button = QPushButton(
            "立即执行"
        )
        self.delete_button = QPushButton(
            "删除任务"
        )
        self.refresh_button = QPushButton(
            "刷新"
        )

        self.run_now_button.clicked.connect(
            self._emit_run_selected
        )
        self.delete_button.clicked.connect(
            self._emit_delete_selected
        )
        self.refresh_button.clicked.connect(
            self.refresh_requested.emit
        )

        if is_android():
            buttons.addWidget(
                self.run_now_button,
                0,
                0,
            )
            buttons.addWidget(
                self.delete_button,
                0,
                1,
            )
            buttons.addWidget(
                self.refresh_button,
                1,
                0,
                1,
                2,
            )
        else:
            buttons.addWidget(
                self.run_now_button
            )
            buttons.addWidget(
                self.delete_button
            )
            buttons.addWidget(
                self.refresh_button
            )
            buttons.addStretch()

        layout.addWidget(
            self.task_table
        )
        layout.addLayout(buttons)

        self.task_status = QLabel()
        self.task_status.setWordWrap(True)
        layout.addWidget(
            self.task_status
        )

        self.layout.addWidget(group)

    def set_tasks(
        self,
        tasks: list[dict],
    ):
        self._tasks = {
            int(item["id"]): item
            for item in tasks
        }

        self.task_table.setRowCount(
            len(tasks)
        )

        for row, task in enumerate(tasks):
            values = [
                str(task["id"]),
                str(task["name"]),
                str(task["run_time"]),
                (
                    "已启用"
                    if task["enabled"]
                    else "已停用"
                ),
                str(
                    task.get("last_run_at")
                    or "-"
                ),
                self._display_status(
                    task.get("last_status")
                ),
            ]

            for col, value in enumerate(values):
                self.task_table.setItem(
                    row,
                    col,
                    QTableWidgetItem(value),
                )

    def _selected_id(
        self,
    ) -> int | None:
        row = self.task_table.currentRow()

        if row < 0:
            return None

        item = self.task_table.item(
            row,
            0,
        )

        if item is None:
            return None

        try:
            return int(item.text())
        except Exception:
            return None

    def _load_selected_task(self):
        task_id = self._selected_id()

        if task_id is None:
            return

        task = self._tasks.get(
            task_id
        )

        if not task:
            return

        self._selected_task_id = task_id
        self.task_name.setText(
            str(task["name"])
        )
        self.task_enabled.setChecked(
            bool(task["enabled"])
        )

        parsed = QTime.fromString(
            str(task["run_time"]),
            "HH:mm",
        )

        if parsed.isValid():
            self.run_time.setTime(parsed)

        index = self.analysis_mode.findData(
            task["analysis_mode"]
        )
        if index >= 0:
            self.analysis_mode.setCurrentIndex(
                index
            )

        index = self.report_type.findData(
            task["report_type"]
        )
        if index >= 0:
            self.report_type.setCurrentIndex(
                index
            )

        self.sectors_edit.setPlainText(
            "\n".join(
                task.get(
                    "sectors",
                    [],
                )
            )
        )
        self.generate_pdf.setChecked(
            bool(task["generate_pdf"])
        )
        self.report_directory.setText(
            str(
                task.get(
                    "report_directory",
                    "",
                )
            )
        )

    def _emit_run_selected(self):
        task_id = self._selected_id()

        if task_id is not None:
            self.run_task_requested.emit(
                task_id
            )

    def _emit_delete_selected(self):
        task_id = self._selected_id()

        if task_id is not None:
            self.delete_task_requested.emit(
                task_id
            )

    def set_task_running(
        self,
        running: bool,
        message: str = "",
    ):
        # Prevent starting a second execution, but keep editing/saving
        # available while the current task runs or waits for retry.
        self.run_now_button.setEnabled(
            not running
        )

        self.save_task_button.setEnabled(
            True
        )
        self.new_task_button.setEnabled(
            True
        )

        if message:
            self.task_status.setText(
                message
            )

    def set_save_feedback(
        self,
        message: str,
        *,
        success: bool | None = None,
    ):
        text = str(
            message or ""
        ).strip()

        self.save_feedback.setText(
            text
        )
        self.save_feedback.setVisible(
            bool(text)
        )

        if success is True:
            self.save_feedback.setStyleSheet(
                "color:#15803d;font-weight:600;"
            )
        elif success is False:
            self.save_feedback.setStyleSheet(
                "color:#b91c1c;font-weight:600;"
            )
        else:
            self.save_feedback.setStyleSheet(
                ""
            )

    def apply_task_progress(
        self,
        event: dict,
    ):
        message = str(
            event.get("message", "")
        ).strip()

        if message:
            self.task_status.setText(
                message
            )

    # ---------------------------------------------------------
    # Task run history
    # ---------------------------------------------------------

    def _build_run_history(self):
        group = QGroupBox(
            "最近自动运行记录"
        )
        layout = QVBoxLayout(group)

        self.run_table = QTableWidget(
            0,
            6,
        )
        self.run_table.setHorizontalHeaderLabels([
            "时间",
            "任务",
            "结果",
            "分析ID",
            "报告ID",
            "错误",
        ])
        self.run_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.run_table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )
        self.run_table.horizontalHeader().setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.Stretch,
        )

        if is_android():
            self.run_table.verticalHeader().setVisible(
                False
            )
            self.run_table.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self.run_table.setMinimumHeight(
                190
            )
            self.run_table.setMaximumHeight(
                300
            )

            # Mobile summary: time / task / result only.
            for column in (
                3,
                4,
                5,
            ):
                self.run_table.setColumnHidden(
                    column,
                    True,
                )

            header = self.run_table.horizontalHeader()
            header.setSectionResizeMode(
                0,
                QHeaderView.ResizeMode.ResizeToContents,
            )
            header.setSectionResizeMode(
                1,
                QHeaderView.ResizeMode.Stretch,
            )
            header.setSectionResizeMode(
                2,
                QHeaderView.ResizeMode.ResizeToContents,
            )

        layout.addWidget(
            self.run_table
        )
        self.layout.addWidget(group)

    def set_task_runs(
        self,
        runs: list[dict],
    ):
        self.run_table.setRowCount(
            len(runs)
        )

        for row, item in enumerate(runs):
            values = [
                str(
                    item.get(
                        "started_at",
                        "",
                    )
                ),
                str(
                    item.get(
                        "task_name",
                        "",
                    )
                ),
                self._display_status(
                    item.get(
                        "status",
                        "",
                    )
                ),
                str(
                    item.get(
                        "analysis_run_id",
                        "",
                    )
                    or "-"
                ),
                str(
                    item.get(
                        "report_id",
                        "",
                    )
                    or "-"
                ),
                str(
                    item.get(
                        "error",
                        "",
                    )
                    or ""
                ),
            ]

            for col, value in enumerate(values):
                self.run_table.setItem(
                    row,
                    col,
                    QTableWidgetItem(value),
                )
