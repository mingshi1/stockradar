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
    saved_report_requested = Signal(int)

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            40,
            25,
            40,
            25,
        )
        layout.setSpacing(12)

        title = QLabel(
            "晨报与报告中心"
        )
        title.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "当前版本 生成预览时会自动归档到 SQLite；同一分析记录 + 同一报告类型会更新，不会无限重复。"
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
            22,
            15,
            22,
            15,
        )
        control_layout.setSpacing(10)

        control_title = QLabel(
            "生成报告"
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
            "生成并归档"
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

        second_row.addWidget(
            QLabel("已归档")
        )

        self.archive_combo = QComboBox()
        second_row.addWidget(
            self.archive_combo,
            2,
        )

        open_archive_button = QPushButton(
            "打开归档"
        )
        open_archive_button.setObjectName(
            "secondaryButton"
        )
        open_archive_button.clicked.connect(
            self._open_archive
        )
        second_row.addWidget(
            open_archive_button
        )

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
            button = QPushButton(text)
            button.setObjectName(
                "secondaryButton"
            )
            button.clicked.connect(
                lambda checked=False,
                f=fmt:
                self.export_requested.emit(f)
            )
            second_row.addWidget(button)

        control_layout.addLayout(
            second_row
        )

        hint = QLabel(
            "30秒晨报和报告归档均基于已有分析结果本地生成，不额外调用 AI。"
        )
        hint.setObjectName(
            "statusLabel"
        )
        control_layout.addWidget(
            hint
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
            20,
            14,
            20,
            14,
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
            "选择历史分析后点击“生成并归档”，或打开已有归档。"
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
            index = self.run_combo.findData(
                current_id
            )

            if index >= 0:
                self.run_combo.setCurrentIndex(
                    index
                )

        self.run_combo.blockSignals(
            False
        )

    def set_saved_reports(
        self,
        reports: list[dict],
    ):
        current_id = (
            self.archive_combo.currentData()
            if self.archive_combo.count()
            else None
        )

        self.archive_combo.blockSignals(
            True
        )
        self.archive_combo.clear()

        for report in reports:
            updated = str(
                report.get(
                    "updated_at",
                    "",
                )
            ).replace(
                "T",
                " ",
            )[:16]

            self.archive_combo.addItem(
                f"{updated} ｜ "
                f"{report.get('title', '')}",
                int(report["id"]),
            )

        if current_id is not None:
            index = self.archive_combo.findData(
                current_id
            )

            if index >= 0:
                self.archive_combo.setCurrentIndex(
                    index
                )

        self.archive_combo.blockSignals(
            False
        )

    def _generate(self):
        run_id = self.run_combo.currentData()

        if run_id is None:
            QMessageBox.information(
                self,
                "没有历史分析",
                "请先完成至少一次板块分析。",
            )
            return

        self.generate_requested.emit(
            int(run_id),
            str(
                self.type_combo.currentData()
            ),
        )

    def _open_archive(self):
        report_id = (
            self.archive_combo
            .currentData()
        )

        if report_id is None:
            QMessageBox.information(
                self,
                "没有归档报告",
                "请先生成并归档一份报告。",
            )
            return

        self.saved_report_requested.emit(
            int(report_id)
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
