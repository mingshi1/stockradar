from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
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

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 30, 50, 30)
        main_layout.setSpacing(15)

        title = QLabel("今日板块事件分析")
        title.setObjectName("pageTitle")

        description = QLabel(
            "选择默认板块，也可以输入任意自定义A股主题，例如“生物医药”。"
        )
        description.setObjectName("pageDescription")

        main_layout.addWidget(title)
        main_layout.addWidget(description)

        sector_card = QFrame()
        sector_card.setObjectName("card")

        self.sector_layout = QVBoxLayout(sector_card)
        self.sector_layout.setContentsMargins(30, 20, 30, 20)
        self.sector_layout.setSpacing(12)

        sector_title = QLabel("分析板块")
        sector_title.setObjectName("cardTitle")
        self.sector_layout.addWidget(sector_title)

        self.checkbox_container = QVBoxLayout()
        self.sector_layout.addLayout(self.checkbox_container)

        self._rebuild_checkboxes()

        custom_row = QHBoxLayout()

        self.custom_sector_input = QLineEdit()
        self.custom_sector_input.setPlaceholderText(
            "输入自定义板块，例如：生物医药、机器人、创新药"
        )
        self.custom_sector_input.returnPressed.connect(
            self.add_session_custom_sector
        )

        add_button = QPushButton("加入本次分析")
        add_button.setObjectName("secondaryButton")
        add_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        add_button.clicked.connect(
            self.add_session_custom_sector
        )

        custom_row.addWidget(self.custom_sector_input, 1)
        custom_row.addWidget(add_button)

        self.sector_layout.addLayout(custom_row)

        self.custom_hint = QLabel(
            "临时加入的板块仅用于当前程序会话；"
            "需要长期保存请到“板块管理”。"
        )
        self.custom_hint.setObjectName("statusLabel")
        self.sector_layout.addWidget(self.custom_hint)

        main_layout.addWidget(sector_card)

        button_row = QHBoxLayout()

        self.status_label = QLabel("等待开始分析")
        self.status_label.setObjectName("statusLabel")
        button_row.addWidget(self.status_label)

        button_row.addStretch()

        self.analyze_button = QPushButton("开始分析")
        self.analyze_button.setObjectName("primaryButton")
        self.analyze_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.analyze_button.setFixedWidth(180)
        self.analyze_button.setFixedHeight(44)
        self.analyze_button.clicked.connect(
            self._emit_analysis_request
        )

        button_row.addWidget(self.analyze_button)
        main_layout.addLayout(button_row)

        result_card = QFrame()
        result_card.setObjectName("card")

        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(25, 18, 25, 18)

        result_title = QLabel("分析结果")
        result_title.setObjectName("cardTitle")
        result_layout.addWidget(result_title)

        self.result_browser = QTextBrowser()
        self.result_browser.setOpenExternalLinks(True)
        self.result_browser.setPlaceholderText(
            "点击“开始分析”后，结果将显示在这里。"
        )
        result_layout.addWidget(self.result_browser)

        main_layout.addWidget(result_card, 1)

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

                self.sector_checkboxes.append(checkbox)
                row.addWidget(checkbox)

            row.addStretch()
            self.checkbox_container.addLayout(row)

    def _emit_analysis_request(self):
        self.analyze_requested.emit(
            self.selected_sectors()
        )

    def set_running(self, running: bool):
        self.analyze_button.setEnabled(not running)

        if running:
            self.analyze_button.setText("分析中...")
            self.status_label.setText(
                "正在联网搜索近期事件，请稍候..."
            )
            self.result_browser.setHtml(
                """
                <div style="padding:20px;">
                    <h3>正在分析...</h3>
                    <p>
                        AI 正在联网搜索近期事件并建立传导链。
                    </p>
                </div>
                """
            )
        else:
            self.analyze_button.setText("开始分析")

    def show_result(self, html_content: str):
        self.status_label.setText(
            "分析完成并已保存到历史"
        )
        self.result_browser.setHtml(html_content)

    def show_error(self, message: str):
        import html

        self.status_label.setText("分析失败")
        self.result_browser.setHtml(
            f"""
            <div style="padding:20px;">
                <h3 style="color:#b91c1c;">分析失败</h3>
                <p>{html.escape(message)}</p>
            </div>
            """
        )
