from pydantic import BaseModel


class TestCaseSuggestion(BaseModel):
    title: str
    type: str
    priority: str
    steps: list[str]
    expected_result: str


class IssueAnalysisResponse(BaseModel):
    issue_key: str
    quality_score: int
    risk_level: str
    risks: list[str]
    suggestions: list[str]
    test_cases: list[TestCaseSuggestion]
