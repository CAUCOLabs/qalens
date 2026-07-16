from pydantic import BaseModel, Field


class ChangedFile(BaseModel):
    path: str
    change_type: str
    additions: int = Field(default=0, ge=0)
    deletions: int = Field(default=0, ge=0)


class ChangeAnalysisRequest(BaseModel):
    issue_key: str | None = None
    repository: str | None = None
    pull_request: str | None = None
    title: str
    description: str | None = None
    changed_files: list[ChangedFile]
    test_evidence: list[str] = []
    linked_artifacts: list[str] = []


class ChangeRiskSignal(BaseModel):
    category: str
    signal: str
    severity: str
    affected_files: list[str] = []


class ChangeAnalysisResponse(BaseModel):
    issue_key: str | None = None
    repository: str | None = None
    pull_request: str | None = None
    total_files_changed: int
    total_additions: int
    total_deletions: int
    change_risk_score: int
    risk_level: str
    test_coverage_readiness: str
    evidence_readiness: str
    release_readiness: str
    quality_gate: str
    risk_signals: list[ChangeRiskSignal]
    missing_controls: list[str]
    recommendations: list[str]
