import html


def render_analysis_html(
    data: dict,
) -> str:
    market_summary = html.escape(
        str(
            data.get(
                "market_summary",
                "",
            )
        )
    )

    providers = [
        str(item)
        for item in data.get(
            "providers_used",
            [],
        )
    ]

    provider_errors = data.get(
        "provider_errors",
        {},
    )

    parts = [
        """
        <html>
        <body style="
            font-family:'Microsoft YaHei';
            color:#1f2937;
        ">
        """
    ]

    if providers:
        provider_text = html.escape(
            "、".join(providers)
        )

        parts.append(
            f"""
            <div style="
                background:#eef6ff;
                padding:14px;
                border-radius:8px;
                margin-bottom:14px;
            ">
                <b>Multi-AI：</b>
                {provider_text}
            """
        )

        if data.get("judge_used"):
            judge = html.escape(
                str(
                    data.get(
                        "judge_provider",
                        "",
                    )
                )
            )
            parts.append(
                f"""
                <br>
                <b>Judge：</b>{judge}
                """
            )

        parts.append("</div>")

    if provider_errors:
        errors = "<br>".join(
            f"• {html.escape(str(name))}: "
            f"{html.escape(str(error))}"
            for name, error
            in provider_errors.items()
        )

        parts.append(
            f"""
            <div style="
                background:#fff7ed;
                padding:12px;
                border-radius:8px;
                margin-bottom:14px;
            ">
                <b>未参与/失败的模型</b><br>
                {errors}
            </div>
            """
        )

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

    for sector in data.get(
        "sectors",
        [],
    ):
        name = html.escape(
            str(
                sector.get(
                    "sector",
                    "",
                )
            )
        )
        direction = html.escape(
            str(
                sector.get(
                    "direction",
                    "中性",
                )
            )
        )
        score = sector.get(
            "score",
            0,
        )
        confidence = sector.get(
            "confidence",
            0,
        )
        agreement = sector.get(
            "agreement"
        )
        dispersion = sector.get(
            "dispersion"
        )
        summary = html.escape(
            str(
                sector.get(
                    "summary",
                    "",
                )
            )
        )

        try:
            numeric_score = float(score)
        except Exception:
            numeric_score = 0.0

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
                <h2>{name}</h2>
                <p>
                    <b>共识方向：</b>{direction}
                    &nbsp;&nbsp;
                    <b>平均评分：</b>
                    <span style="
                        color:{score_color};
                        font-weight:bold;
                    ">
                        {score}
                    </span>
                    &nbsp;&nbsp;
                    <b>共识置信度：</b>
                    {confidence}%
                </p>
        """
        )

        if agreement is not None:
            parts.append(
                f"""
                <p>
                    <b>方向一致度：</b>
                    {agreement}%
                    &nbsp;&nbsp;
                    <b>评分离散度：</b>
                    {dispersion}
                </p>
                """
            )

        parts.append(
            f"<p>{summary}</p>"
        )

        views = sector.get(
            "provider_views",
            [],
        )

        if views:
            parts.append(
                """
                <div style="
                    background:#f8fafc;
                    padding:12px;
                    border-radius:8px;
                    margin:12px 0;
                ">
                    <b>各模型独立判断</b>
                    <table
                        cellspacing="0"
                        cellpadding="6"
                        style="margin-top:8px;"
                    >
                        <tr>
                            <th align="left">模型</th>
                            <th>评分</th>
                            <th>方向</th>
                            <th>置信度</th>
                        </tr>
                """
            )

            for view in views:
                parts.append(
                    f"""
                    <tr>
                        <td>
                            {html.escape(
                                str(
                                    view.get(
                                        "provider",
                                        "",
                                    )
                                )
                            )}
                        </td>
                        <td align="center">
                            {view.get("score", "")}
                        </td>
                        <td align="center">
                            {html.escape(
                                str(
                                    view.get(
                                        "direction",
                                        "",
                                    )
                                )
                            )}
                        </td>
                        <td align="center">
                            {view.get(
                                "confidence",
                                "",
                            )}%
                        </td>
                    </tr>
                    """
                )

            parts.append(
                """
                    </table>
                </div>
                """
            )

        agreements = sector.get(
            "key_agreements",
            [],
        )
        disagreements = sector.get(
            "key_disagreements",
            [],
        )

        if agreements or disagreements:
            parts.append(
                """
                <div style="
                    background:#f0fdf4;
                    padding:12px;
                    border-radius:8px;
                    margin:12px 0;
                ">
                """
            )

            if agreements:
                parts.append(
                    "<b>Judge 提炼的核心共识</b><br>"
                )
                parts.append(
                    "<br>".join(
                        "• "
                        + html.escape(
                            str(item)
                        )
                        for item in agreements
                    )
                )

            if disagreements:
                parts.append(
                    "<br><br><b>核心分歧</b><br>"
                )
                parts.append(
                    "<br>".join(
                        "• "
                        + html.escape(
                            str(item)
                        )
                        for item in disagreements
                    )
                )

            parts.append("</div>")

        events = sector.get(
            "events",
            [],
        )

        if not events:
            parts.append(
                """
                <p style="color:#6b7280;">
                    暂无明显重大新增事件。
                </p>
                """
            )

        for index, event in enumerate(
            events,
            start=1,
        ):
            title = html.escape(
                str(
                    event.get(
                        "title",
                        "",
                    )
                )
            )
            date = html.escape(
                str(
                    event.get(
                        "date",
                        "",
                    )
                )
            )
            source = html.escape(
                str(
                    event.get(
                        "source",
                        "",
                    )
                )
            )
            url = str(
                event.get(
                    "url",
                    "",
                )
            ).strip()
            impact = html.escape(
                str(
                    event.get(
                        "impact",
                        "",
                    )
                )
            )
            importance = event.get(
                "importance",
                "",
            )
            analysis = html.escape(
                str(
                    event.get(
                        "analysis",
                        "",
                    )
                )
            )

            parts.append(
                f"""
                <hr>
                <h3>事件 {index}：{title}</h3>
                <p>
                    <b>日期：</b>{date}
                    &nbsp;&nbsp;
                    <b>来源：</b>{source}
                    &nbsp;&nbsp;
                    <b>影响：</b>{impact}
                    &nbsp;&nbsp;
                    <b>重要度：</b>{importance}/5
                </p>
                """
            )

            if url.startswith("http"):
                safe_url = html.escape(
                    url,
                    quote=True,
                )
                parts.append(
                    f"""
                    <p>
                        <a href="{safe_url}">
                            查看原始来源
                        </a>
                    </p>
                    """
                )

            chain_items = event.get(
                "transmission",
                [],
            )

            if chain_items:
                chain = " → ".join(
                    html.escape(str(item))
                    for item in chain_items
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
                    <b>事件分析：</b><br>
                    {analysis}
                </p>
                """
            )

        risks = sector.get(
            "risks",
            [],
        )

        if risks:
            risk_text = "<br>".join(
                "• "
                + html.escape(str(risk))
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
            多模型共识仍可能出错。本结果仅用于信息研究与技术演示，
            不构成投资建议。
        </div>
        </body>
        </html>
        """
    )

    return "".join(parts)
