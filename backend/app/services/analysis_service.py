from collections.abc import Mapping
from typing import Any

from app.schemas.analysis import IssueAnalysisResponse
from app.schemas.jira import JiraIssue
from app.services.llm_service import LLMService
from app.services.prompt_builder import PromptBuilder


class AnalysisService:
    def _nested_name(self, value: Any, key: str = "name") -> str | None:
        if isinstance(value, Mapping):
            return value.get(key)
        return value

    def _normalize_issue(self, issue: JiraIssue | Mapping[str, Any] | Any) -> JiraIssue:
        if isinstance(issue, JiraIssue):
            return issue

        if isinstance(issue, Mapping):
            fields = issue.get("fields") or {}

            if fields:
                return JiraIssue(
                    key=issue.get("key", ""),
                    summary=fields.get("summary", ""),
                    status=self._nested_name(fields.get("status")) or "",
                    issue_type=self._nested_name(fields.get("issuetype")) or "",
                    priority=self._nested_name(fields.get("priority")),
                    assignee=self._nested_name(fields.get("assignee"), "displayName"),
                    created=fields.get("created"),
                    updated=fields.get("updated"),
                )

            return JiraIssue(
                key=issue.get("key") or issue.get("issue_key") or "",
                summary=issue.get("summary") or "",
                status=issue.get("status") or "",
                issue_type=issue.get("issue_type") or issue.get("issuetype") or "",
                priority=issue.get("priority"),
                assignee=issue.get("assignee"),
                created=issue.get("created"),
                updated=issue.get("updated"),
            )

        return JiraIssue(
            key=getattr(issue, "key", ""),
            summary=getattr(issue, "summary", "") or "",
            status=getattr(issue, "status", "") or "",
            issue_type=getattr(issue, "issue_type", "") or "",
            priority=getattr(issue, "priority", None),
            assignee=getattr(issue, "assignee", None),
            created=getattr(issue, "created", None),
            updated=getattr(issue, "updated", None),
        )

    def analyze_issue_rules(
        self, issue: JiraIssue | Mapping[str, Any] | Any
    ) -> IssueAnalysisResponse:
        issue = self._normalize_issue(issue)
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

    def analyze_issue(self, issue: JiraIssue | Mapping[str, Any] | Any) -> dict:
        issue = self._normalize_issue(issue)
        rule_analysis = self.analyze_issue_rules(issue)

        prompt = PromptBuilder().build_issue_analysis_prompt(
            issue=issue,
            rule_analysis=rule_analysis.model_dump(),
        )

        try:
            ai_report = LLMService().generate_text(prompt)
        except Exception as exc:
            ai_report = (
                "AI report unavailable. "
                f"Rule-based analysis completed successfully. Reason: {exc}"
            )

        return {
            "issue_key": issue.key,
            "quality_score": rule_analysis.quality_score,
            "risk_level": rule_analysis.risk_level,
            "risks": rule_analysis.risks,
            "suggestions": rule_analysis.suggestions,
            "ai_report": ai_report,
        }
