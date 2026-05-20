# Engineering Guardrails

This document is the human-readable version of the repository rules. It exists to keep contributors and AI assistants aligned with one architecture over time.

## Architecture Contract

The project has exactly two major layers:

1. `streamlit_app.py`
   - Streamlit UI only
   - file upload
   - pipeline execution
   - optional advanced manual stage execution
   - report display
2. `src/`
   - Python backend only
   - agents
   - use-case directories
   - structured locator registry
   - page objects
   - utility helpers
   - generated outputs inside each use case

Anything outside these boundaries should be treated as suspicious unless a human explicitly requested the change.

## Folder Responsibilities

### `src/use_cases/`

Use for use-case-specific assets only.

Pattern:

- one folder per use case such as `part_creation` or `bom_creation`
- `config.json` describes the use case
- `manual_steps.txt` stores the active manual steps
- `input_data.csv` stores the active input data
- `generated/` stores the use-case-specific outputs

Do not place shared page objects or shared locator knowledge here.

### `src/agents/`

Use for workflow orchestration modules such as:

- `pipeline_agent.py`
- `planner_agent.py`
- `mcp_snapshot_agent.py`
- `locator_agent.py`
- `generator_agent.py`
- `healer_agent.py`

Pattern:

- load `.env`
- gather local context files
- resolve the selected use case from `src/use_cases/use_case_manager.py`
- require the MCP snapshot where the workflow depends on live UI grounding
- call the hosted Ollama endpoint through `src/llm/ollama_client.py`
- write results into `src/use_cases/<use_case_id>/generated/`

The preferred product flow is:

- `pipeline_agent.py` for normal execution
- individual agents for debugging, reruns, or development

Do not place UI code or Playwright browser flow logic here.

### `src/pages/`

Use for Page Object Model classes only.

Pattern:

- one class per page
- constructor accepts Playwright `Page`
- locators defined in `__init__`
- public methods expose business actions
- use Playwright `expect`
- add `TODO` for unknown Teamcenter locators

Do not place CSV parsing or report writing here.

### `src/test_data/`

Use for typed CSV readers and test data conversion only.

### `src/knowledge/locator-registry/`

Use for structured stable locator records and human-readable notes by environment profile.

Pattern:

- one profile directory per Teamcenter environment
- `locator-registry.json` for structured locator truth
- `locator-notes.md` for rationale and operational notes

This is the preferred place to store approved locators over time.

### `src/mcp/`

Use for MCP transport and Playwright MCP integration only.

Pattern:

- stdio MCP client code
- tool discovery
- request and notification handling
- Playwright MCP specific wrappers

Do not place Streamlit UI code or page object logic here.

### `src/utils/`

Use for reusable helpers such as:

- file utilities
- locator builder and locator resolver helpers
- execution report writing
- evidence capture
- logging

Do not hide page logic or agent workflow here.

### `tests/`

Use for stable reviewed executable automation only.

Pattern:

- one stable test file per use case
- file name format `tests/test_<use_case>.py`
- shared page objects and shared helpers stay outside `tests/`

## Naming Rules

- agent files must end with `_agent.py`
- page files must end with `_page.py`
- tests must start with `test_`
- utilities use descriptive snake_case names
- MCP integration files use descriptive snake_case names inside `src/mcp/`

## Change Rules

When adding a feature:

1. Extend the nearest existing file if the responsibility already matches.
2. Add a new file only when the responsibility is truly new.
3. Put the new file in an existing approved folder.
4. Do not create a parallel architecture.

## Anti-Drift Rules

Never do these unless a human explicitly asks:

- add TypeScript or JavaScript
- replace Streamlit
- replace Python Playwright with another test runner
- move stable tests into a use-case generated folder
- split the same responsibility across multiple duplicate files
- create alternate page object styles in a new folder
- put MCP protocol code inside page objects or Streamlit directly
- store approved stable locators only in ad hoc markdown without updating the structured registry

## Review Checklist

Before accepting any AI-assisted change:

1. Did it keep the change inside the correct folder?
2. Did it preserve Python-only backend rules?
3. Did it avoid renaming or moving stable files?
4. Did it avoid overwriting generated and stable assets incorrectly?
5. Did it keep locators and page actions inside page objects?
6. Did it keep tester UI logic inside Streamlit?

If any answer is no, treat that change as drift and fix it immediately.
