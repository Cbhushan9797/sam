# Teamcenter AI Playwright Automation

## Project Purpose

`teamcenter-ai-playwright` is a Python-first automation framework for Siemens Teamcenter. Manual testers upload plain English steps and structured CSV data through a Streamlit frontend. Python backend agents use a hosted Ollama endpoint plus a required Playwright MCP live browser snapshot to plan automation, suggest locators, generate draft Playwright code, execute stable reviewed flows, and produce healing guidance after failures.

The framework is now organized for multiple Teamcenter use cases. `part_creation` is the first working use case and `bom_creation` is scaffolded for the next phase.

## Architecture

The framework has four layers:

1. `streamlit_app.py`
   Streamlit control panel for uploads, command execution, logs, generated artifacts, and execution reports.
2. `src/agents/`
   Python workflow agents for planning, MCP snapshot capture, locator generation, code generation, and healing suggestions.
3. `src/knowledge/` and `src/pages/`
   Shared Teamcenter locator knowledge, structured locator registry, and reusable page objects.
4. `tests/`
   Stable reviewed Playwright execution flows by use case.

## Multi-Use-Case Structure

Use-case-specific files live under `src/use_cases/<use_case_id>/`.

Each use case owns:

- `config.json`
- `manual_steps.txt`
- `input_data.csv`
- `generated/`

Shared framework code stays outside the use-case folders:

- `src/agents/`
- `src/llm/`
- `src/mcp/`
- `src/pages/`
- `src/utils/`
- `src/knowledge/`

## Current Use Cases

### `part_creation`

- stable reviewed test exists in `tests/test_part_creation.py`
- page objects are already wired for this flow
- sample CSV and manual steps are included

### `bom_creation`

- use-case folder and inputs are scaffolded
- stable test placeholder exists in `tests/test_bom_creation.py`
- this is the next intended Teamcenter flow to implement

## Project Layout

```text
teamcenter-ai-playwright/
  .env.example
  .gitignore
  README.md
  pyproject.toml
  pytest.ini
  requirements.txt
  streamlit_app.py

  src/
    agents/
      planner_agent.py
      pipeline_agent.py
      mcp_snapshot_agent.py
      locator_agent.py
      generator_agent.py
      healer_agent.py
    knowledge/
      teamcenterLocators.md
      teamcenterFlows.md
      locator-registry/
        README.md
        default/
          teamcenter_generic/
            locator-registry.json
            locator-notes.md
    llm/
      ollama_client.py
      prompts.py
    mcp/
      playwright_mcp_client.py
      snapshot_artifact.py
    pages/
      login_page.py
      home_page.py
      part_creation_page.py
      search_page.py
    test_data/
      csv_utils.py
    use_cases/
      use_case_manager.py
      part_creation/
        config.json
        manual_steps.txt
        input_data.csv
        data_reader.py
        generated/
          testPlan.md
          playwrightMcpSnapshot.md
          locatorCandidates.md
          generated_playwright.py
          healingSuggestions.md
          executionReport.json
          testExecution.log
      bom_creation/
        config.json
        manual_steps.txt
        input_data.csv
        data_reader.py
        generated/
          testPlan.md
          playwrightMcpSnapshot.md
          locatorCandidates.md
          generated_playwright.py
          healingSuggestions.md
          executionReport.json
          testExecution.log
    utils/
      evidence.py
      execution_reporter.py
      file_utils.py
      locator_builder.py
      locator_resolver.py
      logger.py

  tests/
    test_part_creation.py
    test_bom_creation.py

  scripts/
    check_project_structure.py
```

## End-To-End Flow

1. Tester opens Streamlit.
2. Tester selects a Teamcenter use case such as `Part Creation` or `BOM Creation`.
3. Tester uploads the manual steps and CSV data for that use case.
4. Streamlit saves the files into the selected `src/use_cases/<use_case_id>/` folder.
5. Streamlit triggers the Pipeline Agent as the primary workflow entry point.
6. Pipeline Agent runs Planner Agent and writes `generated/testPlan.md`.
7. Pipeline Agent runs the MCP Snapshot Agent and writes `generated/playwrightMcpSnapshot.md`.
8. Pipeline Agent runs Locator Agent and writes `generated/locatorCandidates.md`.
9. Pipeline Agent runs Generator Agent and writes `generated/generated_playwright.py`.
10. Pipeline Agent runs the stable reviewed Playwright test under `tests/`.
11. If the test fails, Pipeline Agent triggers Healer Agent automatically.
12. Streamlit reads the selected use-case outputs and displays logs, metrics, results, and artifacts.

