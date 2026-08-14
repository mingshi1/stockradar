import html


def render_analysis_html(data: dict) -> str:
    market_summary = html.escape(
        str(data.get("market_summary", ""))
    )

    parts: list[str] = []

    parts.append("""
    <html>
    <body style="
        font-family:'Microsoft YaHei';
        color:#1f2937;
    ">
    """)

    parts.append(
        f"""
        <div style="
            background:#f8fafc;
            padding:16px;
            border-radius:8px;
            margin-bottom:20px;
        ">
            <b>整体消息面</b>
            <p>{market_summary}</p>
        </div>
        """
    )

    for sector in data.get("sectors", []):
        sector_name = html.escape(
            str(sector.get("sector", ""))
        )
        direction = html.escape(
            str(sector.get("direction", "中性"))
        )
        score = sector.get("score", 0)
        confidence = sector.get("confidence", 0)
        summary = html.escape(
            str(sector.get("summary", ""))
        )

        try:
            numeric_score = int(score)
        except Exception:
            numeric_score = 0

        if numeric_score >= 10:
            score_color = "#b91c1c"
        elif numeric_score <= -10:
            score_color = "#047857"
        else:
            score_color = "#6b7280"

        parts.append(
            f"""
            <div style="
                border:1px solid #e5e7eb;
                border-radius:10px;
                padding:18px;
                margin-bottom:20px;
            ">
                <h2>{sector_name}</h2>
                <p>
                    <b>方向：</b> {direction}
                    &nbsp;&nbsp;
                    <b>事件评分：</b>
                    <span style="
                        color:{score_color};
                        font-weight:bold;
                    ">{score}</span>
                    &nbsp;&nbsp;
                    <b>置信度：</b> {confidence}%
                </p>
                <p>{summary}</p>
            """
        )

        events = sector.get("events", [])

        if not events:
            parts.append(
                """
                <p style="color:#6b7280;">
                    暂无明显重大新增事件。
                </p>
                """
            )

        for index, event in enumerate(events, start=1):
            title = html.escape(
                str(event.get("title", ""))
            )
            date = html.escape(
                str(event.get("date", ""))
            )
            source = html.escape(
                str(event.get("source", ""))
            )
            url = str(event.get("url", "")).strip()
            impact = html.escape(
                str(event.get("impact", ""))
            )
            impact_type = html.escape(
                str(event.get("impact_type", ""))
            )
            importance = event.get("importance", "")
            analysis = html.escape(
                str(event.get("analysis", ""))
            )

            parts.append(
                f"""
                <hr>
                <h3>事件 {index}：{title}</h3>
                <p>
                    <b>日期：</b> {date}
                    &nbsp;&nbsp;
                    <b>来源：</b> {source}
                </p>
                <p>
                    <b>影响：</b> {impact}
                    &nbsp;&nbsp;
                    <b>类型：</b> {impact_type}
                    &nbsp;&nbsp;
                    <b>重要度：</b> {importance}/5
                </p>
                """
            )

            if url.startswith("http"):
                safe_url = html.escape(url, quote=True)
                parts.append(
                    f"""
                    <p>
                        <a href="{safe_url}">
                            查看原始来源
                        </a>
                    </p>
                    """
                )

            transmission = event.get("transmission", [])

            if transmission:
                chain = " → ".join(
                    html.escape(str(item))
                    for item in transmission
                )
                parts.append(
                    f"""
                    <p>
                        <b>传导链：</b><br>
                        {chain}
                    </p>
                    """
                )

            parts.append(
                f"""
                <p>
                    <b>分析：</b><br>
                    {analysis}
                </p>
                """
            )

        risks = sector.get("risks", [])

        if risks:
            risk_text = "<br>".join(
                "• " + html.escape(str(risk))
                for risk in risks
            )

            parts.append(
                f"""
                <div style="
                    background:#fff7ed;
                    padding:12px;
                    border-radius:6px;
                    margin-top:15px;
                ">
                    <b>风险与反向因素</b>
                    <p>{risk_text}</p>
                </div>
                """
            )

        parts.append("</div>")

    parts.append(
        """
        <div style="
            color:#9ca3af;
            font-size:12px;
            margin-top:20px;
        ">
            本结果仅用于信息研究与技术演示，不构成投资建议。
        </div>
        </body>
        </html>
        """
    )

    return "".join(parts)
