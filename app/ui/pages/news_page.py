import html

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class NewsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.events_by_id: dict[int, dict] = {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 35, 50, 35)
        layout.setSpacing(15)

        title = QLabel("新闻事件池")
        title.setObjectName("pageTitle")

        description = QLabel(
            "这里显示已经保存到 SQLite 的结构化事件。"
            "同一标题、日期、来源的事件使用指纹做基础去重。"
        )
        description.setWordWrap(True)
        description.setObjectName("pageDescription")

        layout.addWidget(title)
        layout.addWidget(description)

        content = QHBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.setMaximumWidth(420)
        self.list_widget.currentItemChanged.connect(
            self._current_changed
        )

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setPlaceholderText(
            "选择左侧事件查看详情。"
        )

        content.addWidget(self.list_widget)
        content.addWidget(self.browser, 1)
        layout.addLayout(content, 1)

    def set_events(self, events: list[dict]):
        self.events_by_id = {
            int(event["id"]): event
            for event in events
        }

        self.list_widget.clear()

        for event in events:
            sectors = "、".join(
                event.get("sectors", [])
            )

            item = QListWidgetItem(
                f"{event.get('title', '')}\n"
                f"{event.get('event_date', '')} · "
                f"{event.get('source', '')}\n"
                f"{sectors}"
            )
            item.setData(1000, int(event["id"]))
            self.list_widget.addItem(item)

    def _current_changed(self, current, previous):
        if current is None:
            return

        event_id = current.data(1000)
        event = self.events_by_id.get(int(event_id))

        if not event:
            return

        title = html.escape(str(event.get("title", "")))
        event_date = html.escape(str(event.get("event_date", "")))
        source = html.escape(str(event.get("source", "")))
        analysis = html.escape(str(event.get("analysis", "")))
        sectors = html.escape(
            "、".join(event.get("sectors", []))
        )
        url = str(event.get("url", "")).strip()

        url_html = ""

        if url.startswith("http"):
            safe_url = html.escape(url, quote=True)
            url_html = (
                f'<p><a href="{safe_url}">'
                f'查看原始来源</a></p>'
            )

        self.browser.setHtml(
            f"""
            <h2>{title}</h2>
            <p>
                <b>日期：</b>{event_date}
                &nbsp;&nbsp;
                <b>来源：</b>{source}
            </p>
            <p><b>关联板块：</b>{sectors}</p>
            {url_html}
            <hr>
            <p><b>分析摘要</b></p>
            <p>{analysis}</p>
            """
        )
