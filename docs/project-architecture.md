# Project Architecture

This document is the architecture source of truth for `teamcenter-ai-playwright`.

## Project Intent

This repository is a Python-first Teamcenter automation platform with:

- Streamlit as the frontend control panel
- Python backend agents for AI-assisted planning and generation
- a pipeline agent as the primary workflow entry point
- Playwright MCP for required live browser grounding
- Python Playwright stable tests for real execution
- multi-use-case isolation under `src/use_cases/`

The design goal is to support many Teamcenter use cases without duplicating the framework.

## Top-Level Layers

### `streamlit_app.py`

Owns:

- use-case selection
- file upload
- one-click pipeline execution
- optional advanced manual stage execution for debugging
- command output display
- generated artifact display
- execution report display

Must not own:

- Playwright page object logic
- Ollama prompt logic
- MCP protocol transport
- CSV parsing logic

### `src/`

Owns all backend code.

Inside `src/`:

- `agents/` orchestrates workflow stages and the pipeline entry point
- `knowledge/` stores shared Teamcenter knowledge and stable locator registry
- `llm/` talks to hosted Ollama
- `mcp/` talks to Playwright MCP
- `pages/` stores shared page objects
- `test_data/` stores shared CSV helper utilities
- `use_cases/` stores use-case-specific assets and generated outputs
- `utils/` stores reusable helpers

### `tests/`

Owns stable, reviewed, executable Playwright flows by use case.

Stable tests are not generated files.

## Use-Case Model

Each Teamcenter use case must live under:

`src/use_cases/<use_case_id>/`

Each use case owns:

- `config.json`
- `manual_steps.txt`
- `input_data.csv`
- `data_reader.py`
- `generated/`

Each use case must also have a stable test in:

`tests/test_<use_case_id>.py`

Examples already present:

- `part_creation`
- `bom_creation`

## Shared vs Use-Case-Specific Responsibilities

### Shared

Keep these shared across use cases:

- login page
- common Teamcenter home navigation
- shared search behavior
- locator registry loading
- MCP client
- Ollama client
- evidence capture
- execution report writing

### Use-case-specific

Keep these isolated per use case:

- manual business steps
- CSV input schema
- generated plan
- generated MCP snapshot artifact
- generated locator suggestions
- generated draft automation file
- healing suggestions
- execution report
- execution log
- stable reviewed test file

## Runtime Flow

The expected flow for a use case is:

1. tester selects a use case in Streamlit
2. tester uploads manual steps and CSV
3. tester runs the pipeline from Streamlit
4. `pipeline_agent.py` runs planner agent and writes `generated/testPlan.md`
5. `pipeline_agent.py` runs MCP snapshot agent and writes `generated/playwrightMcpSnapshot.md`
6. `pipeline_agent.py` runs locator agent and writes `generated/locatorCandidates.md`
7. `pipeline_agent.py` runs generator agent and writes `generated/generated_playwright.py`
8. `pipeline_agent.py` runs the stable Playwright test in `tests/`
9. `pipeline_agent.py` runs healer agent automatically if the test fails

The manual individual stage controls still exist in the Streamlit UI, but they are advanced debugging controls rather than the primary workflow.

## MCP Requirement

Playwright MCP is required before locator generation and code generation.

Why:

- it grounds the AI against the live Teamcenter UI
- it reduces hallucinated locators
- it gives current accessibility and navigation context

Do not bypass the MCP snapshot stage for locator or generator changes unless a human explicitly changes the architecture.

## Locator Strategy

Locator knowledge has two layers:

1. structured locator truth
2. human-readable notes

Structured locator truth lives in:

- `src/knowledge/locator-registry/<profile>/locator-registry.json`

Human-readable notes live in:

- `src/knowledge/locator-registry/<profile>/locator-notes.md`

General Teamcenter knowledge lives in:

- `src/knowledge/teamcenterLocators.md`
- `src/knowledge/teamcenterFlows.md`

Runtime locator resolution should prefer:

1. approved registry locator
2. in-code fallback locator in page object

## Generated vs Stable Code

Generated code is an AI output proposal.

Generated code lives in:

- `src/use_cases/<use_case_id>/generated/generated_playwright.py`

Stable reviewed code lives in:

- `tests/test_<use_case_id>.py`

Never overwrite a stable test with generated content automatically.

## Non-Negotiable Architecture Rules

- keep the project Python-first
- keep Streamlit in `streamlit_app.py`
- keep the UI pipeline-first, not button-by-button as the primary user flow
- keep use-case-specific assets under `src/use_cases/`
- keep page objects under `src/pages/`
- keep stable tests under `tests/`
- keep MCP client code under `src/mcp/`
- keep locator truth under `src/knowledge/locator-registry/`
- avoid parallel architectures

## What Copilot Should Infer

When Copilot reads this repository, it should infer:

- this is a multi-use-case framework
- `part_creation` is the current working example
- `bom_creation` is the next intended stable implementation
- the framework is shared and reusable
- the primary user experience is one connected pipeline, not separate required button clicks
- stable tests are separate from generated outputs
- MCP grounding is mandatory for locator and code generation stages
