import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from app.ai.manager import ProviderManager
from app.analysis.consensus import (
    apply_judge_summary,
    build_consensus,
)
from app.analysis.models import (
    AnalysisBundle,
    ProviderAnalysis,
)


class AnalysisService:
    """
    V0.6 Multi-AI pipeline:

    1. 一个 Research Provider 联网取证。
    2. 所有启用的分析模型读取完全相同的证据，独立分析。
    3. Consensus Engine 做确定性聚合。
    4. 可选 Judge AI 只总结共识/分歧，不篡改聚合分数。
    """

    def __init__(
        self,
        provider_manager: ProviderManager,
    ):
        self.provider_manager = (
            provider_manager
        )

    def analyze(
        self,
        *,
        sectors: list[str],
        research_provider_name: str,
        analysis_mode: str,
        judge_enabled: bool,
        judge_provider_name: str,
        provider_settings: dict[str, dict],
        api_keys: dict[str, str],
    ) -> AnalysisBundle:
        if not sectors:
            raise ValueError(
                "没有选择任何板块。"
            )

        generated_at = datetime.now()

        research_settings = (
            provider_settings.get(
                research_provider_name,
                {},
            )
        )
        research_key = api_keys.get(
            research_provider_name
        )

        if not research_key:
            raise RuntimeError(
                f"研究 Provider {research_provider_name} "
                "尚未配置 API Key。"
            )

        research_provider = (
            self.provider_manager.get(
                research_provider_name
            )
        )

        if not research_provider.info.supports_web_search:
            raise RuntimeError(
                f"{research_provider_name} "
                "当前不能作为联网研究 Provider。"
            )

        research_model = str(
            research_settings.get(
                "model",
                research_provider.info.default_model,
            )
        )
        research_base_url = str(
            research_settings.get(
                "base_url",
                research_provider.info.default_base_url,
            )
        )

        sector_text = "、".join(sectors)

        research_text = (
            research_provider.web_research(
                api_key=research_key,
                model=research_model,
                base_url=research_base_url,
                prompt=self._build_research_prompt(
                    generated_at,
                    sector_text,
                ),
                instructions=(
                    "你是一名严谨的A股行业研究员。"
                    "你必须优先依赖联网搜索得到的真实信息，"
                    "不要凭模型记忆虚构近期新闻。"
                ),
            )
        )

        analyst_names = (
            [research_provider_name]
            if analysis_mode == "single"
            else [
                name
                for name, settings
                in provider_settings.items()
                if settings.get("enabled")
            ]
        )

        # Research Provider 即使没勾选，也必须参与单模型/作为 canonical 候选。
        if (
            research_provider_name
            not in analyst_names
        ):
            analyst_names.insert(
                0,
                research_provider_name,
            )

        provider_results: dict[
            str,
            dict,
        ] = {}
        provider_errors: dict[
            str,
            str,
        ] = {}
        provider_analyses: list[
            ProviderAnalysis
        ] = []

        jobs = {}

        max_workers = min(
            max(
                len(analyst_names),
                1,
            ),
            5,
        )

        with ThreadPoolExecutor(
            max_workers=max_workers
        ) as executor:
            for provider_name in analyst_names:
                settings = (
                    provider_settings.get(
                        provider_name,
                        {},
                    )
                )
                api_key = api_keys.get(
                    provider_name
                )

                if not api_key:
                    provider_errors[
                        provider_name
                    ] = "未配置 API Key"
                    continue

                provider = (
                    self.provider_manager.get(
                        provider_name
                    )
                )

                model = str(
                    settings.get(
                        "model",
                        provider.info.default_model,
                    )
                )
                base_url = str(
                    settings.get(
                        "base_url",
                        provider.info.default_base_url,
                    )
                )

                future = executor.submit(
                    provider.analyze_evidence,
                    api_key,
                    model,
                    base_url,
                    self._analysis_system_prompt(),
                    self._analysis_user_prompt(
                        sectors=sectors,
                        research_text=research_text,
                    ),
                )

                jobs[future] = (
                    provider_name,
                    model,
                )

            for future in as_completed(jobs):
                provider_name, model = (
                    jobs[future]
                )

                try:
                    result = future.result()
                    self._validate_provider_result(
                        result
                    )

                    provider_results[
                        provider_name
                    ] = result

                    provider_analyses.append(
                        ProviderAnalysis(
                            provider=provider_name,
                            model=model,
                            result=result,
                        )
                    )

                except Exception as exc:
                    message = str(exc)
                    provider_errors[
                        provider_name
                    ] = message

                    provider_analyses.append(
                        ProviderAnalysis(
                            provider=provider_name,
                            model=model,
                            error=message,
                        )
                    )

        if not provider_results:
            details = "；".join(
                f"{name}: {error}"
                for name, error
                in provider_errors.items()
            )
            raise RuntimeError(
                "所有 AI 分析都失败。"
                + (
                    f"\n{details}"
                    if details
                    else ""
                )
            )

        consensus = build_consensus(
            provider_results,
            canonical_provider=(
                research_provider_name
            ),
        )

        consensus[
            "provider_errors"
        ] = provider_errors
        consensus[
            "research_provider"
        ] = research_provider_name
        consensus[
            "research_model"
        ] = research_model
        consensus[
            "analysis_mode"
        ] = analysis_mode
        consensus[
            "judge_used"
        ] = False

        # Optional judge.
        if (
            judge_enabled
            and len(provider_results) >= 2
        ):
            judge_key = api_keys.get(
                judge_provider_name
            )

            judge_settings = (
                provider_settings.get(
                    judge_provider_name,
                    {},
                )
            )

            if judge_key:
                judge_provider = (
                    self.provider_manager.get(
                        judge_provider_name
                    )
                )
                judge_model = str(
                    judge_settings.get(
                        "model",
                        judge_provider.info.default_model,
                    )
                )
                judge_base_url = str(
                    judge_settings.get(
                        "base_url",
                        judge_provider.info.default_base_url,
                    )
                )

                try:
                    judge_result = (
                        judge_provider.analyze_evidence(
                            api_key=judge_key,
                            model=judge_model,
                            base_url=judge_base_url,
                            system_prompt=(
                                self._judge_system_prompt()
                            ),
                            user_prompt=(
                                self._judge_user_prompt(
                                    consensus,
                                )
                            ),
                        )
                    )

                    consensus = (
                        apply_judge_summary(
                            consensus,
                            judge_result,
                        )
                    )
                    consensus[
                        "judge_provider"
                    ] = judge_provider_name
                    consensus[
                        "judge_model"
                    ] = judge_model

                except Exception as exc:
                    consensus[
                        "judge_error"
                    ] = str(exc)

        return AnalysisBundle(
            structured=consensus,
            research_text=research_text,
            research_provider=(
                research_provider_name
            ),
            research_model=research_model,
            sectors=list(sectors),
            generated_at=generated_at,
            mode=analysis_mode,
            provider_analyses=(
                provider_analyses
            ),
            provider_errors=(
                provider_errors
            ),
        )

    @staticmethod
    def _build_research_prompt(
        current_time: datetime,
        sector_text: str,
    ) -> str:
        time_text = current_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return f"""
当前时间：{time_text}

请联网搜索并研究最近3个交易日内，可能显著影响以下A股板块的重要事件：

{sector_text}

板块名称可能包含用户自行输入的主题，例如：
生物医药、机器人、创新药、低空经济、游戏、光伏等。

如果名称不是传统行业分类，请先理解其通常对应的A股产业链和市场主题，
再搜索真正相关的事件，不得擅自扩大到无关领域。

研究要求：

1. 必须联网搜索。
2. 优先最近3个交易日。
3. 优先真正影响行业基本面、估值或情绪的重要事件。
4. 优先可靠来源：
   - 政府部门
   - 证券交易所
   - 上市公司公告
   - 官方统计机构
   - Reuters / Bloomberg / CNBC
   - 主流财经媒体
   - 行业权威媒体
5. 避免自媒体二次转载、内容农场、无来源传闻。
6. 同一事件多家报道时合并。
7. 每板块最多选择3个核心事件。
8. 没有重大新增事件时明确说明。
9. 尽可能保留标题、日期、来源、URL。
10. 不得虚构来源、日期、URL。

对每个事件说明：
事件发生了什么
→ 为什么重要
→ 影响产业链哪个环节
→ 为什么影响该A股板块
→ 更偏短期情绪还是基本面

请形成详细、可供后续多个AI共同分析的中文证据资料。

本研究仅用于信息研究与技术演示，不构成投资建议。
"""

    @staticmethod
    def _analysis_system_prompt() -> str:
        return """
你是一名独立的A股事件驱动研究分析师。

你正在参与“多模型交叉验证”。

重要规则：

1. 你与其他模型互相看不到对方结论。
2. 只能根据用户提供的同一份联网研究资料分析。
3. 不得自己添加研究资料中不存在的近期事实。
4. 分数代表事件冲击，不代表未来股价预测。
5. 即使你认为其他模型可能不同，也必须独立给出自己的判断。
6. 必须输出合法 JSON，不要 Markdown，不要解释 JSON 格式本身。

输出：

{
  "generated_at": "时间",
  "market_summary": "整体判断",
  "sectors": [
    {
      "sector": "必须对应用户提供的板块名称",
      "score": 0,
      "direction": "中性",
      "confidence": 0,
      "summary": "独立判断及核心理由",
      "events": [
        {
          "title": "事件标题",
          "date": "日期或未知",
          "source": "来源",
          "url": "URL或空字符串",
          "importance": 1,
          "impact": "利好/利空/中性",
          "impact_type": "情绪/基本面/情绪+基本面",
          "transmission": [
            "第一步",
            "第二步",
            "第三步"
          ],
          "analysis": "事件逻辑"
        }
      ],
      "risks": [
        "反向因素"
      ]
    }
  ]
}

score：-100 到 +100。
confidence：0 到 100。
importance：1 到 5。

direction 只能是：
强利好、偏利好、略偏利好、中性、
略偏利空、偏利空、强利空。

没有明显事件时 events=[]，score 接近0。
"""

    @staticmethod
    def _analysis_user_prompt(
        *,
        sectors: list[str],
        research_text: str,
    ) -> str:
        return f"""
需要独立分析的板块：

{'、'.join(sectors)}

以下是所有参与模型都会收到的同一份联网证据：

================ EVIDENCE ================
{research_text}
==========================================

请严格基于以上证据独立分析，并只输出 JSON。
"""

    @staticmethod
    def _judge_system_prompt() -> str:
        return """
你是 Multi-AI Consensus 的仲裁编辑。

你不会重新判断新闻事实，也不能修改系统已经通过数学聚合计算出的：
- score
- agreement
- dispersion
- confidence

你的任务仅仅是阅读不同模型的观点，解释：

1. 模型在哪些核心逻辑上达成一致。
2. 模型在哪些地方存在真正分歧。
3. 为什么这些分歧会导致不同评分。
4. 给出谨慎、可读的综合摘要。

输出合法 JSON：

{
  "market_summary": "总体共识与主要分歧",
  "sectors": [
    {
      "sector": "板块",
      "summary": "综合解释",
      "key_agreements": ["共识1", "共识2"],
      "key_disagreements": ["分歧1", "分歧2"]
    }
  ]
}

不要输出 JSON 外的任何内容。
"""

    @staticmethod
    def _judge_user_prompt(
        consensus: dict,
    ) -> str:
        compact = {
            "providers_used": (
                consensus.get(
                    "providers_used",
                    [],
                )
            ),
            "sectors": [
                {
                    "sector": sector.get(
                        "sector"
                    ),
                    "score": sector.get(
                        "score"
                    ),
                    "agreement": sector.get(
                        "agreement"
                    ),
                    "dispersion": sector.get(
                        "dispersion"
                    ),
                    "provider_views": (
                        sector.get(
                            "provider_views",
                            [],
                        )
                    ),
                }
                for sector in consensus.get(
                    "sectors",
                    [],
                )
            ],
        }

        return (
            "以下是已经完成的多模型独立分析和"
            "确定性共识指标：\n\n"
            + json.dumps(
                compact,
                ensure_ascii=False,
                indent=2,
            )
        )

    @staticmethod
    def _validate_provider_result(
        data: dict,
    ):
        if not isinstance(data, dict):
            raise RuntimeError(
                "结构化结果不是 JSON 对象。"
            )

        sectors = data.get(
            "sectors"
        )

        if not isinstance(
            sectors,
            list,
        ):
            raise RuntimeError(
                "结构化结果缺少 sectors 数组。"
            )
