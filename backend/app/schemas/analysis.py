from pydantic import BaseModel


class IssueAnalysisResponse(BaseModel):
    issue_key: str
    quality_score: int
    risk_level: str
    risks: list[str]
    suggestions: list[str]
