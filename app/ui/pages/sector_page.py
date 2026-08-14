from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class SectorPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)

        title = QLabel("板块管理")
        title.setObjectName("pageTitle")

        description = QLabel(
            "后续版本会允许新增、删除、分组和保存自定义板块。"
        )
        description.setWordWrap(True)
        description.setObjectName("pageDescription")

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()
