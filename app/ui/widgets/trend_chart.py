from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QFontMetrics,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QWidget


class TrendChart(QWidget):
    """
    轻量趋势图，不引入 matplotlib / QtCharts。
    Y 轴固定 -100 ~ +100，与事件评分定义一致。
    """

    def __init__(self):
        super().__init__()

        self.points: list[dict] = []
        self.setMinimumHeight(260)

    def set_points(
        self,
        points: list[dict],
    ):
        self.points = list(points)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        rect = self.rect()
        painter.fillRect(
            rect,
            Qt.GlobalColor.white,
        )

        left = 52
        right = 18
        top = 18
        bottom = 38

        plot = QRectF(
            left,
            top,
            max(
                10,
                rect.width() - left - right,
            ),
            max(
                10,
                rect.height() - top - bottom,
            ),
        )

        # Grid / axis.
        grid_pen = QPen(
            Qt.GlobalColor.lightGray
        )
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)

        for score in (
            -100,
            -50,
            0,
            50,
            100,
        ):
            y = self._score_to_y(
                score,
                plot,
            )

            painter.drawLine(
                QPointF(
                    plot.left(),
                    y,
                ),
                QPointF(
                    plot.right(),
                    y,
                ),
            )

            painter.setPen(
                Qt.GlobalColor.darkGray
            )
            painter.drawText(
                QRectF(
                    4,
                    y - 10,
                    42,
                    20,
                ),
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter,
                str(score),
            )
            painter.setPen(grid_pen)

        if not self.points:
            painter.setPen(
                Qt.GlobalColor.darkGray
            )
            painter.drawText(
                plot,
                Qt.AlignmentFlag.AlignCenter,
                "No trend data",
            )
            return

        count = len(self.points)

        def x_for(index: int) -> float:
            if count <= 1:
                return plot.center().x()

            return (
                plot.left()
                + index
                / (count - 1)
                * plot.width()
            )

        line_pen = QPen(
            Qt.GlobalColor.darkBlue
        )
        line_pen.setWidth(2)
        painter.setPen(line_pen)

        path = QPainterPath()

        for index, point in enumerate(
            self.points
        ):
            x = x_for(index)
            y = self._score_to_y(
                float(
                    point.get(
                        "score",
                        0,
                    )
                ),
                plot,
            )

            if index == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

        painter.drawPath(path)

        painter.setBrush(
            Qt.GlobalColor.darkBlue
        )

        for index, point in enumerate(
            self.points
        ):
            x = x_for(index)
            y = self._score_to_y(
                float(
                    point.get(
                        "score",
                        0,
                    )
                ),
                plot,
            )

            painter.drawEllipse(
                QPointF(x, y),
                3.5,
                3.5,
            )

        # Only draw a few dates to avoid overlap.
        painter.setPen(
            Qt.GlobalColor.darkGray
        )
        date_indexes = sorted({
            0,
            count // 2,
            count - 1,
        })

        metrics = QFontMetrics(
            painter.font()
        )

        for index in date_indexes:
            value = str(
                self.points[index].get(
                    "created_at",
                    "",
                )
            ).replace(
                "T",
                " ",
            )

            label = value[:10]
            width = metrics.horizontalAdvance(
                label
            )

            painter.drawText(
                QPointF(
                    x_for(index)
                    - width / 2,
                    plot.bottom() + 24,
                ),
                label,
            )

    @staticmethod
    def _score_to_y(
        score: float,
        plot: QRectF,
    ) -> float:
        score = max(
            -100.0,
            min(
                100.0,
                score,
            ),
        )

        ratio = (
            score + 100.0
        ) / 200.0

        return (
            plot.bottom()
            - ratio
            * plot.height()
        )
