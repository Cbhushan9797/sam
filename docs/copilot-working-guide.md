# Copilot Working Guide

Use this document when working with GitHub Copilot so changes stay aligned with the repository structure.

## Read These First

Before asking Copilot for any non-trivial change, tell it to follow:

- `.github/copilot-instructions.md`
- `docs/project-architecture.md`
- `docs/use-case-development-guide.md`
- `docs/engineering-guardrails.md`

## Recommended Prompt Prefix

Use this prefix before your actual task:

```text
Follow `.github/copilot-instructions.md`, `docs/project-architecture.md`, `docs/use-case-development-guide.md`, and `docs/engineering-guardrails.md`.

Do not drift from the existing Python multi-use-case Teamcenter architecture.
Do not create new top-level folders.
Do not rename files.
Do not replace shared framework components.
Keep stable tests separate from generated artifacts.
Keep the Streamlit UX pipeline-first.
```

## How To Ask Safely

Always specify:

- the use case name
- the exact files allowed to change
- whether the change is shared or use-case-specific
- what must not change

## Good Prompt Example

```text
Follow `.github/copilot-instructions.md`, `docs/project-architecture.md`, `docs/use-case-development-guide.md`, and `docs/engineering-guardrails.md`.

Task:
Add BOM row validation in the BOM use-case reader.

Change scope:
- Update only `src/use_cases/bom_creation/data_reader.py`
- Do not create new folders
- Do not rename files
- Do not change architecture

Constraints:
- Keep the project Python only
- Keep use-case-specific assets in `src/use_cases/bom_creation/`
- Do not modify Streamlit
- Do not modify stable tests unless absolutely necessary
```

## Another Good Prompt Example

```text
Follow `.github/copilot-instructions.md`, `docs/project-architecture.md`, `docs/use-case-development-guide.md`, and `docs/engineering-guardrails.md`.

Task:
Implement the stable BOM creation Playwright test using the existing framework.

Change scope:
- Update only `tests/test_bom_creation.py`
- Update only the required page objects in `src/pages/`
- Update only BOM-specific files under `src/use_cases/bom_creation/`
- Do not create new top-level folders
- Do not change the architecture contract

Constraints:
- Reuse shared login, home, and search behavior where possible
- Keep generated code separate from stable reviewed code
- Keep execution artifacts under `src/use_cases/bom_creation/generated/`
- Require MCP snapshot for locator and generator stages
```

## Bad Prompt Patterns

Avoid prompts like:

- `Improve the framework`
- `Clean up the whole project`
- `Refactor everything`
- `Add BOM support however you think is best`

These invite Copilot to drift.

## Rules Copilot Must Keep

- `streamlit_app.py` is the only frontend
- `src/agents/pipeline_agent.py` is the primary end-to-end workflow entry point
- `src/use_cases/` is the only use-case asset location
- `tests/test_<use_case>.py` is where stable flows live
- `src/use_cases/<use_case>/generated/` is where generated artifacts live
- `src/pages/` is where page objects live
- `src/mcp/` is where MCP code lives
- `src/knowledge/locator-registry/` stores approved locator truth
- manual per-stage controls are only advanced debugging helpers, not the primary product flow

## After Copilot Changes Code

Run:

```bash
python scripts/check_project_structure.py
python -m compileall src tests streamlit_app.py
python -m ruff format .
python -m ruff check .
```

If Copilot created new folders, duplicated architecture, or moved stable files, stop and fix that immediately.
