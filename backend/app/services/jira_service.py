from app.core.token_store import jira_resources, jira_token_data
from app.integrations.jira.client import JiraClient
from app.schemas.jira import JiraConnectionStatus, JiraIssue, JiraIssuesResponse


DEMO_ISSUES = {
    "SCRUM-1": JiraIssue(
        key="SCRUM-1",
        summary="Fix login",
        status="Backlog",
        issue_type="Bug",
        description="Login broken.",
        priority=None,
        assignee=None,
        created="2026-07-01T09:00:00.000+0000",
        updated="2026-07-01T09:00:00.000+0000",
    ),
    "SCRUM-2": JiraIssue(
        key="SCRUM-2",
        summary="Add password reset email validation",
        status="In Progress",
        issue_type="Story",
        description=(
            "As a returning user, I want to receive a password reset email so "
            "that I can regain access to my account. The issue mentions email "
            "validation and reset link expiry, but the expected QA scenarios are "
            "not fully defined yet."
        ),
        priority="Medium",
        assignee=None,
        created="2026-07-02T10:30:00.000+0000",
        updated="2026-07-03T12:15:00.000+0000",
    ),
    "SCRUM-3": JiraIssue(
        key="SCRUM-3",
        summary="Improve checkout address validation before payment",
        status="Ready for QA",
        issue_type="Story",
        description=(
            "As a shopper, I want invalid shipping addresses to be caught before "
            "payment so that I can correct mistakes without losing my cart. "
            "Acceptance criteria: required address fields are validated, postal "
            "code format is checked for supported countries, inline errors are "
            "shown beside invalid fields, and valid addresses allow payment to continue."
        ),
        priority="High",
        assignee="Mina QA",
        created="2026-07-03T08:45:00.000+0000",
        updated="2026-07-05T14:20:00.000+0000",
    ),
}


class JiraService:
    def get_connection_status(self) -> JiraConnectionStatus:
        access_token = jira_token_data.get("access_token")

        if access_token and jira_resources:
            return JiraConnectionStatus(
                connected=True,
                message="Jira integration is connected.",
            )

        return JiraConnectionStatus(
            connected=False,
            message="Jira integration is not connected yet.",
        )

    def _get_client(self) -> JiraClient | None:
        if not jira_token_data.get("access_token") or not jira_resources:
            return None

        return JiraClient(
            access_token=jira_token_data["access_token"],
            cloud_id=jira_resources[0]["id"],
        )

    def _normalize_issue(self, raw_issue: dict) -> JiraIssue:
        fields = raw_issue.get("fields", {})
        description = fields.get("description")

        if description and not isinstance(description, str):
            description = str(description)

        return JiraIssue(
            key=raw_issue.get("key", ""),
            summary=fields.get("summary", ""),
            status=(fields.get("status") or {}).get("name", ""),
            issue_type=(fields.get("issuetype") or {}).get("name", ""),
            description=description,
            priority=(fields.get("priority") or {}).get("name"),
            assignee=(fields.get("assignee") or {}).get("displayName"),
            created=fields.get("created"),
            updated=fields.get("updated"),
        )

    def _get_demo_issue(self, issue_key: str) -> JiraIssue | None:
        return DEMO_ISSUES.get(issue_key.upper())

    async def get_projects(self) -> dict:
        client = self._get_client()

        if not client:
            return {"error": "Jira is not connected. Visit /jira/oauth/login first."}

        return await client.get_projects()

    async def get_issues(self, project_key: str) -> JiraIssuesResponse | dict:
        client = self._get_client()

        if not client:
            if project_key.upper() == "SCRUM":
                issues = list(DEMO_ISSUES.values())
                return JiraIssuesResponse(
                    total=len(issues),
                    issues=issues,
                )

            return {"error": "Jira is not connected. Visit /jira/oauth/login first."}

        data = await client.get_issues(project_key=project_key)
        raw_issues = data.get("issues", [])

        issues = [self._normalize_issue(issue) for issue in raw_issues]

        return JiraIssuesResponse(
            total=len(issues),
            issues=issues,
        )

    async def get_issue(self, issue_key: str) -> JiraIssue | dict:
        client = self._get_client()

        if not client:
            demo_issue = self._get_demo_issue(issue_key)

            if demo_issue:
                return demo_issue

            return {"error": "Jira is not connected. Visit /jira/oauth/login first."}

        data = await client.get_issue(issue_key=issue_key)
        return self._normalize_issue(data)

    async def get_raw_issue(self, issue_key: str) -> dict:
        client = self._get_client()

        if not client:
            return {"error": "Jira is not connected. Visit /jira/oauth/login first."}

        return await client.get_issue(issue_key=issue_key)

