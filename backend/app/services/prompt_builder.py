from app.schemas.jira import JiraIssue


class PromptBuilder:
    def build_issue_analysis_prompt(self, issue: JiraIssue, rule_analysis: dict) -> str:
        return f"""
You are a senior QA analyst reviewing a Jira issue.

You MUST return ONLY valid JSON.
Do not use Markdown.
Do not use headings.
Do not wrap the response in ```json.
Do not include any text before or after the JSON.

Use exactly this JSON structure:

{{
  "overall_assessment": "string",
  "main_risks": ["string"],
  "missing_information": ["string"],
  "suggested_test_cases": ["string"],
  "recommended_next_actions": ["string"]
}}

Jira Issue:
- Key: {issue.key}
- Summary: {issue.summary}
- Description: {issue.description}
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
- Suggested test cases: {rule_analysis.get("test_cases")}
"""
