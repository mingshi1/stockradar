from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SystemPage(QWidget):
    backup_requested = Signal()
    restore_requested = Signal()
    open_data_requested = Signal()
    open_logs_requested = Signal()
    rerun_onboarding_requested = Signal()
    ui_mode_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            45,
            30,
            45,
            30,
        )
        layout.setSpacing(16)

        title = QLabel(
            "系统与数据"
        )
        title.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "管理数据库备份、恢复、界面布局和本地运行数据。"
        )
        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(title)
        layout.addWidget(description)

        # Database card
        database_card = QFrame()
        database_card.setObjectName(
            "card"
        )

        db_layout = QVBoxLayout(
            database_card
        )
        db_layout.setContentsMargins(
            25,
            20,
            25,
            20,
        )

        db_title = QLabel(
            "SQLite 数据库"
        )
        db_title.setObjectName(
            "cardTitle"
        )
        db_layout.addWidget(
            db_title
        )

        self.schema_label = QLabel(
            "数据库 Schema：读取中…"
        )
        self.schema_label.setObjectName(
            "statusLabel"
        )
        db_layout.addWidget(
            self.schema_label
        )

        self.database_path_label = QLabel()
        self.database_path_label.setWordWrap(
            True
        )
        self.database_path_label.setObjectName(
            "statusLabel"
        )
        db_layout.addWidget(
            self.database_path_label
        )

        db_buttons = QHBoxLayout()

        backup_button = QPushButton(
            "备份数据库"
        )
        backup_button.setObjectName(
            "primaryButton"
        )
        backup_button.clicked.connect(
            self.backup_requested.emit
        )

        restore_button = QPushButton(
            "恢复数据库"
        )
        restore_button.setObjectName(
            "secondaryButton"
        )
        restore_button.clicked.connect(
            self.restore_requested.emit
        )

        open_data_button = QPushButton(
            "打开数据目录"
        )
        open_data_button.setObjectName(
            "secondaryButton"
        )
        open_data_button.clicked.connect(
            self.open_data_requested.emit
        )

        db_buttons.addWidget(
            backup_button
        )
        db_buttons.addWidget(
            restore_button
        )
        db_buttons.addWidget(
            open_data_button
        )
        db_buttons.addStretch()

        db_layout.addLayout(
            db_buttons
        )
        layout.addWidget(
            database_card
        )

        # UI card
        ui_card = QFrame()
        ui_card.setObjectName(
            "card"
        )

        ui_layout = QVBoxLayout(
            ui_card
        )
        ui_layout.setContentsMargins(
            25,
            20,
            25,
            20,
        )

        ui_title = QLabel(
            "响应式界面"
        )
        ui_title.setObjectName(
            "cardTitle"
        )
        ui_layout.addWidget(
            ui_title
        )

        row = QHBoxLayout()
        row.addWidget(
            QLabel("布局模式")
        )

        self.ui_mode_combo = QComboBox()
        self.ui_mode_combo.addItem(
            "自动",
            "auto",
        )
        self.ui_mode_combo.addItem(
            "桌面",
            "desktop",
        )
        self.ui_mode_combo.addItem(
            "移动 / 窄屏",
            "mobile",
        )
        self.ui_mode_combo.currentIndexChanged.connect(
            self._emit_ui_mode
        )

        row.addWidget(
            self.ui_mode_combo
        )
        row.addStretch()

        ui_layout.addLayout(row)

        mobile_hint = QLabel(
            "自动模式会在窗口较窄时隐藏左侧导航并启用顶部移动导航。"
            "Android Beta 默认会自动使用窄屏布局。"
        )
        mobile_hint.setWordWrap(True)
        mobile_hint.setObjectName(
            "statusLabel"
        )
        ui_layout.addWidget(
            mobile_hint
        )

        layout.addWidget(
            ui_card
        )

        # Diagnostics card
        diag_card = QFrame()
        diag_card.setObjectName(
            "card"
        )

        diag_layout = QVBoxLayout(
            diag_card
        )
        diag_layout.setContentsMargins(
            25,
            20,
            25,
            20,
        )

        diag_title = QLabel(
            "诊断与首次启动"
        )
        diag_title.setObjectName(
            "cardTitle"
        )
        diag_layout.addWidget(
            diag_title
        )

        diag_buttons = QHBoxLayout()

        log_button = QPushButton(
            "打开日志目录"
        )
        log_button.setObjectName(
            "secondaryButton"
        )
        log_button.clicked.connect(
            self.open_logs_requested.emit
        )

        wizard_button = QPushButton(
            "重新运行首次启动向导"
        )
        wizard_button.setObjectName(
            "secondaryButton"
        )
        wizard_button.clicked.connect(
            self.rerun_onboarding_requested.emit
        )

        diag_buttons.addWidget(
            log_button
        )
        diag_buttons.addWidget(
            wizard_button
        )
        diag_buttons.addStretch()

        diag_layout.addLayout(
            diag_buttons
        )

        self.secret_status_label = QLabel()
        self.secret_status_label.setWordWrap(
            True
        )
        self.secret_status_label.setObjectName(
            "statusLabel"
        )
        diag_layout.addWidget(
            self.secret_status_label
        )

        layout.addWidget(
            diag_card
        )

        layout.addStretch()

    def set_system_info(
        self,
        *,
        schema_version: int,
        database_path: str,
        ui_mode: str,
        secret_persistent: bool,
    ):
        self.schema_label.setText(
            f"数据库 Schema Version：{schema_version}"
        )
        self.database_path_label.setText(
            f"数据库位置：{database_path}"
        )

        index = self.ui_mode_combo.findData(
            ui_mode
        )

        if index >= 0:
            self.ui_mode_combo.blockSignals(
                True
            )
            self.ui_mode_combo.setCurrentIndex(
                index
            )
            self.ui_mode_combo.blockSignals(
                False
            )

        if secret_persistent:
            self.secret_status_label.setText(
                "API Key：使用系统凭据管理器持久保存。"
            )
        else:
            self.secret_status_label.setText(
                "API Key：当前平台仅保存在本次运行内存中，关闭应用后需要重新输入。"
            )

    def _emit_ui_mode(self):
        mode = self.ui_mode_combo.currentData()

        if mode:
            self.ui_mode_changed.emit(
                str(mode)
            )
