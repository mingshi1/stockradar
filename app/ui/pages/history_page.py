from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from app.platform import is_android


class HistoryPage(QWidget):
    run_selected = Signal(int)

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            14 if is_android() else 50,
            12 if is_android() else 35,
            14 if is_android() else 50,
            18 if is_android() else 35,
        )
        layout.setSpacing(
            10 if is_android() else 15
        )

        title = QLabel(
            "历史报告"
        )
        title.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "每次成功分析都会自动保存到 SQLite。"
        )
        description.setObjectName(
            "pageDescription"
        )
        description.setWordWrap(
            True
        )

        layout.addWidget(
            title
        )
        layout.addWidget(
            description
        )

        # On Android, construct the correct direction immediately.
        # This is more reliable than changing a desktop HBox direction
        # after the widget is already inside a QScrollArea.
        if is_android():
            self.content_layout = QVBoxLayout()
        else:
            self.content_layout = QHBoxLayout()

        self.content_layout.setSpacing(
            10 if is_android() else 12
        )

        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(
            self._current_changed
        )

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(
            True
        )
        self.browser.setPlaceholderText(
            (
                "选择上方历史记录查看完整报告。"
                if is_android()
                else "选择左侧历史记录查看完整报告。"
            )
        )

        if is_android():
            self.list_widget.setMaximumWidth(
                16777215
            )
            self.list_widget.setMinimumHeight(
                150
            )
            self.list_widget.setMaximumHeight(
                210
            )
            self.browser.setMinimumHeight(
                620
            )
        else:
            self.list_widget.setMaximumWidth(
                360
            )

        self.content_layout.addWidget(
            self.list_widget,
            0,
        )
        self.content_layout.addWidget(
            self.browser,
            1,
        )

        layout.addLayout(
            self.content_layout,
            0 if is_android() else 1,
        )

    def set_mobile_mode(
        self,
        mobile: bool,
    ):
        # Keep support for manually choosing mobile UI on desktop,
        # while Android is already created vertically in _build_ui().
        if mobile:
            self.content_layout.setDirection(
                QBoxLayout.Direction.TopToBottom
            )
            self.list_widget.setMaximumWidth(
                16777215
            )
            self.list_widget.setMinimumHeight(
                150
            )
            self.list_widget.setMaximumHeight(
                210
            )
            self.browser.setMinimumHeight(
                620
            )
        else:
            self.content_layout.setDirection(
                QBoxLayout.Direction.LeftToRight
            )
            self.list_widget.setMaximumWidth(
                360
            )
            self.list_widget.setMinimumHeight(
                0
            )
            self.list_widget.setMaximumHeight(
                16777215
            )
            self.browser.setMinimumHeight(
                0
            )

    def set_runs(
        self,
        runs: list[dict],
    ):
        self.list_widget.clear()

        for run in runs:
            sectors = "、".join(
                run.get(
                    "sectors",
                    [],
                )
            )
            created = str(
                run.get(
                    "created_at",
                    "",
                )
            ).replace(
                "T",
                " ",
            )

            provider_count = int(
                run.get(
                    "provider_count",
                    0,
                )
                or 0
            )

            mode_text = (
                f"Multi-AI · {provider_count} 模型"
                if provider_count >= 2
                else (
                    f"{run.get('provider', '')} · "
                    f"{run.get('model', '')}"
                )
            )

            item = QListWidgetItem(
                f"{created}\n"
                f"{sectors}\n"
                f"{mode_text}"
            )
            item.setData(
                1000,
                int(run["id"]),
            )
            self.list_widget.addItem(
                item
            )

    def _current_changed(
        self,
        current,
        previous,
    ):
        if current is None:
            return

        run_id = current.data(
            1000
        )

        if run_id is not None:
            self.run_selected.emit(
                int(run_id)
            )

    def show_report(
        self,
        html_content: str,
    ):
        self.browser.setHtml(
            html_content
        )
