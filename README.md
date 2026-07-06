# QALens

QALens is an AI-powered QA intelligence platform for software teams working with Jira.

The goal of QALens is to help QA engineers, developers, product owners, and engineering teams evaluate the quality of Jira issues before they move into development or testing.

Instead of replacing QA workflows, QALens augments them by identifying missing information, unclear requirements, weak acceptance criteria, ownership gaps, and potential testing risks.

---

## Why QALens?

Many software teams lose time because Jira issues are incomplete, vague, or not ready for development.

Common problems include:

- Unclear issue summaries
- Missing acceptance criteria
- No priority or assignee
- Weak testability
- Ambiguous business requirements
- QA work starting too late in the process

QALens helps teams detect these problems earlier.

---

## Current MVP

The current MVP includes:

- FastAPI backend
- React frontend
- Jira issue analysis endpoint
- Local demo mode for development
- AI-generated QA report
- QA readiness score
- Risk level classification
- Risk detection
- Improvement suggestions
- Markdown-rendered AI report in the frontend

Example output:

```json
{
  "issue_key": "SCRUM-1",
  "quality_score": 50,
  "risk_level": "MEDIUM",
  "risks": [
    "Issue summary is too short.",
    "Priority is not defined.",
    "Issue has no assignee."
  ],
  "suggestions": [
    "Add a clearer and more descriptive summary.",
    "Set a priority level for this issue.",
    "Assign an owner to avoid unclear responsibility."
  ],
  "ai_report": "AI-generated QA assessment..."
}
```

---

## Product Vision

QALens is designed to become a QA intelligence layer for Jira-based software teams.

The long-term vision is to provide:

- QA readiness scoring
- AI-generated test case suggestions
- Acceptance criteria analysis
- Bug report improvement
- Release readiness insights
- QA coverage analysis
- Team-level quality analytics
- Jira workflow intelligence

The product is especially useful for teams that want to improve issue quality before development starts.

---

## Core Features

### Implemented in the MVP

- Jira issue analysis
- QA quality scoring
- Risk level classification
- AI-generated QA assessment
- Suggestions for improving issue quality
- React dashboard for reviewing analysis results
- Markdown rendering for detailed AI reports

### Planned

- Full Jira OAuth flow
- Multi-issue project analysis
- Test case generation
- Acceptance criteria validation
- Release readiness dashboard
- Team analytics
- Historical QA quality trends
- CI/CD and test management integrations

---

## Technology Stack

### Current MVP

- React
- Vite
- FastAPI
- Python
- Jira API integration
- AI/LLM-based analysis
- React Markdown

### Planned / Future

- PostgreSQL
- Docker
- Authentication
- Multi-user workspace support
- Cloud deployment
- CI/CD integrations

---

## Project Structure

```text
qalens/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── integrations/
│   │   ├── schemas/
│   │   └── core/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── docs/
├── scripts/
└── README.md
```

---

## Running the Project Locally

### Backend

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

---

## Demo Flow

1. Start the backend.
2. Start the frontend.
3. Open the React app.
4. Enter an issue key such as:

```text
SCRUM-1
```

5. Click **Analyze**.
6. Review the QA score, risk level, risks, suggestions, and AI-generated QA report.

---

## Example Use Case

A Jira issue with a vague summary such as:

```text
Tarea 1
```

may receive:

- Low QA readiness
- Medium or high risk classification
- Suggestions to add acceptance criteria
- Suggestions to assign an owner
- Suggestions to clarify expected behavior
- AI-generated recommendations for QA next steps

This helps teams improve issue quality before development or testing begins.

---

## Roadmap

### Phase 1 — MVP

- Basic Jira issue analysis
- QA scoring engine
- AI report generation
- React dashboard
- Local demo mode

### Phase 2 — Jira Integration

- Jira OAuth connection
- Real Jira issue fetching
- Project-level analysis
- Multi-issue reports

### Phase 3 — QA Intelligence

- AI test case generation
- Acceptance criteria validation
- Bug report assistant
- Release readiness scoring

### Phase 4 — SaaS Platform

- User accounts
- Team workspaces
- Historical analytics
- Enterprise dashboards
- CI/CD and QA tool integrations

---

## Status

QALens is currently an early-stage MVP.

The current version demonstrates the core concept: using AI to evaluate Jira issue quality and generate actionable QA insights.

---

## License

MIT
