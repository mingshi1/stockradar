from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)

        title = QLabel("历史报告")
        title.setObjectName("pageTitle")

        description = QLabel(
            "V0.5 会在这里接入 SQLite，保存并查询过去的分析记录。"
        )
        description.setWordWrap(True)
        description.setObjectName("pageDescription")

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()
