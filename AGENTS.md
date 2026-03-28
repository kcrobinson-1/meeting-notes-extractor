# AGENTS.md

## Purpose

This file defines persistent instructions for AI agents (e.g., Codex) operating on this repository.

Agents must follow these rules unless explicitly overridden by user instructions.

---

## Core Principles

* Make the smallest change necessary to satisfy the task
* Do not modify unrelated files or behavior
* Prefer clarity over cleverness
* Keep implementations simple and explicit

---

## Project Context

* Backend: FastAPI (Python)
* Purpose: Extract structured data from meeting notes
* Docs in `docs/` are the source of truth for API behavior

---

## Coding Guidelines

* Use Pydantic models for all request/response schemas
* Keep route handlers thin (no heavy logic in endpoints)
* Place business logic in separate modules (e.g., `extractor.py`)
* Prefer explicit typing
* Avoid introducing new dependencies unless necessary

---

## Testing Requirements

When making any logic change:

* Update existing unit tests or add new tests
* Ensure meaningful coverage of new behavior
* Run all unit tests before completing the task
* Do not leave failing tests unless explicitly instructed

If tests fail:

* Diagnose root cause
* Fix implementation or tests
* Re-run until passing

---

## Documentation Requirements

When behavior changes:

* Update relevant docs in `docs/`
* Update `README.md` if setup, usage, or behavior changes
* Ensure documentation matches actual implementation

Do not rewrite entire docs unnecessarily

---

## API Contract Rules

* Follow `docs/api.md` exactly
* Do not introduce fields not defined in the spec
* Do not remove fields without updating the spec
* If implementation conflicts with spec, update the spec first

---

## Change Discipline

* Avoid broad refactors unless explicitly requested
* Do not reformat large sections of code or docs unnecessarily
* Preserve existing structure and naming unless required

---

## Before Completing a Task

Always:

* Summarize files changed
* Summarize tests executed and results
* Call out any assumptions made

---

## Non-Goals

Unless explicitly requested:

* Do not introduce agent frameworks (LangChain, LangGraph, etc.)
* Do not add persistence layers (databases)
* Do not add complex infrastructure

Keep the system minimal and focused

---

## Failure Handling

If a task cannot be completed:

* Explain why clearly
* Identify missing information
* Suggest next steps

Do not guess or fabricate implementation details

---

## Priority Order

1. User instructions
2. This file (AGENTS.md)
3. Existing codebase patterns
