# Use-Case Development Guide

This document explains how to add or change Teamcenter use cases without breaking the framework structure.

## Goal

Every new Teamcenter flow should fit into the existing shared architecture.

Do not clone the framework for each use case.
Do not create new top-level folders for each flow.

## Existing Use Cases

### `part_creation`

Status:

- working stable reviewed Playwright flow exists
- shared page objects already support it

### `bom_creation`

Status:

- scaffold exists
- stable reviewed Playwright implementation is still pending

## How To Add A New Use Case

Create:

`src/use_cases/<new_use_case>/`

Required files:

- `config.json`
- `manual_steps.txt`
- `input_data.csv`
- `data_reader.py`
- `generated/`

Also create:

- `tests/test_<new_use_case>.py`

## `config.json` Expectations

Each use-case config should define:

- `id`
- `displayName`
- `description`
- `stableTestPath`
- `inputMode`
- `recordPluralLabel`
- `resultColumnLabels`

This lets Streamlit render the use case correctly without custom UI branching.

## What Belongs In `data_reader.py`

`data_reader.py` should:

- define the typed row model for the use case
- read `input_data.csv`
- validate required columns
- validate required values
- return typed objects for stable tests

Do not put browser logic here.

## What Belongs In The Stable Test

`tests/test_<use_case_id>.py` should:

- load `.env`
- resolve the use-case paths through `src/use_cases/use_case_manager.py`
- read typed input data from the use-case reader
- use shared page objects where possible
- create new page objects only when the Teamcenter screen is genuinely different
- write execution report and log into the selected use-case `generated/` folder

## Primary Runtime Entry Point

The primary runtime entry point for users is:

- `src/agents/pipeline_agent.py`

That pipeline should own the standard sequence:

1. planner
2. required MCP snapshot
3. locator generation
4. code generation
5. stable Playwright execution
6. automatic healing after failed execution

The Streamlit UI should favor this pipeline-first flow.
Individual stage buttons are only for debugging or selective reruns.

## Reuse Rules

Prefer reuse in this order:

1. existing shared page object methods
2. add a new method to an existing page object if the screen is the same
3. create a new page object only if the UI surface is truly new

Examples:

- reuse `login_page.py` for all use cases
- reuse `home_page.py` for common navigation
- reuse `search_page.py` if search behavior is shared
- add `bom_page.py` only if BOM screens are genuinely distinct

## Generated Outputs

Every use case should keep its generated artifacts isolated:

- `generated/testPlan.md`
- `generated/playwrightMcpSnapshot.md`
- `generated/locatorCandidates.md`
- `generated/generated_playwright.py`
- `generated/healingSuggestions.md`
- `generated/executionReport.json`
- `generated/testExecution.log`

Do not write new generated outputs into a shared `src/generated/` folder.

## Locator Knowledge Rules

Do not store approved locators only in loose markdown.

When a locator becomes stable:

1. keep the explanation in locator notes
2. promote the exact locator into the structured registry

If a Teamcenter environment differs, create or update the correct locator profile instead of hardcoding environment-specific conditions in random files.

## MCP Rules

Before locator generation or draft code generation:

- capture the required Playwright MCP snapshot

This should remain mandatory for all use cases unless the architecture is intentionally redesigned.

## Copilot Rules For Use-Case Work

When using Copilot for a use-case change:

- name the use case explicitly
- name the exact files allowed to change
- say whether the change is shared-framework or use-case-specific
- forbid new top-level folders
- forbid alternate architecture

Good request pattern:

```text
Follow `.github/copilot-instructions.md`, `docs/project-architecture.md`, and `docs/use-case-development-guide.md`.

Task:
Implement BOM creation stable execution flow.

Change scope:
- Update only `tests/test_bom_creation.py`
- Update only the required page objects in `src/pages/`
- Update only the BOM data reader if needed
- Do not create new top-level folders
- Do not change architecture
```

## Anti-Patterns

These are drift signals:

- creating `src/bom/` instead of `src/use_cases/bom_creation/`
- creating a separate Streamlit app for a single use case
- putting stable tests in generated folders
- duplicating shared login logic inside each test
- bypassing the locator registry
- changing the UI back to a required stage-by-stage clicking flow for normal users
- adding JavaScript or TypeScript automation next to the Python framework
