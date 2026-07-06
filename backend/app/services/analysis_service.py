from app.schemas.analysis import IssueAnalysisResponse
from app.schemas.jira import JiraIssue
from app.services.llm_service import LLMService
from app.services.prompt_builder import PromptBuilder


class AnalysisService:
    def analyze_issue_rules(self, issue: JiraIssue) -> IssueAnalysisResponse:
        risks: list[str] = []
        suggestions: list[str] = []
        score = 100

        if not issue.summary or len(issue.summary.strip()) < 10:
            risks.append("Issue summary is too short.")
            suggestions.append("Add a clearer and more descriptive summary.")
            score -= 20

        if not issue.priority:
            risks.append("Priority is not defined.")
            suggestions.append("Set a priority level for this issue.")
            score -= 15

        if not issue.assignee:
            risks.append("Issue has no assignee.")
            suggestions.append("Assign an owner to avoid unclear responsibility.")
            score -= 15

        if issue.issue_type.lower() in ["story", "feature"]:
            risks.append("Acceptance criteria may be missing.")
            suggestions.append("Add clear acceptance criteria before QA starts.")
            score -= 20

        score = max(score, 0)

        if score >= 80:
            risk_level = "LOW"
        elif score >= 50:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        return IssueAnalysisResponse(
            issue_key=issue.key,
            quality_score=score,
            risk_level=risk_level,
            risks=risks,
            suggestions=suggestions,
        )

    def analyze_issue(self, issue: JiraIssue) -> dict:
        rule_analysis = self.analyze_issue_rules(issue)

        prompt = PromptBuilder().build_issue_analysis_prompt(
            issue=issue,
            rule_analysis=rule_analysis.model_dump(),
        )

        ai_report = LLMService().generate_text(prompt)

        return {
            "issue_key": issue.key,
            "quality_score": rule_analysis.quality_score,
            "risk_level": rule_analysis.risk_level,
            "risks": rule_analysis.risks,
            "suggestions": rule_analysis.suggestions,
            "ai_report": ai_report,
        }
