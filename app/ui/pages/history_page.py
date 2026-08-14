from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class HistoryPage(QWidget):
    run_selected = Signal(int)

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 35, 50, 35)
        layout.setSpacing(15)

        title = QLabel("历史报告")
        title.setObjectName("pageTitle")

        description = QLabel(
            "每次成功分析都会自动保存到 SQLite。"
        )
        description.setObjectName("pageDescription")

        layout.addWidget(title)
        layout.addWidget(description)

        content = QHBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.setMaximumWidth(360)
        self.list_widget.currentItemChanged.connect(
            self._current_changed
        )

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setPlaceholderText(
            "选择左侧历史记录查看完整报告。"
        )

        content.addWidget(self.list_widget)
        content.addWidget(self.browser, 1)

        layout.addLayout(content, 1)

    def set_runs(self, runs: list[dict]):
        self.list_widget.clear()

        for run in runs:
            sectors = "、".join(run.get("sectors", []))
            created = str(run.get("created_at", "")).replace(
                "T",
                " ",
            )

            provider_count = int(
                run.get("provider_count", 0) or 0
            )

            mode_text = (
                f"Multi-AI · {provider_count} 模型"
                if provider_count >= 2
                else f"{run.get('provider', '')} · {run.get('model', '')}"
            )

            item = QListWidgetItem(
                f"{created}\n"
                f"{sectors}\n"
                f"{mode_text}"
            )
            item.setData(1000, int(run["id"]))
            self.list_widget.addItem(item)

    def _current_changed(self, current, previous):
        if current is None:
            return

        run_id = current.data(1000)
        if run_id is not None:
            self.run_selected.emit(int(run_id))

    def show_report(self, html_content: str):
        self.browser.setHtml(html_content)
