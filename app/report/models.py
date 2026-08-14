from dataclasses import dataclass


@dataclass(slots=True)
class ReportArtifact:
    title: str
    report_type: str
    html: str
    markdown: str
    plain_summary: str
