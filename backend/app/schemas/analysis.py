from pydantic import BaseModel


class TestCaseSuggestion(BaseModel):
    title: str
    type: str
    priority: str
    steps: list[str]
    expected_result: str


class TrustSignal(BaseModel):
    category: str
    signal: str
    severity: str


class IssueAnalysisResponse(BaseModel):
    issue_key: str
    quality_score: int
    risk_level: str
    risks: list[str]
    suggestions: list[str]
    test_cases: list[TestCaseSuggestion]

    requirement_quality: str
    acceptance_criteria_readiness: str
    test_coverage_readiness: str
    evidence_readiness: str
    trust_readiness: str
    quality_gate: str
    trust_signals: list[TrustSignal]
