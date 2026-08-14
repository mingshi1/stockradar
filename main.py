import sys
import html

from PySide6.QtCore import (
    Qt,
    QThread,
    Signal,
)

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from app.config import AppConfig

from app.ai.deepseek_client import (
    test_connection,
)

from app.ai.analysis_service import (
    analyze_sectors,
)


# =============================================================
# AI 后台线程
# =============================================================

class AnalysisWorker(QThread):

    result_ready = Signal(dict)
    error_occurred = Signal(str)

    def __init__(
        self,
        api_key,
        model,
        sectors,
    ):
        super().__init__()

        self.api_key = api_key
        self.model = model
        self.sectors = sectors

    def run(self):
        try:
            result = analyze_sectors(
                api_key=self.api_key,
                model=self.model,
                sectors=self.sectors,
            )

            self.result_ready.emit(result)

        except Exception as exc:
            self.error_occurred.emit(
                str(exc)
            )


# =============================================================
# 主窗口
# =============================================================

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # 配置
        self.config = AppConfig()

        # 后台线程
        self.analysis_worker = None

        # =====================================================
        # 主窗口
        # =====================================================

        self.setWindowTitle(
            "AI板块事件雷达"
        )

        self.resize(
            1200,
            760
        )

        self.setMinimumSize(
            950,
            600
        )

        root_widget = QWidget()

        self.setCentralWidget(
            root_widget
        )

        root_layout = QHBoxLayout(
            root_widget
        )

        root_layout.setContentsMargins(
            0, 0, 0, 0
        )

        root_layout.setSpacing(0)

        # 左侧导航
        sidebar = self.create_sidebar()

        # 页面栈
        self.pages = QStackedWidget()

        self.dashboard_page = (
            self.create_dashboard_page()
        )

        self.history_page = (
            self.create_placeholder_page(
                "历史报告",
                "以后这里会显示每次生成的 AI 分析报告。"
            )
        )

        self.sector_page = (
            self.create_placeholder_page(
                "板块管理",
                "以后可以在这里新增、删除和编辑板块。"
            )
        )

        self.news_page = (
            self.create_placeholder_page(
                "新闻源",
                "以后可以在这里查看搜索到的原始事件与新闻来源。"
            )
        )

        self.settings_page = (
            self.create_settings_page()
        )

        self.pages.addWidget(
            self.dashboard_page
        )

        self.pages.addWidget(
            self.history_page
        )

        self.pages.addWidget(
            self.sector_page
        )

        self.pages.addWidget(
            self.news_page
        )

        self.pages.addWidget(
            self.settings_page
        )

        root_layout.addWidget(
            sidebar
        )

        root_layout.addWidget(
            self.pages,
            1
        )

        self.pages.setCurrentIndex(0)

        self.apply_styles()

    # =========================================================
    # 左侧导航栏
    # =========================================================

    def create_sidebar(self):

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
            25
        )

        layout.setSpacing(10)

        title = QLabel(
            "AI板块事件雷达"
        )

        title.setObjectName(
            "sidebarTitle"
        )

        subtitle = QLabel(
            "Event Radar"
        )

        subtitle.setObjectName(
            "sidebarSubtitle"
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        self.nav_buttons = []

        nav_items = [
            ("今日分析", 0),
            ("历史报告", 1),
            ("板块管理", 2),
            ("新闻源", 3),
            ("设置", 4),
        ]

        for text, index in nav_items:

            button = QPushButton(text)

            button.setObjectName(
                "navButton"
            )

            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            button.clicked.connect(
                lambda checked=False, i=index:
                self.switch_page(i)
            )

            layout.addWidget(button)

            self.nav_buttons.append(
                button
            )

        layout.addStretch()

        version = QLabel(
            "v0.3.0"
        )

        version.setObjectName(
            "versionLabel"
        )

        layout.addWidget(version)

        return sidebar

    # =========================================================
    # 今日分析页面
    # =========================================================

    def create_dashboard_page(self):

        page = QWidget()

        main_layout = QVBoxLayout(
            page
        )

        main_layout.setContentsMargins(
            50,
            35,
            50,
            35
        )

        main_layout.setSpacing(18)

        # 标题
        title = QLabel(
            "今日板块事件分析"
        )

        title.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "联网搜索近期重大事件，并分析事件对A股板块的传导链路。"
        )

        description.setObjectName(
            "pageDescription"
        )

        main_layout.addWidget(title)

        main_layout.addWidget(
            description
        )

        # =====================================================
        # 板块选择
        # =====================================================

        sector_card = QFrame()

        sector_card.setObjectName(
            "card"
        )

        sector_layout = QVBoxLayout(
            sector_card
        )

        sector_layout.setContentsMargins(
            30,
            22,
            30,
            22
        )

        sector_layout.setSpacing(13)

        sector_title = QLabel(
            "分析板块"
        )

        sector_title.setObjectName(
            "cardTitle"
        )

        sector_layout.addWidget(
            sector_title
        )

        sectors = [
            "黄金",
            "科创芯片",
            "通信",
            "军工 / 卫星",
            "化工",
            "有色金属",
            "白酒 / 食品饮料",
            "家电 / 汽车",
        ]

        self.sector_checkboxes = []

        for i in range(
            0,
            len(sectors),
            2
        ):

            row = QHBoxLayout()

            for sector in sectors[
                i:i + 2
            ]:

                checkbox = QCheckBox(
                    sector
                )

                checkbox.setChecked(
                    True
                )

                self.sector_checkboxes.append(
                    checkbox
                )

                row.addWidget(
                    checkbox
                )

            row.addStretch()

            sector_layout.addLayout(
                row
            )

        main_layout.addWidget(
            sector_card
        )

        # =====================================================
        # 按钮
        # =====================================================

        button_row = QHBoxLayout()

        self.status_label = QLabel(
            "等待开始分析"
        )

        self.status_label.setObjectName(
            "statusLabel"
        )

        button_row.addWidget(
            self.status_label
        )

        button_row.addStretch()

        self.analyze_button = QPushButton(
            "开始分析"
        )

        self.analyze_button.setObjectName(
            "primaryButton"
        )

        self.analyze_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.analyze_button.setFixedWidth(
            180
        )

        self.analyze_button.setFixedHeight(
            46
        )

        self.analyze_button.clicked.connect(
            self.start_analysis
        )

        button_row.addWidget(
            self.analyze_button
        )

        main_layout.addLayout(
            button_row
        )

        # =====================================================
        # 分析结果
        # =====================================================

        result_card = QFrame()

        result_card.setObjectName(
            "card"
        )

        result_layout = QVBoxLayout(
            result_card
        )

        result_layout.setContentsMargins(
            25,
            20,
            25,
            20
        )

        result_title = QLabel(
            "分析结果"
        )

        result_title.setObjectName(
            "cardTitle"
        )

        result_layout.addWidget(
            result_title
        )

        self.result_browser = (
            QTextBrowser()
        )

        self.result_browser.setOpenExternalLinks(
            True
        )

        self.result_browser.setPlaceholderText(
            "点击“开始分析”后，结果将显示在这里。"
        )

        result_layout.addWidget(
            self.result_browser
        )

        main_layout.addWidget(
            result_card,
            1
        )

        return page

    # =========================================================
    # 设置页面
    # =========================================================

    def create_settings_page(self):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            50,
            40,
            50,
            40
        )

        layout.setSpacing(20)

        title = QLabel(
            "设置"
        )

        title.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "配置 AI 服务、API Key 和分析模型。"
        )

        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(title)

        layout.addWidget(
            description
        )

        api_card = QFrame()

        api_card.setObjectName(
            "card"
        )

        card_layout = QVBoxLayout(
            api_card
        )

        card_layout.setContentsMargins(
            30,
            25,
            30,
            25
        )

        card_layout.setSpacing(14)

        api_title = QLabel(
            "AI 服务"
        )

        api_title.setObjectName(
            "cardTitle"
        )

        card_layout.addWidget(
            api_title
        )

        # Provider
        provider_label = QLabel(
            "AI Provider"
        )

        self.provider_combo = (
            QComboBox()
        )

        self.provider_combo.addItems([
            "DeepSeek",
        ])

        self.provider_combo.setCurrentText(
            self.config.provider
        )

        card_layout.addWidget(
            provider_label
        )

        card_layout.addWidget(
            self.provider_combo
        )

        # API Key
        api_key_label = QLabel(
            "API Key"
        )

        self.api_key_input = (
            QLineEdit()
        )

        self.api_key_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        saved_key = (
            self.config.get_api_key(
                "DeepSeek"
            )
        )

        if saved_key:

            self.api_key_input.setPlaceholderText(
                "API Key 已保存，如需修改请重新输入"
            )

        else:

            self.api_key_input.setPlaceholderText(
                "请输入 DeepSeek API Key"
            )

        card_layout.addWidget(
            api_key_label
        )

        card_layout.addWidget(
            self.api_key_input
        )

        # Model
        model_label = QLabel(
            "模型"
        )

        self.model_combo = (
            QComboBox()
        )

        self.model_combo.addItems([
            "deepseek-v4-flash",
            "deepseek-v4-pro",
        ])

        self.model_combo.setCurrentText(
            self.config.model
        )

        card_layout.addWidget(
            model_label
        )

        card_layout.addWidget(
            self.model_combo
        )

        # API 状态
        self.api_status_label = QLabel(
            "尚未测试连接"
        )

        self.api_status_label.setObjectName(
            "statusLabel"
        )

        card_layout.addWidget(
            self.api_status_label
        )

        # Buttons
        button_layout = (
            QHBoxLayout()
        )

        button_layout.addStretch()

        self.test_api_button = (
            QPushButton(
                "测试连接"
            )
        )

        self.test_api_button.setObjectName(
            "secondaryButton"
        )

        self.test_api_button.clicked.connect(
            self.test_api_connection
        )

        self.save_settings_button = (
            QPushButton(
                "保存设置"
            )
        )

        self.save_settings_button.setObjectName(
            "primaryButton"
        )

        self.save_settings_button.clicked.connect(
            self.save_settings
        )

        button_layout.addWidget(
            self.test_api_button
        )

        button_layout.addWidget(
            self.save_settings_button
        )

        card_layout.addLayout(
            button_layout
        )

        layout.addWidget(
            api_card
        )

        layout.addStretch()

        return page

    # =========================================================
    # 占位页面
    # =========================================================

    def create_placeholder_page(
        self,
        title_text,
        description_text
    ):

        page = QWidget()

        layout = QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            50,
            40,
            50,
            40
        )

        title = QLabel(
            title_text
        )

        title.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            description_text
        )

        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(title)

        layout.addWidget(
            description
        )

        layout.addStretch()

        return page

    # =========================================================
    # 页面切换
    # =========================================================

    def switch_page(
        self,
        index
    ):
        self.pages.setCurrentIndex(
            index
        )

    # =========================================================
    # 开始分析
    # =========================================================

    def start_analysis(self):

        selected_sectors = []

        for checkbox in (
            self.sector_checkboxes
        ):

            if checkbox.isChecked():

                selected_sectors.append(
                    checkbox.text()
                )

        if not selected_sectors:

            QMessageBox.warning(
                self,
                "没有选择板块",
                "请至少选择一个板块。"
            )

            return

        api_key = (
            self.config.get_api_key(
                "DeepSeek"
            )
        )

        if not api_key:

            QMessageBox.warning(
                self,
                "尚未配置 API",
                "请先进入设置页面配置 DeepSeek API Key。"
            )

            self.pages.setCurrentIndex(
                4
            )

            return

        model = self.config.model

        # 防止重复点击
        self.analyze_button.setEnabled(
            False
        )

        self.analyze_button.setText(
            "分析中..."
        )

        self.status_label.setText(
            "正在联网搜索近期事件，请稍候..."
        )

        self.result_browser.setHtml(
            """
            <div style="padding:20px;">
                <h3>正在分析...</h3>
                <p>
                DeepSeek 正在联网搜索近期事件，
                并建立板块传导链。
            </p>
                <p>
                第一次可能需要几十秒。
            </p>
            </div>
            """
        )

        # =====================================================
        # 后台线程
        # =====================================================

        self.analysis_worker = (
            AnalysisWorker(
                api_key=api_key,
                model=model,
                sectors=selected_sectors,
            )
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

    # =========================================================
    # AI 返回成功
    # =========================================================

    def on_analysis_ready(
        self,
        data
    ):

        self.status_label.setText(
            "分析完成"
        )

        html_content = (
            self.build_analysis_html(
                data
            )
        )

        self.result_browser.setHtml(
            html_content
        )

    # =========================================================
    # AI 返回错误
    # =========================================================

    def on_analysis_error(
        self,
        error_message
    ):

        self.status_label.setText(
            "分析失败"
        )

        self.result_browser.setHtml(
            f"""
            <div style="padding:20px;">
                <h3 style="color:#b91c1c;">
                    分析失败
                </h3>

                <p>
                    {html.escape(error_message)}
                </p>
            </div>
            """
        )

        QMessageBox.critical(
            self,
            "分析失败",
            error_message
        )

    # =========================================================
    # 线程完成
    # =========================================================

    def on_analysis_finished(
        self
    ):

        self.analyze_button.setEnabled(
            True
        )

        self.analyze_button.setText(
            "开始分析"
        )

        self.analysis_worker = None

    # =========================================================
    # JSON → HTML
    # =========================================================

    def build_analysis_html(
        self,
        data
    ):

        market_summary = html.escape(
            str(
                data.get(
                    "market_summary",
                    ""
                )
            )
        )

        parts = []

        parts.append("""
        <html>

        <body style="
            font-family:Microsoft YaHei;
            color:#1f2937;
        ">
        """)

        parts.append(
            f"""
            <div style="
                background:#f8fafc;
                padding:16px;
                border-radius:8px;
                margin-bottom:20px;
            ">

                <b>整体消息面</b>

                <p>
                    {market_summary}
                </p>

            </div>
            """
        )

        sectors = data.get(
            "sectors",
            []
        )

        for sector in sectors:

            sector_name = html.escape(
                str(
                    sector.get(
                        "sector",
                        ""
                    )
                )
            )

            direction = html.escape(
                str(
                    sector.get(
                        "direction",
                        "中性"
                    )
                )
            )

            score = sector.get(
                "score",
                0
            )

            confidence = sector.get(
                "confidence",
                0
            )

            summary = html.escape(
                str(
                    sector.get(
                        "summary",
                        ""
                    )
                )
            )

            # 分数颜色
            try:
                numeric_score = int(
                    score
                )
            except Exception:
                numeric_score = 0

            if numeric_score >= 10:

                score_color = (
                    "#b91c1c"
                )

            elif numeric_score <= -10:

                score_color = (
                    "#047857"
                )

            else:

                score_color = (
                    "#6b7280"
                )

            parts.append(
                f"""
                <div style="
                    border:1px solid #e5e7eb;
                    border-radius:10px;
                    padding:18px;
                    margin-bottom:20px;
                ">

                <h2>
                    {sector_name}
                </h2>

                <p>
                    <b>方向：</b>
                    {direction}

                    &nbsp;&nbsp;

                    <b>事件评分：</b>

                    <span style="
                        color:{score_color};
                        font-weight:bold;
                    ">
                        {score}
                    </span>

                    &nbsp;&nbsp;

                    <b>置信度：</b>
                    {confidence}%
                </p>

                <p>
                    {summary}
                </p>
                """
            )

            events = sector.get(
                "events",
                []
            )

            if not events:

                parts.append(
                    """
                    <p style="color:#6b7280;">
                        暂无明显重大新增事件。
                    </p>
                    """
                )

            for index, event in enumerate(
                events,
                start=1
            ):

                title = html.escape(
                    str(
                        event.get(
                            "title",
                            ""
                        )
                    )
                )

                date = html.escape(
                    str(
                        event.get(
                            "date",
                            ""
                        )
                    )
                )

                source = html.escape(
                    str(
                        event.get(
                            "source",
                            ""
                        )
                    )
                )

                url = str(
                    event.get(
                        "url",
                        ""
                    )
                ).strip()

                impact = html.escape(
                    str(
                        event.get(
                            "impact",
                            ""
                        )
                    )
                )

                importance = event.get(
                    "importance",
                    ""
                )

                analysis = html.escape(
                    str(
                        event.get(
                            "analysis",
                            ""
                        )
                    )
                )

                parts.append(
                    f"""
                    <hr>

                    <h3>
                        事件 {index}：
                        {title}
                    </h3>

                    <p>
                        <b>日期：</b>
                        {date}

                        &nbsp;&nbsp;

                        <b>来源：</b>
                        {source}
                    </p>

                    <p>
                        <b>影响：</b>
                        {impact}

                        &nbsp;&nbsp;

                        <b>重要度：</b>
                        {importance}/5
                    </p>
                    """
                )

                if url.startswith(
                    "http"
                ):

                    safe_url = html.escape(
                        url,
                        quote=True
                    )

                    parts.append(
                        f"""
                        <p>
                            <a href="{safe_url}">
                                查看原始来源
                            </a>
                        </p>
                        """
                    )

                transmission = (
                    event.get(
                        "transmission",
                        []
                    )
                )

                if transmission:

                    chain = " → ".join(
                        html.escape(
                            str(x)
                        )
                        for x in transmission
                    )

                    parts.append(
                        f"""
                        <p>
                            <b>传导链：</b><br>
                            {chain}
                        </p>
                        """
                    )

                parts.append(
                    f"""
                    <p>
                        <b>分析：</b><br>
                        {analysis}
                    </p>
                    """
                )

            risks = sector.get(
                "risks",
                []
            )

            if risks:

                risk_text = "<br>".join(
                    "• " + html.escape(
                        str(risk)
                    )
                    for risk in risks
                )

                parts.append(
                    f"""
                    <div style="
                        background:#fff7ed;
                        padding:12px;
                        border-radius:6px;
                        margin-top:15px;
                    ">

                    <b>风险与反向因素</b>

                    <p>
                        {risk_text}
                    </p>

                    </div>
                    """
                )

            parts.append(
                "</div>"
            )

        parts.append(
            """
            <div style="
                color:#9ca3af;
                font-size:12px;
                margin-top:20px;
            ">
                本结果仅用于信息研究与技术演示，
                不构成投资建议。
            </div>

            </body>
            </html>
            """
        )

        return "".join(
            parts
        )

    # =========================================================
    # 保存设置
    # =========================================================

    def save_settings(
        self
    ):

        provider = (
            self.provider_combo
            .currentText()
        )

        model = (
            self.model_combo
            .currentText()
        )

        api_key = (
            self.api_key_input
            .text()
            .strip()
        )

        self.config.provider = (
            provider
        )

        self.config.model = (
            model
        )

        self.config.save()

        if api_key:

            try:

                self.config.save_api_key(
                    provider,
                    api_key
                )

                self.api_key_input.clear()

                self.api_key_input.setPlaceholderText(
                    "API Key 已保存，如需修改请重新输入"
                )

            except Exception as exc:

                QMessageBox.critical(
                    self,
                    "保存失败",
                    str(exc)
                )

                return

        QMessageBox.information(
            self,
            "保存成功",
            "AI 设置已保存。"
        )

    # =========================================================
    # 测试 API
    # =========================================================

    def test_api_connection(
        self
    ):

        provider = (
            self.provider_combo
            .currentText()
        )

        model = (
            self.model_combo
            .currentText()
        )

        api_key = (
            self.api_key_input
            .text()
            .strip()
        )

        if not api_key:

            api_key = (
                self.config.get_api_key(
                    provider
                )
            )

        if not api_key:

            QMessageBox.warning(
                self,
                "缺少 API Key",
                "请先输入 DeepSeek API Key。"
            )

            return

        self.test_api_button.setEnabled(
            False
        )

        self.test_api_button.setText(
            "连接中..."
        )

        self.api_status_label.setText(
            "正在连接 DeepSeek..."
        )

        QApplication.processEvents()

        try:

            result = test_connection(
                api_key=api_key,
                model=model,
            )

            self.api_status_label.setText(
                "✓ DeepSeek API 连接成功"
            )

            QMessageBox.information(
                self,
                "连接成功",
                "DeepSeek API 工作正常。\n\n"
                f"模型回复：{result}"
            )

        except Exception as exc:

            self.api_status_label.setText(
                "✕ API 连接失败"
            )

            QMessageBox.critical(
                self,
                "连接失败",
                str(exc)
            )

        finally:

            self.test_api_button.setEnabled(
                True
            )

            self.test_api_button.setText(
                "测试连接"
            )

    # =========================================================
    # 样式
    # =========================================================

    def apply_styles(
        self
    ):

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6f8;
            }

            QWidget {
                font-family: "Microsoft YaHei";
            }

            #sidebar {
                background-color: #171a21;
            }

            #sidebarTitle {
                color: white;
                font-size: 20px;
                font-weight: bold;
            }

            #sidebarSubtitle {
                color: #8b93a1;
                font-size: 12px;
            }

            #navButton {
                background-color: transparent;
                color: #d0d4dc;
                border: none;
                text-align: left;
                padding: 12px 16px;
                border-radius: 6px;
                font-size: 15px;
            }

            #navButton:hover {
                background-color: #282d37;
                color: white;
            }

            #versionLabel {
                color: #6e7684;
                font-size: 12px;
            }

            #pageTitle {
                color: #1c1e21;
                font-size: 28px;
                font-weight: bold;
            }

            #pageDescription {
                color: #666c76;
                font-size: 14px;
            }

            #card {
                background-color: white;
                border: 1px solid #e1e4e8;
                border-radius: 10px;
            }

            #cardTitle {
                color: #202328;
                font-size: 18px;
                font-weight: bold;
            }

            QCheckBox {
                font-size: 15px;
                color: #333333;
                spacing: 10px;
                min-width: 220px;
            }

            QLineEdit {
                background-color: white;
                border: 1px solid #d5d9df;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 1px solid #2563eb;
            }

            QComboBox {
                background-color: white;
                border: 1px solid #d5d9df;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }

            #primaryButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px 20px;
                font-size: 15px;
                font-weight: bold;
            }

            #primaryButton:hover {
                background-color: #1d4ed8;
            }

            #primaryButton:disabled {
                background-color: #94a3b8;
            }

            #secondaryButton {
                background-color: white;
                color: #333333;
                border: 1px solid #cfd4dc;
                border-radius: 7px;
                padding: 10px 20px;
                font-size: 14px;
            }

            #secondaryButton:hover {
                background-color: #f1f3f5;
            }

            #statusLabel {
                color: #666666;
                font-size: 14px;
            }

            QTextBrowser {
                background-color: white;
                border: none;
                font-size: 14px;
                padding: 5px;
            }
        """)


# =============================================================
# 程序入口
# =============================================================

def main():

    app = QApplication(
        sys.argv
    )

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
