from app.schemas.jira import JiraIssue


class PromptBuilder:
    def build_issue_analysis_prompt(self, issue: JiraIssue, rule_analysis: dict) -> str:
        return f"""
You are a senior QA analyst reviewing a Jira issue.

Analyze the issue from a QA perspective.

Jira Issue:
- Key: {issue.key}
- Summary: {issue.summary}
- Type: {issue.issue_type}
- Status: {issue.status}
- Priority: {issue.priority}
- Assignee: {issue.assignee}
- Created: {issue.created}
- Updated: {issue.updated}

Rule-based analysis:
- Quality score: {rule_analysis.get("quality_score")}
- Risk level: {rule_analysis.get("risk_level")}
- Risks: {rule_analysis.get("risks")}
- Suggestions: {rule_analysis.get("suggestions")}

Return a concise QA analysis with:
1. Overall QA assessment
2. Main risks
3. Missing information
4. Suggested test cases
5. Recommended next actions
"""
