from pathlib import PurePosixPath

from app.schemas.change_intelligence import (
    ChangeAnalysisRequest,
    ChangeAnalysisResponse,
    ChangeRiskSignal,
)


class ChangeIntelligenceService:
    SENSITIVE_PATTERNS = {
        "authentication": (
            "auth",
            "login",
            "oauth",
            "jwt",
            "session",
            "password",
            "mfa",
        ),
        "authorization": (
            "permission",
            "permissions",
            "role",
            "roles",
            "access",
            "policy",
        ),
        "payments": (
            "payment",
            "payments",
            "billing",
            "invoice",
            "checkout",
            "transaction",
        ),
        "identity_and_customer_data": (
            "identity",
            "customer",
            "profile",
            "personal",
            "gdpr",
            "kyc",
            "aml",
        ),
        "digital_assets": (
            "wallet",
            "crypto",
            "token",
            "blockchain",
            "custody",
            "asset",
        ),
        "ai_and_agents": (
            "prompt",
            "agent",
            "llm",
            "openai",
            "model",
            "ai_",
        ),
        "secrets_and_cryptography": (
            "secret",
            "credential",
            "private_key",
            "certificate",
            "crypto",
            "encryption",
        ),
    }

    TEST_MARKERS = (
        "/test/",
        "/tests/",
        "test_",
        "_test.",
        ".spec.",
        ".test.",
    )

    API_MARKERS = (
        "openapi",
        "swagger",
        "/api/",
        "routes",
        "router",
        "controller",
        "endpoint",
    )

    MIGRATION_MARKERS = (
        "migration",
        "migrations",
        "alembic",
        "schema.sql",
    )

    INFRASTRUCTURE_MARKERS = (
        "dockerfile",
        "docker-compose",
        ".github/workflows",
        "terraform",
        "kubernetes",
        "k8s",
        "helm",
        "nginx",
    )

    CONFIG_MARKERS = (
        ".env",
        "config",
        "settings",
        "secrets",
    )

    def _matches(self, path: str, markers: tuple[str, ...]) -> bool:
        normalized = path.lower()
        return any(marker in normalized for marker in markers)

    def analyze_change(
        self,
        request: ChangeAnalysisRequest,
    ) -> ChangeAnalysisResponse:
        files = request.changed_files
        paths = [item.path for item in files]

        total_additions = sum(item.additions for item in files)
        total_deletions = sum(item.deletions for item in files)
        total_files = len(files)

        risk_signals: list[ChangeRiskSignal] = []
        missing_controls: list[str] = []
        recommendations: list[str] = []
        score = 0

        sensitive_files: dict[str, list[str]] = {}

        for category, markers in self.SENSITIVE_PATTERNS.items():
            matched = [
                path
                for path in paths
                if self._matches(path, markers)
            ]
            if matched:
                sensitive_files[category] = matched
                risk_signals.append(
                    ChangeRiskSignal(
                        category=category,
                        signal=f"Trust-sensitive change detected in {category}.",
                        severity="HIGH",
                        affected_files=matched,
                    )
                )
                score += 18

        test_files = [
            path for path in paths if self._matches(path, self.TEST_MARKERS)
        ]

        api_files = [
            path for path in paths if self._matches(path, self.API_MARKERS)
        ]

        migration_files = [
            path for path in paths if self._matches(path, self.MIGRATION_MARKERS)
        ]

        infrastructure_files = [
            path
            for path in paths
            if self._matches(path, self.INFRASTRUCTURE_MARKERS)
        ]

        config_files = [
            path for path in paths if self._matches(path, self.CONFIG_MARKERS)
        ]

        if total_files >= 20:
            risk_signals.append(
                ChangeRiskSignal(
                    category="change_scope",
                    signal="Large change scope detected.",
                    severity="HIGH",
                    affected_files=paths,
                )
            )
            score += 20
        elif total_files >= 8:
            risk_signals.append(
                ChangeRiskSignal(
                    category="change_scope",
                    signal="Medium-sized change scope detected.",
                    severity="MEDIUM",
                    affected_files=paths,
                )
            )
            score += 10

        churn = total_additions + total_deletions
        if churn >= 1000:
            risk_signals.append(
                ChangeRiskSignal(
                    category="code_churn",
                    signal="Very high code churn detected.",
                    severity="HIGH",
                    affected_files=paths,
                )
            )
            score += 20
        elif churn >= 300:
            risk_signals.append(
                ChangeRiskSignal(
                    category="code_churn",
                    signal="Elevated code churn detected.",
                    severity="MEDIUM",
                    affected_files=paths,
                )
            )
            score += 10

        if api_files:
            risk_signals.append(
                ChangeRiskSignal(
                    category="api_contract",
                    signal="API or contract-related files changed.",
                    severity="MEDIUM",
                    affected_files=api_files,
                )
            )
            score += 10

        if migration_files:
            risk_signals.append(
                ChangeRiskSignal(
                    category="database_change",
                    signal="Database migration or schema change detected.",
                    severity="HIGH",
                    affected_files=migration_files,
                )
            )
            score += 18

        if infrastructure_files:
            risk_signals.append(
                ChangeRiskSignal(
                    category="infrastructure",
                    signal="Infrastructure or delivery configuration changed.",
                    severity="HIGH",
                    affected_files=infrastructure_files,
                )
            )
            score += 15

        if config_files:
            risk_signals.append(
                ChangeRiskSignal(
                    category="configuration",
                    signal="Configuration-sensitive files changed.",
                    severity="MEDIUM",
                    affected_files=config_files,
                )
            )
            score += 8

        has_test_evidence = bool(request.test_evidence)
        has_test_changes = bool(test_files)

        if not has_test_changes and not has_test_evidence:
            missing_controls.append(
                "No test changes or test execution evidence were provided."
            )
            recommendations.append(
                "Add automated tests or attach test execution evidence."
            )
            score += 20

        if sensitive_files and not has_test_evidence:
            missing_controls.append(
                "Trust-sensitive changes lack explicit validation evidence."
            )
            recommendations.append(
                "Provide targeted security, regression, and control validation evidence."
            )
            score += 15

        if api_files and not any(
            "contract" in evidence.lower() or "api" in evidence.lower()
            for evidence in request.test_evidence
        ):
            missing_controls.append(
                "API changes lack explicit contract-test evidence."
            )
            recommendations.append(
                "Run API contract and backward-compatibility tests."
            )

        if migration_files and not any(
            "migration" in evidence.lower()
            or "rollback" in evidence.lower()
            for evidence in request.test_evidence
        ):
            missing_controls.append(
                "Database changes lack migration and rollback evidence."
            )
            recommendations.append(
                "Validate migration, rollback, and data-integrity scenarios."
            )

        if not request.issue_key:
            missing_controls.append(
                "Change is not linked to a Jira issue or requirement."
            )
            recommendations.append(
                "Link the change to a requirement, issue, or approved work item."
            )
            score += 10

        if not request.linked_artifacts:
            missing_controls.append(
                "No supporting artifacts are linked."
            )
            recommendations.append(
                "Attach design, risk, approval, or implementation evidence."
            )

        score = min(score, 100)

        if score >= 70:
            risk_level = "HIGH"
        elif score >= 35:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        if has_test_changes and has_test_evidence:
            test_coverage_readiness = "HIGH"
        elif has_test_changes or has_test_evidence:
            test_coverage_readiness = "MEDIUM"
        else:
            test_coverage_readiness = "LOW"

        if request.test_evidence and request.linked_artifacts:
            evidence_readiness = "READY"
        elif request.test_evidence or request.linked_artifacts:
            evidence_readiness = "PARTIAL"
        else:
            evidence_readiness = "INCOMPLETE"

        if (
            risk_level == "HIGH"
            or evidence_readiness == "INCOMPLETE"
            or (
                sensitive_files
                and test_coverage_readiness == "LOW"
            )
        ):
            release_readiness = "LOW"
            quality_gate = "BLOCKED_UNTIL_REVIEWED"
        elif risk_level == "MEDIUM" or evidence_readiness == "PARTIAL":
            release_readiness = "MEDIUM"
            quality_gate = "REVIEW_REQUIRED"
        else:
            release_readiness = "HIGH"
            quality_gate = "READY_FOR_RELEASE_REVIEW"

        return ChangeAnalysisResponse(
            issue_key=request.issue_key,
            repository=request.repository,
            pull_request=request.pull_request,
            total_files_changed=total_files,
            total_additions=total_additions,
            total_deletions=total_deletions,
            change_risk_score=score,
            risk_level=risk_level,
            test_coverage_readiness=test_coverage_readiness,
            evidence_readiness=evidence_readiness,
            release_readiness=release_readiness,
            quality_gate=quality_gate,
            risk_signals=risk_signals,
            missing_controls=missing_controls,
            recommendations=list(dict.fromkeys(recommendations)),
        )
