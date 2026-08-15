from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)

from app.ai.manager import ProviderManager
from app.config.settings import AppConfig
from app.platform import is_android


class FirstRunWizard(QWizard):
    def __init__(
        self,
        config: AppConfig,
        provider_manager: ProviderManager,
        parent=None,
    ):
        super().__init__(parent)

        self.config = config
        self.provider_manager = provider_manager

        self.setWindowTitle(
            "欢迎使用 AI板块事件雷达"
        )
        self.setWizardStyle(
            QWizard.WizardStyle.ModernStyle
        )
        if is_android():
            self.resize(
                360,
                620,
            )
        else:
            self.resize(
                680,
                480,
            )

        self._build_pages()

    def _build_pages(self):
        self.addPage(
            self._welcome_page()
        )
        self.addPage(
            self._provider_page()
        )
        self.addPage(
            self._mode_page()
        )
        self.addPage(
            self._finish_page()
        )

    def _welcome_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle(
            "欢迎使用 AI板块事件雷达"
        )
        page.setSubTitle(
            "V0.9 首次启动向导会帮你完成最基本的设置。"
        )

        layout = QVBoxLayout(page)

        text = QLabel(
            "这个软件会：\n\n"
            "1. 联网研究近期板块事件；\n"
            "2. 让多个 AI 基于同一份证据独立判断；\n"
            "3. 保存历史、新闻事件、晨报和统计；\n"
            "4. API Key 由你自己的账号提供。\n\n"
            "你以后可以在“AI 设置”里继续增加 Qwen、GLM、Kimi、豆包、MiniMax。"
        )
        text.setWordWrap(True)
        text.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )
        layout.addWidget(text)

        return page

    def _provider_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle(
            "配置第一个联网 AI"
        )
        page.setSubTitle(
            "至少需要一个可联网研究的 Provider 才能开始正式分析。"
        )

        layout = QVBoxLayout(page)

        layout.addWidget(
            QLabel("联网研究 Provider")
        )

        self.provider_combo = QComboBox()
        self.provider_combo.addItems(
            self.provider_manager
            .research_provider_names()
        )
        self.provider_combo.setCurrentText(
            self.config.research_provider
        )
        layout.addWidget(
            self.provider_combo
        )

        layout.addWidget(
            QLabel("API Key（可暂时留空）")
        )

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )
        self.api_key_input.setPlaceholderText(
            "Key 只会保存到系统凭据管理器；Android Beta 当前为会话内保存"
        )
        layout.addWidget(
            self.api_key_input
        )

        note_text = (
            "如果暂时不填 API Key，也可以先进入软件查看界面，"
            "之后在“AI 设置”中配置。"
        )

        if is_android():
            note_text += (
                "\n\nAndroid Beta 为避免明文落盘，API Key 当前只保存在运行内存；"
                "重新打开 App 后需要再次输入。"
            )

        note = QLabel(
            note_text
        )
        note.setWordWrap(True)
        note.setObjectName(
            "pageDescription"
        )
        layout.addWidget(note)
        layout.addStretch()

        return page

    def _mode_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle(
            "选择默认分析模式"
        )

        layout = QVBoxLayout(page)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem(
            "单模型快速 — 调用少，适合初次测试",
            "single",
        )
        self.mode_combo.addItem(
            "多模型交叉验证 — 推荐正式使用",
            "multi",
        )

        current_index = self.mode_combo.findData(
            self.config.analysis_mode
        )

        if current_index >= 0:
            self.mode_combo.setCurrentIndex(
                current_index
            )

        layout.addWidget(
            self.mode_combo
        )

        explain = QLabel(
            "“多模型交叉验证”不会让每个 AI 各自搜索不同新闻。"
            "系统会先获得一份共同证据，再把同样的证据交给已启用模型。"
        )
        explain.setWordWrap(True)
        layout.addWidget(explain)
        layout.addStretch()

        return page

    def _finish_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle(
            "准备完成"
        )
        page.setSubTitle(
            "完成后会进入主界面。建议先到“AI 设置”测试连接。"
        )

        layout = QVBoxLayout(page)

        text = QLabel(
            "推荐第一次操作：\n\n"
            "AI 设置 → 测试连接\n"
            "今日分析 → 只选 1~2 个板块\n"
            "开始分析 → 观察实时进度\n"
            "晨报 / 报告中心 → 生成晨报"
        )
        text.setWordWrap(True)
        layout.addWidget(text)
        layout.addStretch()

        return page

    def accept(self):
        provider = (
            self.provider_combo
            .currentText()
        )

        self.config.research_provider = provider
        self.config.analysis_mode = (
            self.mode_combo.currentData()
        )

        api_key = (
            self.api_key_input
            .text()
            .strip()
        )

        if api_key:
            self.config.save_api_key(
                provider,
                api_key,
            )

        self.config.onboarding_complete = True
        self.config.save()

        super().accept()
