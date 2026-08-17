import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Callable

from app.ai.manager import ProviderManager
from app.analysis.consensus import (
    apply_judge_summary,
    build_consensus,
)
from app.analysis.models import (
    AnalysisBundle,
    ProviderAnalysis,
    ProviderCallMetric,
)


ProgressCallback = Callable[[dict], None]


class AnalysisService:
    """
    当前版本 可观测 Multi-AI 流程。

    progress_callback 会持续汇报“我们真实知道的阶段”，
    而不是伪造模型内部思考百分比。
    """

    def __init__(
        self,
        provider_manager: ProviderManager,
    ):
        self.provider_manager = provider_manager
        self.logger = logging.getLogger("StockEventRadar")

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
        progress_callback: ProgressCallback | None = None,
    ) -> AnalysisBundle:
        if not sectors:
            raise ValueError("没有选择任何板块。")

        started_at = time.perf_counter()
        generated_at = datetime.now()
        call_metrics: list[ProviderCallMetric] = []

        self._progress(
            progress_callback,
            percent=2,
            stage="prepare",
            status="running",
            message="正在准备分析任务…",
        )

        research_settings = provider_settings.get(
            research_provider_name,
            {},
        )
        research_key = api_keys.get(
            research_provider_name
        )

        if not research_key:
            raise RuntimeError(
                f"研究 Provider {research_provider_name} "
                "尚未配置 API Key。"
            )

        research_provider = self.provider_manager.get(
            research_provider_name
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

        self._progress(
            progress_callback,
            percent=8,
            stage="research",
            provider=research_provider_name,
            status="running",
            message=f"{research_provider_name} 正在联网搜索近期证据…",
        )

        research_started = time.perf_counter()

        try:
            research_call = research_provider.web_research(
                api_key=research_key,
                model=research_model,
                base_url=research_base_url,
                prompt=self._build_research_prompt(
                    generated_at,
                    "、".join(sectors),
                ),
                instructions=(
                    "你是一名严谨的A股行业研究员。"
                    "必须优先依赖联网搜索得到的真实信息，"
                    "不要凭模型记忆虚构近期新闻。"
                ),
            )
        except Exception as exc:
            duration_ms = self._elapsed_ms(research_started)

            call_metrics.append(
                ProviderCallMetric(
                    phase="research",
                    provider=research_provider_name,
                    model=research_model,
                    status="error",
                    duration_ms=duration_ms,
                    error=str(exc),
                )
            )

            self._progress(
                progress_callback,
                percent=8,
                stage="research",
                provider=research_provider_name,
                status="error",
                duration_ms=duration_ms,
                message=f"联网研究失败：{exc}",
            )
            raise

        research_duration = self._elapsed_ms(
            research_started
        )

        research_cost = self._estimate_cost(
            research_settings,
            research_call.usage.input_tokens,
            research_call.usage.output_tokens,
        )

        call_metrics.append(
            ProviderCallMetric(
                phase="research",
                provider=research_provider_name,
                model=research_model,
                status="success",
                duration_ms=research_duration,
                input_tokens=research_call.usage.input_tokens,
                output_tokens=research_call.usage.output_tokens,
                total_tokens=research_call.usage.total_tokens,
                estimated_cost=research_cost,
            )
        )

        research_text = research_call.text

        self._progress(
            progress_callback,
            percent=28,
            stage="research",
            provider=research_provider_name,
            status="success",
            duration_ms=research_duration,
            input_tokens=research_call.usage.input_tokens,
            output_tokens=research_call.usage.output_tokens,
            total_tokens=research_call.usage.total_tokens,
            estimated_cost=research_cost,
            message="联网证据采集完成。",
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

        if research_provider_name not in analyst_names:
            analyst_names.insert(
                0,
                research_provider_name,
            )

        provider_results: dict[str, dict] = {}
        provider_errors: dict[str, str] = {}
        provider_analyses: list[ProviderAnalysis] = []

        runnable: list[tuple[str, object, str, str, str]] = []

        for provider_name in analyst_names:
            settings = provider_settings.get(
                provider_name,
                {},
            )
            api_key = api_keys.get(provider_name)

            provider = self.provider_manager.get(
                provider_name
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

            if not api_key:
                error = "未配置 API Key"
                provider_errors[provider_name] = error
                provider_analyses.append(
                    ProviderAnalysis(
                        provider=provider_name,
                        model=model,
                        error=error,
                    )
                )
                call_metrics.append(
                    ProviderCallMetric(
                        phase="analysis",
                        provider=provider_name,
                        model=model,
                        status="skipped",
                        duration_ms=0,
                        error=error,
                    )
                )
                self._progress(
                    progress_callback,
                    percent=30,
                    stage="analysis",
                    provider=provider_name,
                    status="skipped",
                    message=error,
                )
                continue

            runnable.append(
                (
                    provider_name,
                    provider,
                    model,
                    base_url,
                    api_key,
                )
            )

        if not runnable:
            raise RuntimeError(
                "没有任何配置完整的分析模型。"
            )

        self._progress(
            progress_callback,
            percent=30,
            stage="analysis",
            status="running",
            message=f"开始 {len(runnable)} 个模型并行独立分析…",
        )

        jobs = {}
        job_started_at: dict[object, float] = {}

        max_workers = min(
            max(len(runnable), 1),
            6,
        )

        with ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="AIProvider",
        ) as executor:
            for (
                provider_name,
                provider,
                model,
                base_url,
                api_key,
            ) in runnable:
                self._progress(
                    progress_callback,
                    percent=32,
                    stage="analysis",
                    provider=provider_name,
                    status="running",
                    message=f"{provider_name} 正在独立分析同一份证据…",
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
                    provider_settings.get(
                        provider_name,
                        {},
                    ),
                )
                job_started_at[future] = time.perf_counter()

            completed = 0
            total = len(jobs)

            for future in as_completed(jobs):
                (
                    provider_name,
                    model,
                    settings,
                ) = jobs[future]

                duration_ms = self._elapsed_ms(
                    job_started_at[future]
                )
                completed += 1

                percent = int(
                    32
                    + (completed / total) * 45
                )

                try:
                    call_result = future.result()
                    result = call_result.data

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

                    cost = self._estimate_cost(
                        settings,
                        call_result.usage.input_tokens,
                        call_result.usage.output_tokens,
                    )

                    call_metrics.append(
                        ProviderCallMetric(
                            phase="analysis",
                            provider=provider_name,
                            model=model,
                            status="success",
                            duration_ms=duration_ms,
                            input_tokens=call_result.usage.input_tokens,
                            output_tokens=call_result.usage.output_tokens,
                            total_tokens=call_result.usage.total_tokens,
                            estimated_cost=cost,
                        )
                    )

                    self._progress(
                        progress_callback,
                        percent=percent,
                        stage="analysis",
                        provider=provider_name,
                        status="success",
                        duration_ms=duration_ms,
                        input_tokens=call_result.usage.input_tokens,
                        output_tokens=call_result.usage.output_tokens,
                        total_tokens=call_result.usage.total_tokens,
                        estimated_cost=cost,
                        message=f"{provider_name} 分析完成。",
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

                    call_metrics.append(
                        ProviderCallMetric(
                            phase="analysis",
                            provider=provider_name,
                            model=model,
                            status="error",
                            duration_ms=duration_ms,
                            error=message,
                        )
                    )

                    self.logger.warning(
                        "Provider failed | %s | %s",
                        provider_name,
                        message,
                    )

                    self._progress(
                        progress_callback,
                        percent=percent,
                        stage="analysis",
                        provider=provider_name,
                        status="error",
                        duration_ms=duration_ms,
                        message=message,
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

        self._progress(
            progress_callback,
            percent=80,
            stage="consensus",
            status="running",
            message="正在计算 Multi-AI 共识…",
        )

        consensus_started = time.perf_counter()

        consensus = build_consensus(
            provider_results,
            canonical_provider=research_provider_name,
        )

        consensus_duration = self._elapsed_ms(
            consensus_started
        )

        consensus["provider_errors"] = provider_errors
        consensus["research_provider"] = research_provider_name
        consensus["research_model"] = research_model
        consensus["analysis_mode"] = analysis_mode
        consensus["judge_used"] = False

        self._progress(
            progress_callback,
            percent=86,
            stage="consensus",
            status="success",
            duration_ms=consensus_duration,
            message="共识评分、一致度和离散度计算完成。",
        )

        if (
            judge_enabled
            and len(provider_results) >= 2
        ):
            judge_key = api_keys.get(
                judge_provider_name
            )
            judge_settings = provider_settings.get(
                judge_provider_name,
                {},
            )

            if judge_key:
                judge_provider = self.provider_manager.get(
                    judge_provider_name
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

                self._progress(
                    progress_callback,
                    percent=88,
                    stage="judge",
                    provider=judge_provider_name,
                    status="running",
                    message=f"{judge_provider_name} 正在总结模型共识与分歧…",
                )

                judge_started = time.perf_counter()

                try:
                    judge_call = judge_provider.analyze_evidence(
                        api_key=judge_key,
                        model=judge_model,
                        base_url=judge_base_url,
                        system_prompt=self._judge_system_prompt(),
                        user_prompt=self._judge_user_prompt(
                            consensus,
                        ),
                    )

                    judge_duration = self._elapsed_ms(
                        judge_started
                    )

                    cost = self._estimate_cost(
                        judge_settings,
                        judge_call.usage.input_tokens,
                        judge_call.usage.output_tokens,
                    )

                    call_metrics.append(
                        ProviderCallMetric(
                            phase="judge",
                            provider=judge_provider_name,
                            model=judge_model,
                            status="success",
                            duration_ms=judge_duration,
                            input_tokens=judge_call.usage.input_tokens,
                            output_tokens=judge_call.usage.output_tokens,
                            total_tokens=judge_call.usage.total_tokens,
                            estimated_cost=cost,
                        )
                    )

                    consensus = apply_judge_summary(
                        consensus,
                        judge_call.data,
                    )
                    consensus["judge_provider"] = judge_provider_name
                    consensus["judge_model"] = judge_model

                    self._progress(
                        progress_callback,
                        percent=94,
                        stage="judge",
                        provider=judge_provider_name,
                        status="success",
                        duration_ms=judge_duration,
                        input_tokens=judge_call.usage.input_tokens,
                        output_tokens=judge_call.usage.output_tokens,
                        total_tokens=judge_call.usage.total_tokens,
                        estimated_cost=cost,
                        message="Judge 共识/分歧总结完成。",
                    )

                except Exception as exc:
                    judge_duration = self._elapsed_ms(
                        judge_started
                    )

                    call_metrics.append(
                        ProviderCallMetric(
                            phase="judge",
                            provider=judge_provider_name,
                            model=judge_model,
                            status="error",
                            duration_ms=judge_duration,
                            error=str(exc),
                        )
                    )
                    consensus["judge_error"] = str(exc)

                    self._progress(
                        progress_callback,
                        percent=94,
                        stage="judge",
                        provider=judge_provider_name,
                        status="error",
                        duration_ms=judge_duration,
                        message=f"Judge 失败，继续使用确定性共识：{exc}",
                    )
            else:
                consensus["judge_error"] = (
                    f"{judge_provider_name} 未配置 API Key"
                )

        total_duration_ms = self._elapsed_ms(
            started_at
        )

        consensus["runtime"] = {
            "duration_ms": total_duration_ms,
            "calls": len(call_metrics),
            "input_tokens": sum(
                metric.input_tokens
                for metric in call_metrics
            ),
            "output_tokens": sum(
                metric.output_tokens
                for metric in call_metrics
            ),
            "total_tokens": sum(
                metric.total_tokens
                for metric in call_metrics
            ),
            "estimated_cost": round(
                sum(
                    metric.estimated_cost or 0.0
                    for metric in call_metrics
                ),
                6,
            ),
            "priced_calls": sum(
                1
                for metric in call_metrics
                if metric.estimated_cost is not None
            ),
        }

        self._progress(
            progress_callback,
            percent=96,
            stage="finalize",
            status="running",
            duration_ms=total_duration_ms,
            message="分析完成，正在交给本地数据库保存…",
        )

        return AnalysisBundle(
            structured=consensus,
            research_text=research_text,
            research_provider=research_provider_name,
            research_model=research_model,
            sectors=list(sectors),
            generated_at=generated_at,
            mode=analysis_mode,
            provider_analyses=provider_analyses,
            provider_errors=provider_errors,
            call_metrics=call_metrics,
        )

    @staticmethod
    def _estimate_cost(
        settings: dict,
        input_tokens: int,
        output_tokens: int,
    ) -> float | None:
        try:
            input_price = float(
                settings.get(
                    "input_price_per_million",
                    0.0,
                )
                or 0.0
            )
            output_price = float(
                settings.get(
                    "output_price_per_million",
                    0.0,
                )
                or 0.0
            )
        except Exception:
            return None

        if input_price <= 0 and output_price <= 0:
            return None

        # 部分兼容 API 不返回 usage。
        # Token 全为 0 时不能把“未知”误报成“成本为 0”。
        if input_tokens <= 0 and output_tokens <= 0:
            return None

        return (
            max(0, input_tokens) / 1_000_000 * input_price
            + max(0, output_tokens) / 1_000_000 * output_price
        )

    @staticmethod
    def _elapsed_ms(
        started: float,
    ) -> int:
        return int(
            (time.perf_counter() - started)
            * 1000
        )

    @staticmethod
    def _progress(
        callback: ProgressCallback | None,
        **payload,
    ):
        if callback is None:
            return

        try:
            callback(payload)
        except Exception:
            # UI 进度展示失败不能影响主分析流程。
            pass

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
11. 去掉重复背景和套话，整体证据尽量紧凑；每个事件只保留后续分析真正需要的信息。

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

规则：

1. 你与其他模型互相看不到对方结论。
2. 只能根据用户提供的同一份联网研究资料分析。
3. 不得自行添加研究资料中不存在的近期事实。
4. 分数代表事件冲击，不代表未来股价预测。
5. 必须独立判断。
6. 必须输出合法 JSON，不要 Markdown。
7. 输出保持紧凑：每个 summary 尽量不超过 160 个汉字；
   每个事件 analysis 尽量不超过 180 个汉字；risks 最多 3 条。
   不要复述整段证据，不要输出无关背景。

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

不能修改系统已经通过数学聚合计算出的：
- score
- agreement
- dispersion
- confidence

仅负责解释：
1. 模型核心共识。
2. 模型真正分歧。
3. 分歧为什么造成不同评分。
4. 谨慎的综合摘要。

输出：

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

只输出 JSON。
"""

    @staticmethod
    def _judge_user_prompt(
        consensus: dict,
    ) -> str:
        compact = {
            "providers_used": consensus.get(
                "providers_used",
                [],
            ),
            "sectors": [
                {
                    "sector": sector.get("sector"),
                    "score": sector.get("score"),
                    "agreement": sector.get("agreement"),
                    "dispersion": sector.get("dispersion"),
                    "provider_views": sector.get(
                        "provider_views",
                        [],
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

        if not isinstance(
            data.get("sectors"),
            list,
        ):
            raise RuntimeError(
                "结构化结果缺少 sectors 数组。"
            )
