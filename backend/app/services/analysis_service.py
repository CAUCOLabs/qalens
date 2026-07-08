from collections.abc import Mapping
from typing import Any

from app.schemas.analysis import IssueAnalysisResponse, TestCaseSuggestion, TrustSignal
from app.schemas.jira import JiraIssue
from app.services.llm_service import LLMService
from app.services.prompt_builder import PromptBuilder


class AnalysisService:
    def _nested_name(self, value: Any, key: str = "name") -> str | None:
        if isinstance(value, Mapping):
            return value.get(key)
        return value

    def _description_text(self, value: Any) -> str | None:
        if value is None or isinstance(value, str):
            return value
        return str(value)

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
                    description=self._description_text(fields.get("description")),
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
                description=self._description_text(issue.get("description")),
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
            description=self._description_text(getattr(issue, "description", None)),
            priority=getattr(issue, "priority", None),
            assignee=getattr(issue, "assignee", None),
            created=getattr(issue, "created", None),
            updated=getattr(issue, "updated", None),
        )

    def _has_acceptance_criteria(self, issue: JiraIssue) -> bool:
        issue_text = f"{issue.summary} {issue.description or ''}".lower()
        return "acceptance criteria" in issue_text or (
            "given" in issue_text and "when" in issue_text
        )

    def _assess_requirement_quality(self, issue: JiraIssue) -> str:
        if not issue.summary or len(issue.summary.strip()) < 10:
            return "WEAK"
        if not issue.description or len(issue.description.strip()) < 40:
            return "PARTIAL"
        return "STRONG"

    def _assess_acceptance_criteria_readiness(self, issue: JiraIssue) -> str:
        if issue.issue_type.lower() not in ["story", "feature"]:
            return "NOT_APPLICABLE"
        return "READY" if self._has_acceptance_criteria(issue) else "MISSING"

    def _assess_test_coverage_readiness(self, issue: JiraIssue) -> str:
        if not issue.summary or not issue.description:
            return "LOW"
        if not issue.priority or not issue.assignee:
            return "MEDIUM"
        return "HIGH"

    def _assess_evidence_readiness(self, issue: JiraIssue) -> str:
        if not issue.description or len(issue.description.strip()) < 40:
            return "INCOMPLETE"
        if not self._has_acceptance_criteria(issue) and issue.issue_type.lower() in ["story", "feature"]:
            return "PARTIAL"
        return "READY"

    def _detect_trust_signals(self, issue: JiraIssue) -> list[TrustSignal]:
        issue_text = f"{issue.summary} {issue.description or ''}".lower()
        signals: list[TrustSignal] = []

        sensitive_terms = [
            "payment", "payments", "bank", "account", "customer", "kyc",
            "aml", "asset", "wallet", "crypto", "token", "approval",
            "identity", "authentication", "authorization", "gdpr",
            "personal data", "ai", "agent", "audit", "compliance",
        ]

        for term in sensitive_terms:
            if term in issue_text:
                signals.append(
                    TrustSignal(
                        category="regulated_or_sensitive_functionality",
                        signal=f"Potential trust-sensitive term detected: {term}",
                        severity="MEDIUM",
                    )
                )

        if not issue.description or len(issue.description.strip()) < 40:
            signals.append(
                TrustSignal(
                    category="evidence_readiness",
                    signal="Issue lacks enough description to support evidence-ready QA.",
                    severity="HIGH",
                )
            )

        if issue.issue_type.lower() in ["story", "feature"] and not self._has_acceptance_criteria(issue):
            signals.append(
                TrustSignal(
                    category="requirement_quality",
                    signal="Story or feature may be missing acceptance criteria.",
                    severity="HIGH",
                )
            )

        return signals

    def _assess_trust_readiness(self, issue: JiraIssue, trust_signals: list[TrustSignal]) -> str:
        if any(signal.severity == "HIGH" for signal in trust_signals):
            return "LOW"
        if trust_signals:
            return "MEDIUM"
        return "HIGH"

    def _quality_gate(self, risk_level: str, trust_readiness: str, evidence_readiness: str) -> str:
        if risk_level == "HIGH" or trust_readiness == "LOW" or evidence_readiness == "INCOMPLETE":
            return "BLOCKED_UNTIL_CLARIFIED"
        if risk_level == "MEDIUM" or trust_readiness == "MEDIUM" or evidence_readiness == "PARTIAL":
            return "REVIEW_REQUIRED"
        return "READY_FOR_QA"

    def _generate_test_cases(self, issue: JiraIssue) -> list[TestCaseSuggestion]:
        test_cases: list[TestCaseSuggestion] = [
            TestCaseSuggestion(
                title="Validate issue requirements are testable",
                type="Functional",
                priority="High",
                steps=[
                    "Review the Jira issue summary and description",
                    "Check whether the expected behavior and validation scope are clear",
                    "Confirm the issue contains enough information to design QA coverage",
                ],
                expected_result=(
                    "The issue contains enough detail for development and QA validation."
                ),
            )
        ]

        if not issue.summary or len(issue.summary.strip()) < 10:
            test_cases.append(
                TestCaseSuggestion(
                    title="Validate required issue details",
                    type="Functional",
                    priority="High",
                    steps=[
                        "Review the Jira issue summary",
                        "Check whether description and acceptance criteria are present",
                    ],
                    expected_result=(
                        "The issue contains enough information for development and QA validation."
                    ),
                )
            )

        if not issue.description or len(issue.description.strip()) < 40:
            test_cases.append(
                TestCaseSuggestion(
                    title="Validate issue description completeness",
                    type="Functional",
                    priority="High",
                    steps=[
                        "Review the issue description",
                        "Check whether the current behavior and expected behavior are documented",
                        "Confirm QA can identify the affected workflow and validation scope",
                    ],
                    expected_result=(
                        "The description provides enough context to design reliable tests."
                    ),
                )
            )

        if not issue.priority:
            test_cases.append(
                TestCaseSuggestion(
                    title="Confirm priority-based test coverage",
                    type="Process",
                    priority="Medium",
                    steps=[
                        "Review the issue priority field",
                        "Confirm the business impact and QA urgency are documented",
                        "Map the priority to required test depth and regression scope",
                    ],
                    expected_result=(
                        "The issue priority is clear enough to guide QA planning."
                    ),
                )
            )

        if not issue.assignee:
            test_cases.append(
                TestCaseSuggestion(
                    title="Confirm issue ownership before QA handoff",
                    type="Process",
                    priority="Medium",
                    steps=[
                        "Review the assignee field",
                        "Identify the owner responsible for clarifying requirements",
                        "Confirm unresolved QA questions have a clear contact",
                    ],
                    expected_result=(
                        "A responsible owner is assigned before QA validation begins."
                    ),
                )
            )

        if issue.issue_type.lower() in ["story", "feature"]:
            test_cases.append(
                TestCaseSuggestion(
                    title="Validate acceptance criteria coverage",
                    type="Functional",
                    priority="High",
                    steps=[
                        "Review each acceptance criterion in the Jira issue",
                        "Create a positive validation scenario for each criterion",
                        "Create at least one negative or edge-case scenario",
                    ],
                    expected_result=(
                        "All acceptance criteria can be verified with clear test scenarios."
                    ),
                )
            )

        if issue.issue_type.lower() == "bug":
            test_cases.append(
                TestCaseSuggestion(
                    title="Reproduce the reported defect",
                    type="Regression",
                    priority="High",
                    steps=[
                        "Follow the reproduction details from the Jira issue",
                        "Capture the actual behavior before the fix",
                        "Retest the same flow after the fix is applied",
                    ],
                    expected_result=(
                        "The defect is reproducible before the fix and no longer occurs after the fix."
                    ),
                )
            )

        if issue.priority and issue.priority.lower() in ["high", "highest", "critical"]:
            test_cases.append(
                TestCaseSuggestion(
                    title="Run targeted regression around impacted workflow",
                    type="Regression",
                    priority="High",
                    steps=[
                        "Identify the feature area changed by the issue",
                        "Run existing regression checks around the impacted workflow",
                        "Verify adjacent happy-path and error-path behavior still works",
                    ],
                    expected_result=(
                        "The change works as expected without breaking related workflows."
                    ),
                )
            )

        return test_cases

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

        if not issue.description or len(issue.description.strip()) < 40:
            risks.append("Issue description lacks enough detail.")
            suggestions.append("Add context, expected behavior, and validation scope.")
            score -= 15

        if not issue.priority:
            risks.append("Priority is not defined.")
            suggestions.append("Set a priority level for this issue.")
            score -= 15

        if not issue.assignee:
            risks.append("Issue has no assignee.")
            suggestions.append("Assign an owner to avoid unclear responsibility.")
            score -= 15

        if issue.issue_type.lower() in ["story", "feature"] and not self._has_acceptance_criteria(
            issue
        ):
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

        test_cases = self._generate_test_cases(issue)
        trust_signals = self._detect_trust_signals(issue)
        requirement_quality = self._assess_requirement_quality(issue)
        acceptance_criteria_readiness = self._assess_acceptance_criteria_readiness(issue)
        test_coverage_readiness = self._assess_test_coverage_readiness(issue)
        evidence_readiness = self._assess_evidence_readiness(issue)
        trust_readiness = self._assess_trust_readiness(issue, trust_signals)
        quality_gate = self._quality_gate(risk_level, trust_readiness, evidence_readiness)

        return IssueAnalysisResponse(
            issue_key=issue.key,
            quality_score=score,
            risk_level=risk_level,
            risks=risks,
            suggestions=suggestions,
            test_cases=test_cases,
            requirement_quality=requirement_quality,
            acceptance_criteria_readiness=acceptance_criteria_readiness,
            test_coverage_readiness=test_coverage_readiness,
            evidence_readiness=evidence_readiness,
            trust_readiness=trust_readiness,
            quality_gate=quality_gate,
            trust_signals=trust_signals,
        )

    def analyze_issue(self, issue: JiraIssue | Mapping[str, Any] | Any) -> dict:
        issue = self._normalize_issue(issue)
        rule_analysis = self.analyze_issue_rules(issue)

        prompt = PromptBuilder().build_issue_analysis_prompt(
            issue=issue,
            rule_analysis=rule_analysis.model_dump(),
        )

        try:
            ai_analysis = LLMService().generate_json(prompt)
        except Exception as exc:
            ai_analysis = {
                "overall_assessment": (
                    "AI analysis unavailable. "
                    f"Rule-based analysis completed successfully. Reason: {exc}"
                ),
                "main_risks": [],
                "missing_information": [],
                "suggested_test_cases": [],
                "recommended_next_actions": [],
            }

        return {
            "issue_key": issue.key,
            "quality_score": rule_analysis.quality_score,
            "risk_level": rule_analysis.risk_level,
            "risks": rule_analysis.risks,
            "suggestions": rule_analysis.suggestions,
            "test_cases": [
                test_case.model_dump() for test_case in rule_analysis.test_cases
            ],
            "requirement_quality": rule_analysis.requirement_quality,
            "acceptance_criteria_readiness": rule_analysis.acceptance_criteria_readiness,
            "test_coverage_readiness": rule_analysis.test_coverage_readiness,
            "evidence_readiness": rule_analysis.evidence_readiness,
            "trust_readiness": rule_analysis.trust_readiness,
            "quality_gate": rule_analysis.quality_gate,
            "trust_signals": [
                signal.model_dump() for signal in rule_analysis.trust_signals
            ],
            "ai_analysis": ai_analysis,
        }

    def analyze_project(self, project_key: str, issues: list[JiraIssue]) -> dict:
        analyzed_issues = [self.analyze_issue_rules(issue) for issue in issues]

        total = len(analyzed_issues)

        if total == 0:
            return {
                "project_key": project_key,
                "total_issues": 0,
                "average_quality_score": 0,
                "overall_risk_level": "UNKNOWN",
                "quality_gate": "NO_DATA",
                "summary": "No issues found for this project.",
                "risk_distribution": {},
                "trust_readiness_distribution": {},
                "blocked_issues": [],
                "top_risks": [],
            }

        average_score = round(
            sum(issue.quality_score for issue in analyzed_issues) / total
        )

        risk_distribution = {
            "LOW": sum(1 for issue in analyzed_issues if issue.risk_level == "LOW"),
            "MEDIUM": sum(1 for issue in analyzed_issues if issue.risk_level == "MEDIUM"),
            "HIGH": sum(1 for issue in analyzed_issues if issue.risk_level == "HIGH"),
        }

        trust_readiness_distribution = {
            "HIGH": sum(1 for issue in analyzed_issues if issue.trust_readiness == "HIGH"),
            "MEDIUM": sum(1 for issue in analyzed_issues if issue.trust_readiness == "MEDIUM"),
            "LOW": sum(1 for issue in analyzed_issues if issue.trust_readiness == "LOW"),
        }

        blocked_issues = [
            {
                "issue_key": issue.issue_key,
                "quality_score": issue.quality_score,
                "risk_level": issue.risk_level,
                "quality_gate": issue.quality_gate,
                "trust_readiness": issue.trust_readiness,
                "risks": issue.risks,
            }
            for issue in analyzed_issues
            if issue.quality_gate == "BLOCKED_UNTIL_CLARIFIED"
        ]

        top_risks: list[str] = []
        for issue in analyzed_issues:
            top_risks.extend(issue.risks)

        unique_top_risks = list(dict.fromkeys(top_risks))[:10]

        if risk_distribution["HIGH"] > 0 or trust_readiness_distribution["LOW"] > 0:
            overall_risk_level = "HIGH"
            project_quality_gate = "BLOCKED_UNTIL_CLARIFIED"
        elif risk_distribution["MEDIUM"] > 0 or trust_readiness_distribution["MEDIUM"] > 0:
            overall_risk_level = "MEDIUM"
            project_quality_gate = "REVIEW_REQUIRED"
        else:
            overall_risk_level = "LOW"
            project_quality_gate = "READY_FOR_QA"

        return {
            "project_key": project_key,
            "total_issues": total,
            "average_quality_score": average_score,
            "overall_risk_level": overall_risk_level,
            "quality_gate": project_quality_gate,
            "summary": (
                f"Project {project_key} has {total} analyzed issues with an "
                f"average quality score of {average_score}. "
                f"Overall risk level is {overall_risk_level}."
            ),
            "risk_distribution": risk_distribution,
            "trust_readiness_distribution": trust_readiness_distribution,
            "blocked_issues": blocked_issues,
            "top_risks": unique_top_risks,
        }

