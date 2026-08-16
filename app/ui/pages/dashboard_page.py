from PySide6.QtCore import Qt, Signal

from app.platform import is_android
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


DEFAULT_SECTORS = [
    "黄金",
    "科创芯片",
    "通信",
    "军工 / 卫星",
    "化工",
    "有色金属",
    "白酒 / 食品饮料",
    "家电 / 汽车",
]


class DashboardPage(QWidget):
    analyze_requested = Signal(list)

    def __init__(self):
        super().__init__()

        self.custom_saved_sectors: list[str] = []
        self.session_custom_sectors: list[str] = []
        self.sector_checkboxes: list[QCheckBox] = []
        self.progress_rows: dict[str, int] = {}

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            14 if is_android() else 45,
            12 if is_android() else 25,
            14 if is_android() else 45,
            18 if is_android() else 25,
        )
        main_layout.setSpacing(
            10 if is_android() else 12
        )

        title = QLabel("今日板块事件分析")
        title.setObjectName("pageTitle")

        description = QLabel(
            "V1.0 会实时显示联网研究、每个模型、共识计算和 Judge 的实际任务状态。"
        )
        description.setObjectName("pageDescription")
        description.setWordWrap(True)

        main_layout.addWidget(title)
        main_layout.addWidget(description)

        # =====================================================
        # Sector selection
        # =====================================================
        sector_card = QFrame()
        sector_card.setObjectName("card")

        self.sector_layout = QVBoxLayout(sector_card)
        self.sector_layout.setContentsMargins(25, 16, 25, 16)
        self.sector_layout.setSpacing(10)

        sector_title = QLabel("分析板块")
        sector_title.setObjectName("cardTitle")
        self.sector_layout.addWidget(sector_title)

        self.checkbox_container = QVBoxLayout()
        self.sector_layout.addLayout(self.checkbox_container)
        self._rebuild_checkboxes()

        custom_row = (
            QVBoxLayout()
            if is_android()
            else QHBoxLayout()
        )

        self.custom_sector_input = QLineEdit()
        self.custom_sector_input.setPlaceholderText(
            "输入自定义板块，例如：生物医药、机器人、创新药"
        )
        self.custom_sector_input.returnPressed.connect(
            self.add_session_custom_sector
        )

        add_button = QPushButton("加入本次分析")
        add_button.setObjectName("secondaryButton")
        add_button.clicked.connect(
            self.add_session_custom_sector
        )

        custom_row.addWidget(
            self.custom_sector_input,
            1,
        )
        custom_row.addWidget(add_button)

        self.sector_layout.addLayout(custom_row)
        main_layout.addWidget(sector_card)

        # =====================================================
        # Start row
        # =====================================================
        button_row = (
            QVBoxLayout()
            if is_android()
            else QHBoxLayout()
        )

        self.status_label = QLabel("等待开始分析")
        self.status_label.setObjectName("statusLabel")
        button_row.addWidget(self.status_label)

        if not is_android():
            button_row.addStretch()

        self.analyze_button = QPushButton("开始分析")
        self.analyze_button.setObjectName("primaryButton")
        if is_android():
            self.analyze_button.setMinimumHeight(
                44
            )
        else:
            self.analyze_button.setFixedWidth(
                180
            )
            self.analyze_button.setFixedHeight(
                42
            )
        self.analyze_button.clicked.connect(
            self._emit_analysis_request
        )

        button_row.addWidget(self.analyze_button)
        main_layout.addLayout(button_row)

        # =====================================================
        # Live task monitor
        # =====================================================
        monitor_card = QFrame()
        monitor_card.setObjectName("card")

        monitor_layout = QVBoxLayout(monitor_card)
        monitor_layout.setContentsMargins(20, 14, 20, 14)
        monitor_layout.setSpacing(8)

        monitor_header = QHBoxLayout()

        monitor_title = QLabel("分析任务进度")
        monitor_title.setObjectName("cardTitle")

        self.progress_percent_label = QLabel("0%")
        self.progress_percent_label.setObjectName("statusLabel")

        monitor_header.addWidget(monitor_title)
        monitor_header.addStretch()
        monitor_header.addWidget(
            self.progress_percent_label
        )

        monitor_layout.addLayout(monitor_header)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        monitor_layout.addWidget(self.progress_bar)

        self.stage_label = QLabel(
            "尚未开始。这里显示的是任务阶段进度，不伪造模型内部思考百分比。"
        )
        self.stage_label.setWordWrap(True)
        self.stage_label.setObjectName("statusLabel")
        monitor_layout.addWidget(self.stage_label)

        self.progress_table = QTableWidget(0, 6)
        self.progress_table.setHorizontalHeaderLabels([
            "任务",
            "模型",
            "状态",
            "耗时",
            "Token",
            "估算成本*",
        ])
        self.progress_table.verticalHeader().setVisible(False)
        self.progress_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.progress_table.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection
        )
        self.progress_table.setMaximumHeight(
            220 if is_android() else 170
        )

        if is_android():
            # Mobile intentionally omits Token/cost columns.
            self.progress_table.setColumnHidden(
                4,
                True,
            )
            self.progress_table.setColumnHidden(
                5,
                True,
            )

        header = self.progress_table.horizontalHeader()

        if is_android():
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
            header.setSectionResizeMode(
                3,
                QHeaderView.ResizeMode.ResizeToContents,
            )
        else:
            header.setSectionResizeMode(
                0,
                QHeaderView.ResizeMode.ResizeToContents,
            )
            header.setSectionResizeMode(
                1,
                QHeaderView.ResizeMode.Stretch,
            )
            for column in range(2, 6):
                header.setSectionResizeMode(
                    column,
                    QHeaderView.ResizeMode.ResizeToContents,
                )

        monitor_layout.addWidget(self.progress_table)

        cost_hint = QLabel(
            "* 成本只在“AI 设置”填写每百万 Token 单价后估算；未配置时显示 —。"
        )
        cost_hint.setObjectName("statusLabel")
        if not is_android():
            monitor_layout.addWidget(
                cost_hint
            )

        main_layout.addWidget(monitor_card)

        # =====================================================
        # Result
        # =====================================================
        result_card = QFrame()
        result_card.setObjectName("card")

        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(22, 14, 22, 14)

        result_title = QLabel("分析结果")
        result_title.setObjectName("cardTitle")
        result_layout.addWidget(result_title)

        self.result_browser = QTextBrowser()
        self.result_browser.setOpenExternalLinks(True)

        if is_android():
            self.result_browser.setMinimumHeight(
                300
            )
        self.result_browser.setPlaceholderText(
            "分析完成后，Multi-AI 共识结果将显示在这里。"
        )
        result_layout.addWidget(self.result_browser)

        main_layout.addWidget(
            result_card,
            0 if is_android() else 1,
        )

    def set_mobile_mode(
        self,
        enabled: bool,
    ):
        if not enabled:
            return

        self.progress_table.setColumnHidden(
            4,
            True,
        )
        self.progress_table.setColumnHidden(
            5,
            True,
        )
        self.result_browser.setMinimumHeight(
            300
        )

    # =========================================================
    # Sector management
    # =========================================================

    def set_saved_custom_sectors(self, sectors: list[str]):
        current_checked = {
            checkbox.text()
            for checkbox in self.sector_checkboxes
            if checkbox.isChecked()
        }

        self.custom_saved_sectors = list(sectors)

        self._rebuild_checkboxes(
            checked_names=current_checked
        )

    def add_session_custom_sector(self):
        name = " ".join(
            self.custom_sector_input.text().strip().split()
        )

        if not name:
            return

        all_names = (
            DEFAULT_SECTORS
            + self.custom_saved_sectors
            + self.session_custom_sectors
        )

        if name.lower() in {
            item.lower()
            for item in all_names
        }:
            QMessageBox.information(
                self,
                "板块已存在",
                f"“{name}”已经在板块列表中。",
            )
            return

        self.session_custom_sectors.append(name)
        self.custom_sector_input.clear()

        current_checked = {
            checkbox.text()
            for checkbox in self.sector_checkboxes
            if checkbox.isChecked()
        }
        current_checked.add(name)

        self._rebuild_checkboxes(
            checked_names=current_checked
        )

    def selected_sectors(self) -> list[str]:
        return [
            checkbox.text()
            for checkbox in self.sector_checkboxes
            if checkbox.isChecked()
        ]

    def _rebuild_checkboxes(
        self,
        checked_names: set[str] | None = None,
    ):
        while self.checkbox_container.count():
            item = self.checkbox_container.takeAt(0)

            if item.layout():
                layout = item.layout()

                while layout.count():
                    child = layout.takeAt(0)

                    if child.widget():
                        child.widget().deleteLater()

        self.sector_checkboxes = []

        all_sectors = (
            DEFAULT_SECTORS
            + self.custom_saved_sectors
            + self.session_custom_sectors
        )

        seen = set()
        unique = []

        for sector in all_sectors:
            key = sector.lower()

            if key not in seen:
                seen.add(key)
                unique.append(sector)

        for index in range(0, len(unique), 2):
            row = QHBoxLayout()

            for sector in unique[index:index + 2]:
                checkbox = QCheckBox(sector)

                if checked_names is None:
                    checkbox.setChecked(True)
                else:
                    checkbox.setChecked(
                        sector in checked_names
                    )

                self.sector_checkboxes.append(
                    checkbox
                )
                row.addWidget(checkbox)

            row.addStretch()
            self.checkbox_container.addLayout(row)

    def _emit_analysis_request(self):
        self.analyze_requested.emit(
            self.selected_sectors()
        )

    # =========================================================
    # Progress monitor
    # =========================================================

    def prepare_progress(
        self,
        *,
        research_provider: str,
        analyst_names: list[str],
        judge_enabled: bool,
        judge_provider: str,
    ):
        self.progress_rows.clear()
        self.progress_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.progress_percent_label.setText("0%")
        self.stage_label.setText(
            "任务已创建，准备开始。"
        )

        self._ensure_progress_row(
            key=f"research:{research_provider}",
            task="联网研究",
            provider=research_provider,
        )

        for provider in analyst_names:
            self._ensure_progress_row(
                key=f"analysis:{provider}",
                task="独立分析",
                provider=provider,
            )

        if judge_enabled:
            self._ensure_progress_row(
                key=f"judge:{judge_provider}",
                task="Judge",
                provider=judge_provider,
            )

    def _ensure_progress_row(
        self,
        *,
        key: str,
        task: str,
        provider: str,
    ) -> int:
        if key in self.progress_rows:
            return self.progress_rows[key]

        row = self.progress_table.rowCount()
        self.progress_table.insertRow(row)

        values = [
            task,
            provider,
            "等待",
            "—",
            "—",
            "—",
        ]

        for column, value in enumerate(values):
            self.progress_table.setItem(
                row,
                column,
                QTableWidgetItem(value),
            )

        self.progress_rows[key] = row
        return row

    def apply_progress(self, event: dict):
        percent = int(
            event.get(
                "percent",
                self.progress_bar.value(),
            )
        )
        percent = max(0, min(100, percent))

        self.progress_bar.setValue(percent)
        self.progress_percent_label.setText(
            f"{percent}%"
        )

        message = str(
            event.get(
                "message",
                "",
            )
        ).strip()

        if message:
            self.stage_label.setText(message)
            self.status_label.setText(message)

        stage = str(
            event.get(
                "stage",
                "",
            )
        )
        provider = str(
            event.get(
                "provider",
                "",
            )
        )
        status = str(
            event.get(
                "status",
                "",
            )
        )

        if not provider or stage not in {
            "research",
            "analysis",
            "judge",
        }:
            return

        task_names = {
            "research": "联网研究",
            "analysis": "独立分析",
            "judge": "Judge",
        }

        key = f"{stage}:{provider}"

        row = self._ensure_progress_row(
            key=key,
            task=task_names[stage],
            provider=provider,
        )

        status_text = {
            "running": "进行中…",
            "success": "✓ 完成",
            "error": "✕ 失败",
            "skipped": "— 跳过",
        }.get(
            status,
            status or "等待",
        )

        self._set_cell(
            row,
            2,
            status_text,
        )

        duration_ms = event.get(
            "duration_ms"
        )

        if duration_ms is not None:
            try:
                duration_seconds = (
                    float(duration_ms)
                    / 1000
                )
                self._set_cell(
                    row,
                    3,
                    f"{duration_seconds:.1f}s",
                )
            except Exception:
                pass

        total_tokens = event.get(
            "total_tokens"
        )

        if total_tokens is not None:
            try:
                total_tokens = int(
                    total_tokens
                )

                if total_tokens > 0:
                    self._set_cell(
                        row,
                        4,
                        f"{total_tokens:,}",
                    )
            except Exception:
                pass

        if "estimated_cost" in event:
            cost = event.get(
                "estimated_cost"
            )

            if cost is None:
                self._set_cell(
                    row,
                    5,
                    "—",
                )
            else:
                try:
                    self._set_cell(
                        row,
                        5,
                        f"{float(cost):.6f}",
                    )
                except Exception:
                    pass

    def mark_saved(self):
        self.progress_bar.setValue(100)
        self.progress_percent_label.setText(
            "100%"
        )
        self.stage_label.setText(
            "分析完成，结果已写入 SQLite。"
        )
        self.status_label.setText(
            "分析完成并已保存到历史"
        )

    def _set_cell(
        self,
        row: int,
        column: int,
        text: str,
    ):
        item = self.progress_table.item(
            row,
            column,
        )

        if item is None:
            item = QTableWidgetItem()
            self.progress_table.setItem(
                row,
                column,
                item,
            )

        item.setText(text)

    # =========================================================
    # Running/result
    # =========================================================

    def set_running(self, running: bool):
        self.analyze_button.setEnabled(
            not running
        )
        self.analyze_button.setText(
            "分析中..."
            if running
            else "开始分析"
        )

        if running:
            self.result_browser.setHtml(
                """
                <div style="padding:15px;">
                    <h3>Multi-AI 分析进行中</h3>
                    <p>
                        上方会实时显示每个可观察阶段的状态。
                        模型内部推理过程无法获得真实百分比，因此不会伪造。
                    </p>
                </div>
                """
            )

    def show_result(
        self,
        html_content: str,
    ):
        self.result_browser.setHtml(
            html_content
        )

    def show_error(self, message: str):
        import html

        self.status_label.setText(
            "分析失败"
        )

        self.result_browser.setHtml(
            f"""
            <div style="padding:20px;">
                <h3 style="color:#b91c1c;">分析失败</h3>
                <p>{html.escape(message)}</p>
            </div>
            """
        )
