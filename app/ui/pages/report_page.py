from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class ReportPage(QWidget):
    generate_requested = Signal(
        int,
        str,
    )
    export_requested = Signal(str)
    copy_requested = Signal()

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
        layout.setSpacing(15)

        title = QLabel(
            "晨报与报告中心"
        )
        title.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "从 SQLite 历史分析生成晨报、标准报告、"
            "Multi-AI 共识报告或深度研究报告，并可导出文件。"
        )
        description.setWordWrap(True)
        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(title)
        layout.addWidget(description)

        control_card = QFrame()
        control_card.setObjectName("card")

        control_layout = QVBoxLayout(
            control_card
        )
        control_layout.setContentsMargins(
            25,
            18,
            25,
            18,
        )
        control_layout.setSpacing(12)

        control_title = QLabel(
            "报告生成"
        )
        control_title.setObjectName(
            "cardTitle"
        )
        control_layout.addWidget(
            control_title
        )

        first_row = QHBoxLayout()

        first_row.addWidget(
            QLabel("分析记录")
        )

        self.run_combo = QComboBox()
        first_row.addWidget(
            self.run_combo,
            2,
        )

        first_row.addWidget(
            QLabel("报告类型")
        )

        self.type_combo = QComboBox()
        self.type_combo.addItem(
            "30秒晨报",
            "morning",
        )
        self.type_combo.addItem(
            "标准报告",
            "standard",
        )
        self.type_combo.addItem(
            "Multi-AI共识报告",
            "consensus",
        )
        self.type_combo.addItem(
            "深度研究报告",
            "deep",
        )

        first_row.addWidget(
            self.type_combo,
            1,
        )

        generate_button = QPushButton(
            "生成预览"
        )
        generate_button.setObjectName(
            "primaryButton"
        )
        generate_button.clicked.connect(
            self._generate
        )

        first_row.addWidget(
            generate_button
        )

        control_layout.addLayout(
            first_row
        )

        second_row = QHBoxLayout()

        hint = QLabel(
            "晨报基于已保存的分析结果本地生成，不额外调用 AI。"
        )
        hint.setObjectName(
            "statusLabel"
        )
        second_row.addWidget(hint)

        second_row.addStretch()

        copy_button = QPushButton(
            "复制摘要"
        )
        copy_button.setObjectName(
            "secondaryButton"
        )
        copy_button.clicked.connect(
            self.copy_requested.emit
        )
        second_row.addWidget(
            copy_button
        )

        for text, fmt in [
            ("Markdown", "markdown"),
            ("HTML", "html"),
            ("PDF", "pdf"),
            ("PNG长图", "png"),
        ]:
            button = QPushButton(
                text
            )
            button.setObjectName(
                "secondaryButton"
            )
            button.clicked.connect(
                lambda checked=False,
                f=fmt:
                self.export_requested.emit(f)
            )
            second_row.addWidget(
                button
            )

        control_layout.addLayout(
            second_row
        )

        layout.addWidget(
            control_card
        )

        preview_card = QFrame()
        preview_card.setObjectName(
            "card"
        )

        preview_layout = QVBoxLayout(
            preview_card
        )
        preview_layout.setContentsMargins(
            22,
            18,
            22,
            18,
        )

        self.preview_title = QLabel(
            "报告预览"
        )
        self.preview_title.setObjectName(
            "cardTitle"
        )
        preview_layout.addWidget(
            self.preview_title
        )

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(
            True
        )
        self.browser.setPlaceholderText(
            "选择历史分析后点击“生成预览”。"
        )

        preview_layout.addWidget(
            self.browser
        )

        layout.addWidget(
            preview_card,
            1,
        )

    def set_runs(
        self,
        runs: list[dict],
    ):
        current_id = (
            self.run_combo.currentData()
            if self.run_combo.count()
            else None
        )

        self.run_combo.blockSignals(
            True
        )
        self.run_combo.clear()

        for run in runs:
            created = str(
                run.get(
                    "created_at",
                    "",
                )
            ).replace(
                "T",
                " ",
            )[:16]

            sectors = "、".join(
                run.get(
                    "sectors",
                    [],
                )
            )

            provider_count = int(
                run.get(
                    "provider_count",
                    0,
                )
                or 0
            )

            label = (
                f"{created} ｜ "
                f"{sectors} ｜ "
                f"{max(provider_count, 1)}模型"
            )

            self.run_combo.addItem(
                label,
                int(run["id"]),
            )

        if current_id is not None:
            index = (
                self.run_combo.findData(
                    current_id
                )
            )

            if index >= 0:
                self.run_combo.setCurrentIndex(
                    index
                )

        self.run_combo.blockSignals(
            False
        )

    def _generate(self):
        run_id = (
            self.run_combo.currentData()
        )

        if run_id is None:
            QMessageBox.information(
                self,
                "没有历史分析",
                "请先完成至少一次板块分析。",
            )
            return

        report_type = (
            self.type_combo.currentData()
        )

        self.generate_requested.emit(
            int(run_id),
            str(report_type),
        )

    def show_artifact(
        self,
        title: str,
        html_content: str,
    ):
        self.preview_title.setText(
            title
        )
        self.browser.setHtml(
            html_content
        )
