from app.schemas.change_intelligence import ChangeAnalysisResponse
from app.schemas.quality_intelligence import QualityIntelligenceResponse
from app.schemas.traceability import TraceabilityReport


class QualityIntelligenceService:
    RISK_RANK = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
    }

    def _highest_risk(self, *risk_levels: str) -> str:
        normalized = [
            level.upper()
            for level in risk_levels
            if level and level.upper() in self.RISK_RANK
        ]

        if not normalized:
            return "UNKNOWN"

        return max(
            normalized,
            key=lambda level: self.RISK_RANK[level],
        )

    def _deduplicate(self, values: list[str]) -> list[str]:
        return list(dict.fromkeys(value for value in values if value))

    def orchestrate(
        self,
        issue_key: str,
        issue_analysis: dict,
        traceability: TraceabilityReport,
        change_analysis: ChangeAnalysisResponse,
    ) -> QualityIntelligenceResponse:
        decision_reasons: list[str] = []
        required_actions: list[str] = []

        issue_gate = str(
            issue_analysis.get("quality_gate", "UNKNOWN")
        ).upper()
        issue_risk = str(
            issue_analysis.get("risk_level", "UNKNOWN")
        ).upper()

        change_gate = change_analysis.quality_gate.upper()
        change_risk = change_analysis.risk_level.upper()

        traceability_risk = "LOW"

        if traceability.readiness == "WEAK":
            traceability_risk = "HIGH"
            decision_reasons.append(
                "Issue traceability is weak."
            )
        elif traceability.readiness == "PARTIAL":
            traceability_risk = "MEDIUM"
            decision_reasons.append(
                "Issue traceability requires further review."
            )

        if issue_gate.startswith("BLOCKED"):
            decision_reasons.append(
                "Issue-level quality gate is blocked."
            )

        if change_gate.startswith("BLOCKED"):
            decision_reasons.append(
                "Change-level quality gate is blocked."
            )

        if issue_analysis.get("evidence_readiness") == "INCOMPLETE":
            decision_reasons.append(
                "Issue evidence readiness is incomplete."
            )

        if change_analysis.evidence_readiness == "INCOMPLETE":
            decision_reasons.append(
                "Technical change evidence is incomplete."
            )

        overall_risk_level = self._highest_risk(
            issue_risk,
            change_risk,
            traceability_risk,
        )

        blocked = (
            issue_gate.startswith("BLOCKED")
            or change_gate.startswith("BLOCKED")
            or traceability.readiness == "WEAK"
        )

        review_required = (
            issue_gate == "REVIEW_REQUIRED"
            or change_gate == "REVIEW_REQUIRED"
            or traceability.readiness == "PARTIAL"
            or issue_analysis.get("evidence_readiness") == "PARTIAL"
            or change_analysis.evidence_readiness == "PARTIAL"
        )

        if blocked:
            overall_quality_gate = "BLOCKED_UNTIL_REVIEWED"
            release_readiness = "LOW"
        elif review_required:
            overall_quality_gate = "REVIEW_REQUIRED"
            release_readiness = "MEDIUM"
        else:
            overall_quality_gate = "READY_FOR_RELEASE_REVIEW"
            release_readiness = "HIGH"

        required_actions.extend(
            issue_analysis.get("suggestions", [])
        )
        required_actions.extend(traceability.recommendations)
        required_actions.extend(change_analysis.recommendations)

        if overall_quality_gate == "BLOCKED_UNTIL_REVIEWED":
            required_actions.append(
                "Resolve blocking quality, traceability, and evidence gaps "
                "before release review."
            )

        return QualityIntelligenceResponse(
            issue_key=issue_key,
            issue_analysis=issue_analysis,
            traceability=traceability,
            change_analysis=change_analysis,
            overall_risk_level=overall_risk_level,
            release_readiness=release_readiness,
            overall_quality_gate=overall_quality_gate,
            decision_reasons=self._deduplicate(decision_reasons),
            required_actions=self._deduplicate(required_actions),
        )
