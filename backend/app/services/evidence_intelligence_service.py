from app.schemas.evidence_intelligence import (
    EvidenceArtifact,
    EvidenceIntelligenceRequest,
    EvidenceIntelligenceResponse,
    EvidenceSignal,
)


class EvidenceIntelligenceService:
    REQUIRED_CATEGORIES = {
        "test_execution": "Test execution evidence",
        "api_contract": "API contract evidence",
        "security_review": "Security review evidence",
        "qa_approval": "QA approval",
        "architecture_decision": "Architecture decision record",
        "risk_assessment": "Risk assessment",
        "deployment_evidence": "Deployment evidence",
    }

    HIGH_VALUE_CATEGORIES = {
        "test_execution",
        "security_review",
        "qa_approval",
        "risk_assessment",
    }

    def _normalize_category(self, category: str) -> str:
        return category.strip().lower().replace(" ", "_").replace("-", "_")

    def analyze(
        self,
        request: EvidenceIntelligenceRequest,
    ) -> EvidenceIntelligenceResponse:
        provided_artifacts = [
            artifact
            for artifact in request.evidence
            if artifact.provided
        ]

        provided_categories = {
            self._normalize_category(artifact.category)
            for artifact in provided_artifacts
        }

        provided_evidence = [
            artifact.name
            for artifact in provided_artifacts
        ]

        missing_evidence: list[str] = []
        evidence_signals: list[EvidenceSignal] = []
        recommendations: list[str] = []

        score = 0

        for category, label in self.REQUIRED_CATEGORIES.items():
            if category in provided_categories:
                score += 15 if category in self.HIGH_VALUE_CATEGORIES else 10

                evidence_signals.append(
                    EvidenceSignal(
                        category=category,
                        signal=f"{label} is available.",
                        severity="LOW",
                    )
                )
            else:
                missing_evidence.append(label)

                severity = (
                    "HIGH"
                    if category in self.HIGH_VALUE_CATEGORIES
                    else "MEDIUM"
                )

                evidence_signals.append(
                    EvidenceSignal(
                        category=category,
                        signal=f"{label} is missing.",
                        severity=severity,
                    )
                )

        if not provided_artifacts:
            recommendations.append(
                "Attach evidence before requesting release review."
            )
        else:
            recommendations.append(
                "Verify that all attached evidence is current, traceable, and reviewable."
            )

        if "test_execution" not in provided_categories:
            recommendations.append(
                "Provide automated or manual test execution results."
            )

        if "security_review" not in provided_categories:
            recommendations.append(
                "Add security review evidence for trust-sensitive changes."
            )

        if "qa_approval" not in provided_categories:
            recommendations.append(
                "Capture explicit QA approval before release review."
            )

        if "risk_assessment" not in provided_categories:
            recommendations.append(
                "Document residual risks and mitigation decisions."
            )

        score = min(score, 100)

        if score >= 80:
            evidence_readiness = "HIGH"
            quality_gate = "READY_FOR_REVIEW"
        elif score >= 50:
            evidence_readiness = "MEDIUM"
            quality_gate = "REVIEW_REQUIRED"
        else:
            evidence_readiness = "LOW"
            quality_gate = "BLOCKED_UNTIL_EVIDENCE_COMPLETE"

        return EvidenceIntelligenceResponse(
            issue_key=request.issue_key,
            evidence_score=score,
            evidence_readiness=evidence_readiness,
            quality_gate=quality_gate,
            provided_evidence=provided_evidence,
            missing_evidence=missing_evidence,
            evidence_signals=evidence_signals,
            recommendations=list(dict.fromkeys(recommendations)),
        )
