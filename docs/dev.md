# Meeting Notes Extractor — Development Guide

## Purpose

This document explains how to run, test, and work on the project locally.

It is intended for both human developers and AI coding agents operating on the repository.

---

## Development Workflow

General expectations:

* make the smallest change necessary
* keep changes localized
* update tests when logic changes
* update docs when behavior or setup changes
* verify changes locally before considering the task complete

---

## Local Setup

Open the repository in VS Code using the WSL extension, not through the Windows
filesystem view.

From a WSL shell:

```bash
code .
```

If VS Code is opened against the Windows-side path instead, Python discovery,
debugging, and test execution may use a Windows interpreter instead of the
Ubuntu virtual environment in `.venv`.

### Python Version

Use Python 3.11 or newer. CI currently runs on Python 3.11 and 3.12.

### Create Virtual Environment

```bash
make venv
```

### Activate Virtual Environment

#### macOS / Linux

```bash
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Install Dependencies

From the repository root:

```bash
make install-dev
```

If `.venv` is missing, `make install-dev` will create it first. If you want to
rebuild the environment from scratch, run:

```bash
make reset-venv
```

When dependency declarations change in `pyproject.toml`, update the committed lockfile:

```bash
make compile-deps
make sync-deps
```

---

## Common Commands

| Command | Purpose |
| --- | --- |
| `make venv` | Create `.venv` if needed and install development dependencies |
| `make reset-venv` | Delete and recreate `.venv`, then reinstall development dependencies |
| `make install-dev` | Sync `.venv` to the committed development lockfile |
| `make sync-deps` | Install the exact locked development dependencies |
| `make compile-deps` | Regenerate `requirements-dev.txt` after dependency changes |
| `make run` | Start the FastAPI app with reload enabled |
| `make smoke` | Post the checked-in sample request to the local `/extract` endpoint |
| `make smoke-ai` | Start a temporary local server with `EXTRACTOR_STRATEGY=ai` and send the sample request |
| `make lint` | Run Ruff checks and formatting verification |
| `make typecheck` | Run mypy |
| `make test` | Run the test suite |
| `make build` | Build the source distribution and wheel |
| `make clean` | Remove generated caches, bytecode, and build artifacts |

---

## Running the Backend

From the repository root:

```bash
make run
```

Expected local URL:

```text
http://127.0.0.1:8000
```

FastAPI docs should be available at:

```text
http://127.0.0.1:8000/docs
```

---

## Running Tests

From the repository root:

```bash
make lint
make typecheck
make test
make build
```

If a task changes business logic, schema behavior, or routes:

* update tests
* run lint before finishing
* run tests before finishing
* ensure the package still builds before finishing

Do not leave the repository in a state where tests fail unless explicitly instructed.

---

## Manual Smoke Test

With the server running locally:

```bash
make smoke
```

Use this when you want a quick end-to-end check without opening the browser or running
the full test suite.

The sample payload lives in `examples/extract-request.json`. You can edit that file,
or override the request file or URL for one-off runs:

```bash
SMOKE_REQUEST=examples/extract-request.json make smoke
SMOKE_URL=http://127.0.0.1:8000/extract make smoke
```

## AI Smoke Test

For changes that touch the AI path, run:

```bash
make smoke-ai
```

This command:

* verifies `OPENAI_API_KEY` is available
* starts a temporary local server with `EXTRACTOR_STRATEGY=ai`
* waits for the health endpoint
* posts `examples/extract-request.json`
* validates that the response matches the shared `ExtractResponse` contract
* checks that the sample produced at least one structured item
* prints the formatted JSON response
* includes the server log tail if startup or request handling fails

Optional overrides:

```bash
SMOKE_AI_REQUEST=examples/extract-request.json make smoke-ai
SMOKE_AI_PORT=8010 make smoke-ai
```

This check is intended for local and agentic validation of the live AI path.
It is not part of the default CI flow because it depends on secrets, network
access, and available OpenAI quota.

---

## Workspace Hygiene

The shared VS Code workspace hides common generated directories from Explorer and
search results:

* `.pytest_cache/`
* `.ruff_cache/`
* `build/`
* `dist/`
* `*.egg-info/`

This does not hide maintained folders such as `.github/` or `.vscode/`.

To remove generated directories entirely, run `make clean` from the repository root.

The canonical shared development commands live in `Makefile`. VS Code tasks and CI
should call `make` targets rather than duplicating shell commands.

Shared project settings live in `.vscode/settings.json`.

Personal editor preferences should go in your VS Code User Settings. This repository
also ignores `.vscode/settings.local.json` as a scratch file for personal workspace
preferences, but VS Code does not load that file automatically.

---

## Environment Variables

Expected environment variables may include:

* `OPENAI_API_KEY`
* `OPENAI_MODEL` (optional)
* `EXTRACTOR_STRATEGY` (optional)

The AI extractor now reads these variables:

* `OPENAI_API_KEY`: required when using the AI extraction strategy
* `OPENAI_MODEL`: optional override for the OpenAI model name; defaults to `gpt-5-mini`
* `EXTRACTOR_STRATEGY`: optional strategy selector for the app route; supports `deterministic` and `ai`, and defaults to `deterministic`

Recommended local setup:

1. Create an OpenAI API key in the OpenAI dashboard.
2. Copy `.env.example` to `.env`.
3. Replace the placeholder value in `.env` with your real key.
4. Optionally change `OPENAI_MODEL` in `.env` if you want to test another model.
5. Optionally set `EXTRACTOR_STRATEGY=ai` if you want the FastAPI route to use the AI extractor.

Example:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
OPENAI_API_KEY=your_real_openai_api_key
OPENAI_MODEL=gpt-5-mini
EXTRACTOR_STRATEGY=deterministic
```

`.env` is ignored by git, so local secrets should not be committed.
The application loads `.env` automatically, so you do not need to re-run `export ...`
commands every time you start work on the project.
 
Do not hardcode secrets.

---

## Development Conventions

### FastAPI

* keep route handlers thin
* place extraction logic outside the route layer
* use Pydantic models for request/response validation

### Testing

* prefer focused unit tests
* add tests for new logic
* avoid brittle tests tied to unnecessary implementation details
* keep API tests and lower-level unit tests balanced

### Documentation

Treat documentation ownership as:

* `README.md`: repository entrypoint and docs map
* `docs/dev.md`: setup, workflow, and contributor expectations
* `docs/api.md`: API contract only
* `docs/architecture.md`: boundaries and extension points
* `docs/product.md`: product goals and acceptance criteria

When setup, API behavior, or architecture changes:

* update relevant files in `docs/`
* update `README.md` if the change affects how someone uses or runs the project

---

## Adding a New Feature

Typical process:

1. update docs first if the API or behavior changes
2. implement code changes
3. update or add tests
4. run lint, type checks, tests, and build
5. verify docs still match implementation

---

## Debugging Expectations

When something fails:

* identify whether the issue is request validation, extraction logic, model output, or infrastructure
* prefer explicit errors over silent fallback behavior
* do not hide ambiguity or invalid output

---

## Non-Goals for Development

Unless explicitly requested:

* do not add major new dependencies
* do not introduce agent frameworks
* do not add persistence layers
* do not perform broad refactors unrelated to the task

---

## Pre-Completion Checklist

Before considering a task complete:

* code changes are minimal and targeted
* lint passes locally
* type checks pass locally
* tests have been updated if needed
* tests pass locally
* the package builds locally
* relevant docs have been updated
* no unrelated files were changed unnecessarily