## Prerequisites

- Python 3.10 or later
- a reachable hosted Ollama endpoint
- Teamcenter test credentials with access to the target use case
- Chromium browser support for Playwright
- Node.js 18 or later for the official Playwright MCP server

Node.js is required because the Python backend launches the official Playwright MCP server through `npx @playwright/mcp@latest`.

## Installation

Run these commands from the project directory:

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

For moving the project to another machine, see:

- `docs/run-on-new-computer.md`

## Environment Setup

Copy `.env.example` to `.env` and set the values:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
TEAMCENTER_URL=https://teamcenter.example.com
TEAMCENTER_USERNAME=your.username
TEAMCENTER_PASSWORD=change-me
TEAMCENTER_USE_CASE=part_creation
TEAMCENTER_LOCATOR_PROFILE=default/teamcenter_generic
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_MCP_ENABLED=true
PLAYWRIGHT_MCP_COMMAND=npx
PLAYWRIGHT_MCP_ARGS=["-y","@playwright/mcp@latest","--headless","--output-dir","test-results/mcp"]
PLAYWRIGHT_MCP_TARGET_URL=
PLAYWRIGHT_MCP_TIMEOUT_SECONDS=120
```

Notes:

- `TEAMCENTER_USE_CASE` provides the default use case for backend commands.
- `PLAYWRIGHT_MCP_TARGET_URL` can stay empty. The MCP snapshot agent will then use `TEAMCENTER_URL`.
- `TEAMCENTER_LOCATOR_PROFILE` selects the structured locator registry profile.

## Start The Streamlit UI

```bash
streamlit run streamlit_app.py
```

The UI lets you:

- choose a use case
- upload manual steps
- upload CSV data
- preview the current CSV
- run one full connected pipeline
- optionally rerun individual stages for debugging
- inspect use-case-specific generated artifacts

## Upload Manual Steps And CSV

When you upload files in Streamlit:

- manual steps are saved to `src/use_cases/<use_case_id>/manual_steps.txt`
- CSV data is saved to `src/use_cases/<use_case_id>/input_data.csv`

The selected use case determines which files are read and updated.

## Run The Full Pipeline

Primary command:

```bash
python -m src.agents.pipeline_agent --use-case part_creation
python -m src.agents.pipeline_agent --use-case bom_creation
```

What it does:

1. generates the test plan
2. captures the required Playwright MCP snapshot
3. generates locator candidates
4. generates draft Playwright code
5. runs the stable Playwright test
6. generates healing suggestions automatically if the test fails

## Capture The Required Playwright MCP Snapshot

This step is required before locator generation and code generation.

```bash
python -m src.agents.mcp_snapshot_agent --use-case part_creation
python -m src.agents.mcp_snapshot_agent --use-case bom_creation
```

Writes:

- `src/use_cases/<use_case_id>/generated/playwrightMcpSnapshot.md`

## Generate Test Plan

```bash
python -m src.agents.planner_agent --use-case part_creation
python -m src.agents.planner_agent --use-case bom_creation
```

Writes:

- `src/use_cases/<use_case_id>/generated/testPlan.md`

## Generate Locator Candidates

```bash
python -m src.agents.locator_agent --use-case part_creation
python -m src.agents.locator_agent --use-case bom_creation
```

Writes:

- `src/use_cases/<use_case_id>/generated/locatorCandidates.md`

This step will stop if the required MCP snapshot is missing or invalid.

## Generate Playwright Code

```bash
python -m src.agents.generator_agent --use-case part_creation
python -m src.agents.generator_agent --use-case bom_creation
```

Writes:

- `src/use_cases/<use_case_id>/generated/generated_playwright.py`

Generated code stays separate from stable reviewed tests.

## Run The Stable Playwright Tests

Current stable commands:

```bash
python -m pytest tests/test_part_creation.py -s
python -m pytest tests/test_bom_creation.py -s
```

Right now:

- `test_part_creation.py` is the working reviewed flow
- `test_bom_creation.py` is a scaffold placeholder

The part creation flow:

1. reads CSV records from `src/use_cases/part_creation/input_data.csv`
2. opens Teamcenter using `.env`
3. logs in using configured credentials
4. creates, saves, verifies, and searches each part
5. captures evidence screenshots
6. writes execution results to `src/use_cases/part_creation/generated/executionReport.json`
7. writes logs to `src/use_cases/part_creation/generated/testExecution.log`

## Generate Healing Suggestions

```bash
python -m src.agents.healer_agent --use-case part_creation
python -m src.agents.healer_agent --use-case bom_creation
```

Writes:

- `src/use_cases/<use_case_id>/generated/healingSuggestions.md`

## View Execution Results

Streamlit reads the selected use-case report and shows:

- total records
- passed
- failed
- total time taken
- average time per record
- execution result table
- screenshot paths when available

Execution artifacts live under:

- `src/use_cases/<use_case_id>/generated/executionReport.json`
- `src/use_cases/<use_case_id>/generated/testExecution.log`
- `test-results/evidence/<use_case_id>/`

## Locator Knowledge Strategy

Shared Teamcenter knowledge is stored in:

- `src/knowledge/teamcenterLocators.md`
- `src/knowledge/teamcenterFlows.md`

Approved stable locator truth is stored in:

- `src/knowledge/locator-registry/default/teamcenter_generic/locator-registry.json`
- `src/knowledge/locator-registry/default/teamcenter_generic/locator-notes.md`

Use the registry for exact approved locators and the markdown notes for rationale, validation history, and environment-specific guidance.

## How To Add More Teamcenter Use Cases

To add a new use case later:

1. create `src/use_cases/<new_use_case>/`
2. add `config.json`
3. add `manual_steps.txt`
4. add `input_data.csv`
5. add `data_reader.py`
6. add `generated/` placeholder artifacts
7. add a stable test such as `tests/test_<new_use_case>.py`
8. reuse shared page objects where possible
9. add new page objects only when the Teamcenter screen is genuinely new

This keeps the framework shared while isolating use-case-specific artifacts.

## Commands

```bash
pip install -r requirements.txt
python -m playwright install chromium
streamlit run streamlit_app.py
python -m src.agents.pipeline_agent --use-case part_creation
python -m src.agents.planner_agent --use-case part_creation
python -m src.agents.mcp_snapshot_agent --use-case part_creation
python -m src.agents.locator_agent --use-case part_creation
python -m src.agents.generator_agent --use-case part_creation
python -m pytest tests/test_part_creation.py -s
python -m src.agents.healer_agent --use-case part_creation
python -m src.agents.pipeline_agent --use-case bom_creation
python -m src.agents.planner_agent --use-case bom_creation
python -m src.agents.mcp_snapshot_agent --use-case bom_creation
python -m src.agents.locator_agent --use-case bom_creation
python -m src.agents.generator_agent --use-case bom_creation
python -m pytest tests/test_bom_creation.py -s
python -m src.agents.healer_agent --use-case bom_creation
```

## Keep Copilot Aligned

To reduce drift with Copilot:

1. keep `.github/copilot-instructions.md`
2. keep `docs/project-architecture.md`
3. keep `docs/use-case-development-guide.md`
4. keep `docs/copilot-working-guide.md`
5. keep `docs/engineering-guardrails.md`
6. use `docs/copilot-task-template.md`
7. keep tasks narrow and file-scoped
8. validate after AI-assisted changes

Validation commands:

```bash
python scripts/check_project_structure.py
python -m compileall src tests streamlit_app.py
python -m ruff format .
python -m ruff check .
```

## Playwright MCP References

- [Playwright MCP introduction](https://playwright.dev/mcp/introduction)
- [Playwright MCP getting started](https://playwright.dev/docs/getting-started-mcp)
- [MCP architecture and tools](https://modelcontextprotocol.io/docs/learn/architecture)
