from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class AnalysisBundle:
    """
    一次完整分析的返回对象。

    structured:
        UI / 数据库后续真正消费的结构化分析结果。

    research_text:
        AI 联网研究阶段的原始研究资料。
    """

    structured: dict
    research_text: str
    provider: str
    model: str
    sectors: list[str]
    generated_at: datetime
