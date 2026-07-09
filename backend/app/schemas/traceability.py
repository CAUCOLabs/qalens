from pydantic import BaseModel


class TraceabilityRelation(BaseModel):
    relation_type: str
    key: str | None = None
    summary: str | None = None
    status: str | None = None
    issue_type: str | None = None


class TraceabilityReport(BaseModel):
    issue_key: str
    has_parent: bool
    has_subtasks: bool
    has_linked_issues: bool
    traceability_score: int
    readiness: str
    relations: list[TraceabilityRelation]
    gaps: list[str]
    recommendations: list[str]
