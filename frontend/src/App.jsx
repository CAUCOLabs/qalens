import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function getRiskBadgeClass(riskLevel) {
  const normalizedRisk = String(riskLevel || "").toLowerCase();

  if (normalizedRisk === "low") {
    return "badge badge-low";
  }

  if (normalizedRisk === "high") {
    return "badge badge-high";
  }

  return "badge badge-medium";
}

function App() {
  const [issueKey, setIssueKey] = useState("SCRUM-1");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function analyzeIssue(event) {
    event?.preventDefault();

    const trimmedIssueKey = issueKey.trim();

    if (!trimmedIssueKey || loading) {
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/jira/issue/${encodeURIComponent(trimmedIssueKey)}/analyze`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Backend request failed");
      }

      setResult(data);
    } catch (error) {
      setResult({
        error: String(error.message || error),
      });
    } finally {
      setLoading(false);
    }
  }

  const hasAnalysis = result && !result.error;

  return (
    <main className="app-shell">
      <section className="dashboard">
        <header className="app-header">
          <div>
            <p className="eyebrow">Jira QA Analysis</p>
            <h1>QALens</h1>
            <p className="subtitle">AI-powered QA intelligence for Jira teams</p>
          </div>
        </header>

        <form className="search-card" onSubmit={analyzeIssue}>
          <label htmlFor="issue-key">Issue key</label>
          <div className="search-row">
            <input
              id="issue-key"
              value={issueKey}
              onChange={(event) => setIssueKey(event.target.value)}
              placeholder="Issue key, e.g. SCRUM-1"
              autoComplete="off"
            />

            <button type="submit" disabled={loading || !issueKey.trim()}>
              {loading ? "Analyzing..." : "Analyze"}
            </button>
          </div>
          {loading && <p className="loading-text">Analyzing issue...</p>}
        </form>

        {result?.error && (
          <section className="error-card" role="alert">
            <strong>Analysis failed</strong>
            <p>{result.error}</p>
          </section>
        )}

        {hasAnalysis && (
          <section className="results">
            <div className="summary-grid" aria-label="Analysis summary">
              <article className="summary-card">
                <span>Issue key</span>
                <strong>{result.issue_key || issueKey.trim()}</strong>
              </article>

              <article className="summary-card">
                <span>Quality score</span>
                <strong>{result.quality_score}</strong>
              </article>

              <article className="summary-card">
                <span>Risk level</span>
                <strong className={getRiskBadgeClass(result.risk_level)}>
                  {result.risk_level}
                </strong>
              </article>
            </div>

            <div className="insight-grid">
              <section className="panel">
                <div className="panel-heading">
                  <h2>Risks</h2>
                  <span>{result.risks?.length || 0}</span>
                </div>
                <ul className="insight-list">
                  {result.risks?.map((risk, index) => (
                    <li key={index}>{risk}</li>
                  ))}
                </ul>
              </section>

              <section className="panel">
                <div className="panel-heading">
                  <h2>Suggestions</h2>
                  <span>{result.suggestions?.length || 0}</span>
                </div>
                <ul className="insight-list">
                  {result.suggestions?.map((suggestion, index) => (
                    <li key={index}>{suggestion}</li>
                  ))}
                </ul>
              </section>
            </div>

            <section className="test-case-section">
              <div className="section-heading">
                <div>
                  <h2>Suggested Test Cases</h2>
                  <p>Rule-based scenarios generated from the issue details</p>
                </div>
                <span>{result.test_cases?.length || 0}</span>
              </div>

              <div className="test-case-grid">
                {result.test_cases?.map((testCase, index) => (
                  <article className="test-case-card" key={`${testCase.title}-${index}`}>
                    <div className="test-case-header">
                      <h3>{testCase.title}</h3>
                      <span>{testCase.priority}</span>
                    </div>
                    <p className="test-case-type">{testCase.type}</p>

                    <div className="test-case-block">
                      <strong>Steps</strong>
                      <ol>
                        {testCase.steps?.map((step, stepIndex) => (
                          <li key={stepIndex}>{step}</li>
                        ))}
                      </ol>
                    </div>

                    <div className="test-case-block">
                      <strong>Expected result</strong>
                      <p>{testCase.expected_result}</p>
                    </div>
                  </article>
                ))}
              </div>
            </section>

            <section className="report-card">
              <div className="report-heading">
                <h2>AI Report</h2>
                <p>Generated QA review</p>
              </div>
              <div className="markdown-body">
                <ReactMarkdown>{result.ai_report}</ReactMarkdown>
              </div>
            </section>
          </section>
        )}
      </section>
    </main>
  );
}

export default App;
