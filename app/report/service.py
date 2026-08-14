import html
import json
import re
from datetime import datetime

from app.report.html_renderer import render_analysis_html
from app.report.models import ReportArtifact


class ReportService:
    """
    将 SQLite 中已经保存的分析结果转换成不同层级的研究报告。

    V0.7 的晨报不额外调用 AI：
    它只是对已完成的 Multi-AI 共识结果做确定性压缩，
    因此没有额外 API 成本。
    """

    REPORT_TYPES = {
        "morning": "30秒晨报",
        "standard": "标准报告",
        "consensus": "Multi-AI共识报告",
        "deep": "深度研究报告",
    }

    def generate(
        self,
        run: dict,
        provider_results: list[dict],
        report_type: str,
    ) -> ReportArtifact:
        if report_type not in self.REPORT_TYPES:
            raise ValueError(
                f"未知报告类型：{report_type}"
            )

        if report_type == "morning":
            return self._morning_report(
                run,
            )

        if report_type == "standard":
            return self._standard_report(
                run,
            )

        if report_type == "consensus":
            return self._consensus_report(
                run,
                provider_results,
            )

        return self._deep_report(
            run,
            provider_results,
        )

    # =========================================================
    # 30 秒晨报
    # =========================================================

    def _morning_report(
        self,
        run: dict,
    ) -> ReportArtifact:
        data = run["result"]
        created = self._display_time(
            run.get("created_at", "")
        )

        sectors = list(
            data.get(
                "sectors",
                [],
            )
        )

        sectors.sort(
            key=lambda item: abs(
                self._safe_float(
                    item.get(
                        "score",
                        0,
                    )
                )
            ),
            reverse=True,
        )

        top_sectors = sectors[:6]

        event_candidates = []

        for sector in sectors:
            sector_name = str(
                sector.get(
                    "sector",
                    "",
                )
            )

            for event in sector.get(
                "events",
                [],
            ):
                event_candidates.append(
                    {
                        "sector": sector_name,
                        "title": str(
                            event.get(
                                "title",
                                "",
                            )
                        ),
                        "importance": self._safe_float(
                            event.get(
                                "importance",
                                0,
                            )
                        ),
                        "impact": str(
                            event.get(
                                "impact",
                                "",
                            )
                        ),
                        "source": str(
                            event.get(
                                "source",
                                "",
                            )
                        ),
                    }
                )

        event_candidates.sort(
            key=lambda item: item[
                "importance"
            ],
            reverse=True,
        )

        top_events = event_candidates[:5]

        title = (
            f"AI板块事件晨报｜{created}"
        )

        plain_lines = [
            title,
            "",
            "【市场摘要】",
            str(
                data.get(
                    "market_summary",
                    "",
                )
            ).strip(),
            "",
            "【板块雷达】",
        ]

        for sector in top_sectors:
            score = self._safe_float(
                sector.get(
                    "score",
                    0,
                )
            )
            agreement = sector.get(
                "agreement"
            )

            agreement_text = (
                f"｜一致度 {agreement}%"
                if agreement is not None
                else ""
            )

            plain_lines.append(
                f"{sector.get('sector', '')} "
                f"{score:+.1f} "
                f"{sector.get('direction', '中性')}"
                f"{agreement_text}"
            )

        plain_lines.extend([
            "",
            "【核心事件】",
        ])

        if top_events:
            for index, event in enumerate(
                top_events,
                start=1,
            ):
                plain_lines.append(
                    f"{index}. "
                    f"[{event['sector']}] "
                    f"{event['title']} "
                    f"({event['source']})"
                )
        else:
            plain_lines.append(
                "暂无明显重大新增事件。"
            )

        plain_lines.extend([
            "",
            "仅用于信息研究，不构成投资建议。",
        ])

        plain_summary = "\n".join(
            plain_lines
        )

        html_parts = [
            "<html><body style="
            "\"font-family:'Microsoft YaHei';"
            "color:#1f2937;line-height:1.6;\">",
            f"<h1>{html.escape(title)}</h1>",
            """
            <div style="
                background:#eff6ff;
                padding:16px;
                border-radius:10px;
                margin-bottom:18px;
            ">
                <b>市场摘要</b>
            """,
            f"<p>{html.escape(str(data.get('market_summary', '')))}</p>",
            "</div>",
            "<h2>板块雷达</h2>",
            """
            <table cellspacing="0" cellpadding="7"
                style="border-collapse:collapse;width:100%;">
                <tr>
                    <th align="left">板块</th>
                    <th>评分</th>
                    <th>方向</th>
                    <th>AI一致度</th>
                </tr>
            """,
        ]

        for sector in top_sectors:
            score = self._safe_float(
                sector.get(
                    "score",
                    0,
                )
            )
            agreement = sector.get(
                "agreement",
                "-",
            )

            html_parts.append(
                f"""
                <tr>
                    <td>{html.escape(str(sector.get("sector", "")))}</td>
                    <td align="center">{score:+.1f}</td>
                    <td align="center">{html.escape(str(sector.get("direction", "中性")))}</td>
                    <td align="center">{agreement}%</td>
                </tr>
                """
            )

        html_parts.append(
            "</table><h2>核心事件</h2>"
        )

        if top_events:
            html_parts.append("<ol>")

            for event in top_events:
                html_parts.append(
                    "<li>"
                    f"<b>{html.escape(event['sector'])}</b>｜"
                    f"{html.escape(event['title'])}"
                    f" <span style='color:#6b7280;'>"
                    f"{html.escape(event['source'])}</span>"
                    "</li>"
                )

            html_parts.append("</ol>")
        else:
            html_parts.append(
                "<p>暂无明显重大新增事件。</p>"
            )

        html_parts.append(
            """
            <p style="color:#9ca3af;font-size:12px;">
                本晨报由已完成的分析结果自动压缩生成，
                不额外调用 AI，不构成投资建议。
            </p>
            </body></html>
            """
        )

        markdown = self._morning_markdown(
            title=title,
            data=data,
            sectors=top_sectors,
            events=top_events,
        )

        return ReportArtifact(
            title=title,
            report_type="morning",
            html="".join(html_parts),
            markdown=markdown,
            plain_summary=plain_summary,
        )

    # =========================================================
    # 标准报告
    # =========================================================

    def _standard_report(
        self,
        run: dict,
    ) -> ReportArtifact:
        created = self._display_time(
            run.get("created_at", "")
        )
        title = (
            f"AI板块事件标准报告｜{created}"
        )

        data = run["result"]

        body_fragment = self._body_fragment(
            render_analysis_html(data)
        )

        html_content = (
            "<html><body style="
            "\"font-family:'Microsoft YaHei';"
            "color:#1f2937;line-height:1.6;\">"
            f"<h1>{html.escape(title)}</h1>"
            + body_fragment
            + "</body></html>"
        )

        markdown = self._standard_markdown(
            title,
            data,
        )

        plain_summary = self._plain_summary(
            title,
            data,
        )

        return ReportArtifact(
            title=title,
            report_type="standard",
            html=html_content,
            markdown=markdown,
            plain_summary=plain_summary,
        )

    # =========================================================
    # Multi-AI 共识报告
    # =========================================================

    def _consensus_report(
        self,
        run: dict,
        provider_results: list[dict],
    ) -> ReportArtifact:
        data = run["result"]
        created = self._display_time(
            run.get("created_at", "")
        )
        title = (
            f"Multi-AI共识报告｜{created}"
        )

        providers = data.get(
            "providers_used",
            [],
        )

        parts = [
            "<html><body style="
            "\"font-family:'Microsoft YaHei';"
            "color:#1f2937;line-height:1.6;\">",
            f"<h1>{html.escape(title)}</h1>",
            "<p><b>参与模型：</b>"
            + html.escape(
                "、".join(
                    str(item)
                    for item in providers
                )
            )
            + "</p>",
            "<p>"
            + html.escape(
                str(
                    data.get(
                        "market_summary",
                        "",
                    )
                )
            )
            + "</p>",
        ]

        md_lines = [
            f"# {title}",
            "",
            f"**参与模型：** {'、'.join(str(x) for x in providers)}",
            "",
            str(
                data.get(
                    "market_summary",
                    "",
                )
            ),
            "",
        ]

        for sector in data.get(
            "sectors",
            [],
        ):
            sector_name = str(
                sector.get(
                    "sector",
                    "",
                )
            )
            score = sector.get(
                "score",
                0,
            )
            agreement = sector.get(
                "agreement",
                "-",
            )
            dispersion = sector.get(
                "dispersion",
                "-",
            )

            parts.append(
                f"""
                <div style="
                    border:1px solid #e5e7eb;
                    border-radius:10px;
                    padding:16px;
                    margin:16px 0;
                ">
                    <h2>{html.escape(sector_name)}</h2>
                    <p>
                        <b>共识评分：</b>{score}
                        &nbsp;&nbsp;
                        <b>方向：</b>{html.escape(str(sector.get("direction", "")))}
                        &nbsp;&nbsp;
                        <b>一致度：</b>{agreement}%
                        &nbsp;&nbsp;
                        <b>离散度：</b>{dispersion}
                    </p>
                """
            )

            md_lines.extend([
                f"## {sector_name}",
                "",
                f"- 共识评分：{score}",
                f"- 方向：{sector.get('direction', '')}",
                f"- 一致度：{agreement}%",
                f"- 离散度：{dispersion}",
                "",
            ])

            views = sector.get(
                "provider_views",
                [],
            )

            if views:
                parts.append(
                    """
                    <table cellspacing="0" cellpadding="6"
                        style="border-collapse:collapse;width:100%;">
                        <tr>
                            <th align="left">模型</th>
                            <th>评分</th>
                            <th>方向</th>
                            <th>置信度</th>
                        </tr>
                    """
                )

                md_lines.extend([
                    "| 模型 | 评分 | 方向 | 置信度 |",
                    "|---|---:|---|---:|",
                ])

                for view in views:
                    parts.append(
                        f"""
                        <tr>
                            <td>{html.escape(str(view.get("provider", "")))}</td>
                            <td align="center">{view.get("score", "")}</td>
                            <td align="center">{html.escape(str(view.get("direction", "")))}</td>
                            <td align="center">{view.get("confidence", "")}%</td>
                        </tr>
                        """
                    )

                    md_lines.append(
                        f"| {view.get('provider', '')} "
                        f"| {view.get('score', '')} "
                        f"| {view.get('direction', '')} "
                        f"| {view.get('confidence', '')}% |"
                    )

                parts.append("</table>")
                md_lines.append("")

            agreements = sector.get(
                "key_agreements",
                [],
            )
            disagreements = sector.get(
                "key_disagreements",
                [],
            )

            if agreements:
                parts.append(
                    "<p><b>核心共识</b></p><ul>"
                )

                md_lines.extend([
                    "**核心共识**",
                    "",
                ])

                for item in agreements:
                    parts.append(
                        f"<li>{html.escape(str(item))}</li>"
                    )
                    md_lines.append(
                        f"- {item}"
                    )

                parts.append("</ul>")
                md_lines.append("")

            if disagreements:
                parts.append(
                    "<p><b>核心分歧</b></p><ul>"
                )

                md_lines.extend([
                    "**核心分歧**",
                    "",
                ])

                for item in disagreements:
                    parts.append(
                        f"<li>{html.escape(str(item))}</li>"
                    )
                    md_lines.append(
                        f"- {item}"
                    )

                parts.append("</ul>")
                md_lines.append("")

            parts.append(
                f"<p>{html.escape(str(sector.get('summary', '')))}</p></div>"
            )

        if provider_results:
            failed = [
                item
                for item in provider_results
                if item.get("error")
            ]

            if failed:
                parts.append(
                    "<h2>Provider 异常</h2><ul>"
                )
                md_lines.extend([
                    "## Provider 异常",
                    "",
                ])

                for item in failed:
                    text = (
                        f"{item.get('provider', '')}: "
                        f"{item.get('error', '')}"
                    )
                    parts.append(
                        f"<li>{html.escape(text)}</li>"
                    )
                    md_lines.append(
                        f"- {text}"
                    )

                parts.append("</ul>")
                md_lines.append("")

        parts.append(
            """
            <p style="color:#9ca3af;font-size:12px;">
                共识不代表正确，模型之间可能共享相似偏差。
                本报告仅用于信息研究，不构成投资建议。
            </p>
            </body></html>
            """
        )

        plain_summary = self._plain_summary(
            title,
            data,
        )

        return ReportArtifact(
            title=title,
            report_type="consensus",
            html="".join(parts),
            markdown="\n".join(md_lines),
            plain_summary=plain_summary,
        )

    # =========================================================
    # 深度研究报告
    # =========================================================

    def _deep_report(
        self,
        run: dict,
        provider_results: list[dict],
    ) -> ReportArtifact:
        standard = self._standard_report(
            run
        )

        created = self._display_time(
            run.get("created_at", "")
        )
        title = (
            f"AI板块事件深度研究报告｜{created}"
        )

        research_text = str(
            run.get(
                "research_text",
                "",
            )
        )

        provider_section_html = []
        provider_section_md = []

        for item in provider_results:
            provider = str(
                item.get(
                    "provider",
                    "",
                )
            )
            model = str(
                item.get(
                    "model",
                    "",
                )
            )
            error = item.get(
                "error"
            )
            result = item.get(
                "result"
            )

            provider_section_html.append(
                f"<h3>{html.escape(provider)} · {html.escape(model)}</h3>"
            )
            provider_section_md.extend([
                f"### {provider} · {model}",
                "",
            ])

            if error:
                provider_section_html.append(
                    f"<p style='color:#b91c1c;'>"
                    f"{html.escape(str(error))}</p>"
                )
                provider_section_md.append(
                    f"调用失败：{error}"
                )
            elif result:
                pretty = json.dumps(
                    result,
                    ensure_ascii=False,
                    indent=2,
                )

                provider_section_html.append(
                    "<pre style="
                    "'white-space:pre-wrap;"
                    "background:#f8fafc;"
                    "padding:12px;"
                    "border-radius:8px;'>"
                    + html.escape(pretty)
                    + "</pre>"
                )

                provider_section_md.extend([
                    "```json",
                    pretty,
                    "```",
                ])

            provider_section_md.append("")

        standard_fragment = self._body_fragment(
            standard.html
        )

        html_content = (
            "<html><body style="
            "\"font-family:'Microsoft YaHei';"
            "color:#1f2937;line-height:1.6;\">"
            f"<h1>{html.escape(title)}</h1>"
            "<h2>一、综合分析</h2>"
            + standard_fragment
            + "<hr><h2>二、原始联网研究证据</h2>"
            + "<pre style='white-space:pre-wrap;"
            "background:#f8fafc;padding:14px;"
            "border-radius:8px;'>"
            + html.escape(research_text)
            + "</pre>"
            + "<hr><h2>三、各模型原始结构化判断</h2>"
            + "".join(provider_section_html)
            + """
            <p style="color:#9ca3af;font-size:12px;">
                深度报告保留更多底层证据与模型输出，
                适合复核研究过程，不构成投资建议。
            </p>
            </body></html>
            """
        )

        markdown = "\n".join([
            f"# {title}",
            "",
            "## 一、综合分析",
            "",
            standard.markdown,
            "",
            "## 二、原始联网研究证据",
            "",
            research_text,
            "",
            "## 三、各模型原始结构化判断",
            "",
            *provider_section_md,
        ])

        return ReportArtifact(
            title=title,
            report_type="deep",
            html=html_content,
            markdown=markdown,
            plain_summary=standard.plain_summary,
        )

    # =========================================================
    # Helpers
    # =========================================================

    def _morning_markdown(
        self,
        *,
        title: str,
        data: dict,
        sectors: list[dict],
        events: list[dict],
    ) -> str:
        lines = [
            f"# {title}",
            "",
            "## 市场摘要",
            "",
            str(
                data.get(
                    "market_summary",
                    "",
                )
            ),
            "",
            "## 板块雷达",
            "",
            "| 板块 | 评分 | 方向 | AI一致度 |",
            "|---|---:|---|---:|",
        ]

        for sector in sectors:
            score = self._safe_float(
                sector.get(
                    "score",
                    0,
                )
            )
            agreement = sector.get(
                "agreement",
                "-",
            )

            lines.append(
                f"| {sector.get('sector', '')} "
                f"| {score:+.1f} "
                f"| {sector.get('direction', '中性')} "
                f"| {agreement}% |"
            )

        lines.extend([
            "",
            "## 核心事件",
            "",
        ])

        if events:
            for event in events:
                lines.append(
                    f"- **{event['sector']}**｜"
                    f"{event['title']} "
                    f"（{event['source']}）"
                )
        else:
            lines.append(
                "- 暂无明显重大新增事件。"
            )

        lines.extend([
            "",
            "> 本晨报由已完成分析结果自动压缩生成，不额外调用 AI，不构成投资建议。",
        ])

        return "\n".join(lines)

    def _standard_markdown(
        self,
        title: str,
        data: dict,
    ) -> str:
        lines = [
            f"# {title}",
            "",
            "## 整体消息面",
            "",
            str(
                data.get(
                    "market_summary",
                    "",
                )
            ),
            "",
        ]

        for sector in data.get(
            "sectors",
            [],
        ):
            lines.extend([
                f"## {sector.get('sector', '')}",
                "",
                f"- 方向：{sector.get('direction', '')}",
                f"- 事件评分：{sector.get('score', 0)}",
                f"- 置信度：{sector.get('confidence', 0)}%",
            ])

            if sector.get(
                "agreement"
            ) is not None:
                lines.extend([
                    f"- AI方向一致度：{sector.get('agreement')}%",
                    f"- 评分离散度：{sector.get('dispersion', '-')}",
                ])

            lines.extend([
                "",
                str(
                    sector.get(
                        "summary",
                        "",
                    )
                ),
                "",
            ])

            views = sector.get(
                "provider_views",
                [],
            )

            if views:
                lines.extend([
                    "### 各模型独立判断",
                    "",
                    "| 模型 | 评分 | 方向 | 置信度 |",
                    "|---|---:|---|---:|",
                ])

                for view in views:
                    lines.append(
                        f"| {view.get('provider', '')} "
                        f"| {view.get('score', '')} "
                        f"| {view.get('direction', '')} "
                        f"| {view.get('confidence', '')}% |"
                    )

                lines.append("")

            for index, event in enumerate(
                sector.get(
                    "events",
                    [],
                ),
                start=1,
            ):
                lines.extend([
                    f"### 事件 {index}：{event.get('title', '')}",
                    "",
                    f"- 日期：{event.get('date', '')}",
                    f"- 来源：{event.get('source', '')}",
                    f"- URL：{event.get('url', '')}",
                    f"- 影响：{event.get('impact', '')}",
                    f"- 重要度：{event.get('importance', '')}/5",
                    "",
                ])

                chain = event.get(
                    "transmission",
                    [],
                )

                if chain:
                    lines.extend([
                        "**传导链**",
                        "",
                        " → ".join(
                            str(item)
                            for item in chain
                        ),
                        "",
                    ])

                lines.extend([
                    str(
                        event.get(
                            "analysis",
                            "",
                        )
                    ),
                    "",
                ])

            risks = sector.get(
                "risks",
                [],
            )

            if risks:
                lines.extend([
                    "### 风险与反向因素",
                    "",
                ])

                for risk in risks:
                    lines.append(
                        f"- {risk}"
                    )

                lines.append("")

        lines.append(
            "> 本报告仅用于信息研究与技术演示，不构成投资建议。"
        )

        return "\n".join(lines)

    def _plain_summary(
        self,
        title: str,
        data: dict,
    ) -> str:
        lines = [
            title,
            str(
                data.get(
                    "market_summary",
                    "",
                )
            ),
            "",
        ]

        for sector in data.get(
            "sectors",
            [],
        ):
            score = self._safe_float(
                sector.get(
                    "score",
                    0,
                )
            )

            lines.append(
                f"{sector.get('sector', '')}: "
                f"{score:+.1f} "
                f"{sector.get('direction', '')}"
            )

        lines.extend([
            "",
            "仅用于信息研究，不构成投资建议。",
        ])

        return "\n".join(lines)


    @staticmethod
    def _body_fragment(
        html_content: str,
    ) -> str:
        text = re.sub(
            r"</?html[^>]*>",
            "",
            html_content,
            flags=re.IGNORECASE,
        )
        text = re.sub(
            r"</?body[^>]*>",
            "",
            text,
            flags=re.IGNORECASE,
        )
        return text.strip()

    @staticmethod
    def _display_time(
        value: str,
    ) -> str:
        if not value:
            return datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )

        return str(value).replace(
            "T",
            " ",
        )[:16]

    @staticmethod
    def _safe_float(
        value,
    ) -> float:
        try:
            return float(value)
        except Exception:
            return 0.0
