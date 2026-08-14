from collections import Counter
from statistics import mean, pstdev


def score_bucket(score: float) -> str:
    if score >= 10:
        return "positive"
    if score <= -10:
        return "negative"
    return "neutral"


def direction_from_score(score: float) -> str:
    if score >= 80:
        return "强利好"
    if score >= 40:
        return "偏利好"
    if score >= 10:
        return "略偏利好"
    if score > -10:
        return "中性"
    if score > -40:
        return "略偏利空"
    if score > -80:
        return "偏利空"
    return "强利空"


def build_consensus(
    provider_results: dict[str, dict],
    canonical_provider: str | None = None,
) -> dict:
    """
    对多个模型的独立结果做透明、可解释的确定性聚合。

    注意：
    - 不让 Judge 模型直接决定分数。
    - 最终分数 = 多模型 score 均值。
    - agreement = 正/中/负方向桶的一致比例。
    """
    if not provider_results:
        raise RuntimeError(
            "没有可用于共识计算的模型结果。"
        )

    canonical_name = (
        canonical_provider
        if canonical_provider in provider_results
        else next(iter(provider_results))
    )
    canonical = provider_results[canonical_name]

    all_sector_names = []

    for result in provider_results.values():
        for sector in result.get("sectors", []):
            name = str(
                sector.get("sector", "")
            ).strip()

            if name and name not in all_sector_names:
                all_sector_names.append(name)

    consensus_sectors = []

    for sector_name in all_sector_names:
        views = []

        for provider_name, result in provider_results.items():
            sector = _find_sector(
                result,
                sector_name,
            )

            if sector is None:
                continue

            score = _safe_float(
                sector.get("score", 0)
            )
            confidence = _clamp(
                _safe_float(
                    sector.get("confidence", 0)
                ),
                0,
                100,
            )

            views.append(
                {
                    "provider": provider_name,
                    "score": round(score, 1),
                    "direction": str(
                        sector.get(
                            "direction",
                            direction_from_score(score),
                        )
                    ),
                    "confidence": round(
                        confidence,
                        1,
                    ),
                    "summary": str(
                        sector.get(
                            "summary",
                            "",
                        )
                    ),
                }
            )

        if not views:
            continue

        scores = [
            float(view["score"])
            for view in views
        ]
        confidences = [
            float(view["confidence"])
            for view in views
        ]

        avg_score = mean(scores)
        dispersion = (
            pstdev(scores)
            if len(scores) >= 2
            else 0.0
        )

        buckets = [
            score_bucket(score)
            for score in scores
        ]
        bucket_counts = Counter(buckets)
        agreement = (
            max(bucket_counts.values())
            / len(buckets)
            * 100
        )

        avg_confidence = mean(confidences)
        consensus_confidence = _clamp(
            avg_confidence * 0.6
            + agreement * 0.4
            - min(dispersion, 50) * 0.25,
            0,
            100,
        )

        canonical_sector = _find_sector(
            canonical,
            sector_name,
        ) or {}

        positive = bucket_counts.get(
            "positive",
            0,
        )
        neutral = bucket_counts.get(
            "neutral",
            0,
        )
        negative = bucket_counts.get(
            "negative",
            0,
        )

        summary = (
            f"{len(views)} 个模型独立判断："
            f"{positive} 个偏正面、"
            f"{neutral} 个中性、"
            f"{negative} 个偏负面。"
            f"平均事件评分 {avg_score:+.1f}，"
            f"方向一致度 {agreement:.0f}%。"
        )

        consensus_sectors.append(
            {
                "sector": sector_name,
                "score": round(
                    avg_score,
                    1,
                ),
                "direction": direction_from_score(
                    avg_score
                ),
                "confidence": round(
                    consensus_confidence,
                    1,
                ),
                "agreement": round(
                    agreement,
                    1,
                ),
                "dispersion": round(
                    dispersion,
                    1,
                ),
                "summary": summary,
                "provider_views": views,
                "events": canonical_sector.get(
                    "events",
                    [],
                ),
                "risks": canonical_sector.get(
                    "risks",
                    [],
                ),
            }
        )

    provider_names = list(
        provider_results.keys()
    )

    return {
        "generated_at": canonical.get(
            "generated_at",
            "",
        ),
        "market_summary": (
            f"本报告由 {len(provider_names)} 个模型"
            f"基于同一份联网研究证据独立分析后聚合。"
            f"参与模型：{'、'.join(provider_names)}。"
        ),
        "providers_used": provider_names,
        "canonical_provider": canonical_name,
        "mode": (
            "multi"
            if len(provider_names) > 1
            else "single"
        ),
        "sectors": consensus_sectors,
    }


def apply_judge_summary(
    consensus: dict,
    judge_result: dict,
) -> dict:
    """
    Judge 只增强解释，不覆盖确定性聚合得到的 score/agreement。
    """
    if not isinstance(judge_result, dict):
        return consensus

    market_summary = judge_result.get(
        "market_summary"
    )

    if market_summary:
        consensus["market_summary"] = str(
            market_summary
        )

    judge_sectors = {
        str(item.get("sector", "")).strip(): item
        for item in judge_result.get(
            "sectors",
            [],
        )
        if isinstance(item, dict)
    }

    for sector in consensus.get(
        "sectors",
        [],
    ):
        judge_sector = judge_sectors.get(
            sector.get("sector", "")
        )

        if not judge_sector:
            continue

        if judge_sector.get(
            "summary"
        ):
            sector["summary"] = str(
                judge_sector["summary"]
            )

        sector["key_agreements"] = list(
            judge_sector.get(
                "key_agreements",
                [],
            )
        )
        sector["key_disagreements"] = list(
            judge_sector.get(
                "key_disagreements",
                [],
            )
        )

    consensus["judge_used"] = True
    return consensus


def _find_sector(
    result: dict,
    sector_name: str,
) -> dict | None:
    target = sector_name.strip().lower()

    for sector in result.get(
        "sectors",
        [],
    ):
        name = str(
            sector.get(
                "sector",
                "",
            )
        ).strip()

        if name.lower() == target:
            return sector

    return None


def _safe_float(value) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )
