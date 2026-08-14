import html

from PySide6.QtWidgets import (
    QLabel,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from app.news.models import ResearchSnapshot


class NewsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(18)

        title = QLabel("新闻源")
        title.setObjectName("pageTitle")

        description = QLabel(
            "V0.4 先显示最近一次 AI 联网搜索得到的原始研究资料。"
            "V0.5 会把它升级成逐条新闻 Event Pool。"
        )
        description.setWordWrap(True)
        description.setObjectName("pageDescription")

        self.meta_label = QLabel(
            "尚未产生联网研究资料"
        )
        self.meta_label.setObjectName("statusLabel")

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setPlaceholderText(
            "完成一次“今日分析”后，这里会显示搜索阶段的原始资料。"
        )

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.meta_label)
        layout.addWidget(self.browser, 1)

    def set_snapshot(self, snapshot: ResearchSnapshot):
        sectors = "、".join(snapshot.sectors)
        time_text = snapshot.created_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        self.meta_label.setText(
            f"{time_text} ｜ {snapshot.provider} ｜ "
            f"{snapshot.model} ｜ {sectors}"
        )

        safe_text = html.escape(snapshot.text).replace(
            "\n",
            "<br>",
        )

        self.browser.setHtml(
            f"""
            <div style="
                font-family:'Microsoft YaHei';
                line-height:1.65;
                color:#1f2937;
            ">
                {safe_text}
            </div>
            """
        )
