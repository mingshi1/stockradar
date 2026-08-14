from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.trend_chart import TrendChart


class StatsPage(QWidget):
    sector_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            45,
            28,
            45,
            28,
        )
        layout.setSpacing(14)

        title = QLabel(
            "数据统计与历史趋势"
        )
        title.setObjectName(
            "pageTitle"
        )

        description = QLabel(
            "查看板块事件评分变化、AI Provider 耗时、成功率、Token 和用户配置价格下的成本估算。"
        )
        description.setWordWrap(True)
        description.setObjectName(
            "pageDescription"
        )

        layout.addWidget(title)
        layout.addWidget(description)

        # =====================================================
        # Sector trend
        # =====================================================
        trend_card = QFrame()
        trend_card.setObjectName("card")

        trend_layout = QVBoxLayout(
            trend_card
        )
        trend_layout.setContentsMargins(
            22,
            16,
            22,
            16,
        )
        trend_layout.setSpacing(8)

        trend_header = QHBoxLayout()

        trend_title = QLabel(
            "板块事件评分趋势"
        )
        trend_title.setObjectName(
            "cardTitle"
        )

        trend_header.addWidget(
            trend_title
        )
        trend_header.addStretch()

        trend_header.addWidget(
            QLabel("板块")
        )

        self.sector_combo = QComboBox()
        self.sector_combo.setMinimumWidth(
            180
        )
        self.sector_combo.currentTextChanged.connect(
            self.sector_changed.emit
        )

        trend_header.addWidget(
            self.sector_combo
        )

        trend_layout.addLayout(
            trend_header
        )

        self.trend_chart = TrendChart()
        trend_layout.addWidget(
            self.trend_chart
        )

        self.trend_summary = QLabel(
            "暂无趋势数据"
        )
        self.trend_summary.setObjectName(
            "statusLabel"
        )
        trend_layout.addWidget(
            self.trend_summary
        )

        layout.addWidget(
            trend_card
        )

        # =====================================================
        # Provider stats
        # =====================================================
        provider_card = QFrame()
        provider_card.setObjectName(
            "card"
        )

        provider_layout = QVBoxLayout(
            provider_card
        )
        provider_layout.setContentsMargins(
            22,
            16,
            22,
            16,
        )

        provider_title = QLabel(
            "Provider 性能与用量"
        )
        provider_title.setObjectName(
            "cardTitle"
        )
        provider_layout.addWidget(
            provider_title
        )

        self.provider_table = QTableWidget(
            0,
            8,
        )
        self.provider_table.setHorizontalHeaderLabels([
            "Provider",
            "调用",
            "成功率",
            "平均耗时",
            "Input Tokens",
            "Output Tokens",
            "Total Tokens",
            "估算成本*",
        ])
        self.provider_table.verticalHeader().setVisible(
            False
        )
        self.provider_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        header = (
            self.provider_table
            .horizontalHeader()
        )
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )

        for column in range(
            1,
            8,
        ):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )

        provider_layout.addWidget(
            self.provider_table
        )

        note = QLabel(
            "* 成本来自你在 AI 设置中填写的每百万 Token 单价；未定价的调用不会被强行估算。"
        )
        note.setObjectName(
            "statusLabel"
        )
        provider_layout.addWidget(note)

        layout.addWidget(
            provider_card,
            1,
        )

    def set_sector_names(
        self,
        names: list[str],
    ):
        current = (
            self.sector_combo
            .currentText()
        )

        self.sector_combo.blockSignals(
            True
        )
        self.sector_combo.clear()
        self.sector_combo.addItems(
            names
        )

        if current in names:
            self.sector_combo.setCurrentText(
                current
            )

        self.sector_combo.blockSignals(
            False
        )

    def current_sector(self) -> str:
        return (
            self.sector_combo
            .currentText()
        )

    def set_trend(
        self,
        points: list[dict],
    ):
        self.trend_chart.set_points(
            points
        )

        if not points:
            self.trend_summary.setText(
                "暂无趋势数据。完成多次分析后，这里会形成时间序列。"
            )
            return

        first = float(
            points[0].get(
                "score",
                0,
            )
        )
        last = float(
            points[-1].get(
                "score",
                0,
            )
        )
        change = last - first

        avg_agreement = sum(
            float(
                point.get(
                    "agreement",
                    0,
                )
            )
            for point in points
        ) / len(points)

        self.trend_summary.setText(
            f"样本 {len(points)} 次 ｜ "
            f"首期 {first:+.1f} → 最新 {last:+.1f} ｜ "
            f"变化 {change:+.1f} ｜ "
            f"平均 AI 一致度 {avg_agreement:.1f}%"
        )

    def set_provider_stats(
        self,
        stats: list[dict],
    ):
        self.provider_table.setRowCount(
            0
        )

        for item in stats:
            row = (
                self.provider_table
                .rowCount()
            )
            self.provider_table.insertRow(
                row
            )

            calls = int(
                item.get(
                    "call_count",
                    0,
                )
                or 0
            )
            success = int(
                item.get(
                    "success_count",
                    0,
                )
                or 0
            )
            success_rate = (
                success / calls * 100
                if calls
                else 0.0
            )
            avg_ms = float(
                item.get(
                    "avg_duration_ms",
                    0,
                )
                or 0
            )

            priced_calls = int(
                item.get(
                    "priced_call_count",
                    0,
                )
                or 0
            )

            cost_text = (
                f"{float(item.get('estimated_cost', 0) or 0):.6f}"
                if priced_calls > 0
                else "—"
            )

            values = [
                str(
                    item.get(
                        "provider",
                        "",
                    )
                ),
                f"{calls:,}",
                f"{success_rate:.1f}%",
                f"{avg_ms / 1000:.1f}s",
                f"{int(item.get('input_tokens', 0) or 0):,}",
                f"{int(item.get('output_tokens', 0) or 0):,}",
                f"{int(item.get('total_tokens', 0) or 0):,}",
                cost_text,
            ]

            for column, value in enumerate(
                values
            ):
                self.provider_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(value),
                )
