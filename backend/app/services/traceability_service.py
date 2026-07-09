from collections.abc import Mapping
from typing import Any

from app.schemas.traceability import TraceabilityRelation, TraceabilityReport


class TraceabilityService:
    def _fields(self, raw_issue: Mapping[str, Any]) -> Mapping[str, Any]:
        return raw_issue.get("fields") or {}

    def _relation_from_issue(
        self,
        relation_type: str,
        raw_issue: Mapping[str, Any],
    ) -> TraceabilityRelation:
        fields = raw_issue.get("fields") or {}

        return TraceabilityRelation(
            relation_type=relation_type,
            key=raw_issue.get("key"),
            summary=fields.get("summary"),
            status=(fields.get("status") or {}).get("name"),
            issue_type=(fields.get("issuetype") or {}).get("name"),
        )

    def analyze_issue_traceability(self, raw_issue: Mapping[str, Any]) -> TraceabilityReport:
        fields = self._fields(raw_issue)

        relations: list[TraceabilityRelation] = []
        gaps: list[str] = []
        recommendations: list[str] = []
        score = 100

        parent = fields.get("parent")
        subtasks = fields.get("subtasks") or []
        issue_links = fields.get("issuelinks") or []

        if parent:
            relations.append(self._relation_from_issue("parent", parent))
        else:
            gaps.append("Issue has no parent or epic context.")
            recommendations.append("Link this issue to an epic, parent story, or higher-level requirement.")
            score -= 25

        if subtasks:
            for subtask in subtasks:
                relations.append(self._relation_from_issue("subtask", subtask))
        else:
            gaps.append("Issue has no subtasks.")
            recommendations.append("Break down implementation or QA work into subtasks when useful.")
            score -= 15

        if issue_links:
            for link in issue_links:
                inward = link.get("inwardIssue")
                outward = link.get("outwardIssue")
                link_type = (link.get("type") or {}).get("name", "linked issue")

                if inward:
                    relations.append(self._relation_from_issue(f"linked:{link_type}", inward))

                if outward:
                    relations.append(self._relation_from_issue(f"linked:{link_type}", outward))
        else:
            gaps.append("Issue has no linked issues.")
            recommendations.append("Link related bugs, dependencies, requirements, or test evidence.")
            score -= 20

        score = max(score, 0)

        has_parent = bool(parent)
        has_subtasks = bool(subtasks)
        has_linked_issues = bool(issue_links)

        if score >= 80:
            readiness = "TRACEABLE"
        elif score >= 50:
            readiness = "PARTIAL"
        else:
            readiness = "WEAK"

        return TraceabilityReport(
            issue_key=raw_issue.get("key", ""),
            has_parent=has_parent,
            has_subtasks=has_subtasks,
            has_linked_issues=has_linked_issues,
            traceability_score=score,
            readiness=readiness,
            relations=relations,
            gaps=gaps,
            recommendations=recommendations,
        )
