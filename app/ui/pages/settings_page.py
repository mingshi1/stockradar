from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.ai.manager import ProviderManager
from app.config.settings import AppConfig
from app.platform import is_android


class SettingsPage(QWidget):
    save_requested = Signal(object)
    test_requested = Signal(
        str,
        str,
        str,
        str,
    )

    def __init__(
        self,
        config: AppConfig,
        provider_manager: ProviderManager,
    ):
        super().__init__()

        self.config = config
        self.provider_manager = provider_manager
        self.provider_widgets: dict[str, dict] = {}

        self._build_ui()
        self._load_config()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            12 if is_android() else 40,
            12 if is_android() else 25,
            12 if is_android() else 40,
            16 if is_android() else 25,
        )
        layout.setSpacing(12)

        title = QLabel(
            "AI 模型设置"
            if is_android()
            else "AI 模型与成本设置"
        )
        title.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            (
                "Android 版只保留必要配置：选择模型、填写 API Key、测试连接。"
                "Base URL 自动使用各 Provider 官方默认值，不在手机端配置成本单价。"
            )
            if is_android()
            else (
                "配置国产 Multi-AI、联网研究 Provider，以及可选的 Token 单价。"
                "单价完全由你维护，软件不会把可能过期的官方价格硬编码进去。"
            )
        )
        description.setWordWrap(True)
        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(title)
        layout.addWidget(description)

        # =====================================================
        # Global flow
        # =====================================================
        global_card = QFrame()
        global_card.setObjectName("card")

        global_layout = QVBoxLayout(
            global_card
        )
        global_layout.setContentsMargins(
            14 if is_android() else 22,
            12 if is_android() else 15,
            14 if is_android() else 22,
            12 if is_android() else 15,
        )
        global_layout.setSpacing(8)

        global_title = QLabel(
            "分析流程"
        )
        global_title.setObjectName(
            "cardTitle"
        )
        global_layout.addWidget(
            global_title
        )

        self.research_combo = QComboBox()
        self.research_combo.addItems(
            self.provider_manager
            .research_provider_names()
        )

        self.mode_combo = QComboBox()
        self.mode_combo.addItem(
            "单模型快速",
            "single",
        )
        self.mode_combo.addItem(
            "多模型交叉验证",
            "multi",
        )

        self.judge_checkbox = QCheckBox(
            "启用 Judge AI 总结共识与分歧"
        )

        self.judge_combo = QComboBox()
        self.judge_combo.addItems(
            self.provider_manager
            .provider_names()
        )

        if is_android():
            global_layout.addWidget(
                QLabel("联网研究 Provider")
            )
            global_layout.addWidget(
                self.research_combo
            )
            global_layout.addWidget(
                QLabel("分析模式")
            )
            global_layout.addWidget(
                self.mode_combo
            )
            global_layout.addWidget(
                self.judge_checkbox
            )
            global_layout.addWidget(
                QLabel("Judge Provider")
            )
            global_layout.addWidget(
                self.judge_combo
            )
        else:
            row = QHBoxLayout()

            row.addWidget(
                QLabel("联网研究 Provider")
            )
            row.addWidget(
                self.research_combo,
                1,
            )
            row.addWidget(
                QLabel("分析模式")
            )
            row.addWidget(
                self.mode_combo,
                1,
            )

            global_layout.addLayout(
                row
            )

            judge_row = QHBoxLayout()
            judge_row.addWidget(
                self.judge_checkbox
            )
            judge_row.addStretch()
            judge_row.addWidget(
                QLabel("Judge Provider")
            )
            judge_row.addWidget(
                self.judge_combo
            )

            global_layout.addLayout(
                judge_row
            )

        hint = QLabel(
            "日常建议启用 2~3 个模型。当前版本 会记录每次 Provider 耗时和 Token；"
            "价格字段留空/0 时仍记录 Token，但不估算成本。"
        )
        hint.setWordWrap(True)
        hint.setObjectName(
            "statusLabel"
        )
        if not is_android():
            global_layout.addWidget(
                hint
            )

        layout.addWidget(
            global_card
        )

        # =====================================================
        # Provider tabs
        # =====================================================
        self.tabs = QTabWidget()

        for provider_name in (
            self.provider_manager
            .provider_names()
        ):
            tab = self._create_provider_tab(
                provider_name
            )
            self.tabs.addTab(
                tab,
                provider_name,
            )

        layout.addWidget(
            self.tabs,
            1,
        )

        save_row = QHBoxLayout()
        save_row.addStretch()

        save_button = QPushButton(
            "保存全部设置"
        )
        save_button.setObjectName(
            "primaryButton"
        )
        save_button.clicked.connect(
            self._emit_save
        )
        if is_android():
            save_button.setMinimumHeight(
                44
            )
            layout.addWidget(
                save_button
            )
        else:
            save_row.addWidget(
                save_button
            )
            layout.addLayout(
                save_row
            )

    def _create_provider_tab(
        self,
        provider_name: str,
    ) -> QWidget:
        info = self.provider_manager.info(
            provider_name
        )

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(
            12 if is_android() else 18,
            12 if is_android() else 16,
            12 if is_android() else 18,
            12 if is_android() else 16,
        )
        layout.setSpacing(10)

        enabled = QCheckBox(
            "参与多模型独立分析"
        )

        if (
            info.supports_web_search
            and not is_android()
        ):
            enabled.setText(
                "参与多模型独立分析"
                "（也可作为联网研究 Provider）"
            )

        layout.addWidget(
            enabled
        )

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(8)

        model_combo = QComboBox()
        model_combo.setEditable(True)
        model_combo.addItems(
            list(info.models)
        )

        base_input = QLineEdit()

        api_input = QLineEdit()
        api_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        input_price = QDoubleSpinBox()
        input_price.setRange(
            0.0,
            1_000_000.0,
        )
        input_price.setDecimals(6)
        input_price.setSingleStep(0.1)
        input_price.setSuffix(
            " /1M"
            if is_android()
            else " / 1M input tokens"
        )

        output_price = QDoubleSpinBox()
        output_price.setRange(
            0.0,
            1_000_000.0,
        )
        output_price.setDecimals(6)
        output_price.setSingleStep(0.1)
        output_price.setSuffix(
            " /1M"
            if is_android()
            else " / 1M output tokens"
        )

        if is_android():
            # Mobile: intentionally minimal.  Base URL and price
            # controls still exist internally for config compatibility,
            # but they are not placed in the Android UI.
            model_label = QLabel(
                "模型"
            )
            key_label = QLabel(
                "API Key"
            )

            grid.setColumnStretch(
                0,
                1,
            )
            grid.addWidget(
                model_label,
                0,
                0,
            )
            grid.addWidget(
                model_combo,
                1,
                0,
            )
            grid.addWidget(
                key_label,
                2,
                0,
            )
            grid.addWidget(
                api_input,
                3,
                0,
            )

            model_combo.setMinimumHeight(
                40
            )
            api_input.setMinimumHeight(
                40
            )
        else:
            grid.addWidget(
                QLabel("模型"),
                0,
                0,
            )
            grid.addWidget(
                model_combo,
                0,
                1,
            )
            grid.addWidget(
                QLabel("Base URL"),
                1,
                0,
            )
            grid.addWidget(
                base_input,
                1,
                1,
            )
            grid.addWidget(
                QLabel("API Key"),
                2,
                0,
            )
            grid.addWidget(
                api_input,
                2,
                1,
            )
            grid.addWidget(
                QLabel("输入单价*"),
                3,
                0,
            )
            grid.addWidget(
                input_price,
                3,
                1,
            )
            grid.addWidget(
                QLabel("输出单价*"),
                4,
                0,
            )
            grid.addWidget(
                output_price,
                4,
                1,
            )

        layout.addLayout(
            grid
        )

        price_hint = QLabel(
            "* 单价货币单位由你自己保持一致，例如全部使用人民币。"
            "填写 0 表示“不估算此 Provider 成本”。"
        )
        price_hint.setWordWrap(True)
        price_hint.setObjectName(
            "statusLabel"
        )
        if not is_android():
            layout.addWidget(
                price_hint
            )

        status = QLabel(
            "尚未测试连接"
        )
        status.setObjectName(
            "statusLabel"
        )
        layout.addWidget(
            status
        )

        button_row = QHBoxLayout()
        button_row.addStretch()

        test_button = QPushButton(
            "测试此 Provider"
        )
        test_button.setObjectName(
            "secondaryButton"
        )
        test_button.clicked.connect(
            lambda checked=False,
            name=provider_name:
            self._emit_test(name)
        )

        if is_android():
            test_button.setMinimumHeight(
                42
            )
            layout.addWidget(
                test_button
            )
        else:
            button_row.addWidget(
                test_button
            )
            layout.addLayout(
                button_row
            )

        specific_hint = self._provider_hint(
            provider_name
        )

        if (
            specific_hint
            and not is_android()
        ):
            label = QLabel(
                specific_hint
            )
            label.setWordWrap(True)
            label.setObjectName(
                "statusLabel"
            )
            layout.addWidget(
                label
            )

        layout.addStretch()

        self.provider_widgets[
            provider_name
        ] = {
            "enabled": enabled,
            "model": model_combo,
            "base_url": base_input,
            "api_key": api_input,
            "input_price": input_price,
            "output_price": output_price,
            "status": status,
            "test_button": test_button,
        }

        return tab

    @staticmethod
    def _provider_hint(
        provider_name: str,
    ) -> str:
        hints = {
            "Qwen": (
                "千问不同地域/计费模式的 API Host 可能不同；"
                "控制台地址优先于软件默认值。"
            ),
            "Doubao": (
                "豆包模型更新较快，建议复制火山方舟控制台“API 接入”"
                "页面显示的准确 Model ID。"
            ),
            "MiniMax": (
                "MiniMax 默认使用中国开放平台 api.minimaxi.com。"
            ),
        }

        return hints.get(
            provider_name,
            "",
        )

    def _load_config(self):
        self.research_combo.setCurrentText(
            self.config.research_provider
        )

        mode_index = self.mode_combo.findData(
            self.config.analysis_mode
        )

        if mode_index >= 0:
            self.mode_combo.setCurrentIndex(
                mode_index
            )

        self.judge_checkbox.setChecked(
            self.config.judge_enabled
        )
        self.judge_combo.setCurrentText(
            self.config.judge_provider
        )

        for provider_name, widgets in (
            self.provider_widgets.items()
        ):
            info = self.provider_manager.info(
                provider_name
            )
            saved = self.config.get_provider_config(
                provider_name
            )

            widgets["enabled"].setChecked(
                bool(
                    saved.get(
                        "enabled",
                        False,
                    )
                )
            )
            widgets["model"].setCurrentText(
                str(
                    saved.get(
                        "model",
                        info.default_model,
                    )
                )
            )
            widgets["base_url"].setText(
                (
                    info.default_base_url
                    if is_android()
                    else str(
                        saved.get(
                            "base_url",
                            info.default_base_url,
                        )
                    )
                )
            )

            if is_android():
                widgets["input_price"].setValue(
                    0.0
                )
                widgets["output_price"].setValue(
                    0.0
                )
            else:
                widgets["input_price"].setValue(
                    float(
                        saved.get(
                            "input_price_per_million",
                            0.0,
                        )
                        or 0.0
                    )
                )
                widgets["output_price"].setValue(
                    float(
                        saved.get(
                            "output_price_per_million",
                            0.0,
                        )
                        or 0.0
                    )
                )

            self._refresh_key_placeholder(
                provider_name
            )

    def _refresh_key_placeholder(
        self,
        provider_name: str,
    ):
        widget = self.provider_widgets[
            provider_name
        ]["api_key"]

        if self.config.has_api_key(
            provider_name
        ):
            widget.setPlaceholderText(
                "API Key 已安全保存；留空继续使用原 Key"
            )
        else:
            widget.setPlaceholderText(
                f"请输入 {provider_name} API Key"
            )

    def collect_settings(self) -> dict:
        providers = {}

        for provider_name, widgets in (
            self.provider_widgets.items()
        ):
            providers[
                provider_name
            ] = {
                "enabled": (
                    widgets["enabled"]
                    .isChecked()
                ),
                "model": (
                    widgets["model"]
                    .currentText()
                    .strip()
                ),
                "base_url": (
                    self.provider_manager
                    .info(provider_name)
                    .default_base_url
                    if is_android()
                    else widgets[
                        "base_url"
                    ].text().strip()
                ),
                "api_key": (
                    widgets["api_key"]
                    .text()
                    .strip()
                ),
                "input_price_per_million": (
                    0.0
                    if is_android()
                    else widgets[
                        "input_price"
                    ].value()
                ),
                "output_price_per_million": (
                    0.0
                    if is_android()
                    else widgets[
                        "output_price"
                    ].value()
                ),
            }

        return {
            "research_provider": (
                self.research_combo
                .currentText()
            ),
            "analysis_mode": (
                self.mode_combo
                .currentData()
            ),
            "judge_enabled": (
                self.judge_checkbox
                .isChecked()
            ),
            "judge_provider": (
                self.judge_combo
                .currentText()
            ),
            "providers": providers,
        }

    def _emit_save(self):
        self.save_requested.emit(
            self.collect_settings()
        )

    def _emit_test(
        self,
        provider_name: str,
    ):
        widgets = self.provider_widgets[
            provider_name
        ]

        self.test_requested.emit(
            provider_name,
            widgets["api_key"]
            .text()
            .strip(),
            widgets["model"]
            .currentText()
            .strip(),
            (
                self.provider_manager
                .info(provider_name)
                .default_base_url
                if is_android()
                else widgets[
                    "base_url"
                ].text().strip()
            ),
        )

    def mark_saved(self):
        for provider_name, widgets in (
            self.provider_widgets.items()
        ):
            widgets["api_key"].clear()
            self._refresh_key_placeholder(
                provider_name
            )

    def set_test_running(
        self,
        provider_name: str,
        running: bool,
    ):
        widgets = self.provider_widgets[
            provider_name
        ]

        button = widgets[
            "test_button"
        ]

        button.setEnabled(
            not running
        )
        button.setText(
            "连接中..."
            if running
            else "测试此 Provider"
        )

        if running:
            widgets["status"].setText(
                "正在连接..."
            )

    def show_test_success(
        self,
        provider_name: str,
    ):
        self.provider_widgets[
            provider_name
        ]["status"].setText(
            "✓ API 连接成功"
        )

    def show_test_error(
        self,
        provider_name: str,
    ):
        self.provider_widgets[
            provider_name
        ]["status"].setText(
            "✕ API 连接失败"
        )
