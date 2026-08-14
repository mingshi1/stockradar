from app.analysis.models import AnalysisBundle
from app.news.models import ResearchSnapshot


class NewsService:
    """
    v0.4 的“新闻层”还是一个轻量内存实现。

    它先负责保存最近一次 Web Search 的原始研究资料。
    v0.5 会把这里升级成真正的 Event Pool + SQLite。
    """

    def __init__(self):
        self._latest_snapshot: ResearchSnapshot | None = None

    def update_from_analysis(self, bundle: AnalysisBundle):
        self._latest_snapshot = ResearchSnapshot(
            provider=bundle.provider,
            model=bundle.model,
            sectors=list(bundle.sectors),
            text=bundle.research_text,
            created_at=bundle.generated_at,
        )

    def latest_snapshot(self) -> ResearchSnapshot | None:
        return self._latest_snapshot
