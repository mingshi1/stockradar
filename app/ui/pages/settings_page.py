from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ai.manager import ProviderManager
from app.config.settings import AppConfig


class SettingsPage(QWidget):
    save_requested = Signal(str, str, str)
    test_requested = Signal(str, str, str)

    def __init__(
        self,
        config: AppConfig,
        provider_manager: ProviderManager,
    ):
        super().__init__()

        self.config = config
        self.provider_manager = provider_manager

        self._build_ui()
        self._load_config()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)

        title = QLabel("设置")
        title.setObjectName("pageTitle")

        description = QLabel(
            "配置 AI 服务、API Key 和分析模型。"
        )
        description.setObjectName("pageDescription")

        layout.addWidget(title)
        layout.addWidget(description)

        api_card = QFrame()
        api_card.setObjectName("card")

        card_layout = QVBoxLayout(api_card)
        card_layout.setContentsMargins(30, 25, 30, 25)
        card_layout.setSpacing(14)

        api_title = QLabel("AI 服务")
        api_title.setObjectName("cardTitle")
        card_layout.addWidget(api_title)

        provider_label = QLabel("AI Provider")

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(
            self.provider_manager.provider_names()
        )
        self.provider_combo.currentTextChanged.connect(
            self._provider_changed
        )

        card_layout.addWidget(provider_label)
        card_layout.addWidget(self.provider_combo)

        api_key_label = QLabel("API Key")

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        card_layout.addWidget(api_key_label)
        card_layout.addWidget(self.api_key_input)

        model_label = QLabel("模型")

        self.model_combo = QComboBox()

        card_layout.addWidget(model_label)
        card_layout.addWidget(self.model_combo)

        self.api_status_label = QLabel("尚未测试连接")
        self.api_status_label.setObjectName("statusLabel")
        card_layout.addWidget(self.api_status_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.test_api_button = QPushButton("测试连接")
        self.test_api_button.setObjectName("secondaryButton")
        self.test_api_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.test_api_button.clicked.connect(
            self._emit_test
        )

        self.save_settings_button = QPushButton("保存设置")
        self.save_settings_button.setObjectName("primaryButton")
        self.save_settings_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.save_settings_button.clicked.connect(
            self._emit_save
        )

        button_layout.addWidget(self.test_api_button)
        button_layout.addWidget(self.save_settings_button)
        card_layout.addLayout(button_layout)

        layout.addWidget(api_card)

        info_card = QFrame()
        info_card.setObjectName("card")

        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(30, 20, 30, 20)

        info_title = QLabel("V0.4 Provider 架构")
        info_title.setObjectName("cardTitle")

        info_text = QLabel(
            "当前只启用 DeepSeek，但软件已经改成统一 AIProvider 架构。"
            "后续增加 OpenAI、Qwen、GLM 时，不需要重写首页分析逻辑。"
        )
        info_text.setWordWrap(True)
        info_text.setObjectName("pageDescription")

        info_layout.addWidget(info_title)
        info_layout.addWidget(info_text)

        layout.addWidget(info_card)
        layout.addStretch()

    def _load_config(self):
        if self.config.provider in self.provider_manager.provider_names():
            self.provider_combo.setCurrentText(
                self.config.provider
            )

        self._refresh_models(
            preferred_model=self.config.model
        )
        self._refresh_api_key_placeholder()

    def _provider_changed(self, provider_name: str):
        self._refresh_models()
        self._refresh_api_key_placeholder()

    def _refresh_models(self, preferred_model: str | None = None):
        provider = self.provider_combo.currentText()
        models = self.provider_manager.models_for(provider)

        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        self.model_combo.addItems(models)

        if preferred_model in models:
            self.model_combo.setCurrentText(preferred_model)

        self.model_combo.blockSignals(False)

    def _refresh_api_key_placeholder(self):
        provider = self.provider_combo.currentText()

        if not provider:
            return

        if self.config.get_api_key(provider):
            self.api_key_input.setPlaceholderText(
                "API Key 已保存，如需修改请重新输入"
            )
        else:
            self.api_key_input.setPlaceholderText(
                f"请输入 {provider} API Key"
            )

    def values(self) -> tuple[str, str, str]:
        return (
            self.provider_combo.currentText(),
            self.model_combo.currentText(),
            self.api_key_input.text().strip(),
        )

    def _emit_save(self):
        self.save_requested.emit(*self.values())

    def _emit_test(self):
        self.test_requested.emit(*self.values())

    def mark_saved(self):
        self.api_key_input.clear()
        self._refresh_api_key_placeholder()

    def set_test_running(self, running: bool):
        self.test_api_button.setEnabled(not running)
        self.test_api_button.setText(
            "连接中..." if running else "测试连接"
        )

        if running:
            self.api_status_label.setText(
                "正在连接 AI 服务..."
            )

    def show_test_success(self):
        self.api_status_label.setText(
            "✓ API 连接成功"
        )

    def show_test_error(self):
        self.api_status_label.setText(
            "✕ API 连接失败"
        )
