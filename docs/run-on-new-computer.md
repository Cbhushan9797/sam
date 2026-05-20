# Run On A New Computer

This guide explains how to move and run `teamcenter-ai-playwright` on another machine.

## What To Copy

Copy the whole project folder:

- `teamcenter-ai-playwright/`

You can move it by:

- zip file
- USB drive
- shared drive
- git clone if the project is stored in a repository

## What Not To Rely On Copying

Do not depend on old runtime folders from another machine:

- `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- `.ruff_cache/`
- `test-results/`

These can be recreated on the new machine.

## Software Needed On The New Computer

Install:

- Python 3.10 or later
- Node.js 18 or later

Why Node.js is needed:

- Playwright MCP runs through `npx`

## Open The Project Folder

Open PowerShell in the project folder:

```powershell
cd C:\path\to\teamcenter-ai-playwright
```

## Create And Activate A Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

## Install Python Dependencies

```powershell
pip install -r requirements.txt
```

## Install Playwright Browser Support

```powershell
python -m playwright install chromium
```

## Create The Environment File

Create `.env` from `.env.example`:

```powershell
copy .env.example .env
notepad .env
```

Fill in the real values for:

- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `TEAMCENTER_URL`
- `TEAMCENTER_USERNAME`
- `TEAMCENTER_PASSWORD`

Important notes:

- if `OLLAMA_BASE_URL` points to a hosted server, local Ollama is not required
- if `OLLAMA_BASE_URL` points to `localhost`, Ollama must be running on that machine
- `TEAMCENTER_USE_CASE=part_creation` is the default starting use case

## Validate The Project

Run:

```powershell
python scripts/check_project_structure.py
python -m compileall src tests streamlit_app.py
```

If both pass, the project is structurally ready.

## Run The Streamlit UI

```powershell
streamlit run streamlit_app.py
```

Then in the UI:

1. select the use case
2. upload manual steps if needed
3. upload CSV input if needed
4. click `Run Full AI Automation Pipeline`

## What The Main Pipeline Does

The main pipeline runs:

1. planner agent
2. required Playwright MCP snapshot agent
3. locator agent
4. generator agent
5. stable Playwright test
6. healer agent automatically if the test fails

## Run From Command Line Without Streamlit

For Part Creation:

```powershell
python -m src.agents.pipeline_agent --use-case part_creation
```

For BOM Creation:

```powershell
python -m src.agents.pipeline_agent --use-case bom_creation
```

## Current Use-Case Status

- `part_creation` is the working stable flow
- `bom_creation` is scaffolded and not yet fully implemented as a stable reviewed Playwright flow

## Common Problems

### `npx` not found

Cause:

- Node.js is not installed

Fix:

- install Node.js 18 or later

### Playwright browser missing

Cause:

- Chromium support was not installed yet

Fix:

```powershell
python -m playwright install chromium
```

### `.env` is incomplete

Cause:

- Teamcenter or Ollama settings are missing

Fix:

- complete the `.env` file with real values

### Teamcenter login fails

Cause:

- incorrect URL, username, or password

Fix:

- verify `TEAMCENTER_URL`
- verify `TEAMCENTER_USERNAME`
- verify `TEAMCENTER_PASSWORD`

### Ollama call fails

Cause:

- hosted Ollama endpoint is unreachable
- model name is incorrect

Fix:

- verify `OLLAMA_BASE_URL`
- verify `OLLAMA_MODEL`
- verify network access to the Ollama server

## Recommended Quick Start

From a fresh machine:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
copy .env.example .env
streamlit run streamlit_app.py
```

After that, fill `.env`, open the UI, and run the full pipeline.
