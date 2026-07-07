# AGENTS.md

## Project

Qalens is a QA intelligence assistant for Jira issues. It analyzes Jira issues, detects QA risks, suggests improvements, and generates test cases and AI reports for QA and development teams.

## General Rules

- Read the existing codebase before making changes.
- Prefer existing project patterns over new abstractions.
- Keep changes scoped to the user's request.
- Do not refactor unrelated files.
- Do not modify secrets, `.env` files, virtual environments, build output, or dependency folders.
- Do not revert user changes unless explicitly requested.
- Never run destructive Git commands such as `git reset --hard` or `git checkout --` unless explicitly requested.
- Check `git status` before staging or committing.
- Use small, reviewable commits.

## Backend

- Backend code lives in `backend/`.
- Follow the existing FastAPI structure.
- Keep schemas in `backend/app/schemas/`.
- Keep services in `backend/app/services/`.
- Keep AI prompt construction in the prompt builder or service layer.
- Validate inputs clearly.
- Avoid hardcoded secrets or credentials.

## Frontend

- Frontend code lives in `frontend/`.
- Follow the existing React structure.
- Keep UI changes consistent with the current app design.
- Build practical product screens, not marketing placeholders.
- Prioritize clear QA workflows, readable reports, and fast scanning.
- Make sure long reports, issue summaries, and test cases do not overflow or overlap.

## AI Analysis Behavior

- Do not invent Jira fields that are not present in the issue payload.
- Separate detected risks from suggestions.
- Prefer structured outputs where the frontend needs predictable rendering.
- Test cases should be specific, actionable, and connected to the issue context.
- Risk levels should be explainable from the available issue data.
- If issue data is incomplete, reflect that clearly in the analysis.

## Testing And Verification

- Run backend validation when backend files change.
- Run frontend build when frontend files change.
- Prefer targeted checks first, then broader builds if needed.
- If a test or build cannot be run, explain why.

## Git

- Inspect `git status` before staging.
- Stage only files related to the current task.
- Use clear commit messages.
- Do not commit unless the user explicitly asks for it.

## Final Response

- Summarize what changed.
- Mention what was tested.
- Mention anything that could not be verified.
- Keep the answer practical and concise.