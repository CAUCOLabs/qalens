import { useMemo, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

const demoResult = {
  issue_key: "SCRUM-1",
  issue_analysis: {
    issue_key: "SCRUM-1",
    quality_score: 35,
    risk_level: "HIGH",
    requirement_quality: "WEAK",
    acceptance_criteria_readiness: "NOT_APPLICABLE",
    test_coverage_readiness: "LOW",
    evidence_readiness: "INCOMPLETE",
    trust_readiness: "LOW",
    quality_gate: "BLOCKED_UNTIL_CLARIFIED",
    risks: [
      "Issue summary is too short.",
      "Issue description lacks enough detail.",
      "Priority is not defined.",
      "Issue has no assignee.",
    ],
    suggestions: [
      "Add a clearer and more descriptive summary.",
      "Add context, expected behavior, and validation scope.",
      "Set a priority level for this issue.",
      "Assign an owner to avoid unclear responsibility.",
    ],
    trust_signals: [
      {
        category: "Evidence readiness",
        signal: "Issue lacks enough description to support evidence-ready QA.",
        severity: "HIGH",
      },
    ],
  },
  traceability: {
    issue_key: "SCRUM-1",
    traceability_score: 40,
    readiness: "WEAK",
    has_parent: false,
    has_subtasks: false,
    has_linked_issues: false,
    gaps: [
      "Issue has no parent or epic context.",
      "Issue has no subtasks.",
      "Issue has no linked issues.",
    ],
  },
  change_analysis: {
    repository: "qalens",
    pull_request: "PR-12",
    total_files_changed: 3,
    total_additions: 325,
    total_deletions: 80,
    change_risk_score: 99,
    risk_level: "HIGH",
    test_coverage_readiness: "LOW",
    evidence_readiness: "INCOMPLETE",
    release_readiness: "LOW",
    quality_gate: "BLOCKED_UNTIL_REVIEWED",
    risk_signals: [
      {
        category: "Authentication",
        signal: "Trust-sensitive authentication change detected.",
        severity: "HIGH",
        affected_files: ["backend/app/auth/oauth.py"],
      },
      {
        category: "Payments",
        signal: "Payment workflow and API changes detected.",
        severity: "HIGH",
        affected_files: ["backend/app/api/routes/payments.py"],
      },
      {
        category: "API contract",
        signal: "API or contract-related files changed.",
        severity: "MEDIUM",
        affected_files: ["backend/app/api/routes/payments.py"],
      },
      {
        category: "Configuration",
        signal: "Configuration-sensitive files changed.",
        severity: "MEDIUM",
        affected_files: ["backend/app/core/settings.py"],
      },
    ],
  },
  overall_risk_level: "HIGH",
  release_readiness: "LOW",
  overall_quality_gate: "BLOCKED_UNTIL_REVIEWED",
  decision_reasons: [
    "Issue traceability is weak.",
    "Issue-level quality gate is blocked.",
    "Change-level quality gate is blocked.",
    "Issue evidence readiness is incomplete.",
    "Technical change evidence is incomplete.",
  ],
  required_actions: [
    "Clarify the requirement and expected behavior.",
    "Link the issue to a parent requirement or epic.",
    "Add automated test coverage.",
    "Run API contract and backward-compatibility tests.",
    "Attach security, regression and validation evidence.",
  ],
};

const pipeline = [
  {
    index: "01",
    name: "Requirement",
    label: "Issue Intelligence",
    status: "WEAK",
  },
  {
    index: "02",
    name: "Traceability",
    label: "Delivery Context",
    status: "WEAK",
  },
  {
    index: "03",
    name: "Change",
    label: "Code Intelligence",
    status: "HIGH RISK",
  },
  {
    index: "04",
    name: "Orchestrator",
    label: "Quality Decision",
    status: "BLOCKED",
  },
];

function statusClass(value) {
  const normalized = String(value || "").toLowerCase();

  if (
    normalized.includes("high") ||
    normalized.includes("blocked") ||
    normalized.includes("weak") ||
    normalized.includes("low")
  ) {
    return "status status-danger";
  }

  if (
    normalized.includes("medium") ||
    normalized.includes("partial") ||
    normalized.includes("review")
  ) {
    return "status status-warning";
  }

  return "status status-success";
}

function MetricCard({ label, value, detail, emphasis = false }) {
  return (
    <article className={`metric-card ${emphasis ? "metric-card-emphasis" : ""}`}>
      <span className="metric-label">{label}</span>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </article>
  );
}

function App() {
  const [issueKey, setIssueKey] = useState("SCRUM-1");
  const [result, setResult] = useState(demoResult);
  const [mode, setMode] = useState("DEMO");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const issue = result.issue_analysis || {};
  const traceability = result.traceability || {};
  const change = result.change_analysis || {};

  const combinedSignals = useMemo(() => {
    return [
      ...(issue.trust_signals || []),
      ...(change.risk_signals || []),
    ].slice(0, 6);
  }, [issue.trust_signals, change.risk_signals]);

  async function runLiveAnalysis() {
    const trimmedIssueKey = issueKey.trim();

    if (!trimmedIssueKey || loading) {
      return;
    }

    setLoading(true);
    setError("");

    const payload = {
      issue_key: trimmedIssueKey,
      change: {
        issue_key: trimmedIssueKey,
        repository: "qalens",
        pull_request: "PR-12",
        title: "Update OAuth authentication and payment API",
        description:
          "Changes authentication, permissions and payment processing.",
        changed_files: [
          {
            path: "backend/app/auth/oauth.py",
            change_type: "modified",
            additions: 120,
            deletions: 30,
          },
          {
            path: "backend/app/api/routes/payments.py",
            change_type: "modified",
            additions: 180,
            deletions: 40,
          },
          {
            path: "backend/app/core/settings.py",
            change_type: "modified",
            additions: 25,
            deletions: 10,
          },
        ],
        test_evidence: [],
        linked_artifacts: [],
      },
    };

    try {
      const response = await fetch(
        `${API_BASE_URL}/quality-intelligence/analyze`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Quality analysis failed.");
      }

      setResult(data);
      setMode("LIVE");
    } catch (requestError) {
      setError(String(requestError.message || requestError));
      setResult(demoResult);
      setMode("DEMO");
    } finally {
      setLoading(false);
    }
  }

  function loadDemo() {
    setResult(demoResult);
    setMode("DEMO");
    setError("");
  }

  return (
    <main className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      <div className="grid-overlay" />

      <section className="console">
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark">
              <span />
              <span />
              <span />
            </div>
            <div>
              <strong>QALENS</strong>
              <small>Quality Intelligence Platform</small>
            </div>
          </div>

          <div className="topbar-meta">
            <span className={`mode-pill ${mode === "LIVE" ? "mode-live" : ""}`}>
              <i />
              {mode} INTELLIGENCE
            </span>
            <span>JIRA / SCRUM</span>
            <span>16 JUL 2026</span>
          </div>
        </header>

        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">AI Engineering & Quality Intelligence</p>
            <h1>
              Software delivery,
              <br />
              evaluated as <em>trust infrastructure.</em>
            </h1>
            <p className="hero-description">
              QALens connects requirements, traceability, code changes,
              evidence and release decisions through a unified quality
              intelligence pipeline.
            </p>
          </div>

          <div className="hero-control">
            <label htmlFor="issue-key">Analyze delivery asset</label>
            <div className="control-row">
              <input
                id="issue-key"
                value={issueKey}
                onChange={(event) => setIssueKey(event.target.value)}
                placeholder="SCRUM-1"
              />
              <button onClick={runLiveAnalysis} disabled={loading}>
                {loading ? "Running..." : "Run Intelligence"}
              </button>
            </div>
            <button className="demo-button" onClick={loadDemo}>
              Load presentation mode
            </button>
            {error && <p className="control-error">{error}</p>}
          </div>
        </section>

        <section className="gate-card">
          <div>
            <span className="gate-label">Overall Quality Gate</span>
            <h2>{result.overall_quality_gate}</h2>
            <p>
              Delivery cannot advance until quality, traceability and evidence
              gaps are resolved.
            </p>
          </div>

          <div className="gate-code">
            <span>DECISION / 04</span>
            <strong>BLOCK</strong>
          </div>
        </section>

        <section className="metrics-grid">
          <MetricCard
            label="Overall risk"
            value={result.overall_risk_level}
            detail="Cross-engine assessment"
            emphasis
          />
          <MetricCard
            label="Release readiness"
            value={result.release_readiness}
            detail="Pre-release decision"
          />
          <MetricCard
            label="Quality score"
            value={`${issue.quality_score ?? 0}/100`}
            detail={issue.requirement_quality}
          />
          <MetricCard
            label="Traceability"
            value={`${traceability.traceability_score ?? 0}/100`}
            detail={traceability.readiness}
          />
          <MetricCard
            label="Change risk"
            value={`${change.change_risk_score ?? 0}/100`}
            detail={`${change.total_files_changed ?? 0} files changed`}
          />
          <MetricCard
            label="Evidence"
            value={change.evidence_readiness || issue.evidence_readiness}
            detail="Delivery evidence status"
          />
        </section>

        <section className="pipeline-section">
          <div className="section-title">
            <div>
              <span>INTELLIGENCE PIPELINE</span>
              <h2>One delivery decision. Multiple specialized engines.</h2>
            </div>
            <p>QALENS CORE / ACTIVE</p>
          </div>

          <div className="pipeline">
            {pipeline.map((step, index) => (
              <article className="pipeline-node" key={step.name}>
                <span className="node-index">{step.index}</span>
                <small>{step.label}</small>
                <strong>{step.name}</strong>
                <span className={statusClass(step.status)}>{step.status}</span>
                {index < pipeline.length - 1 && (
                  <span className="pipeline-connector">→</span>
                )}
              </article>
            ))}
          </div>
        </section>

        <section className="intelligence-grid">
          <article className="intelligence-panel signals-panel">
            <div className="panel-title">
              <div>
                <span>TRUST & RISK SIGNALS</span>
                <h2>Detected across the delivery chain</h2>
              </div>
              <strong>{combinedSignals.length}</strong>
            </div>

            <div className="signal-list">
              {combinedSignals.map((signal, index) => (
                <div className="signal-row" key={`${signal.category}-${index}`}>
                  <span className={statusClass(signal.severity)}>
                    {signal.severity}
                  </span>
                  <div>
                    <strong>{signal.category}</strong>
                    <p>{signal.signal}</p>
                  </div>
                </div>
              ))}
            </div>
          </article>

          <article className="intelligence-panel action-panel">
            <div className="panel-title">
              <div>
                <span>REQUIRED ACTIONS</span>
                <h2>Controls before release review</h2>
              </div>
              <strong>{result.required_actions?.length || 0}</strong>
            </div>

            <ol className="action-list">
              {result.required_actions?.slice(0, 6).map((action, index) => (
                <li key={index}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <p>{action}</p>
                </li>
              ))}
            </ol>
          </article>
        </section>

        <section className="decision-grid">
          <article className="decision-card">
            <span>Issue Intelligence</span>
            <h3>{result.issue_key}</h3>
            <dl>
              <div>
                <dt>Requirement</dt>
                <dd>{issue.requirement_quality}</dd>
              </div>
              <div>
                <dt>Trust readiness</dt>
                <dd>{issue.trust_readiness}</dd>
              </div>
              <div>
                <dt>Test coverage</dt>
                <dd>{issue.test_coverage_readiness}</dd>
              </div>
            </dl>
          </article>

          <article className="decision-card">
            <span>Traceability Intelligence</span>
            <h3>{traceability.readiness}</h3>
            <dl>
              <div>
                <dt>Parent context</dt>
                <dd>{traceability.has_parent ? "Linked" : "Missing"}</dd>
              </div>
              <div>
                <dt>Subtasks</dt>
                <dd>{traceability.has_subtasks ? "Linked" : "Missing"}</dd>
              </div>
              <div>
                <dt>Issue links</dt>
                <dd>{traceability.has_linked_issues ? "Linked" : "Missing"}</dd>
              </div>
            </dl>
          </article>

          <article className="decision-card">
            <span>Change Intelligence</span>
            <h3>{change.pull_request || "PR-12"}</h3>
            <dl>
              <div>
                <dt>Repository</dt>
                <dd>{change.repository}</dd>
              </div>
              <div>
                <dt>Code churn</dt>
                <dd>
                  +{change.total_additions} / -{change.total_deletions}
                </dd>
              </div>
              <div>
                <dt>Quality gate</dt>
                <dd>Blocked</dd>
              </div>
            </dl>
          </article>
        </section>

        <footer className="footer">
          <div>
            <strong>QALENS</strong>
            <span>AI Engineering & Quality Intelligence</span>
          </div>
          <p>
            Part of the Trust Infrastructure Ecosystem · Aurora · QALens ·
            AISOSEC Audit
          </p>
        </footer>
      </section>
    </main>
  );
}

export default App;
