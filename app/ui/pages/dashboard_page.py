from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
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

        self.sector_checkboxes: list[QCheckBox] = []
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 35, 50, 35)
        main_layout.setSpacing(18)

        title = QLabel("今日板块事件分析")
        title.setObjectName("pageTitle")

        description = QLabel(
            "联网搜索近期重大事件，并分析事件对A股板块的传导链路。"
        )
        description.setObjectName("pageDescription")

        main_layout.addWidget(title)
        main_layout.addWidget(description)

        sector_card = QFrame()
        sector_card.setObjectName("card")

        sector_layout = QVBoxLayout(sector_card)
        sector_layout.setContentsMargins(30, 22, 30, 22)
        sector_layout.setSpacing(13)

        sector_title = QLabel("分析板块")
        sector_title.setObjectName("cardTitle")
        sector_layout.addWidget(sector_title)

        for index in range(0, len(DEFAULT_SECTORS), 2):
            row = QHBoxLayout()

            for sector in DEFAULT_SECTORS[index:index + 2]:
                checkbox = QCheckBox(sector)
                checkbox.setChecked(True)
                self.sector_checkboxes.append(checkbox)
                row.addWidget(checkbox)

            row.addStretch()
            sector_layout.addLayout(row)

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
        self.analyze_button.setFixedHeight(46)
        self.analyze_button.clicked.connect(
            self._emit_analysis_request
        )

        button_row.addWidget(self.analyze_button)
        main_layout.addLayout(button_row)

        result_card = QFrame()
        result_card.setObjectName("card")

        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(25, 20, 25, 20)

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

    def selected_sectors(self) -> list[str]:
        return [
            checkbox.text()
            for checkbox in self.sector_checkboxes
            if checkbox.isChecked()
        ]

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
                        AI 正在联网搜索近期事件，
                        并建立板块传导链。
                    </p>
                    <p>
                        第一次可能需要几十秒。
                    </p>
                </div>
                """
            )
        else:
            self.analyze_button.setText("开始分析")

    def show_result(self, html_content: str):
        self.status_label.setText("分析完成")
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
