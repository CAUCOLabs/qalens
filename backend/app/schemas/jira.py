from pydantic import BaseModel


class JiraConnectionStatus(BaseModel):
    connected: bool
    message: str


class JiraIssue(BaseModel):
    key: str
    summary: str
    status: str
    issue_type: str
    description: str | None = None
    priority: str | None = None
    assignee: str | None = None
    created: str | None = None
    updated: str | None = None


class JiraIssuesResponse(BaseModel):
    total: int
    issues: list[JiraIssue]
