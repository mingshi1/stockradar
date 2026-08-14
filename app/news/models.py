from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ResearchSnapshot:
    provider: str
    model: str
    sectors: list[str]
    text: str
    created_at: datetime
