# Copilot Instructions For This Repository

This repository is intentionally strict. Follow the existing Python structure and do not drift away from it.

## Required Context

Before making a non-trivial change, read and follow:

- `README.md`
- `docs/project-architecture.md`
- `docs/use-case-development-guide.md`
- `docs/engineering-guardrails.md`
- `docs/copilot-working-guide.md`

## Non-Negotiable Rules

1. This project is Python only.
   - Do not introduce Node.js, TypeScript, JavaScript, `package.json`, or Playwright TypeScript files.
2. The frontend must stay in `streamlit_app.py`.
   - Do not move Streamlit logic into another UI framework.
3. Backend logic must stay under `src/`.
4. Use-case-specific inputs and generated artifacts must stay under `src/use_cases/<use_case_id>/`.
5. Stable executable browser automation must stay in `tests/test_<use_case>.py`.
   - Do not overwrite stable reviewed automation with generated code.
6. AI-generated code must stay in `src/use_cases/<use_case_id>/generated/generated_playwright.py`.
7. The primary user flow must remain pipeline-first through `src/agents/pipeline_agent.py`.
   - Do not change the normal UX back to a required stage-by-stage button flow.
8. Page Objects must stay in `src/pages/` and use the `*_page.py` naming pattern.
9. Agents must stay in `src/agents/` and use the `*_agent.py` naming pattern.
10. Shared helpers must stay in `src/utils/`.
11. MCP protocol and Playwright MCP integration must stay in `src/mcp/`.
12. CSV readers and structured test data helpers must stay in `src/test_data/`.
13. Locator knowledge and flow knowledge must stay in `src/knowledge/`.
14. Locator generation and automation code generation must require a valid Playwright MCP snapshot.
15. Approved stable locators must be written into `src/knowledge/locator-registry/` and not only into loose markdown.

## Change Behavior

1. Prefer editing an existing file over creating a parallel alternative.
2. Do not rename folders, move files, or change architecture unless explicitly asked.
3. Keep function and class names consistent with the existing style.
4. Add small focused changes, not broad rewrites.
5. Preserve Page Object Model boundaries.
6. Use `TODO` comments for unknown Teamcenter-specific locators instead of inventing brittle logic.
7. Avoid hard waits.
8. Avoid dynamic Teamcenter IDs and fragile XPath.
9. Never hardcode Teamcenter credentials.
10. Keep generated outputs file-based under the selected use case directory.
11. Keep individual stage controls as advanced/debug behavior only when editing Streamlit.

## File Ownership

- `streamlit_app.py`
  Owns the Streamlit UI only.
- `src/use_cases/<use_case_id>/`
  Own use-case-specific inputs, generated artifacts, and config only.
- `src/agents/*.py`
  Own backend agent orchestration only.
- `src/llm/*.py`
  Own Ollama communication and prompts only.
- `src/mcp/*.py`
  Own MCP transport and Playwright MCP integration only.
- `src/pages/*.py`
  Own UI interactions and page-level assertions only.
- `src/utils/*.py`
  Own reusable helpers only.
- `src/knowledge/locator-registry/*`
  Own structured locator truth and human-readable locator notes by environment profile.
- `tests/test_*.py`
  Own stable end-to-end Python Playwright execution flows by use case.

## Before Finishing A Change

After edits, make sure the repo still follows its guardrails:

1. Run `python scripts/check_project_structure.py`
2. Run `python -m compileall src tests streamlit_app.py`
3. If formatting is needed, run `python -m ruff format .`
4. If linting is needed, run `python -m ruff check .`

## If The Request Is Ambiguous

- Ask for clarification before performing a large refactor.
- If only one file needs to change, keep the change inside that file.
- If a new file is necessary, place it in the correct existing folder rather than creating a new architecture branch.
