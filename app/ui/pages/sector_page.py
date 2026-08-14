from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.pages.dashboard_page import DEFAULT_SECTORS


class SectorPage(QWidget):
    add_requested = Signal(str)
    delete_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 35, 50, 35)
        layout.setSpacing(18)

        title = QLabel("板块管理")
        title.setObjectName("pageTitle")

        description = QLabel(
            "默认板块由程序提供；你可以新增长期保存的自定义板块。"
        )
        description.setObjectName("pageDescription")

        layout.addWidget(title)
        layout.addWidget(description)

        default_card = QFrame()
        default_card.setObjectName("card")

        default_layout = QVBoxLayout(default_card)
        default_layout.setContentsMargins(25, 20, 25, 20)

        default_title = QLabel("默认板块")
        default_title.setObjectName("cardTitle")

        default_text = QLabel("、".join(DEFAULT_SECTORS))
        default_text.setWordWrap(True)

        default_layout.addWidget(default_title)
        default_layout.addWidget(default_text)
        layout.addWidget(default_card)

        custom_card = QFrame()
        custom_card.setObjectName("card")

        custom_layout = QVBoxLayout(custom_card)
        custom_layout.setContentsMargins(25, 20, 25, 20)

        custom_title = QLabel("我的自定义板块")
        custom_title.setObjectName("cardTitle")
        custom_layout.addWidget(custom_title)

        add_row = QHBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText(
            "例如：生物医药、机器人、创新药"
        )
        self.input.returnPressed.connect(self._add)

        add_button = QPushButton("保存板块")
        add_button.setObjectName("primaryButton")
        add_button.clicked.connect(self._add)

        add_row.addWidget(self.input, 1)
        add_row.addWidget(add_button)
        custom_layout.addLayout(add_row)

        self.list_widget = QListWidget()
        custom_layout.addWidget(self.list_widget)

        delete_row = QHBoxLayout()
        delete_row.addStretch()

        delete_button = QPushButton("删除选中板块")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(self._delete)

        delete_row.addWidget(delete_button)
        custom_layout.addLayout(delete_row)

        layout.addWidget(custom_card, 1)

    def set_sectors(self, sectors: list[str]):
        self.list_widget.clear()
        self.list_widget.addItems(sectors)

    def _add(self):
        name = " ".join(
            self.input.text().strip().split()
        )
        if name:
            self.add_requested.emit(name)

    def add_success(self):
        self.input.clear()

    def _delete(self):
        item = self.list_widget.currentItem()

        if item is None:
            QMessageBox.information(
                self,
                "没有选择",
                "请先选择一个要删除的自定义板块。",
            )
            return

        self.delete_requested.emit(
            item.text()
        )
