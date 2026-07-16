from pydantic import BaseModel, Field


class EvidenceArtifact(BaseModel):
    category: str
    name: str
    provided: bool = True


class EvidenceIntelligenceRequest(BaseModel):
    issue_key: str
    repository: str | None = None
    pull_request: str | None = None

    evidence: list[EvidenceArtifact] = Field(default_factory=list)


class EvidenceSignal(BaseModel):
    category: str
    signal: str
    severity: str


class EvidenceIntelligenceResponse(BaseModel):
    issue_key: str

    evidence_score: int

    evidence_readiness: str

    quality_gate: str

    provided_evidence: list[str]

    missing_evidence: list[str]

    evidence_signals: list[EvidenceSignal]

    recommendations: list[str]