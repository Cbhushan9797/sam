# Copilot Task Template

Use this when you ask Copilot to make a change. It keeps the request narrow and reduces drift.

```text
Follow `.github/copilot-instructions.md`, `docs/project-architecture.md`, `docs/use-case-development-guide.md`, and `docs/engineering-guardrails.md`.

Task:
[Describe the exact change]

Change scope:
- Update only these files: [list files]
- Do not create new folders
- Do not rename files
- Do not change architecture

Constraints:
- Keep the project Python only
- Keep Streamlit in `streamlit_app.py`
- Keep use-case-specific inputs and generated outputs under `src/use_cases/<use_case_id>/`
- Keep page objects in `src/pages/`
- Keep agents in `src/agents/`
- Keep MCP integration in `src/mcp/`
- Keep approved stable locators in `src/knowledge/locator-registry/`
- Keep stable automation in `tests/test_<use_case>.py`
- Put generated output only in `src/use_cases/<use_case_id>/generated/`
- Avoid hard waits
- Add `TODO` comments for unknown Teamcenter locators

Output format:
- First summarize what you changed
- Then show the exact code changes
- Then list any follow-up TODOs
```

## Good Example

```text
Follow `.github/copilot-instructions.md`, `docs/project-architecture.md`, `docs/use-case-development-guide.md`, and `docs/engineering-guardrails.md`.

Task:
Add a method in `src/pages/search_page.py` to clear the search box before entering a new part ID.

Change scope:
- Update only `src/pages/search_page.py`
- Do not create new folders
- Do not rename files
- Do not change architecture
```

## Bad Example

```text
Improve the framework and clean up the project.
```

The bad example is too broad and invites Copilot to drift.
