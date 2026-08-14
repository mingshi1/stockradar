from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class ProviderAnalysis:
    provider: str
    model: str
    result: dict | None = None
    error: str | None = None


@dataclass(slots=True)
class AnalysisBundle:
    structured: dict
    research_text: str
    research_provider: str
    research_model: str
    sectors: list[str]
    generated_at: datetime
    mode: str = "single"
    provider_analyses: list[ProviderAnalysis] = field(
        default_factory=list
    )
    provider_errors: dict[str, str] = field(
        default_factory=dict
    )

    @property
    def provider(self) -> str:
        # V0.5 database compatibility.
        return self.research_provider

    @property
    def model(self) -> str:
        return self.research_model
