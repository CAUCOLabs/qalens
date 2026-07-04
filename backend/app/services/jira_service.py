from app.core.token_store import jira_resources, jira_token_data
from app.integrations.jira.client import JiraClient
from app.schemas.jira import JiraConnectionStatus, JiraIssue, JiraIssuesResponse


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

        return JiraIssue(
            key=raw_issue.get("key", ""),
            summary=fields.get("summary", ""),
            status=(fields.get("status") or {}).get("name", ""),
            issue_type=(fields.get("issuetype") or {}).get("name", ""),
            priority=(fields.get("priority") or {}).get("name"),
            assignee=(fields.get("assignee") or {}).get("displayName"),
            created=fields.get("created"),
            updated=fields.get("updated"),
        )

    async def get_projects(self) -> dict:
        client = self._get_client()

        if not client:
            return {"error": "Jira is not connected. Visit /jira/oauth/login first."}

        return await client.get_projects()

    async def get_issues(self, project_key: str) -> JiraIssuesResponse | dict:
        client = self._get_client()

        if not client:
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
            return {"error": "Jira is not connected. Visit /jira/oauth/login first."}

        data = await client.get_issue(issue_key=issue_key)
        return self._normalize_issue(data)
