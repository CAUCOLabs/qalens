import httpx


class JiraClient:
    API_BASE_URL = "https://api.atlassian.com/ex/jira"

    def __init__(self, access_token: str, cloud_id: str):
        self.access_token = access_token
        self.cloud_id = cloud_id

    @property
    def base_url(self) -> str:
        return f"{self.API_BASE_URL}/{self.cloud_id}/rest/api/3"

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

    async def get_projects(self) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.base_url}/project/search",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_issues(self, project_key: str) -> dict:
        params = {
            "jql": f"project = {project_key} ORDER BY created DESC",
            "maxResults": 50,
            "fields": "summary,status,issuetype,priority,assignee,created,updated",
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.base_url}/search/jql",
                headers=self.headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def get_issue(self, issue_key: str) -> dict:
        params = {
            "fields": "summary,status,issuetype,priority,assignee,created,updated,description,parent,subtasks,issuelinks",
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.base_url}/issue/{issue_key}",
                headers=self.headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()
