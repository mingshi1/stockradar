from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
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
        self.provider_widgets: dict[
            str,
            dict,
        ] = {}

        self._build_ui()
        self._load_config()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            45,
            30,
            45,
            30,
        )
        layout.setSpacing(15)

        title = QLabel("AI 模型与验证设置")
        title.setObjectName("pageTitle")

        description = QLabel(
            "V0.6 支持 DeepSeek、OpenAI、Qwen、GLM、Kimi。"
            "多个模型会读取同一份联网证据后独立判断。"
        )
        description.setWordWrap(True)
        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(title)
        layout.addWidget(description)

        # =====================================================
        # Multi-AI global settings
        # =====================================================
        global_card = QFrame()
        global_card.setObjectName("card")

        global_layout = QVBoxLayout(
            global_card
        )
        global_layout.setContentsMargins(
            25,
            20,
            25,
            20,
        )
        global_layout.setSpacing(10)

        global_title = QLabel(
            "分析流程"
        )
        global_title.setObjectName(
            "cardTitle"
        )
        global_layout.addWidget(
            global_title
        )

        research_row = QHBoxLayout()

        research_row.addWidget(
            QLabel("联网研究 Provider")
        )

        self.research_combo = (
            QComboBox()
        )
        self.research_combo.addItems(
            self.provider_manager
            .research_provider_names()
        )

        research_row.addWidget(
            self.research_combo,
            1,
        )

        research_row.addWidget(
            QLabel("分析模式")
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

        research_row.addWidget(
            self.mode_combo,
            1,
        )

        global_layout.addLayout(
            research_row
        )

        judge_row = QHBoxLayout()

        self.judge_checkbox = (
            QCheckBox(
                "启用 Judge AI 汇总共识与分歧"
            )
        )
        judge_row.addWidget(
            self.judge_checkbox
        )

        judge_row.addStretch()

        judge_row.addWidget(
            QLabel("Judge Provider")
        )

        self.judge_combo = (
            QComboBox()
        )
        self.judge_combo.addItems(
            self.provider_manager
            .provider_names()
        )
        judge_row.addWidget(
            self.judge_combo
        )

        global_layout.addLayout(
            judge_row
        )

        hint = QLabel(
            "建议：日常先用 2~3 个模型。"
            "Judge 会额外增加一次 API 调用；"
            "它只总结分歧，不修改数学聚合得到的评分。"
        )
        hint.setWordWrap(True)
        hint.setObjectName("statusLabel")
        global_layout.addWidget(hint)

        layout.addWidget(global_card)

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

        save_row.addWidget(save_button)
        layout.addLayout(save_row)

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
            20,
            20,
            20,
            20,
        )
        layout.setSpacing(12)

        enabled = QCheckBox(
            "参与多模型独立分析"
        )

        if info.supports_web_search:
            enabled.setText(
                "参与多模型独立分析"
                "（也可作为联网研究 Provider）"
            )

        layout.addWidget(enabled)

        model_label = QLabel("模型")
        model_combo = QComboBox()
        model_combo.setEditable(True)
        model_combo.addItems(
            list(info.models)
        )

        layout.addWidget(model_label)
        layout.addWidget(model_combo)

        base_label = QLabel("Base URL")
        base_input = QLineEdit()

        layout.addWidget(base_label)
        layout.addWidget(base_input)

        api_label = QLabel("API Key")
        api_input = QLineEdit()
        api_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        layout.addWidget(api_label)
        layout.addWidget(api_input)

        status = QLabel("尚未测试连接")
        status.setObjectName("statusLabel")
        layout.addWidget(status)

        button_row = QHBoxLayout()
        button_row.addStretch()

        test_button = QPushButton(
            "测试此 Provider"
        )
        test_button.setObjectName(
            "secondaryButton"
        )
        test_button.clicked.connect(
            lambda checked=False, name=provider_name:
            self._emit_test(name)
        )

        button_row.addWidget(test_button)
        layout.addLayout(button_row)

        if provider_name == "Qwen":
            qwen_hint = QLabel(
                "千问提示：不同地域/计费模式的 API Host "
                "可能不同。如果控制台给你的 API Host "
                "与默认值不同，请把 Base URL 改成控制台显示的地址。"
            )
            qwen_hint.setWordWrap(True)
            qwen_hint.setObjectName(
                "statusLabel"
            )
            layout.addWidget(qwen_hint)

        layout.addStretch()

        self.provider_widgets[
            provider_name
        ] = {
            "enabled": enabled,
            "model": model_combo,
            "base_url": base_input,
            "api_key": api_input,
            "status": status,
            "test_button": test_button,
        }

        return tab

    def _load_config(self):
        self.research_combo.setCurrentText(
            self.config.research_provider
        )

        mode_index = (
            self.mode_combo.findData(
                self.config.analysis_mode
            )
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
            info = (
                self.provider_manager.info(
                    provider_name
                )
            )
            saved = (
                self.config
                .get_provider_config(
                    provider_name
                )
            )

            widgets[
                "enabled"
            ].setChecked(
                bool(
                    saved.get(
                        "enabled",
                        False,
                    )
                )
            )

            model = saved.get(
                "model",
                info.default_model,
            )

            widgets[
                "model"
            ].setCurrentText(
                model
            )

            widgets[
                "base_url"
            ].setText(
                saved.get(
                    "base_url",
                    info.default_base_url,
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
                "API Key 已安全保存；留空表示继续使用原 Key"
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
                    widgets[
                        "enabled"
                    ].isChecked()
                ),
                "model": (
                    widgets[
                        "model"
                    ].currentText().strip()
                ),
                "base_url": (
                    widgets[
                        "base_url"
                    ].text().strip()
                ),
                "api_key": (
                    widgets[
                        "api_key"
                    ].text().strip()
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
            widgets[
                "api_key"
            ].text().strip(),
            widgets[
                "model"
            ].currentText().strip(),
            widgets[
                "base_url"
            ].text().strip(),
        )

    def mark_saved(self):
        for provider_name, widgets in (
            self.provider_widgets.items()
        ):
            widgets[
                "api_key"
            ].clear()
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
            widgets[
                "status"
            ].setText(
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
